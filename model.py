import cv2
import numpy as np
from ultralytics import YOLO
def enhance(frame):
    gamma = 1.5
    invGamma = 1.0 / gamma
    table = np.array(
        [((i / 255.0) ** invGamma) * 255 for i in range(256)]
    ).astype("uint8")
    return cv2.LUT(frame, table)


class Detector:

    def __init__(self,
                 model_path="/home/keshav/rajan/new_pipeline/models/best_openvino_model",
                 img_size=(640,640)):

        self.model = YOLO(model_path, task="detect")
        self.img_size = img_size
        self.imgsz = max(img_size)

    def process_frame(self, frame):
        frame = enhance(frame)
        results = self.model.track(
            frame,
            persist=True,
            classes=0,
            conf=0.15,
            iou=0.5,
            imgsz=self.imgsz,
            tracker="botsort.yaml",
            verbose=False,
            stream=False,
            augment=False,
            agnostic_nms=True
        )

        result = results[0]
        output = frame.copy()

        if result.boxes is None or len(result.boxes) == 0:
            return output

        boxes = result.boxes.xyxy.cpu().numpy()
        confs = result.boxes.conf.cpu().numpy()

        ids = None
        if result.boxes.id is not None:
            ids = result.boxes.id.cpu().numpy().astype(int)

        for idx, (box, conf) in enumerate(zip(boxes, confs)):

            x1, y1, x2, y2 = box.astype(int)

            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(frame.shape[1], x2)
            y2 = min(frame.shape[0], y2)

            cv2.rectangle(output, (x1, y1), (x2, y2), (0, 255, 0), 2)

            if ids is not None:
                label = f"id:{ids[idx]} {conf:.2f}"
            else:
                label = f"person {conf:.2f}"

            font_scale = max(0.35, self.imgsz / 1800)
            thickness = 1

            (tw, th), _ = cv2.getTextSize(
                label,
                cv2.FONT_HERSHEY_SIMPLEX,
                font_scale,
                thickness
            )

            bg_y1 = max(0, y1 - th - 4)

            cv2.rectangle(
                output,
                (x1, bg_y1),
                (x1 + tw + 4, y1),
                (0, 255, 0),
                -1
            )

            cv2.putText(
                output,
                label,
                (x1 + 2, max(th, y1 - 2)),
                cv2.FONT_HERSHEY_SIMPLEX,
                font_scale,
                (0, 0, 0),
                thickness,
                cv2.LINE_AA
            )

        return output