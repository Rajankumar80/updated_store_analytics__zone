import os
os.environ.setdefault("QT_QPA_PLATFORM", "xcb")
import gi
gi.require_version("Gst", "1.0")
from gi.repository import Gst
import numpy as np
import multiprocessing as mp
import signal
import sys
import time
import cv2
from model import Detector


def make_no_signal_frame(width, height):
    try:
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:] = (30, 30, 30)
        text = "NO SIGNAL"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = width / 400.0
        thickness = max(2, int(font_scale * 2))
        (tw, th), _ = cv2.getTextSize(text, font, font_scale, thickness)
        tx = (width - tw) // 2
        ty = (height + th) // 2
        cv2.putText(frame, text, (tx + 2, ty + 2), font, font_scale, (0, 0, 0), thickness + 2, cv2.LINE_AA)
        cv2.putText(frame, text, (tx, ty), font, font_scale, (60, 60, 60), thickness, cv2.LINE_AA)
        line_color = (50, 50, 50)
        spacing = max(20, width // 32)
        for i in range(0, height, spacing):
            cv2.line(frame, (0, i), (width, i), line_color, 1)
        for j in range(0, width, spacing):
            cv2.line(frame, (j, 0), (j, height), line_color, 1)
        return frame
    except Exception:
        return np.zeros((height, width, 3), dtype=np.uint8)


class StreamProcessor(mp.Process):
    def __init__(self, cam_id, url, frame_queue, img_size, buffer_size, fps):
        super().__init__()
        self.cam_id = cam_id
        self.url = url
        self.frame_queue = frame_queue
        self.width, self.height = img_size
        self.buffer_size = buffer_size
        self.fps = fps
        self.running = mp.Value('b', True)
        self.pipeline = None

    def _build_pipeline(self):
        try:
            return Gst.parse_launch(
                f'rtspsrc location="{self.url}" protocols=tcp latency=300 retry=3 timeout=5000000 ! '
                f'rtph265depay ! h265parse ! avdec_h265 ! '
                f'videorate ! video/x-raw,framerate={self.fps}/1 ! '
                f'videoconvert ! videoscale method=3 ! '
                f'video/x-raw,width={self.width},height={self.height},format=BGR ! '
                f'appsink name=sink emit-signals=true sync=false max-buffers={self.buffer_size} drop=true'
            )
        except Exception:
            return None

    def on_sample(self, sink):
        try:
            sample = sink.emit("pull-sample")
            if not sample:
                return Gst.FlowReturn.OK
            buf = sample.get_buffer()
            res, map_info = buf.map(Gst.MapFlags.READ)
            if not res:
                return Gst.FlowReturn.OK
            try:
                frame = np.ndarray(
                    (self.height, self.width, 3),
                    buffer=map_info.data,
                    dtype=np.uint8
                ).copy()
                try:
                    if self.frame_queue.full():
                        self.frame_queue.get_nowait()
                    self.frame_queue.put_nowait(frame)
                except Exception:
                    pass
            finally:
                buf.unmap(map_info)
        except Exception:
            pass
        return Gst.FlowReturn.OK

    def _cleanup(self):
        try:
            if self.pipeline:
                self.pipeline.set_state(Gst.State.NULL)
                self.pipeline.get_state(timeout=2 * Gst.SECOND)
        except Exception:
            pass
        finally:
            self.pipeline = None

    def run(self):
        try:
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            signal.signal(signal.SIGTERM, lambda s, f: setattr(self.running, 'value', False))
        except Exception:
            pass
        try:
            Gst.init(None)
        except Exception:
            return
        while self.running.value:
            try:
                self.pipeline = self._build_pipeline()
                if self.pipeline is None:
                    raise RuntimeError()
                try:
                    sink = self.pipeline.get_by_name("sink")
                    sink.connect("new-sample", self.on_sample)
                except Exception:
                    raise RuntimeError()
                ret = self.pipeline.set_state(Gst.State.PLAYING)
                if ret == Gst.StateChangeReturn.FAILURE:
                    raise RuntimeError()
                try:
                    bus = self.pipeline.get_bus()
                    while self.running.value:
                        try:
                            msg = bus.timed_pop(100 * Gst.MSECOND)
                            if msg:
                                if msg.type == Gst.MessageType.ERROR:
                                    break
                                elif msg.type == Gst.MessageType.EOS:
                                    break
                        except Exception:
                            break
                except Exception:
                    pass
            except Exception:
                pass
            finally:
                self._cleanup()
            if self.running.value:
                try:
                    time.sleep(3)
                except Exception:
                    pass


class MultiCameraManager:
    def __init__(self, cameras, buffer_size=2, fps=15, img_size=(640, 640)):
        self.urls = cameras
        self.img_size = img_size
        self.buffer_size = buffer_size
        self.fps = fps
        self.queues = []
        self.processes = []
        self._stopped = False
        self._no_signal_frames = {}
        self._last_frame_time = {}
        self._current_frames = {}

        self.detectors = [Detector(img_size=img_size) for _ in cameras]

        try:
            self.queues = [mp.Queue(maxsize=buffer_size) for _ in cameras]
        except Exception:
            sys.exit(1)

        try:
            no_signal = make_no_signal_frame(img_size[0], img_size[1])
            for i in range(len(cameras)):
                self._no_signal_frames[i] = no_signal
                self._last_frame_time[i] = time.time()
                self._current_frames[i] = no_signal
        except Exception:
            pass

        try:
            signal.signal(signal.SIGINT, self._shutdown)
            signal.signal(signal.SIGTERM, self._shutdown)
        except Exception:
            pass

        for i, url in enumerate(self.urls):
            try:
                p = StreamProcessor(i, url, self.queues[i], self.img_size, self.buffer_size, self.fps)
                p.daemon = True
                p.start()
                self.processes.append(p)
            except Exception:
                pass

    def _run_inference(self, frame, cam_id):
        h, w = self.img_size[1], self.img_size[0]
        if frame.shape[:2] != (h, w):
            frame = cv2.resize(frame, (w, h), interpolation=cv2.INTER_LINEAR)
        annotated = self.detectors[cam_id].process_frame(frame)
        label = f"CAM {cam_id}"
        font_scale = max(0.5, self.img_size[0] / 900)
        thickness = max(1, int(font_scale * 2))
        cv2.putText(annotated, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 0), thickness, cv2.LINE_AA)
        return annotated

    def _update_frames(self):
        for cam_id, q in enumerate(self.queues):
            latest = None
            try:
                while not q.empty():
                    try:
                        latest = q.get_nowait()
                    except Exception:
                        break
            except Exception:
                pass

            if latest is not None:
                self._last_frame_time[cam_id] = time.time()
                processed_frame = self._run_inference(latest, cam_id)
                self._current_frames[cam_id] = processed_frame
            else:
                elapsed = time.time() - self._last_frame_time.get(cam_id, 0)
                if elapsed > 2.0:
                    self._current_frames[cam_id] = self._no_signal_frames.get(cam_id)

    def display_streams(self):
        win_w = self.img_size[0] * len(self.urls)
        win_h = self.img_size[1]
        cv2.namedWindow("Multi Camera View", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Multi Camera View", win_w, win_h)
        delay = max(1, int(1000 / self.fps))

        try:
            while not self._stopped:
                self._update_frames()
                frames = []
                for i in range(len(self.urls)):
                    f = self._current_frames[i]
                    if f is None or f.shape[:2] != (self.img_size[1], self.img_size[0]):
                        f = self._no_signal_frames[i]
                    frames.append(f)
                combined = np.hstack(frames)
                cv2.imshow("Multi Camera View", combined)
                if cv2.waitKey(delay) & 0xFF == ord('q'):
                    break
        except Exception:
            pass
        finally:
            self.stop()
            cv2.destroyAllWindows()

    def stop(self):
        if self._stopped:
            return
        self._stopped = True
        for p in self.processes:
            try:
                p.running.value = False
            except Exception:
                pass
        for p in self.processes:
            try:
                if p.is_alive():
                    os.kill(p.pid, signal.SIGTERM)
            except Exception:
                pass
        for p in self.processes:
            try:
                if p.is_alive():
                    p.join(timeout=5)
                    if p.is_alive():
                        p.kill()
                        p.join(timeout=2)
            except Exception:
                pass
        for q in self.queues:
            try:
                while not q.empty():
                    try:
                        q.get_nowait()
                    except Exception:
                        break
                q.close()
                q.join_thread()
            except Exception:
                pass
        self.processes.clear()

    def _shutdown(self, sig=None, frame=None):
        try:
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            signal.signal(signal.SIGTERM, signal.SIG_DFL)
        except Exception:
            pass
        self.stop()
        try:
            cv2.destroyAllWindows()
        except Exception:
            pass
        sys.exit(0)