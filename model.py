import cv2
import numpy as np
import json
import time
from ultralytics import YOLO


ZONE_FILE    = "/home/keshav/rajan/new_pipeline/zones_runtime.json"
METRICS_FILE = "zone_metrics.json"


def enhance(frame):
    gamma    = 1.5
    invGamma = 1.0 / gamma
    table    = np.array(
        [((i / 255.0) ** invGamma) * 255 for i in range(256)]
    ).astype("uint8")
    return cv2.LUT(frame, table)


def point_in_polygon(point, polygon):
    polygon = np.array(polygon, dtype=np.float32)
    return cv2.pointPolygonTest(polygon, point, False) >= 0


class Detector:

    def __init__(self, camera_name="cam_entry"):

        self.model = YOLO("yolov8x.pt")

        # Load zones + homography
        with open(ZONE_FILE) as f:
            data = json.load(f)[camera_name]

        self.homography = None
        if data.get("homography") is not None:
            self.homography = np.array(data["homography"], dtype=np.float32)

        self.zones_pixel = {}
        self.zones_world = {}
        for name, info in data["zones"].items():
            self.zones_pixel[name] = info["pixel"]
            self.zones_world[name] = info["world"]

        # Zone state tracking
        self.zone_state    = {name: set() for name in self.zones_pixel}
        self.zone_prev     = {}
        self.metrics_log   = []
        self.last_log_time = time.time()

        # Floor map config — tune to your store size
        # MAP_SCALE = pixels per metre
        # MAP_W / MAP_H = canvas size in pixels
        # Example: store 6m x 5m  →  MAP_W=6*150=900, MAP_H=5*150=750
        self.MAP_SCALE = 150
        self.MAP_W     = 900
        self.MAP_H     = 750

    # ------------------------------------------------
    # Pixel -> World coordinate conversion
    # ------------------------------------------------
    def pixel_to_world(self, x, y):
        if self.homography is None:
            return None
        pt    = np.array([[[x, y]]], dtype=np.float32)
        world = cv2.perspectiveTransform(pt, self.homography)
        return world[0][0]

    # ------------------------------------------------
    # Draw top-down floor map
    # ------------------------------------------------
    def draw_floor_map(self, tracks):

        floor_map = np.ones((self.MAP_H, self.MAP_W, 3), dtype=np.uint8) * 25

        # grid every 1 metre
        for x in range(0, self.MAP_W, self.MAP_SCALE):
            cv2.line(floor_map, (x, 0), (x, self.MAP_H), (50, 50, 50), 1)
        for y in range(0, self.MAP_H, self.MAP_SCALE):
            cv2.line(floor_map, (0, y), (self.MAP_W, y), (50, 50, 50), 1)

        # metre axis labels
        for i in range(self.MAP_W // self.MAP_SCALE + 1):
            cv2.putText(floor_map, f"{i}m",
                        (i * self.MAP_SCALE + 3, 14),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (80, 80, 80), 1)
        for i in range(self.MAP_H // self.MAP_SCALE + 1):
            cv2.putText(floor_map, f"{i}m",
                        (3, i * self.MAP_SCALE + 14),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (80, 80, 80), 1)

        # zone colours
        zone_colors = {
            "billing":  (200,  60,  60),
            "cashier":  ( 60, 160, 200),
            "security": ( 60, 200,  60),
        }

        # draw zones in world space
        for name, poly_world in self.zones_world.items():
            if len(poly_world) < 3:
                continue
            color = zone_colors.get(name, (150, 150, 150))
            pts = np.array([
                [int(p[0] * self.MAP_SCALE), int(p[1] * self.MAP_SCALE)]
                for p in poly_world
            ], dtype=np.int32)

            overlay = floor_map.copy()
            cv2.fillPoly(overlay, [pts], color)
            cv2.addWeighted(overlay, 0.35, floor_map, 0.65, 0, floor_map)
            cv2.polylines(floor_map, [pts], True, color, 2)

            cx    = int(np.mean(pts[:, 0]))
            cy    = int(np.mean(pts[:, 1]))
            count = len(self.zone_state[name])
            cv2.putText(floor_map, name,
                        (cx - 25, cy - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            cv2.putText(floor_map, f"n={count}",
                        (cx - 18, cy + 14),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 100), 1)

        # draw tracked people
        for track in tracks:
            world_pt = self.pixel_to_world(track["foot"][0], track["foot"][1])
            if world_pt is None:
                continue
            mx = int(world_pt[0] * self.MAP_SCALE)
            my = int(world_pt[1] * self.MAP_SCALE)
            if not (0 <= mx < self.MAP_W and 0 <= my < self.MAP_H):
                continue
            color = (0, 80, 255) if track["zones"] else (0, 220, 220)
            cv2.circle(floor_map, (mx, my), 8, color, -1)
            cv2.circle(floor_map, (mx, my), 9, (255, 255, 255), 1)
            cv2.putText(floor_map, str(track["id"]),
                        (mx + 10, my + 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

        # legend
        lx, ly = self.MAP_W - 130, self.MAP_H - 45
        cv2.circle(floor_map, (lx, ly),      7, (0, 220, 220), -1)
        cv2.putText(floor_map, "open area", (lx + 12, ly + 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (180, 180, 180), 1)
        cv2.circle(floor_map, (lx, ly + 20), 7, (0, 80, 255), -1)
        cv2.putText(floor_map, "in zone",   (lx + 12, ly + 24),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (180, 180, 180), 1)

        # title bar
        cv2.rectangle(floor_map, (0, 0), (self.MAP_W, 22), (40, 40, 40), -1)
        cv2.putText(floor_map, "STORE FLOOR MAP  (bird's-eye view)",
                    (self.MAP_W // 2 - 140, 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 220, 220), 1)

        return floor_map

    # ------------------------------------------------
    # Process a single frame — called from main.py
    # ------------------------------------------------
    def process_frame(self, frame):

        frame = enhance(frame)

        results = self.model.track(
            frame,
            persist=True,
            classes=0,
            conf=0.3,
            iou=0.7,
            tracker="botsort.yaml",
            verbose=False
        )

        result    = results[0]
        output    = frame.copy()
        active_ids = set()
        tracks    = []

        if result.boxes is not None and result.boxes.id is not None:

            boxes = result.boxes.xyxy.cpu().numpy()
            ids   = result.boxes.id.cpu().numpy().astype(int)

            for box, tid in zip(boxes, ids):

                x1, y1, x2, y2 = box.astype(int)
                cx = int((x1 + x2) / 2)
                cy = int(y2)
                foot_pixel = (cx, cy)

                active_ids.add(tid)
                world_pt = self.pixel_to_world(cx, cy)

                cv2.circle(output, foot_pixel, 4, (0, 255, 255), -1)

                person_zones = []
                for zone_name in self.zones_pixel:
                    inside = False
                    if world_pt is not None and len(self.zones_world[zone_name]) >= 3:
                        inside = point_in_polygon(tuple(world_pt), self.zones_world[zone_name])
                    else:
                        inside = point_in_polygon(foot_pixel, self.zones_pixel[zone_name])

                    prev = self.zone_prev.get((tid, zone_name), False)
                    if inside and not prev:
                        self.zone_state[zone_name].add(tid)
                    if not inside and prev:
                        self.zone_state[zone_name].discard(tid)
                    self.zone_prev[(tid, zone_name)] = inside
                    if inside:
                        person_zones.append(zone_name)

                cv2.rectangle(output, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(output, f"id:{tid}", (x1, y1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                tracks.append({
                    "id":    tid,
                    "bbox":  (x1, y1, x2, y2),
                    "foot":  foot_pixel,
                    "zones": person_zones,
                })

        # remove lost tracks
        for zone in self.zone_state:
            self.zone_state[zone] = self.zone_state[zone].intersection(active_ids)

        # draw pixel-space zones on camera view
        for name, poly in self.zones_pixel.items():
            if len(poly) >= 3:
                cv2.polylines(output, [np.array(poly, dtype=np.int32)], True, (255, 0, 0), 2)
                cx = int(np.mean([p[0] for p in poly]))
                cy = int(np.mean([p[1] for p in poly]))
                cv2.putText(output, name, (cx - 20, cy),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        # occupancy overlay
        y = 30
        for zone, ids_in_zone in self.zone_state.items():
            cv2.putText(output, f"{zone}: {len(ids_in_zone)}",
                        (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            y += 30

        # metrics log every minute
        if time.time() - self.last_log_time >= 60:
            log = {"time": time.strftime("%H:%M:%S")}
            for zone in self.zone_state:
                log[zone] = len(self.zone_state[zone])
            self.metrics_log.append(log)
            with open(METRICS_FILE, "w") as f:
                json.dump(self.metrics_log, f, indent=2)
            self.last_log_time = time.time()

        # build and return floor map
        floor_map = self.draw_floor_map(tracks)

        return output, tracks, floor_map