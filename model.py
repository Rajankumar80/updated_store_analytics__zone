# # # # # # # import cv2
# # # # # # # import numpy as np
# # # # # # # import json
# # # # # # # import time
# # # # # # # from ultralytics import YOLO
# # # # # # # from gender_classifier import GenderClassifier


# # # # # # # ZONE_FILE    = "/home/keshav/rajan/new_pipeline/zones_runtime.json"
# # # # # # # METRICS_FILE = "zone_metrics.json"
# # # # # # # EVENTS_FILE  = "zone_events.json"
# # # # # # # DWELL_FILE   = "zone_dwell_summary.json"
# # # # # # # gender_model="/home/keshav/rajan/new_pipeline/models/mobilenetv3_gender_best.pth"
# # # # # # # classifier=GenderClassifier(gender_model)

# # # # # # # ENTRY_FRAMES = 4
# # # # # # # EXIT_FRAMES  = 6

# # # # # # # UNIQUE_ID_GLOBAL = False

# # # # # # # C_WHITE    = (255, 255, 255)
# # # # # # # C_BLACK    = (0,   0,   0)
# # # # # # # C_DARK     = (18,  18,  26)
# # # # # # # C_ACCENT   = (255, 200,  60)
# # # # # # # C_GREEN    = ( 60, 220, 120)
# # # # # # # C_RED      = ( 60,  60, 230)

# # # # # # # _ZONE_COLOR_BANK = [
# # # # # # #     ((255, 190,  60), (200, 140,  40)),
# # # # # # #     ((100, 220, 100), ( 60, 180,  60)),
# # # # # # #     (( 60, 160, 255), ( 40, 120, 220)),
# # # # # # #     ((255, 100, 100), (220,  60,  60)),
# # # # # # #     ((180,  80, 220), (140,  50, 180)),
# # # # # # #     ((  0, 210, 210), (  0, 160, 160)),
# # # # # # #     ((255, 220,   0), (200, 170,   0)),
# # # # # # #     ((255, 140,  40), (200, 100,  20)),
# # # # # # #     ((160, 255, 160), (100, 200, 100)),
# # # # # # #     ((255, 130, 220), (200,  80, 170)),
# # # # # # # ]


# # # # # # # def enhance(frame):
# # # # # # #     gamma    = 1.5
# # # # # # #     invGamma = 1.0 / gamma
# # # # # # #     table    = np.array(
# # # # # # #         [((i / 255.0) ** invGamma) * 255 for i in range(256)]
# # # # # # #     ).astype("uint8")
# # # # # # #     return cv2.LUT(frame, table)


# # # # # # # def point_in_polygon(point, polygon):
# # # # # # #     polygon = np.array(polygon, dtype=np.float32)
# # # # # # #     return cv2.pointPolygonTest(polygon, point, False) >= 0


# # # # # # # def fmt_ts(epoch):
# # # # # # #     return time.strftime("%H:%M:%S", time.localtime(epoch))


# # # # # # # def fmt_duration(secs):
# # # # # # #     secs = int(secs)
# # # # # # #     m, s = divmod(secs, 60)
# # # # # # #     return f"{m}m {s:02d}s" if m else f"{s}s"


# # # # # # # def draw_filled_rect_alpha(img, x1, y1, x2, y2, color, alpha=0.55):
# # # # # # #     x1, y1 = max(0, x1), max(0, y1)
# # # # # # #     x2, y2 = min(img.shape[1], x2), min(img.shape[0], y2)
# # # # # # #     if x2 <= x1 or y2 <= y1:
# # # # # # #         return
# # # # # # #     sub  = img[y1:y2, x1:x2]
# # # # # # #     rect = np.full(sub.shape, color, dtype=np.uint8)
# # # # # # #     cv2.addWeighted(rect, alpha, sub, 1 - alpha, 0, sub)
# # # # # # #     img[y1:y2, x1:x2] = sub


# # # # # # # def draw_rounded_rect(img, x1, y1, x2, y2, r, color, thickness=2):
# # # # # # #     cv2.line(img, (x1+r, y1),   (x2-r, y1),   color, thickness)
# # # # # # #     cv2.line(img, (x1+r, y2),   (x2-r, y2),   color, thickness)
# # # # # # #     cv2.line(img, (x1,   y1+r), (x1,   y2-r), color, thickness)
# # # # # # #     cv2.line(img, (x2,   y1+r), (x2,   y2-r), color, thickness)
# # # # # # #     cv2.ellipse(img, (x1+r, y1+r), (r, r), 180,  0, 90, color, thickness)
# # # # # # #     cv2.ellipse(img, (x2-r, y1+r), (r, r), 270,  0, 90, color, thickness)
# # # # # # #     cv2.ellipse(img, (x1+r, y2-r), (r, r),  90,  0, 90, color, thickness)
# # # # # # #     cv2.ellipse(img, (x2-r, y2-r), (r, r),   0,  0, 90, color, thickness)


# # # # # # # def draw_badge(img, text, x, y, bg_color, text_color=C_WHITE,
# # # # # # #                font_scale=0.48, thickness=1, pad_x=10, pad_y=6):
# # # # # # #     font = cv2.FONT_HERSHEY_DUPLEX
# # # # # # #     (tw, th), _ = cv2.getTextSize(text, font, font_scale, thickness)
# # # # # # #     bx1, by1 = x, y - th - pad_y
# # # # # # #     bx2, by2 = x + tw + 2 * pad_x, y + pad_y
# # # # # # #     r = max(1, (by2 - by1) // 2)
# # # # # # #     draw_filled_rect_alpha(img, bx1, by1, bx2, by2, bg_color, alpha=0.80)
# # # # # # #     draw_rounded_rect(img, bx1, by1, bx2, by2, r, bg_color, thickness=1)
# # # # # # #     cv2.putText(img, text, (bx1 + pad_x, y), font,
# # # # # # #                 font_scale, text_color, thickness, cv2.LINE_AA)
# # # # # # #     return bx2 + 6


# # # # # # # def draw_label_with_bg(img, text, x, y, text_color=C_WHITE,
# # # # # # #                        bg_color=C_DARK, font_scale=0.5, thickness=1, pad=6):
# # # # # # #     font = cv2.FONT_HERSHEY_DUPLEX
# # # # # # #     (tw, th), _ = cv2.getTextSize(text, font, font_scale, thickness)
# # # # # # #     draw_filled_rect_alpha(img,
# # # # # # #                            x - pad, y - th - pad,
# # # # # # #                            x + tw + pad, y + pad,
# # # # # # #                            bg_color, alpha=0.75)
# # # # # # #     cv2.putText(img, text, (x, y), font,
# # # # # # #                 font_scale, text_color, thickness, cv2.LINE_AA)


# # # # # # # class Detector:

# # # # # # #     def __init__(self, camera_name="cam_entry"):

# # # # # # #         self.model = YOLO("/home/keshav/rajan/new_pipeline/models/best.pt")

# # # # # # #         with open(ZONE_FILE) as f:
# # # # # # #             data = json.load(f)[camera_name]

# # # # # # #         self.homography = None
# # # # # # #         if data.get("homography") is not None:
# # # # # # #             self.homography = np.array(data["homography"], dtype=np.float32)

# # # # # # #         self.zones_pixel = {}
# # # # # # #         self.zones_world = {}
# # # # # # #         for name, info in data["zones"].items():
# # # # # # #             self.zones_pixel[name] = info["pixel"]
# # # # # # #             self.zones_world[name] = info["world"]

# # # # # # #         self.zone_color_bgr = {}
# # # # # # #         self.zone_color_map = {}
# # # # # # #         for idx, name in enumerate(self.zones_pixel):
# # # # # # #             bright, dark = _ZONE_COLOR_BANK[idx % len(_ZONE_COLOR_BANK)]
# # # # # # #             self.zone_color_bgr[name] = bright
# # # # # # #             self.zone_color_map[name] = dark

# # # # # # #         self.confirmed_inside = {name: set() for name in self.zones_pixel}
# # # # # # #         self.inside_streak    = {}
# # # # # # #         self.outside_streak   = {}

# # # # # # #         self.zone_entry_count = {name: 0 for name in self.zones_pixel}
# # # # # # #         self.zone_exit_count  = {name: 0 for name in self.zones_pixel}

# # # # # # #         self.entry_epoch      = {}
# # # # # # #         self.cumulative_dwell = {}

# # # # # # #         # ── ID management ─────────────────────────────────────────────────
# # # # # # #         # Counter only ever increments — IDs are never reused.
# # # # # # #         # This prevents the ID-collision bug where a new entrant gets the
# # # # # # #         # same local ID as a person who just exited.
# # # # # # #         self.zone_id_counter = {name: 0 for name in self.zones_pixel}
# # # # # # #         # tracker_tid → local display id  (cleared on exit, never recycled)
# # # # # # #         self.zone_id_map     = {name: {} for name in self.zones_pixel}

# # # # # # #         self.event_log     = []
# # # # # # #         self.metrics_log   = []
# # # # # # #         self.last_log_time = time.time()

# # # # # # #         self.MAP_SCALE = 150
# # # # # # #         self.MAP_W     = 900
# # # # # # #         self.MAP_H     = 750

# # # # # # #     # ── ID helpers ─────────────────────────────────────────────────────────

# # # # # # #     def _get_display_id(self, tracker_tid, zone):
# # # # # # #         if UNIQUE_ID_GLOBAL:
# # # # # # #             return tracker_tid
# # # # # # #         if tracker_tid not in self.zone_id_map[zone]:
# # # # # # #             # Always take the next number — never reuse a freed slot
# # # # # # #             self.zone_id_counter[zone] += 1
# # # # # # #             self.zone_id_map[zone][tracker_tid] = self.zone_id_counter[zone]
# # # # # # #         return self.zone_id_map[zone][tracker_tid]

# # # # # # #     def _release_display_id(self, tracker_tid, zone):
# # # # # # #         if UNIQUE_ID_GLOBAL:
# # # # # # #             return
# # # # # # #         # Remove the mapping so memory stays clean,
# # # # # # #         # but do NOT put the number back into any free pool.
# # # # # # #         self.zone_id_map[zone].pop(tracker_tid, None)

# # # # # # #     # ──────────────────────────────────────────────────────────────────────

# # # # # # #     def pixel_to_world(self, x, y):
# # # # # # #         if self.homography is None:
# # # # # # #             return None
# # # # # # #         pt    = np.array([[[x, y]]], dtype=np.float32)
# # # # # # #         world = cv2.perspectiveTransform(pt, self.homography)
# # # # # # #         return world[0][0]

# # # # # # #     def _apply_hysteresis(self, tracker_tid, zone, raw_inside, now):
# # # # # # #         key          = (tracker_tid, zone)
# # # # # # #         confirmed_in = tracker_tid in self.confirmed_inside[zone]

# # # # # # #         if raw_inside:
# # # # # # #             self.outside_streak[key] = 0
# # # # # # #             if not confirmed_in:
# # # # # # #                 self.inside_streak[key] = self.inside_streak.get(key, 0) + 1
# # # # # # #                 if self.inside_streak[key] >= ENTRY_FRAMES:
# # # # # # #                     self.confirmed_inside[zone].add(tracker_tid)
# # # # # # #                     self.inside_streak[key]      = 0
# # # # # # #                     self.zone_entry_count[zone] += 1
# # # # # # #                     display_id             = self._get_display_id(tracker_tid, zone)
# # # # # # #                     dkey                   = (display_id, zone)
# # # # # # #                     self.entry_epoch[dkey] = now
# # # # # # #                     self.event_log.append({
# # # # # # #                         "event":       "ENTRY",
# # # # # # #                         "id":          display_id,
# # # # # # #                         "tracker_id":  int(tracker_tid),
# # # # # # #                         "zone":        zone,
# # # # # # #                         "entry_time":  fmt_ts(now),
# # # # # # #                         "entry_epoch": round(now, 3),
# # # # # # #                         "id_mode":     "global" if UNIQUE_ID_GLOBAL else "zone_local",
# # # # # # #                     })
# # # # # # #                     print(f"[ENTRY] display_id:{display_id}  "
# # # # # # #                           f"tracker:{tracker_tid}  zone:{zone}  {fmt_ts(now)}")
# # # # # # #             else:
# # # # # # #                 self.inside_streak[key] = 0

# # # # # # #         else:
# # # # # # #             self.inside_streak[key] = 0
# # # # # # #             if confirmed_in:
# # # # # # #                 self.outside_streak[key] = self.outside_streak.get(key, 0) + 1
# # # # # # #                 if self.outside_streak[key] >= EXIT_FRAMES:
# # # # # # #                     self.confirmed_inside[zone].discard(tracker_tid)
# # # # # # #                     self.outside_streak[key]    = 0
# # # # # # #                     self.zone_exit_count[zone] += 1
# # # # # # #                     display_id = self._get_display_id(tracker_tid, zone)
# # # # # # #                     dkey       = (display_id, zone)
# # # # # # #                     entry_ep   = self.entry_epoch.pop(dkey, now)
# # # # # # #                     dwell_secs = round(now - entry_ep, 1)
# # # # # # #                     if display_id not in self.cumulative_dwell:
# # # # # # #                         self.cumulative_dwell[display_id] = {}
# # # # # # #                     prev = self.cumulative_dwell[display_id].get(zone, 0.0)
# # # # # # #                     self.cumulative_dwell[display_id][zone] = round(
# # # # # # #                         prev + dwell_secs, 1)
# # # # # # #                     self.event_log.append({
# # # # # # #                         "event":            "EXIT",
# # # # # # #                         "id":               display_id,
# # # # # # #                         "tracker_id":       int(tracker_tid),
# # # # # # #                         "zone":             zone,
# # # # # # #                         "entry_time":       fmt_ts(entry_ep),
# # # # # # #                         "exit_time":        fmt_ts(now),
# # # # # # #                         "entry_epoch":      round(entry_ep, 3),
# # # # # # #                         "exit_epoch":       round(now, 3),
# # # # # # #                         "dwell_secs":       dwell_secs,
# # # # # # #                         "dwell_formatted":  fmt_duration(dwell_secs),
# # # # # # #                         "total_dwell_secs": self.cumulative_dwell[display_id][zone],
# # # # # # #                         "total_dwell_fmt":  fmt_duration(
# # # # # # #                             self.cumulative_dwell[display_id][zone]),
# # # # # # #                         "id_mode":          "global" if UNIQUE_ID_GLOBAL else "zone_local",
# # # # # # #                     })
# # # # # # #                     print(f"[EXIT]  display_id:{display_id}  "
# # # # # # #                           f"tracker:{tracker_tid}  zone:{zone}  "
# # # # # # #                           f"entry:{fmt_ts(entry_ep)}  exit:{fmt_ts(now)}  "
# # # # # # #                           f"dwell:{fmt_duration(dwell_secs)}")
# # # # # # #                     self._release_display_id(tracker_tid, zone)
# # # # # # #                     self._flush_dwell_summary()
# # # # # # #             else:
# # # # # # #                 self.outside_streak[key] = 0

# # # # # # #     def _cleanup_lost_tracks(self, active_ids, now):
# # # # # # #         all_confirmed = set()
# # # # # # #         for zone in self.zones_pixel:
# # # # # # #             all_confirmed |= self.confirmed_inside[zone]

# # # # # # #         for tracker_tid in (all_confirmed - active_ids):
# # # # # # #             for zone in self.zones_pixel:
# # # # # # #                 if tracker_tid not in self.confirmed_inside[zone]:
# # # # # # #                     continue
# # # # # # #                 self.confirmed_inside[zone].discard(tracker_tid)
# # # # # # #                 self.zone_exit_count[zone] += 1
# # # # # # #                 display_id = self._get_display_id(tracker_tid, zone)
# # # # # # #                 dkey       = (display_id, zone)
# # # # # # #                 entry_ep   = self.entry_epoch.pop(dkey, now)
# # # # # # #                 dwell_secs = round(now - entry_ep, 1)
# # # # # # #                 if display_id not in self.cumulative_dwell:
# # # # # # #                     self.cumulative_dwell[display_id] = {}
# # # # # # #                 prev = self.cumulative_dwell[display_id].get(zone, 0.0)
# # # # # # #                 self.cumulative_dwell[display_id][zone] = round(
# # # # # # #                     prev + dwell_secs, 1)
# # # # # # #                 self.event_log.append({
# # # # # # #                     "event":            "EXIT",
# # # # # # #                     "id":               display_id,
# # # # # # #                     "tracker_id":       int(tracker_tid),
# # # # # # #                     "zone":             zone,
# # # # # # #                     "entry_time":       fmt_ts(entry_ep),
# # # # # # #                     "exit_time":        fmt_ts(now),
# # # # # # #                     "entry_epoch":      round(entry_ep, 3),
# # # # # # #                     "exit_epoch":       round(now, 3),
# # # # # # #                     "dwell_secs":       dwell_secs,
# # # # # # #                     "dwell_formatted":  fmt_duration(dwell_secs),
# # # # # # #                     "total_dwell_secs": self.cumulative_dwell[display_id][zone],
# # # # # # #                     "total_dwell_fmt":  fmt_duration(
# # # # # # #                         self.cumulative_dwell[display_id][zone]),
# # # # # # #                     "reason":           "track_lost",
# # # # # # #                     "id_mode":          "global" if UNIQUE_ID_GLOBAL else "zone_local",
# # # # # # #                 })
# # # # # # #                 print(f"[EXIT-LOST] display_id:{display_id}  "
# # # # # # #                       f"tracker:{tracker_tid}  zone:{zone}  "
# # # # # # #                       f"dwell:{fmt_duration(dwell_secs)}")
# # # # # # #                 self._release_display_id(tracker_tid, zone)

# # # # # # #             for zone in self.zones_pixel:
# # # # # # #                 self.inside_streak.pop((tracker_tid, zone),  None)
# # # # # # #                 self.outside_streak.pop((tracker_tid, zone), None)

# # # # # # #         self._flush_dwell_summary()

# # # # # # #     def _flush_dwell_summary(self):
# # # # # # #         summary = {}
# # # # # # #         for did, zones in self.cumulative_dwell.items():
# # # # # # #             summary[f"id_{did}"] = {
# # # # # # #                 zone: {"total_secs": secs, "total_fmt": fmt_duration(secs)}
# # # # # # #                 for zone, secs in zones.items()
# # # # # # #             }
# # # # # # #         with open(DWELL_FILE, "w") as f:
# # # # # # #             json.dump(summary, f, indent=2)

# # # # # # #     def _draw_hud(self, output):
# # # # # # #         font    = cv2.FONT_HERSHEY_DUPLEX
# # # # # # #         pad     = 14
# # # # # # #         row_h   = 36
# # # # # # #         col_w   = 110
# # # # # # #         label_w = 115
# # # # # # #         n_zones = len(self.zones_pixel)

# # # # # # #         panel_w = label_w + 3 * col_w + 2 * pad
# # # # # # #         panel_h = pad + 28 + n_zones * row_h + pad

# # # # # # #         draw_filled_rect_alpha(output, 10, 10,
# # # # # # #                                10 + panel_w, 10 + panel_h,
# # # # # # #                                C_DARK, alpha=0.72)
# # # # # # #         cv2.rectangle(output, (10, 10),
# # # # # # #                       (10 + panel_w, 10 + panel_h), C_ACCENT, 1)

# # # # # # #         mode_text = "ID: GLOBAL" if UNIQUE_ID_GLOBAL else "ID: PER-ZONE"
# # # # # # #         mode_col  = (100, 220, 100) if UNIQUE_ID_GLOBAL else (60, 160, 255)
# # # # # # #         draw_badge(output, mode_text,
# # # # # # #                    10 + panel_w - 115, 10 + 20,
# # # # # # #                    bg_color=mode_col, text_color=C_BLACK,
# # # # # # #                    font_scale=0.36, thickness=1, pad_x=6, pad_y=4)

# # # # # # #         hx = 10 + pad
# # # # # # #         hy = 10 + pad + 16
# # # # # # #         cv2.putText(output, "ZONE",  (hx,                     hy),
# # # # # # #                     font, 0.42, C_ACCENT, 1, cv2.LINE_AA)
# # # # # # #         cv2.putText(output, "NOW",   (hx + label_w,           hy),
# # # # # # #                     font, 0.42, C_ACCENT, 1, cv2.LINE_AA)
# # # # # # #         cv2.putText(output, "ENTRY", (hx + label_w + col_w,   hy),
# # # # # # #                     font, 0.42, C_ACCENT, 1, cv2.LINE_AA)
# # # # # # #         cv2.putText(output, "EXIT",  (hx + label_w + 2*col_w, hy),
# # # # # # #                     font, 0.42, C_ACCENT, 1, cv2.LINE_AA)

# # # # # # #         div_y = 10 + pad + 22
# # # # # # #         cv2.line(output, (10 + pad, div_y),
# # # # # # #                  (10 + panel_w - pad, div_y), C_ACCENT, 1)

# # # # # # #         for i, zone in enumerate(self.zones_pixel):
# # # # # # #             ry      = div_y + 8 + (i + 1) * row_h - 6
# # # # # # #             inside  = len(self.confirmed_inside[zone])
# # # # # # #             entries = self.zone_entry_count[zone]
# # # # # # #             exits   = self.zone_exit_count[zone]
# # # # # # #             z_color = self.zone_color_bgr[zone]

# # # # # # #             cv2.circle(output, (hx + 6, ry - 5), 5, z_color, -1)
# # # # # # #             cv2.putText(output, zone.upper(),
# # # # # # #                         (hx + 18, ry), font, 0.44, z_color, 1, cv2.LINE_AA)

# # # # # # #             now_col = C_GREEN if inside > 0 else C_WHITE
# # # # # # #             cv2.putText(output, str(inside),
# # # # # # #                         (hx + label_w + 30, ry),
# # # # # # #                         font, 0.55, now_col, 1, cv2.LINE_AA)
# # # # # # #             cv2.putText(output, str(entries),
# # # # # # #                         (hx + label_w + col_w + 20, ry),
# # # # # # #                         font, 0.55, C_GREEN, 1, cv2.LINE_AA)
# # # # # # #             cv2.putText(output, str(exits),
# # # # # # #                         (hx + label_w + 2*col_w + 20, ry),
# # # # # # #                         font, 0.55, C_RED, 1, cv2.LINE_AA)

# # # # # # #     def _draw_zones(self, output):
# # # # # # #         for name, poly in self.zones_pixel.items():
# # # # # # #             if len(poly) < 3:
# # # # # # #                 continue
# # # # # # #             pts     = np.array(poly, dtype=np.int32)
# # # # # # #             color   = self.zone_color_bgr[name]
# # # # # # #             overlay = output.copy()
# # # # # # #             cv2.fillPoly(overlay, [pts], color)
# # # # # # #             cv2.addWeighted(overlay, 0.12, output, 0.88, 0, output)
# # # # # # #             cv2.polylines(output, [pts], True, color, 2, cv2.LINE_AA)
# # # # # # #             cx = int(np.mean([p[0] for p in poly]))
# # # # # # #             cy = int(np.mean([p[1] for p in poly]))
# # # # # # #             draw_label_with_bg(output, name.upper(), cx - 30, cy,
# # # # # # #                                text_color=color, bg_color=C_DARK,
# # # # # # #                                font_scale=0.5, thickness=1)

# # # # # # #     def _draw_track(self, output, track):
# # # # # # #         x1, y1, x2, y2 = track["bbox"]
# # # # # # #         tracker_tid     = track["id"]
# # # # # # #         person_zones    = track["zones"]

# # # # # # #         in_zone   = len(person_zones) > 0
# # # # # # #         box_color = C_GREEN if in_zone else (200, 200, 200)

# # # # # # #         blen, t = 18, 2
# # # # # # #         cv2.line(output, (x1, y1), (x1+blen, y1), box_color, t)
# # # # # # #         cv2.line(output, (x1, y1), (x1, y1+blen), box_color, t)
# # # # # # #         cv2.line(output, (x2, y1), (x2-blen, y1), box_color, t)
# # # # # # #         cv2.line(output, (x2, y1), (x2, y1+blen), box_color, t)
# # # # # # #         cv2.line(output, (x1, y2), (x1+blen, y2), box_color, t)
# # # # # # #         cv2.line(output, (x1, y2), (x1, y2-blen), box_color, t)
# # # # # # #         cv2.line(output, (x2, y2), (x2-blen, y2), box_color, t)
# # # # # # #         cv2.line(output, (x2, y2), (x2, y2-blen), box_color, t)

# # # # # # #         cx, cy_foot = track["foot"]
# # # # # # #         cv2.circle(output, (cx, cy_foot), 4, C_ACCENT, -1)

# # # # # # #         if UNIQUE_ID_GLOBAL:
# # # # # # #             draw_badge(output, f"ID {tracker_tid}", x1, y1 - 6,
# # # # # # #                        bg_color=C_DARK, text_color=C_WHITE,
# # # # # # #                        font_scale=0.45, thickness=1)
# # # # # # #         else:
# # # # # # #             if person_zones:
# # # # # # #                 next_x = x1
# # # # # # #                 for zone_name in person_zones:
# # # # # # #                     local_id = self.zone_id_map[zone_name].get(tracker_tid, "?")
# # # # # # #                     z_col    = self.zone_color_bgr.get(zone_name, C_ACCENT)
# # # # # # #                     next_x   = draw_badge(
# # # # # # #                         output,
# # # # # # #                         f"{zone_name[:3].upper()}-{local_id}",
# # # # # # #                         next_x, y1 - 6,
# # # # # # #                         bg_color=z_col, text_color=C_BLACK,
# # # # # # #                         font_scale=0.45, thickness=1
# # # # # # #                     )
# # # # # # #             else:
# # # # # # #                 draw_badge(output, f"T{tracker_tid}", x1, y1 - 6,
# # # # # # #                            bg_color=(50, 50, 60), text_color=(160, 160, 160),
# # # # # # #                            font_scale=0.40, thickness=1)

# # # # # # #     def draw_floor_map(self, tracks):
# # # # # # #         floor_map = np.full((self.MAP_H, self.MAP_W, 3),
# # # # # # #                             (22, 22, 30), dtype=np.uint8)

# # # # # # #         for x in range(0, self.MAP_W, self.MAP_SCALE):
# # # # # # #             cv2.line(floor_map, (x, 0), (x, self.MAP_H), (45, 45, 55), 1)
# # # # # # #         for y in range(0, self.MAP_H, self.MAP_SCALE):
# # # # # # #             cv2.line(floor_map, (0, y), (self.MAP_W, y), (45, 45, 55), 1)
# # # # # # #         for i in range(self.MAP_W // self.MAP_SCALE + 1):
# # # # # # #             cv2.putText(floor_map, f"{i}m",
# # # # # # #                         (i * self.MAP_SCALE + 3, 13),
# # # # # # #                         cv2.FONT_HERSHEY_DUPLEX, 0.3, (80, 80, 100), 1)
# # # # # # #         for i in range(self.MAP_H // self.MAP_SCALE + 1):
# # # # # # #             cv2.putText(floor_map, f"{i}m",
# # # # # # #                         (3, i * self.MAP_SCALE + 13),
# # # # # # #                         cv2.FONT_HERSHEY_DUPLEX, 0.3, (80, 80, 100), 1)

# # # # # # #         for name, poly_world in self.zones_world.items():
# # # # # # #             if len(poly_world) < 3:
# # # # # # #                 continue
# # # # # # #             color = self.zone_color_map[name]
# # # # # # #             pts   = np.array([
# # # # # # #                 [int(p[0] * self.MAP_SCALE), int(p[1] * self.MAP_SCALE)]
# # # # # # #                 for p in poly_world
# # # # # # #             ], dtype=np.int32)
# # # # # # #             overlay = floor_map.copy()
# # # # # # #             cv2.fillPoly(overlay, [pts], color)
# # # # # # #             cv2.addWeighted(overlay, 0.30, floor_map, 0.70, 0, floor_map)
# # # # # # #             cv2.polylines(floor_map, [pts], True, color, 2, cv2.LINE_AA)

# # # # # # #             cx         = int(np.mean(pts[:, 0]))
# # # # # # #             cy         = int(np.mean(pts[:, 1]))
# # # # # # #             inside_now = len(self.confirmed_inside[name])
# # # # # # #             entries    = self.zone_entry_count[name]
# # # # # # #             exits      = self.zone_exit_count[name]

# # # # # # #             cv2.putText(floor_map, name.upper(),
# # # # # # #                         (cx - 34, cy - 24),
# # # # # # #                         cv2.FONT_HERSHEY_DUPLEX, 0.45, color, 1, cv2.LINE_AA)
# # # # # # #             cv2.putText(floor_map, f"NOW {inside_now}",
# # # # # # #                         (cx - 38, cy),
# # # # # # #                         cv2.FONT_HERSHEY_DUPLEX, 0.4, C_GREEN, 1, cv2.LINE_AA)
# # # # # # #             cv2.putText(floor_map, f"E:{entries}",
# # # # # # #                         (cx - 38, cy + 20),
# # # # # # #                         cv2.FONT_HERSHEY_DUPLEX, 0.38,
# # # # # # #                         (120, 255, 120), 1, cv2.LINE_AA)
# # # # # # #             cv2.putText(floor_map, f"X:{exits}",
# # # # # # #                         (cx + 14, cy + 20),
# # # # # # #                         cv2.FONT_HERSHEY_DUPLEX, 0.38,
# # # # # # #                         (80, 80, 230), 1, cv2.LINE_AA)

# # # # # # #         for track in tracks:
# # # # # # #             world_pt = self.pixel_to_world(track["foot"][0], track["foot"][1])
# # # # # # #             if world_pt is None:
# # # # # # #                 continue
# # # # # # #             mx = int(world_pt[0] * self.MAP_SCALE)
# # # # # # #             my = int(world_pt[1] * self.MAP_SCALE)
# # # # # # #             if not (0 <= mx < self.MAP_W and 0 <= my < self.MAP_H):
# # # # # # #                 continue
# # # # # # #             in_zone = bool(track["zones"])
# # # # # # #             dot_col = C_GREEN if in_zone else (180, 180, 180)
# # # # # # #             cv2.circle(floor_map, (mx, my), 8, dot_col, -1)
# # # # # # #             cv2.circle(floor_map, (mx, my), 9, C_WHITE,  1)

# # # # # # #             tracker_tid = track["id"]
# # # # # # #             if not UNIQUE_ID_GLOBAL and track["zones"]:
# # # # # # #                 zone0    = track["zones"][0]
# # # # # # #                 local_id = self.zone_id_map[zone0].get(tracker_tid, tracker_tid)
# # # # # # #                 label    = f"{zone0[:1].upper()}{local_id}"
# # # # # # #             else:
# # # # # # #                 label = str(tracker_tid)
# # # # # # #             cv2.putText(floor_map, label,
# # # # # # #                         (mx + 11, my + 4),
# # # # # # #                         cv2.FONT_HERSHEY_DUPLEX, 0.38, dot_col, 1, cv2.LINE_AA)

# # # # # # #         cv2.rectangle(floor_map, (0, 0), (self.MAP_W, 24), (30, 30, 40), -1)
# # # # # # #         cv2.line(floor_map, (0, 24), (self.MAP_W, 24), C_ACCENT, 1)
# # # # # # #         cv2.putText(floor_map, "STORE FLOOR MAP  —  bird's-eye view",
# # # # # # #                     (self.MAP_W // 2 - 155, 17),
# # # # # # #                     cv2.FONT_HERSHEY_DUPLEX, 0.46, C_ACCENT, 1, cv2.LINE_AA)

# # # # # # #         lx, ly = self.MAP_W - 140, self.MAP_H - 52
# # # # # # #         draw_filled_rect_alpha(floor_map, lx - 8, ly - 14,
# # # # # # #                                self.MAP_W - 6, self.MAP_H - 6,
# # # # # # #                                C_DARK, alpha=0.7)
# # # # # # #         cv2.circle(floor_map, (lx + 6, ly),      5, (180, 180, 180), -1)
# # # # # # #         cv2.putText(floor_map, "open area",
# # # # # # #                     (lx + 16, ly + 4),
# # # # # # #                     cv2.FONT_HERSHEY_DUPLEX, 0.36, (180, 180, 180), 1)
# # # # # # #         cv2.circle(floor_map, (lx + 6, ly + 22), 5, C_GREEN, -1)
# # # # # # #         cv2.putText(floor_map, "in zone",
# # # # # # #                     (lx + 16, ly + 26),
# # # # # # #                     cv2.FONT_HERSHEY_DUPLEX, 0.36, C_GREEN, 1)

# # # # # # #         return floor_map

# # # # # # #     def process_frame(self, frame):
# # # # # # #         frame = enhance(frame)
# # # # # # #         now   = time.time()

# # # # # # #         results = self.model.track(
# # # # # # #             frame,
# # # # # # #             persist=True,
# # # # # # #             classes=0,
# # # # # # #             conf=0.1,
# # # # # # #             iou=0.7,
# # # # # # #             tracker="botsort.yaml",
# # # # # # #             verbose=False
# # # # # # #         )

# # # # # # #         result     = results[0]
# # # # # # #         output     = frame.copy()
# # # # # # #         active_ids = set()
# # # # # # #         tracks     = []

# # # # # # #         if result.boxes is not None and result.boxes.id is not None:
# # # # # # #             boxes = result.boxes.xyxy.cpu().numpy()
# # # # # # #             ids   = result.boxes.id.cpu().numpy().astype(int)

# # # # # # #             for box, tid in zip(boxes, ids):
# # # # # # #                 x1, y1, x2, y2 = box.astype(int)
# # # # # # #                 cx         = int((x1 + x2) / 2)
# # # # # # #                 cy         = int(y2)
# # # # # # #                 foot_pixel = (cx, cy)
# # # # # # #                 active_ids.add(tid)
# # # # # # #                 world_pt = self.pixel_to_world(cx, cy)

# # # # # # #                 person_zones = []
# # # # # # #                 for zone_name in self.zones_pixel:
# # # # # # #                     if world_pt is not None and \
# # # # # # #                             len(self.zones_world[zone_name]) >= 3:
# # # # # # #                         raw_inside = point_in_polygon(
# # # # # # #                             tuple(world_pt), self.zones_world[zone_name])
# # # # # # #                     else:
# # # # # # #                         raw_inside = point_in_polygon(
# # # # # # #                             foot_pixel, self.zones_pixel[zone_name])

# # # # # # #                     self._apply_hysteresis(tid, zone_name, raw_inside, now)

# # # # # # #                     if tid in self.confirmed_inside[zone_name]:
# # # # # # #                         person_zones.append(zone_name)

# # # # # # #                 tracks.append({
# # # # # # #                     "id":    tid,
# # # # # # #                     "bbox":  (x1, y1, x2, y2),
# # # # # # #                     "foot":  foot_pixel,
# # # # # # #                     "zones": person_zones,
# # # # # # #                 })

# # # # # # #         self._cleanup_lost_tracks(active_ids, now)

# # # # # # #         self._draw_zones(output)
# # # # # # #         for track in tracks:
# # # # # # #             self._draw_track(output, track)
# # # # # # #         self._draw_hud(output)

# # # # # # #         with open(EVENTS_FILE, "w") as f:
# # # # # # #             json.dump(self.event_log, f, indent=2)

# # # # # # #         if time.time() - self.last_log_time >= 60:
# # # # # # #             log = {"time": fmt_ts(now)}
# # # # # # #             for zone in self.zones_pixel:
# # # # # # #                 log[zone] = {
# # # # # # #                     "current": len(self.confirmed_inside[zone]),
# # # # # # #                     "entries": self.zone_entry_count[zone],
# # # # # # #                     "exits":   self.zone_exit_count[zone],
# # # # # # #                 }
# # # # # # #             self.metrics_log.append(log)
# # # # # # #             with open(METRICS_FILE, "w") as f:
# # # # # # #                 json.dump(self.metrics_log, f, indent=2)
# # # # # # #             self.last_log_time = time.time()

# # # # # # #         floor_map = self.draw_floor_map(tracks)
# # # # # # #         return output, tracks, floor_map




# # # # # # import cv2
# # # # # # import numpy as np
# # # # # # import json
# # # # # # import time
# # # # # # import torch
# # # # # # import torch.nn as nn
# # # # # # from torchvision import transforms, models
# # # # # # from PIL import Image
# # # # # # from ultralytics import YOLO


# # # # # # # ─── CONFIGURATION & CONSTANTS ─────────────────────────────────────────

# # # # # # ZONE_FILE    = "/home/keshav/rajan/new_pipeline/zones_runtime.json"
# # # # # # METRICS_FILE = "zone_metrics.json"
# # # # # # EVENTS_FILE  = "zone_events.json"
# # # # # # DWELL_FILE   = "zone_dwell_summary.json"

# # # # # # YOLO_MODEL   = "/home/keshav/rajan/new_pipeline/models/best.pt"
# # # # # # GENDER_MODEL = "/home/keshav/rajan/new_pipeline/models/mobilenetv3_gender_best.pth"

# # # # # # ENTRY_FRAMES = 4
# # # # # # EXIT_FRAMES  = 6
# # # # # # UNIQUE_ID_GLOBAL = True

# # # # # # # Colors
# # # # # # C_WHITE    = (255, 255, 255)
# # # # # # C_BLACK    = (0,   0,   0)
# # # # # # C_DARK     = (18,  18,  26)
# # # # # # C_ACCENT   = (255, 200,  60)
# # # # # # C_GREEN    = ( 60, 220, 120)
# # # # # # C_RED      = ( 60,  60, 230)

# # # # # # _ZONE_COLOR_BANK = [
# # # # # #     ((255, 190,  60), (200, 140,  40)),
# # # # # #     ((100, 220, 100), ( 60, 180,  60)),
# # # # # #     (( 60, 160, 255), ( 40, 120, 220)),
# # # # # #     ((255, 100, 100), (220,  60,  60)),
# # # # # #     ((180,  80, 220), (140,  50, 180)),
# # # # # #     ((  0, 210, 210), (  0, 160, 160)),
# # # # # #     ((255, 220,   0), (200, 170,   0)),
# # # # # #     ((255, 140,  40), (200, 100,  20)),
# # # # # #     ((160, 255, 160), (100, 200, 100)),
# # # # # #     ((255, 130, 220), (200,  80, 170)),
# # # # # # ]


# # # # # # # ─── HELPER FUNCTIONS ──────────────────────────────────────────────────

# # # # # # def enhance(frame):
# # # # # #     """Enhance frame visibility using Gamma correction."""
# # # # # #     gamma = 1.5
# # # # # #     invGamma = 1.0 / gamma
# # # # # #     table = np.array([((i / 255.0) ** invGamma) * 255 for i in range(256)]).astype("uint8")
# # # # # #     return cv2.LUT(frame, table)

# # # # # # def point_in_polygon(point, polygon):
# # # # # #     """Check if a point is inside a polygon using OpenCV."""
# # # # # #     polygon = np.array(polygon, dtype=np.float32)
# # # # # #     return cv2.pointPolygonTest(polygon, point, False) >= 0

# # # # # # def fmt_ts(epoch):
# # # # # #     """Format epoch time to HH:MM:SS."""
# # # # # #     return time.strftime("%H:%M:%S", time.localtime(epoch))

# # # # # # def fmt_duration(secs):
# # # # # #     """Format seconds into a readable string (e.g., '1m 05s')."""
# # # # # #     secs = int(secs)
# # # # # #     m, s = divmod(secs, 60)
# # # # # #     return f"{m}m {s:02d}s" if m else f"{s}s"

# # # # # # def draw_filled_rect_alpha(img, x1, y1, x2, y2, color, alpha=0.55):
# # # # # #     """Draw a semi-transparent rectangle."""
# # # # # #     x1, y1 = max(0, x1), max(0, y1)
# # # # # #     x2, y2 = min(img.shape[1], x2), min(img.shape[0], y2)
# # # # # #     if x2 <= x1 or y2 <= y1: return
# # # # # #     sub = img[y1:y2, x1:x2]
# # # # # #     rect = np.full(sub.shape, color, dtype=np.uint8)
# # # # # #     cv2.addWeighted(rect, alpha, sub, 1 - alpha, 0, sub)
# # # # # #     img[y1:y2, x1:x2] = sub

# # # # # # def draw_rounded_rect(img, x1, y1, x2, y2, r, color, thickness=2):
# # # # # #     """Draw a rectangle with rounded corners."""
# # # # # #     cv2.line(img, (x1+r, y1),   (x2-r, y1),   color, thickness)
# # # # # #     cv2.line(img, (x1+r, y2),   (x2-r, y2),   color, thickness)
# # # # # #     cv2.line(img, (x1,   y1+r), (x1,   y2-r), color, thickness)
# # # # # #     cv2.line(img, (x2,   y1+r), (x2,   y2-r), color, thickness)
# # # # # #     cv2.ellipse(img, (x1+r, y1+r), (r, r), 180,  0, 90, color, thickness)
# # # # # #     cv2.ellipse(img, (x2-r, y1+r), (r, r), 270,  0, 90, color, thickness)
# # # # # #     cv2.ellipse(img, (x1+r, y2-r), (r, r),  90,  0, 90, color, thickness)
# # # # # #     cv2.ellipse(img, (x2-r, y2-r), (r, r),   0,  0, 90, color, thickness)

# # # # # # def draw_badge(img, text, x, y, bg_color, text_color=C_WHITE, font_scale=0.48, thickness=1, pad_x=10, pad_y=6):
# # # # # #     """Draw a text badge with a background."""
# # # # # #     font = cv2.FONT_HERSHEY_DUPLEX
# # # # # #     (tw, th), _ = cv2.getTextSize(text, font, font_scale, thickness)
# # # # # #     bx1, by1 = x, y - th - pad_y
# # # # # #     bx2, by2 = x + tw + 2 * pad_x, y + pad_y
# # # # # #     r = max(1, (by2 - by1) // 2)
# # # # # #     draw_filled_rect_alpha(img, bx1, by1, bx2, by2, bg_color, alpha=0.80)
# # # # # #     draw_rounded_rect(img, bx1, by1, bx2, by2, r, bg_color, thickness=1)
# # # # # #     cv2.putText(img, text, (bx1 + pad_x, y), font, font_scale, text_color, thickness, cv2.LINE_AA)
# # # # # #     return bx2 + 6

# # # # # # def draw_label_with_bg(img, text, x, y, text_color=C_WHITE, bg_color=C_DARK, font_scale=0.5, thickness=1, pad=6):
# # # # # #     """Draw text with a simple rectangular background block."""
# # # # # #     font = cv2.FONT_HERSHEY_DUPLEX
# # # # # #     (tw, th), _ = cv2.getTextSize(text, font, font_scale, thickness)
# # # # # #     draw_filled_rect_alpha(img, x - pad, y - th - pad, x + tw + pad, y + pad, bg_color, alpha=0.75)
# # # # # #     cv2.putText(img, text, (x, y), font, font_scale, text_color, thickness, cv2.LINE_AA)


# # # # # # # ─── MODELS ────────────────────────────────────────────────────────────

# # # # # # class GenderClassifier:
# # # # # #     """MobileNetV3 model for classifying cropped bounding boxes by gender."""
# # # # # #     def __init__(self, weights_path, device=None):
# # # # # #         self.device = device if device else torch.device("cuda" if torch.cuda.is_available() else "cpu")

# # # # # #         # Load & modify MobileNetV3 structure for 2 classes
# # # # # #         self.model = models.mobilenet_v3_small()
# # # # # #         in_features = self.model.classifier[3].in_features
# # # # # #         self.model.classifier[3] = nn.Linear(in_features, 2)

# # # # # #         # Load weights
# # # # # #         state_dict = torch.load(weights_path, map_location=self.device)
# # # # # #         self.model.load_state_dict(state_dict)
# # # # # #         self.model = self.model.to(self.device)
# # # # # #         self.model.eval()

# # # # # #         self.classes = ["F", "M"] # Shortened for tighter UI integration

# # # # # #         # Transforms for inference
# # # # # #         self.transform = transforms.Compose([
# # # # # #             transforms.Resize((224, 224)),
# # # # # #             transforms.ToTensor(),
# # # # # #             transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
# # # # # #         ])

# # # # # #     def predict(self, frame, boxes):
# # # # # #         """Returns a list of prediction dicts strictly matching the order/length of input boxes."""
# # # # # #         results = []

# # # # # #         for box in boxes:
# # # # # #             x1, y1, x2, y2 = map(int, box)
            
# # # # # #             # Bound crop to frame size to prevent errors
# # # # # #             x1, y1 = max(0, x1), max(0, y1)
# # # # # #             x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)
            
# # # # # #             crop = frame[y1:y2, x1:x2]

# # # # # #             # Failsafe: if the box is out of bounds or invalid
# # # # # #             if crop.size == 0 or crop.shape[0] == 0 or crop.shape[1] == 0:
# # # # # #                 results.append({"box": [x1, y1, x2, y2], "label": "?", "confidence": 0.0})
# # # # # #                 continue

# # # # # #             img = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
# # # # # #             img = Image.fromarray(img)
# # # # # #             img = self.transform(img).unsqueeze(0).to(self.device)

# # # # # #             with torch.no_grad():
# # # # # #                 output = self.model(img)
# # # # # #                 prob = torch.softmax(output, dim=1)
# # # # # #                 conf, pred = torch.max(prob, 1)

# # # # # #             results.append({
# # # # # #                 "box": [x1, y1, x2, y2],
# # # # # #                 "label": self.classes[pred.item()],
# # # # # #                 "confidence": float(conf.item())
# # # # # #             })

# # # # # #         return results


# # # # # # class Detector:
# # # # # #     """Main object tracker and zone manager."""
# # # # # #     def __init__(self, camera_name="cam_entry"):
# # # # # #         self.model = YOLO(YOLO_MODEL)
# # # # # #         self.gender_model = GenderClassifier(GENDER_MODEL)

# # # # # #         with open(ZONE_FILE) as f:
# # # # # #             data = json.load(f)[camera_name]

# # # # # #         self.homography = None
# # # # # #         if data.get("homography") is not None:
# # # # # #             self.homography = np.array(data["homography"], dtype=np.float32)

# # # # # #         self.zones_pixel = {}
# # # # # #         self.zones_world = {}
# # # # # #         for name, info in data["zones"].items():
# # # # # #             self.zones_pixel[name] = info["pixel"]
# # # # # #             self.zones_world[name] = info["world"]

# # # # # #         self.zone_color_bgr = {}
# # # # # #         self.zone_color_map = {}
# # # # # #         for idx, name in enumerate(self.zones_pixel):
# # # # # #             bright, dark = _ZONE_COLOR_BANK[idx % len(_ZONE_COLOR_BANK)]
# # # # # #             self.zone_color_bgr[name] = bright
# # # # # #             self.zone_color_map[name] = dark

# # # # # #         self.confirmed_inside = {name: set() for name in self.zones_pixel}
# # # # # #         self.inside_streak    = {}
# # # # # #         self.outside_streak   = {}

# # # # # #         self.zone_entry_count = {name: 0 for name in self.zones_pixel}
# # # # # #         self.zone_exit_count  = {name: 0 for name in self.zones_pixel}
# # # # # #         self.entry_epoch      = {}
# # # # # #         self.cumulative_dwell = {}

# # # # # #         self.zone_id_counter = {name: 0 for name in self.zones_pixel}
# # # # # #         self.zone_id_map     = {name: {} for name in self.zones_pixel}

# # # # # #         self.event_log     = []
# # # # # #         self.metrics_log   = []
# # # # # #         self.last_log_time = time.time()

# # # # # #         self.MAP_SCALE = 150
# # # # # #         self.MAP_W     = 900
# # # # # #         self.MAP_H     = 750

# # # # # #     # ── ID helpers ──
# # # # # #     def _get_display_id(self, tracker_tid, zone):
# # # # # #         return tracker_tid

# # # # # #     def _release_display_id(self, tracker_tid, zone):
# # # # # #         return

# # # # # #     # ── Geometry & Logic ──
# # # # # #     def pixel_to_world(self, x, y):
# # # # # #         if self.homography is None: return None
# # # # # #         pt = np.array([[[x, y]]], dtype=np.float32)
# # # # # #         world = cv2.perspectiveTransform(pt, self.homography)
# # # # # #         return world[0][0]

# # # # # #     def _apply_hysteresis(self, tracker_tid, zone, raw_inside, now):
# # # # # #         key = (tracker_tid, zone)
# # # # # #         confirmed_in = tracker_tid in self.confirmed_inside[zone]

# # # # # #         if raw_inside:
# # # # # #             self.outside_streak[key] = 0
# # # # # #             if not confirmed_in:
# # # # # #                 self.inside_streak[key] = self.inside_streak.get(key, 0) + 1
# # # # # #                 if self.inside_streak[key] >= ENTRY_FRAMES:
# # # # # #                     self.confirmed_inside[zone].add(tracker_tid)
# # # # # #                     self.inside_streak[key] = 0
# # # # # #                     self.zone_entry_count[zone] += 1
# # # # # #                     display_id = self._get_display_id(tracker_tid, zone)
# # # # # #                     self.entry_epoch[(display_id, zone)] = now
# # # # # #                     self.event_log.append({
# # # # # #                         "event": "ENTRY", "id": display_id, "tracker_id": int(tracker_tid),
# # # # # #                         "zone": zone, "entry_time": fmt_ts(now), "entry_epoch": round(now, 3),
# # # # # #                         "id_mode": "global" if UNIQUE_ID_GLOBAL else "zone_local",
# # # # # #                     })
# # # # # #             else:
# # # # # #                 self.inside_streak[key] = 0
# # # # # #         else:
# # # # # #             self.inside_streak[key] = 0
# # # # # #             if confirmed_in:
# # # # # #                 self.outside_streak[key] = self.outside_streak.get(key, 0) + 1
# # # # # #                 if self.outside_streak[key] >= EXIT_FRAMES:
# # # # # #                     self.confirmed_inside[zone].discard(tracker_tid)
# # # # # #                     self.outside_streak[key] = 0
# # # # # #                     self.zone_exit_count[zone] += 1
# # # # # #                     display_id = self._get_display_id(tracker_tid, zone)
# # # # # #                     entry_ep = self.entry_epoch.pop((display_id, zone), now)
# # # # # #                     dwell_secs = round(now - entry_ep, 1)
                    
# # # # # #                     if display_id not in self.cumulative_dwell:
# # # # # #                         self.cumulative_dwell[display_id] = {}
# # # # # #                     prev = self.cumulative_dwell[display_id].get(zone, 0.0)
# # # # # #                     self.cumulative_dwell[display_id][zone] = round(prev + dwell_secs, 1)
                    
# # # # # #                     self.event_log.append({
# # # # # #                         "event": "EXIT", "id": display_id, "tracker_id": int(tracker_tid),
# # # # # #                         "zone": zone, "entry_time": fmt_ts(entry_ep), "exit_time": fmt_ts(now),
# # # # # #                         "entry_epoch": round(entry_ep, 3), "exit_epoch": round(now, 3),
# # # # # #                         "dwell_secs": dwell_secs, "dwell_formatted": fmt_duration(dwell_secs),
# # # # # #                         "total_dwell_secs": self.cumulative_dwell[display_id][zone],
# # # # # #                         "total_dwell_fmt": fmt_duration(self.cumulative_dwell[display_id][zone]),
# # # # # #                         "id_mode": "global" if UNIQUE_ID_GLOBAL else "zone_local",
# # # # # #                     })
# # # # # #                     self._release_display_id(tracker_tid, zone)
# # # # # #                     self._flush_dwell_summary()
# # # # # #             else:
# # # # # #                 self.outside_streak[key] = 0

# # # # # #     def _cleanup_lost_tracks(self, active_ids, now):
# # # # # #         all_confirmed = set().union(*self.confirmed_inside.values())
# # # # # #         for tracker_tid in (all_confirmed - active_ids):
# # # # # #             for zone in self.zones_pixel:
# # # # # #                 if tracker_tid in self.confirmed_inside[zone]:
# # # # # #                     self.confirmed_inside[zone].discard(tracker_tid)
# # # # # #                     self.zone_exit_count[zone] += 1
# # # # # #                     display_id = self._get_display_id(tracker_tid, zone)
# # # # # #                     entry_ep = self.entry_epoch.pop((display_id, zone), now)
# # # # # #                     dwell_secs = round(now - entry_ep, 1)
                    
# # # # # #                     if display_id not in self.cumulative_dwell:
# # # # # #                         self.cumulative_dwell[display_id] = {}
# # # # # #                     prev = self.cumulative_dwell[display_id].get(zone, 0.0)
# # # # # #                     self.cumulative_dwell[display_id][zone] = round(prev + dwell_secs, 1)
                    
# # # # # #                     self.event_log.append({
# # # # # #                         "event": "EXIT", "id": display_id, "tracker_id": int(tracker_tid),
# # # # # #                         "zone": zone, "entry_time": fmt_ts(entry_ep), "exit_time": fmt_ts(now),
# # # # # #                         "dwell_secs": dwell_secs, "reason": "track_lost"
# # # # # #                     })
# # # # # #                     self._release_display_id(tracker_tid, zone)
            
# # # # # #             for zone in self.zones_pixel:
# # # # # #                 self.inside_streak.pop((tracker_tid, zone), None)
# # # # # #                 self.outside_streak.pop((tracker_tid, zone), None)
# # # # # #         self._flush_dwell_summary()

# # # # # #     def _flush_dwell_summary(self):
# # # # # #         summary = {f"id_{did}": {z: {"total_secs": s, "total_fmt": fmt_duration(s)} for z, s in zs.items()} 
# # # # # #                    for did, zs in self.cumulative_dwell.items()}
# # # # # #         with open(DWELL_FILE, "w") as f:
# # # # # #             json.dump(summary, f, indent=2)

# # # # # #     # ── Visuals ──
# # # # # #     def _draw_hud(self, output):
# # # # # #         font, pad, row_h, col_w, label_w = cv2.FONT_HERSHEY_DUPLEX, 14, 36, 110, 115
# # # # # #         n_zones = len(self.zones_pixel)
# # # # # #         panel_w = label_w + 3 * col_w + 2 * pad
# # # # # #         panel_h = pad + 28 + n_zones * row_h + pad

# # # # # #         draw_filled_rect_alpha(output, 10, 10, 10 + panel_w, 10 + panel_h, C_DARK, alpha=0.72)
# # # # # #         cv2.rectangle(output, (10, 10), (10 + panel_w, 10 + panel_h), C_ACCENT, 1)

# # # # # #         mode_text = "ID: GLOBAL" if UNIQUE_ID_GLOBAL else "ID: PER-ZONE"
# # # # # #         mode_col  = (100, 220, 100) if UNIQUE_ID_GLOBAL else (60, 160, 255)
# # # # # #         draw_badge(output, mode_text, 10 + panel_w - 115, 30, bg_color=mode_col, text_color=C_BLACK, font_scale=0.36, pad_x=6, pad_y=4)

# # # # # #         hx, hy = 10 + pad, 10 + pad + 16
# # # # # #         for title, offset in zip(["ZONE", "NOW", "ENTRY", "EXIT"], [0, label_w, label_w + col_w, label_w + 2*col_w]):
# # # # # #             cv2.putText(output, title, (hx + offset, hy), font, 0.42, C_ACCENT, 1, cv2.LINE_AA)

# # # # # #         div_y = 10 + pad + 22
# # # # # #         cv2.line(output, (10 + pad, div_y), (10 + panel_w - pad, div_y), C_ACCENT, 1)

# # # # # #         for i, zone in enumerate(self.zones_pixel):
# # # # # #             ry = div_y + 8 + (i + 1) * row_h - 6
# # # # # #             inside, entries, exits = len(self.confirmed_inside[zone]), self.zone_entry_count[zone], self.zone_exit_count[zone]
# # # # # #             z_color = self.zone_color_bgr[zone]

# # # # # #             cv2.circle(output, (hx + 6, ry - 5), 5, z_color, -1)
# # # # # #             cv2.putText(output, zone.upper(), (hx + 18, ry), font, 0.44, z_color, 1, cv2.LINE_AA)

# # # # # #             now_col = C_GREEN if inside > 0 else C_WHITE
# # # # # #             cv2.putText(output, str(inside), (hx + label_w + 30, ry), font, 0.55, now_col, 1, cv2.LINE_AA)
# # # # # #             cv2.putText(output, str(entries), (hx + label_w + col_w + 20, ry), font, 0.55, C_GREEN, 1, cv2.LINE_AA)
# # # # # #             cv2.putText(output, str(exits), (hx + label_w + 2*col_w + 20, ry), font, 0.55, C_RED, 1, cv2.LINE_AA)

# # # # # #     def _draw_zones(self, output):
# # # # # #         for name, poly in self.zones_pixel.items():
# # # # # #             if len(poly) < 3: continue
# # # # # #             pts = np.array(poly, dtype=np.int32)
# # # # # #             color = self.zone_color_bgr[name]
# # # # # #             overlay = output.copy()
# # # # # #             cv2.fillPoly(overlay, [pts], color)
# # # # # #             cv2.addWeighted(overlay, 0.12, output, 0.88, 0, output)
# # # # # #             cv2.polylines(output, [pts], True, color, 2, cv2.LINE_AA)
# # # # # #             cx, cy = int(np.mean([p[0] for p in poly])), int(np.mean([p[1] for p in poly]))
# # # # # #             draw_label_with_bg(output, name.upper(), cx - 30, cy, text_color=color, bg_color=C_DARK)

# # # # # #     def _draw_track(self, output, track):

# # # # # #         x1, y1, x2, y2 = track["bbox"]
# # # # # #         tracker_tid = track["id"]
# # # # # #         gender_label = track.get("gender", "?")

# # # # # #         person_zones = track["zones"]

# # # # # #         # thin bbox
# # # # # #         box_color = C_GREEN if person_zones else (180,180,180)

# # # # # #         cv2.rectangle(
# # # # # #             output,
# # # # # #             (x1, y1),
# # # # # #             (x2, y2),
# # # # # #             box_color,
# # # # # #             1   # thin line
# # # # # #         )

# # # # # #         # foot point
# # # # # #         cx, cy = track["foot"]
# # # # # #         cv2.circle(output,(cx,cy),4,C_ACCENT,-1)

# # # # # #         # label text
# # # # # #         label = f"ID {tracker_tid} | {gender_label}"

# # # # # #         font = cv2.FONT_HERSHEY_SIMPLEX
# # # # # #         font_scale = 0.5
# # # # # #         thickness = 1

# # # # # #         (tw,th),_ = cv2.getTextSize(label,font,font_scale,thickness)

# # # # # #         # black background at top of bbox
# # # # # #         cv2.rectangle(
# # # # # #             output,
# # # # # #             (x1, y1-th-8),
# # # # # #             (x1+tw+6, y1),
# # # # # #             (0,0,0),
# # # # # #             -1
# # # # # #         )

# # # # # #         # green text
# # # # # #         cv2.putText(
# # # # # #             output,
# # # # # #             label,
# # # # # #             (x1+3, y1-4),
# # # # # #             font,
# # # # # #             font_scale,
# # # # # #             (0,255,0),
# # # # # #             thickness,
# # # # # #             cv2.LINE_AA
# # # # # #         )

# # # # # #     def draw_floor_map(self, tracks):
# # # # # #         floor_map = np.full((self.MAP_H, self.MAP_W, 3), (22, 22, 30), dtype=np.uint8)

# # # # # #         # Draw Grid
# # # # # #         for x in range(0, self.MAP_W, self.MAP_SCALE): cv2.line(floor_map, (x, 0), (x, self.MAP_H), (45, 45, 55), 1)
# # # # # #         for y in range(0, self.MAP_H, self.MAP_SCALE): cv2.line(floor_map, (0, y), (self.MAP_W, y), (45, 45, 55), 1)
        
# # # # # #         for name, poly_world in self.zones_world.items():
# # # # # #             if len(poly_world) < 3: continue
# # # # # #             color = self.zone_color_map[name]
# # # # # #             pts = np.array([[int(p[0] * self.MAP_SCALE), int(p[1] * self.MAP_SCALE)] for p in poly_world], dtype=np.int32)
# # # # # #             overlay = floor_map.copy()
# # # # # #             cv2.fillPoly(overlay, [pts], color)
# # # # # #             cv2.addWeighted(overlay, 0.30, floor_map, 0.70, 0, floor_map)
# # # # # #             cv2.polylines(floor_map, [pts], True, color, 2, cv2.LINE_AA)

# # # # # #             cx, cy = int(np.mean(pts[:, 0])), int(np.mean(pts[:, 1]))
# # # # # #             cv2.putText(floor_map, name.upper(), (cx - 34, cy - 24), cv2.FONT_HERSHEY_DUPLEX, 0.45, color, 1, cv2.LINE_AA)
# # # # # #             cv2.putText(floor_map, f"NOW {len(self.confirmed_inside[name])}", (cx - 38, cy), cv2.FONT_HERSHEY_DUPLEX, 0.4, C_GREEN, 1)

# # # # # #         # Draw Tracking dots
# # # # # #         for track in tracks:
# # # # # #             world_pt = self.pixel_to_world(track["foot"][0], track["foot"][1])
# # # # # #             if world_pt is None: continue
# # # # # #             mx, my = int(world_pt[0] * self.MAP_SCALE), int(world_pt[1] * self.MAP_SCALE)
# # # # # #             if not (0 <= mx < self.MAP_W and 0 <= my < self.MAP_H): continue
            
# # # # # #             dot_col = C_GREEN if track["zones"] else (180, 180, 180)
# # # # # #             cv2.circle(floor_map, (mx, my), 8, dot_col, -1)
# # # # # #             cv2.circle(floor_map, (mx, my), 9, C_WHITE,  1)

# # # # # #             # Minimalist Map Label
# # # # # #             label = str(track["id"])
# # # # # #             cv2.putText(floor_map, label, (mx + 11, my + 4), cv2.FONT_HERSHEY_DUPLEX, 0.38, dot_col, 1)

# # # # # #         cv2.rectangle(floor_map, (0, 0), (self.MAP_W, 24), (30, 30, 40), -1)
# # # # # #         cv2.putText(floor_map, "STORE FLOOR MAP", (self.MAP_W // 2 - 80, 17), cv2.FONT_HERSHEY_DUPLEX, 0.46, C_ACCENT, 1)

# # # # # #         return floor_map

# # # # # #     # ── Main Processing Loop ──
# # # # # #     def process_frame(self, frame):
# # # # # #         frame = enhance(frame)
# # # # # #         now = time.time()

# # # # # #         results = self.model.track(
# # # # # #             frame, persist=True, classes=0, conf=0.1, iou=0.7, tracker="botsort.yaml", verbose=False
# # # # # #         )

# # # # # #         result = results[0]
# # # # # #         output = frame.copy()
# # # # # #         active_ids = set()
# # # # # #         tracks = []

# # # # # #         if result.boxes is not None and result.boxes.id is not None:
# # # # # #             boxes = result.boxes.xyxy.cpu().numpy()
# # # # # #             ids   = result.boxes.id.cpu().numpy().astype(int)

# # # # # #             # ── GENDER CLASSIFICATION INJECTION ──
# # # # # #             # Run prediction on the whole batch of boxes for this frame
# # # # # #             gender_preds = self.gender_model.predict(frame, boxes)

# # # # # #             # Zip the boxes, tracking IDs, and gender predictions together
# # # # # #             for box, tid, g_pred in zip(boxes, ids, gender_preds):
# # # # # #                 x1, y1, x2, y2 = box.astype(int)
# # # # # #                 cx, cy = int((x1 + x2) / 2), int(y2)
# # # # # #                 foot_pixel = (cx, cy)
# # # # # #                 active_ids.add(tid)
# # # # # #                 world_pt = self.pixel_to_world(cx, cy)

# # # # # #                 person_zones = []
# # # # # #                 for zone_name in self.zones_pixel:
# # # # # #                     if world_pt is not None and len(self.zones_world[zone_name]) >= 3:
# # # # # #                         raw_inside = point_in_polygon(tuple(world_pt), self.zones_world[zone_name])
# # # # # #                     else:
# # # # # #                         raw_inside = point_in_polygon(foot_pixel, self.zones_pixel[zone_name])

# # # # # #                     self._apply_hysteresis(tid, zone_name, raw_inside, now)
# # # # # #                     if tid in self.confirmed_inside[zone_name]:
# # # # # #                         person_zones.append(zone_name)

# # # # # #                 tracks.append({
# # # # # #                     "id":    tid,
# # # # # #                     "bbox":  (x1, y1, x2, y2),
# # # # # #                     "foot":  foot_pixel,
# # # # # #                     "zones": person_zones,
# # # # # #                     "gender": g_pred["label"]  # Add gender to the track dict
# # # # # #                 })

# # # # # #         self._cleanup_lost_tracks(active_ids, now)

# # # # # #         self._draw_zones(output)
# # # # # #         for track in tracks:
# # # # # #             self._draw_track(output, track)
# # # # # #         self._draw_hud(output)

# # # # # #         with open(EVENTS_FILE, "w") as f:
# # # # # #             json.dump(self.event_log, f, indent=2,default=int)

# # # # # #         if time.time() - self.last_log_time >= 60:
# # # # # #             log = {"time": fmt_ts(now)}
# # # # # #             for zone in self.zones_pixel:
# # # # # #                 log[zone] = {"current": len(self.confirmed_inside[zone]), "entries": self.zone_entry_count[zone], "exits": self.zone_exit_count[zone]}
# # # # # #             self.metrics_log.append(log)
# # # # # #             with open(METRICS_FILE, "w") as f:
# # # # # #                 json.dump(self.metrics_log, f, indent=2,default=int)
# # # # # #             self.last_log_time = time.time()

# # # # # #         floor_map = self.draw_floor_map(tracks)
# # # # # #         return output, tracks, floor_map
# # # # # # -------modular design model.py file-------------------------
# # # # # import cv2
# # # # # import numpy as np
# # # # # import json
# # # # # import time
# # # # # from ultralytics import YOLO
# # # # # from gender_classifier import GenderClassifier
# # # # # from zone import ZoneManager

# # # # # class Detector:
# # # # #     def __init__(self, camera_name="cam_entry"):
# # # # #         # Constants
# # # # #         self.ZONE_FILE = "/home/keshav/rajan/new_pipeline/zones_runtime.json"
# # # # #         self.YOLO_MODEL = "/home/keshav/rajan/new_pipeline/models/best.pt"
# # # # #         self.GENDER_MODEL_PATH = "/home/keshav/rajan/new_pipeline/models/mobilenetv3_gender_best.pth"
# # # # #         self.METRICS_FILE, self.EVENTS_FILE = "zone_metrics.json", "zone_events.json"
        
# # # # #         self.C_WHITE, self.C_BLACK, self.C_DARK = (255, 255, 255), (0, 0, 0), (18, 18, 26)
# # # # #         self.C_ACCENT, self.C_GREEN, self.C_RED = (255, 200, 60), (60, 220, 120), (60, 60, 230)
# # # # #         self.ZONE_COLORS = [(255, 190, 60), (100, 220, 100), (60, 160, 255), (255, 100, 100), (180, 80, 220)]

# # # # #         # Init Sub-modules
# # # # #         self.model = YOLO(self.YOLO_MODEL)
# # # # #         self.gender_model = GenderClassifier(self.GENDER_MODEL_PATH)
# # # # #         with open(self.ZONE_FILE) as f:
# # # # #             camera_data = json.load(f)[camera_name]
# # # # #         self.zm = ZoneManager(camera_data)

# # # # #         self.event_log, self.metrics_log = [], []
# # # # #         self.last_log_time = time.time()
# # # # #         self.MAP_SCALE, self.MAP_W, self.MAP_H = 150, 900, 750

# # # # #     def enhance(self, frame):
# # # # #         table = np.array([((i / 255.0) ** (1.0/1.5)) * 255 for i in range(256)]).astype("uint8")
# # # # #         return cv2.LUT(frame, table)

# # # # #     # ── DRAWING HELPERS ──
# # # # #     def draw_filled_rect_alpha(self, img, x1, y1, x2, y2, color, alpha=0.55):
# # # # #         x1, y1, x2, y2 = max(0, x1), max(0, y1), min(img.shape[1], x2), min(img.shape[0], y2)
# # # # #         if x2 <= x1 or y2 <= y1: return
# # # # #         sub = img[y1:y2, x1:x2]
# # # # #         rect = np.full(sub.shape, color, dtype=np.uint8)
# # # # #         cv2.addWeighted(rect, alpha, sub, 1 - alpha, 0, sub)
# # # # #         img[y1:y2, x1:x2] = sub

# # # # #     def draw_badge(self, img, text, x, y, bg_color):
# # # # #         font, scale, thick = cv2.FONT_HERSHEY_DUPLEX, 0.48, 1
# # # # #         (tw, th), _ = cv2.getTextSize(text, font, scale, thick)
# # # # #         bx1, by1, bx2, by2 = x, y - th - 6, x + tw + 20, y + 6
# # # # #         self.draw_filled_rect_alpha(img, bx1, by1, bx2, by2, bg_color, 0.8)
# # # # #         cv2.putText(img, text, (bx1 + 10, y), font, scale, self.C_WHITE, thick, cv2.LINE_AA)

# # # # #     # ── MAIN VISUALS ──
# # # # #     def draw_zones(self, output):
# # # # #         for i, (name, poly) in enumerate(self.zm.zones_pixel.items()):
# # # # #             pts = np.array(poly, np.int32)
# # # # #             color = self.ZONE_COLORS[i % len(self.ZONE_COLORS)]
# # # # #             overlay = output.copy()
# # # # #             cv2.fillPoly(overlay, [pts], color)
# # # # #             cv2.addWeighted(overlay, 0.12, output, 0.88, 0, output)
# # # # #             cv2.polylines(output, [pts], True, color, 2, cv2.LINE_AA)
# # # # #             cx, cy = int(np.mean(pts[:, 0])), int(np.mean(pts[:, 1]))
# # # # #             cv2.putText(output, name.upper(), (cx - 30, cy), cv2.FONT_HERSHEY_DUPLEX, 0.5, color, 1)

# # # # #     def draw_track(self, output, track):
# # # # #         x1, y1, x2, y2 = track["bbox"]
# # # # #         color = self.C_GREEN if track["zones"] else (180, 180, 180)
# # # # #         cv2.rectangle(output, (x1, y1), (x2, y2), color, 1)
# # # # #         cv2.circle(output, track["foot"], 4, self.C_ACCENT, -1)
# # # # #         label = f"ID {track['id']} | {track['gender']}"
# # # # #         (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
# # # # #         cv2.rectangle(output, (x1, y1 - th - 8), (x1 + tw + 6, y1), (0, 0, 0), -1)
# # # # #         cv2.putText(output, label, (x1 + 3, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

# # # # #     def draw_hud(self, output):
# # # # #         panel_w, panel_h = 420, 50 + len(self.zm.zones_pixel) * 36
# # # # #         self.draw_filled_rect_alpha(output, 10, 10, 10 + panel_w, 10 + panel_h, self.C_DARK, 0.72)
# # # # #         cv2.putText(output, "ZONE MONITOR", (25, 35), cv2.FONT_HERSHEY_DUPLEX, 0.5, self.C_ACCENT, 1)
# # # # #         for i, zone in enumerate(self.zm.zones_pixel):
# # # # #             y = 75 + (i * 36)
# # # # #             txt = f"{zone.upper()}: NOW {len(self.zm.confirmed_inside[zone])} | IN {self.zm.zone_entry_count[zone]} | OUT {self.zm.zone_exit_count[zone]}"
# # # # #             cv2.putText(output, txt, (25, y), cv2.FONT_HERSHEY_DUPLEX, 0.45, self.C_WHITE, 1)

# # # # #     def draw_floor_map(self, tracks):
# # # # #         fmap = np.full((self.MAP_H, self.MAP_W, 3), (22, 22, 30), dtype=np.uint8)
# # # # #         for x in range(0, self.MAP_W, self.MAP_SCALE): cv2.line(fmap, (x, 0), (x, self.MAP_H), (45, 45, 55), 1)
# # # # #         for y in range(0, self.MAP_H, self.MAP_SCALE): cv2.line(fmap, (0, y), (self.MAP_W, y), (45, 45, 55), 1)
# # # # #         for name, poly in self.zm.zones_world.items():
# # # # #             pts = np.array([[int(p[0]*self.MAP_SCALE), int(p[1]*self.MAP_SCALE)] for p in poly], np.int32)
# # # # #             cv2.polylines(fmap, [pts], True, self.C_ACCENT, 2)
# # # # #             cv2.putText(fmap, name, (pts[0][0], pts[0][1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, self.C_WHITE, 1)
# # # # #         for t in tracks:
# # # # #             wp = self.zm.pixel_to_world(*t["foot"])
# # # # #             if wp is not None:
# # # # #                 mx, my = int(wp[0]*self.MAP_SCALE), int(wp[1]*self.MAP_SCALE)
# # # # #                 cv2.circle(fmap, (mx, my), 8, self.C_GREEN if t["zones"] else (180, 180, 180), -1)
# # # # #         return fmap

# # # # #     def process_frame(self, frame):
# # # # #         frame = self.enhance(frame)
# # # # #         res = self.model.track(frame, persist=True, classes=0, verbose=False)[0]
# # # # #         active_ids, tracks, now = set(), [], time.time()

# # # # #         if res.boxes is not None and res.boxes.id is not None:
# # # # #             boxes, ids = res.boxes.xyxy.cpu().numpy(), res.boxes.id.cpu().numpy().astype(int)
# # # # #             genders = self.gender_model.predict(frame, boxes)
# # # # #             for box, tid, g in zip(boxes, ids, genders):
# # # # #                 active_ids.add(tid)
# # # # #                 foot = (int((box[0]+box[2])/2), int(box[3]))
# # # # #                 wp = self.zm.pixel_to_world(*foot)
# # # # #                 pz = []
# # # # #                 for name in self.zm.zones_pixel:
# # # # #                     raw = cv2.pointPolygonTest(np.array(self.zm.zones_world[name], np.float32), tuple(wp), False) >= 0 if wp is not None \
# # # # #                           else cv2.pointPolygonTest(np.array(self.zm.zones_pixel[name], np.float32), foot, False) >= 0
# # # # #                     self.zm.apply_hysteresis(tid, name, raw, now, self.event_log)
# # # # #                     if tid in self.zm.confirmed_inside[name]: pz.append(name)
# # # # #                 tracks.append({"id": tid, "bbox": box.astype(int), "foot": foot, "gender": g["label"], "zones": pz})

# # # # #         self.zm.cleanup_lost_tracks(active_ids, now, self.event_log)
# # # # #         out_img = frame.copy()
# # # # #         self.draw_zones(out_img)
# # # # #         for t in tracks: self.draw_track(out_img, t)
# # # # #         self.draw_hud(out_img)
        
# # # # #         # Periodic Metrics Logging
# # # # #         if time.time() - self.last_log_time >= 60:
# # # # #             log = {"time": self.zm.fmt_ts(now)}
# # # # #             for z in self.zm.zones_pixel:
# # # # #                 log[z] = {"current": len(self.zm.confirmed_inside[z]), "entries": self.zm.zone_entry_count[z]}
# # # # #             self.metrics_log.append(log)
# # # # #             with open(self.METRICS_FILE, "w") as f: json.dump(self.metrics_log, f, indent=2)
# # # # #             self.last_log_time = time.time()

# # # # #         with open(self.EVENTS_FILE, "w") as f: json.dump(self.event_log, f, indent=2, default=int)
# # # # #         return out_img, tracks, self.draw_floor_map(tracks)
# # # # # ---------------------------------------------------------------------------new------------
# # # # import cv2
# # # # import numpy as np
# # # # import json
# # # # import time
# # # # from ultralytics import YOLO
# # # # from gender_classifier import GenderClassifier
# # # # from zone import ZoneManager


# # # # # ─── CONFIGURATION ─────────────────────────────────────────────────────────────

# # # # ZONE_FILE    = "/home/keshav/rajan/new_pipeline/zones_runtime.json"
# # # # YOLO_MODEL   = "/home/keshav/rajan/new_pipeline/models/Yolov8x_openvino_model"
# # # # GENDER_MODEL = "/home/keshav/rajan/new_pipeline/models/mobilenetv3_gender_best.pth"
# # # # METRICS_FILE = "zone_metrics.json"
# # # # EVENTS_FILE  = "zone_events.json"

# # # # ENTRY_FRAMES = 4
# # # # EXIT_FRAMES  = 6


# # # # # ─── PALETTE ───────────────────────────────────────────────────────────────────

# # # # C_WHITE      = (255, 255, 255)
# # # # C_BLACK      = (0,   0,   0)
# # # # C_DARK       = (18,  18,  26)
# # # # C_ACCENT     = (255, 200,  60)
# # # # C_GREEN      = ( 60, 220, 120)    # HUD / floor-map highlights
# # # # C_RED        = ( 60,  60, 230)    # HUD exit counter
# # # # C_BBOX       = ( 0,  100,   0)    # dark green — bounding box & foot dot
# # # # C_LABEL_TEXT = (  0, 255,   0)    # bright green — label text

# # # # _ZONE_COLOR_BANK = [
# # # #     (255, 190,  60),
# # # #     (100, 220, 100),
# # # #     ( 60, 160, 255),
# # # #     (255, 100, 100),
# # # #     (180,  80, 220),
# # # #     (  0, 210, 210),
# # # #     (255, 220,   0),
# # # #     (255, 140,  40),
# # # #     (160, 255, 160),
# # # #     (255, 130, 220),
# # # # ]


# # # # # ─── DRAWING HELPERS ───────────────────────────────────────────────────────────

# # # # def draw_filled_rect_alpha(img, x1, y1, x2, y2, color, alpha=0.55):
# # # #     x1, y1 = max(0, x1), max(0, y1)
# # # #     x2, y2 = min(img.shape[1], x2), min(img.shape[0], y2)
# # # #     if x2 <= x1 or y2 <= y1:
# # # #         return
# # # #     sub  = img[y1:y2, x1:x2]
# # # #     rect = np.full(sub.shape, color, dtype=np.uint8)
# # # #     cv2.addWeighted(rect, alpha, sub, 1 - alpha, 0, sub)
# # # #     img[y1:y2, x1:x2] = sub


# # # # def draw_rounded_rect(img, x1, y1, x2, y2, r, color, thickness=2):
# # # #     cv2.line(img, (x1 + r, y1),   (x2 - r, y1),   color, thickness)
# # # #     cv2.line(img, (x1 + r, y2),   (x2 - r, y2),   color, thickness)
# # # #     cv2.line(img, (x1,   y1 + r), (x1,   y2 - r), color, thickness)
# # # #     cv2.line(img, (x2,   y1 + r), (x2,   y2 - r), color, thickness)
# # # #     cv2.ellipse(img, (x1 + r, y1 + r), (r, r), 180,  0, 90, color, thickness)
# # # #     cv2.ellipse(img, (x2 - r, y1 + r), (r, r), 270,  0, 90, color, thickness)
# # # #     cv2.ellipse(img, (x1 + r, y2 - r), (r, r),  90,  0, 90, color, thickness)
# # # #     cv2.ellipse(img, (x2 - r, y2 - r), (r, r),   0,  0, 90, color, thickness)


# # # # def draw_badge(img, text, x, y, bg_color, text_color=C_WHITE,
# # # #                font_scale=0.48, thickness=1, pad_x=10, pad_y=6):
# # # #     font = cv2.FONT_HERSHEY_DUPLEX
# # # #     (tw, th), _ = cv2.getTextSize(text, font, font_scale, thickness)
# # # #     bx1, by1 = x,                y - th - pad_y
# # # #     bx2, by2 = x + tw + 2*pad_x, y + pad_y
# # # #     r = max(1, (by2 - by1) // 2)
# # # #     draw_filled_rect_alpha(img, bx1, by1, bx2, by2, bg_color, alpha=0.80)
# # # #     draw_rounded_rect(img, bx1, by1, bx2, by2, r, bg_color, thickness=1)
# # # #     cv2.putText(img, text, (bx1 + pad_x, y),
# # # #                 font, font_scale, text_color, thickness, cv2.LINE_AA)
# # # #     return bx2 + 6


# # # # def draw_label_with_bg(img, text, x, y, text_color=C_WHITE,
# # # #                        bg_color=C_DARK, font_scale=0.5, thickness=1, pad=6):
# # # #     font = cv2.FONT_HERSHEY_DUPLEX
# # # #     (tw, th), _ = cv2.getTextSize(text, font, font_scale, thickness)
# # # #     draw_filled_rect_alpha(img,
# # # #                            x - pad, y - th - pad,
# # # #                            x + tw + pad, y + pad,
# # # #                            bg_color, alpha=0.75)
# # # #     cv2.putText(img, text, (x, y), font, font_scale,
# # # #                 text_color, thickness, cv2.LINE_AA)


# # # # # ─── DETECTOR ──────────────────────────────────────────────────────────────────

# # # # class Detector:

# # # #     def __init__(self, camera_name="cam_entry"):
# # # #         self.model        = YOLO(YOLO_MODEL)
# # # #         self.gender_model = GenderClassifier(GENDER_MODEL)

# # # #         with open(ZONE_FILE) as f:
# # # #             camera_data = json.load(f)[camera_name]

# # # #         self.zm = ZoneManager(
# # # #             camera_data,
# # # #             entry_frames = ENTRY_FRAMES,
# # # #             exit_frames  = EXIT_FRAMES,
# # # #         )

# # # #         # One colour per zone (polyline + name label only — no fill)
# # # #         self.zone_color = {}
# # # #         for idx, name in enumerate(self.zm.zones_pixel):
# # # #             self.zone_color[name] = _ZONE_COLOR_BANK[idx % len(_ZONE_COLOR_BANK)]

# # # #         self.event_log     = []
# # # #         self.metrics_log   = []
# # # #         self.last_log_time = time.time()

# # # #         self.MAP_SCALE = 150
# # # #         self.MAP_W     = 900
# # # #         self.MAP_H     = 750

# # # #     # ── Frame enhancement ──────────────────────────────────────────────────────

# # # #     @staticmethod
# # # #     def enhance(frame):
# # # #         gamma    = 1.5
# # # #         invGamma = 1.0 / gamma
# # # #         table    = np.array(
# # # #             [((i / 255.0) ** invGamma) * 255 for i in range(256)]
# # # #         ).astype("uint8")
# # # #         return cv2.LUT(frame, table)

# # # #     # ── HUD ────────────────────────────────────────────────────────────────────

# # # #     def _draw_hud(self, output):
# # # #         """Top-left panel: ZONE | NOW | ENTRY | EXIT  (no ID-mode badge)."""
# # # #         font    = cv2.FONT_HERSHEY_DUPLEX
# # # #         pad     = 14
# # # #         row_h   = 36
# # # #         col_w   = 110
# # # #         label_w = 115
# # # #         n_zones = len(self.zm.zones_pixel)

# # # #         panel_w = label_w + 3 * col_w + 2 * pad
# # # #         panel_h = pad + 28 + n_zones * row_h + pad

# # # #         draw_filled_rect_alpha(output, 10, 10,
# # # #                                10 + panel_w, 10 + panel_h, C_DARK, alpha=0.72)
# # # #         cv2.rectangle(output, (10, 10),
# # # #                       (10 + panel_w, 10 + panel_h), C_ACCENT, 1)

# # # #         hx = 10 + pad
# # # #         hy = 10 + pad + 16
# # # #         for title, offset in zip(
# # # #             ["ZONE", "NOW", "ENTRY", "EXIT"],
# # # #             [0, label_w, label_w + col_w, label_w + 2 * col_w],
# # # #         ):
# # # #             cv2.putText(output, title, (hx + offset, hy),
# # # #                         font, 0.42, C_ACCENT, 1, cv2.LINE_AA)

# # # #         div_y = 10 + pad + 22
# # # #         cv2.line(output, (10 + pad, div_y),
# # # #                  (10 + panel_w - pad, div_y), C_ACCENT, 1)

# # # #         for i, zone in enumerate(self.zm.zones_pixel):
# # # #             ry      = div_y + 8 + (i + 1) * row_h - 6
# # # #             inside  = len(self.zm.confirmed_inside[zone])
# # # #             entries = self.zm.zone_entry_count[zone]
# # # #             exits   = self.zm.zone_exit_count[zone]
# # # #             z_color = self.zone_color[zone]

# # # #             cv2.circle(output, (hx + 6, ry - 5), 5, z_color, -1)
# # # #             cv2.putText(output, zone.upper(),
# # # #                         (hx + 18, ry), font, 0.44, z_color, 1, cv2.LINE_AA)

# # # #             now_col = C_GREEN if inside > 0 else C_WHITE
# # # #             cv2.putText(output, str(inside),
# # # #                         (hx + label_w + 30, ry),
# # # #                         font, 0.55, now_col, 1, cv2.LINE_AA)
# # # #             cv2.putText(output, str(entries),
# # # #                         (hx + label_w + col_w + 20, ry),
# # # #                         font, 0.55, C_GREEN, 1, cv2.LINE_AA)
# # # #             cv2.putText(output, str(exits),
# # # #                         (hx + label_w + 2 * col_w + 20, ry),
# # # #                         font, 0.55, C_RED, 1, cv2.LINE_AA)

# # # #     # ── Zone outlines ──────────────────────────────────────────────────────────

# # # #     def _draw_zones(self, output):
# # # #         """
# # # #         Draw zone boundaries as coloured polylines with name labels.
# # # #         No transparent fill is applied — the interior is left untouched.
# # # #         """
# # # #         for name, poly in self.zm.zones_pixel.items():
# # # #             if len(poly) < 3:
# # # #                 continue
# # # #             pts   = np.array(poly, dtype=np.int32)
# # # #             color = self.zone_color[name]
# # # #             cv2.polylines(output, [pts], True, color, 2, cv2.LINE_AA)
# # # #             cx = int(np.mean([p[0] for p in poly]))
# # # #             cy = int(np.mean([p[1] for p in poly]))
# # # #             draw_label_with_bg(output, name.upper(), cx - 30, cy,
# # # #                                text_color=color, bg_color=C_DARK,
# # # #                                font_scale=0.5, thickness=1)

# # # #     # ── Per-track drawing ──────────────────────────────────────────────────────

# # # #     def _draw_track(self, output, track):
# # # #         """
# # # #         Renders each tracked person with:
# # # #           • thin dark-green bounding box
# # # #           • dark-green foot-point dot
# # # #           • black-background label above the box showing "ID {n} | {G}"
# # # #             in bright green text
# # # #         """
# # # #         x1, y1, x2, y2 = track["bbox"]
# # # #         tid             = track["id"]
# # # #         gender_label    = track.get("gender", "?")

# # # #         # ── Thin dark-green bounding box ──────────────────────────────────────
# # # #         cv2.rectangle(output, (x1, y1), (x2, y2), C_BBOX, 1)

# # # #         # ── Foot-point dot ────────────────────────────────────────────────────
# # # #         cv2.circle(output, track["foot"], 4, C_BBOX, -1)

# # # #         # ── Label: black background, bright-green text ─────────────────────
# # # #         label = f"ID {tid} | {gender_label}"
# # # #         font  = cv2.FONT_HERSHEY_SIMPLEX
# # # #         scale, thick = 0.5, 1
# # # #         (tw, th), _ = cv2.getTextSize(label, font, scale, thick)

# # # #         # Solid black rectangle behind text
# # # #         cv2.rectangle(output,
# # # #                       (x1, y1 - th - 8),
# # # #                       (x1 + tw + 6, y1),
# # # #                       C_BLACK, -1)
# # # #         cv2.putText(output, label, (x1 + 3, y1 - 4),
# # # #                     font, scale, C_LABEL_TEXT, thick, cv2.LINE_AA)

# # # #     # ── Bird's-eye floor map ───────────────────────────────────────────────────

# # # #     def draw_floor_map(self, tracks):
# # # #         floor_map = np.full((self.MAP_H, self.MAP_W, 3),
# # # #                             (22, 22, 30), dtype=np.uint8)

# # # #         # Metric grid
# # # #         for x in range(0, self.MAP_W, self.MAP_SCALE):
# # # #             cv2.line(floor_map, (x, 0), (x, self.MAP_H), (45, 45, 55), 1)
# # # #             cv2.putText(floor_map, f"{x // self.MAP_SCALE}m",
# # # #                         (x + 3, 13),
# # # #                         cv2.FONT_HERSHEY_DUPLEX, 0.3, (80, 80, 100), 1)
# # # #         for y in range(0, self.MAP_H, self.MAP_SCALE):
# # # #             cv2.line(floor_map, (0, y), (self.MAP_W, y), (45, 45, 55), 1)
# # # #             cv2.putText(floor_map, f"{y // self.MAP_SCALE}m",
# # # #                         (3, y + 13),
# # # #                         cv2.FONT_HERSHEY_DUPLEX, 0.3, (80, 80, 100), 1)

# # # #         # Zone outlines + stats (no fill on floor map either)
# # # #         for name, poly_world in self.zm.zones_world.items():
# # # #             if len(poly_world) < 3:
# # # #                 continue
# # # #             color = self.zone_color[name]
# # # #             pts   = np.array(
# # # #                 [[int(p[0] * self.MAP_SCALE), int(p[1] * self.MAP_SCALE)]
# # # #                  for p in poly_world],
# # # #                 dtype=np.int32,
# # # #             )
# # # #             cv2.polylines(floor_map, [pts], True, color, 2, cv2.LINE_AA)

# # # #             cx         = int(np.mean(pts[:, 0]))
# # # #             cy         = int(np.mean(pts[:, 1]))
# # # #             inside_now = len(self.zm.confirmed_inside[name])
# # # #             entries    = self.zm.zone_entry_count[name]
# # # #             exits      = self.zm.zone_exit_count[name]

# # # #             cv2.putText(floor_map, name.upper(),
# # # #                         (cx - 34, cy - 24),
# # # #                         cv2.FONT_HERSHEY_DUPLEX, 0.45, color, 1, cv2.LINE_AA)
# # # #             cv2.putText(floor_map, f"NOW {inside_now}",
# # # #                         (cx - 38, cy),
# # # #                         cv2.FONT_HERSHEY_DUPLEX, 0.40, C_GREEN, 1)
# # # #             cv2.putText(floor_map, f"E:{entries}",
# # # #                         (cx - 38, cy + 20),
# # # #                         cv2.FONT_HERSHEY_DUPLEX, 0.38, (120, 255, 120), 1)
# # # #             cv2.putText(floor_map, f"X:{exits}",
# # # #                         (cx + 14, cy + 20),
# # # #                         cv2.FONT_HERSHEY_DUPLEX, 0.38, (80, 80, 230), 1)

# # # #         # Person dots
# # # #         for track in tracks:
# # # #             world_pt = self.zm.pixel_to_world(track["foot"][0], track["foot"][1])
# # # #             if world_pt is None:
# # # #                 continue
# # # #             mx = int(world_pt[0] * self.MAP_SCALE)
# # # #             my = int(world_pt[1] * self.MAP_SCALE)
# # # #             if not (0 <= mx < self.MAP_W and 0 <= my < self.MAP_H):
# # # #                 continue
# # # #             dot_col = C_GREEN if track["zones"] else (180, 180, 180)
# # # #             cv2.circle(floor_map, (mx, my), 8, dot_col, -1)
# # # #             cv2.circle(floor_map, (mx, my), 9, C_WHITE,  1)
# # # #             cv2.putText(floor_map, str(track["id"]),
# # # #                         (mx + 11, my + 4),
# # # #                         cv2.FONT_HERSHEY_DUPLEX, 0.38, dot_col, 1)

# # # #         # Title bar
# # # #         cv2.rectangle(floor_map, (0, 0), (self.MAP_W, 24), (30, 30, 40), -1)
# # # #         cv2.line(floor_map, (0, 24), (self.MAP_W, 24), C_ACCENT, 1)
# # # #         cv2.putText(floor_map,
# # # #                     "STORE FLOOR MAP  —  bird's-eye view",
# # # #                     (self.MAP_W // 2 - 155, 17),
# # # #                     cv2.FONT_HERSHEY_DUPLEX, 0.46, C_ACCENT, 1)

# # # #         # Legend
# # # #         lx, ly = self.MAP_W - 140, self.MAP_H - 52
# # # #         draw_filled_rect_alpha(floor_map, lx - 8, ly - 14,
# # # #                                self.MAP_W - 6, self.MAP_H - 6,
# # # #                                C_DARK, alpha=0.70)
# # # #         cv2.circle(floor_map, (lx + 6, ly),      5, (180, 180, 180), -1)
# # # #         cv2.putText(floor_map, "open area",
# # # #                     (lx + 16, ly + 4),
# # # #                     cv2.FONT_HERSHEY_DUPLEX, 0.36, (180, 180, 180), 1)
# # # #         cv2.circle(floor_map, (lx + 6, ly + 22), 5, C_GREEN, -1)
# # # #         cv2.putText(floor_map, "in zone",
# # # #                     (lx + 16, ly + 26),
# # # #                     cv2.FONT_HERSHEY_DUPLEX, 0.36, C_GREEN, 1)

# # # #         return floor_map

# # # #     # ── Main per-frame entry-point ─────────────────────────────────────────────

# # # #     def process_frame(self, frame):
# # # #         frame = self.enhance(frame)
# # # #         now   = time.time()

# # # #         results = self.model.track(
# # # #             frame,
# # # #             persist = True,
# # # #             classes = 0,
# # # #             conf    = 0.1,
# # # #             iou     = 0.7,
# # # #             tracker = "botsort.yaml",
# # # #             verbose = False,
# # # #         )

# # # #         result     = results[0]
# # # #         output     = frame.copy()
# # # #         active_ids = set()
# # # #         tracks     = []

# # # #         if result.boxes is not None and result.boxes.id is not None:
# # # #             boxes        = result.boxes.xyxy.cpu().numpy()
# # # #             ids          = result.boxes.id.cpu().numpy().astype(int)
# # # #             gender_preds = self.gender_model.predict(frame, boxes)

# # # #             for box, tid, g_pred in zip(boxes, ids, gender_preds):
# # # #                 x1, y1, x2, y2 = box.astype(int)
# # # #                 cx, cy          = int((x1 + x2) / 2), int(y2)
# # # #                 foot_pixel      = (cx, cy)
# # # #                 active_ids.add(tid)
# # # #                 world_pt        = self.zm.pixel_to_world(cx, cy)

# # # #                 person_zones = []
# # # #                 for zone_name in self.zm.zones_pixel:
# # # #                     if world_pt is not None and len(self.zm.zones_world[zone_name]) >= 3:
# # # #                         raw_inside = (
# # # #                             cv2.pointPolygonTest(
# # # #                                 np.array(self.zm.zones_world[zone_name], np.float32),
# # # #                                 tuple(world_pt), False,
# # # #                             ) >= 0
# # # #                         )
# # # #                     else:
# # # #                         raw_inside = (
# # # #                             cv2.pointPolygonTest(
# # # #                                 np.array(self.zm.zones_pixel[zone_name], np.float32),
# # # #                                 foot_pixel, False,
# # # #                             ) >= 0
# # # #                         )

# # # #                     self.zm.apply_hysteresis(tid, zone_name, raw_inside, now, self.event_log)
# # # #                     if tid in self.zm.confirmed_inside[zone_name]:
# # # #                         person_zones.append(zone_name)

# # # #                 tracks.append({
# # # #                     "id":     tid,
# # # #                     "bbox":   (x1, y1, x2, y2),
# # # #                     "foot":   foot_pixel,
# # # #                     "zones":  person_zones,
# # # #                     "gender": g_pred["label"],
# # # #                 })

# # # #         self.zm.cleanup_lost_tracks(active_ids, now, self.event_log)

# # # #         self._draw_zones(output)
# # # #         for track in tracks:
# # # #             self._draw_track(output, track)
# # # #         self._draw_hud(output)

# # # #         with open(EVENTS_FILE, "w") as f:
# # # #             json.dump(self.event_log, f, indent=2, default=int)

# # # #         if time.time() - self.last_log_time >= 60:
# # # #             log = {"time": self.zm.fmt_ts(now)}
# # # #             for zone in self.zm.zones_pixel:
# # # #                 log[zone] = {
# # # #                     "current": len(self.zm.confirmed_inside[zone]),
# # # #                     "entries": self.zm.zone_entry_count[zone],
# # # #                     "exits":   self.zm.zone_exit_count[zone],
# # # #                 }
# # # #             self.metrics_log.append(log)
# # # #             with open(METRICS_FILE, "w") as f:
# # # #                 json.dump(self.metrics_log, f, indent=2, default=int)
# # # #             self.last_log_time = time.time()

# # # #         return output, tracks, self.draw_floor_map(tracks)
# # # # ------------------------new2----------------------------------------------
# # # import cv2
# # # import numpy as np
# # # import json
# # # import time
# # # from ultralytics import YOLO
# # # from gender_classifier import GenderClassifier
# # # from zone import ZoneManager


# # # # ─── CONFIGURATION ─────────────────────────────────────────────────────────────

# # # ZONE_FILE    = "/home/keshav/rajan/new_pipeline/zones_runtime.json"
# # # YOLO_MODEL   = "/home/keshav/rajan/new_pipeline/models/best.pt"
# # # GENDER_MODEL = "/home/keshav/rajan/new_pipeline/models/mobilenetv3_gender_best.pth"
# # # METRICS_FILE = "zone_metrics.json"
# # # EVENTS_FILE  = "zone_events.json"

# # # ENTRY_FRAMES = 4
# # # EXIT_FRAMES  = 6

# # # # ── Latency-tuning knobs ──────────────────────────────────────────────────────
# # # # Re-run gender inference for a track only after this many frames have passed
# # # # since the last confident prediction.  Higher → faster; lower → fresher labels.
# # # GENDER_CACHE_TTL    = 30     # frames
# # # GENDER_CONF_THRESH  = 0.80   # skip re-inference if cached conf >= this value

# # # # Write zone_events.json to disk at most this often (seconds).
# # # # Events are still accumulated in memory every frame.
# # # EVENTS_FLUSH_INTERVAL = 5.0  # seconds


# # # # ─── PALETTE ───────────────────────────────────────────────────────────────────

# # # C_WHITE      = (255, 255, 255)
# # # C_BLACK      = (0,   0,   0)
# # # C_DARK       = (18,  18,  26)
# # # C_ACCENT     = (255, 200,  60)
# # # C_GREEN      = ( 60, 220, 120)
# # # C_RED        = ( 60,  60, 230)
# # # C_BBOX       = (  0, 100,   0)   # dark green — bounding box & foot dot
# # # C_LABEL_TEXT = (  0, 255,   0)   # bright green — label text

# # # _ZONE_COLOR_BANK = [
# # #     (255, 190,  60),
# # #     (100, 220, 100),
# # #     ( 60, 160, 255),
# # #     (255, 100, 100),
# # #     (180,  80, 220),
# # #     (  0, 210, 210),
# # #     (255, 220,   0),
# # #     (255, 140,  40),
# # #     (160, 255, 160),
# # #     (255, 130, 220),
# # # ]


# # # # ─── DRAWING HELPERS ───────────────────────────────────────────────────────────

# # # def draw_filled_rect_alpha(img, x1, y1, x2, y2, color, alpha=0.55):
# # #     x1, y1 = max(0, x1), max(0, y1)
# # #     x2, y2 = min(img.shape[1], x2), min(img.shape[0], y2)
# # #     if x2 <= x1 or y2 <= y1:
# # #         return
# # #     sub  = img[y1:y2, x1:x2]
# # #     rect = np.full(sub.shape, color, dtype=np.uint8)
# # #     cv2.addWeighted(rect, alpha, sub, 1 - alpha, 0, sub)
# # #     img[y1:y2, x1:x2] = sub


# # # def draw_rounded_rect(img, x1, y1, x2, y2, r, color, thickness=2):
# # #     cv2.line(img, (x1 + r, y1),   (x2 - r, y1),   color, thickness)
# # #     cv2.line(img, (x1 + r, y2),   (x2 - r, y2),   color, thickness)
# # #     cv2.line(img, (x1,   y1 + r), (x1,   y2 - r), color, thickness)
# # #     cv2.line(img, (x2,   y1 + r), (x2,   y2 - r), color, thickness)
# # #     cv2.ellipse(img, (x1 + r, y1 + r), (r, r), 180,  0, 90, color, thickness)
# # #     cv2.ellipse(img, (x2 - r, y1 + r), (r, r), 270,  0, 90, color, thickness)
# # #     cv2.ellipse(img, (x1 + r, y2 - r), (r, r),  90,  0, 90, color, thickness)
# # #     cv2.ellipse(img, (x2 - r, y2 - r), (r, r),   0,  0, 90, color, thickness)


# # # def draw_badge(img, text, x, y, bg_color, text_color=C_WHITE,
# # #                font_scale=0.48, thickness=1, pad_x=10, pad_y=6):
# # #     font = cv2.FONT_HERSHEY_DUPLEX
# # #     (tw, th), _ = cv2.getTextSize(text, font, font_scale, thickness)
# # #     bx1, by1 = x,                y - th - pad_y
# # #     bx2, by2 = x + tw + 2*pad_x, y + pad_y
# # #     r = max(1, (by2 - by1) // 2)
# # #     draw_filled_rect_alpha(img, bx1, by1, bx2, by2, bg_color, alpha=0.80)
# # #     draw_rounded_rect(img, bx1, by1, bx2, by2, r, bg_color, thickness=1)
# # #     cv2.putText(img, text, (bx1 + pad_x, y),
# # #                 font, font_scale, text_color, thickness, cv2.LINE_AA)
# # #     return bx2 + 6


# # # def draw_label_with_bg(img, text, x, y, text_color=C_WHITE,
# # #                        bg_color=C_DARK, font_scale=0.5, thickness=1, pad=6):
# # #     font = cv2.FONT_HERSHEY_DUPLEX
# # #     (tw, th), _ = cv2.getTextSize(text, font, font_scale, thickness)
# # #     draw_filled_rect_alpha(img,
# # #                            x - pad, y - th - pad,
# # #                            x + tw + pad, y + pad,
# # #                            bg_color, alpha=0.75)
# # #     cv2.putText(img, text, (x, y), font, font_scale,
# # #                 text_color, thickness, cv2.LINE_AA)


# # # # ─── DETECTOR ──────────────────────────────────────────────────────────────────

# # # class Detector:

# # #     def __init__(self, camera_name="cam_entry"):
# # #         self.model        = YOLO(YOLO_MODEL)
# # #         self.gender_model = GenderClassifier(GENDER_MODEL)

# # #         with open(ZONE_FILE) as f:
# # #             camera_data = json.load(f)[camera_name]

# # #         self.zm = ZoneManager(
# # #             camera_data,
# # #             entry_frames = ENTRY_FRAMES,
# # #             exit_frames  = EXIT_FRAMES,
# # #         )

# # #         self.zone_color = {
# # #             name: _ZONE_COLOR_BANK[idx % len(_ZONE_COLOR_BANK)]
# # #             for idx, name in enumerate(self.zm.zones_pixel)
# # #         }

# # #         self.event_log     = []
# # #         self.metrics_log   = []
# # #         self.last_log_time      = time.time()
# # #         self.last_events_flush  = time.time()

# # #         # ── Gender cache ──────────────────────────────────────────────────────
# # #         # tid → {"label": str, "confidence": float, "age": int}
# # #         # "age" counts how many frames have passed since the last inference.
# # #         self._gender_cache: dict = {}

# # #         self._frame_count = 0

# # #         self.MAP_SCALE = 150
# # #         self.MAP_W     = 900
# # #         self.MAP_H     = 750

# # #     # ── Gender caching ─────────────────────────────────────────────────────────

# # #     def _resolve_genders(self, frame, boxes, ids):
# # #         """
# # #         Return a gender label for every (box, tid) pair.

# # #         Inference is skipped for tracks whose cached result is still fresh
# # #         (age < TTL) and confident (>= threshold).  Only stale or uncertain
# # #         tracks are batched together for a single GPU forward pass.
# # #         """
# # #         self._frame_count += 1

# # #         labels       = ["?"] * len(ids)
# # #         stale_idx    = []   # indices into ids/boxes that need re-inference
# # #         stale_boxes  = []

# # #         for i, tid in enumerate(ids):
# # #             cached = self._gender_cache.get(tid)
# # #             if (cached is not None
# # #                     and cached["age"] < GENDER_CACHE_TTL
# # #                     and cached["confidence"] >= GENDER_CONF_THRESH):
# # #                 labels[i] = cached["label"]
# # #                 cached["age"] += 1
# # #             else:
# # #                 stale_idx.append(i)
# # #                 stale_boxes.append(boxes[i])

# # #         # Batch-infer only the stale tracks
# # #         if stale_boxes:
# # #             preds = self.gender_model.predict(frame, stale_boxes)
# # #             for list_pos, orig_i in enumerate(stale_idx):
# # #                 pred = preds[list_pos]
# # #                 labels[orig_i] = pred["label"]
# # #                 self._gender_cache[ids[orig_i]] = {
# # #                     "label":      pred["label"],
# # #                     "confidence": pred["confidence"],
# # #                     "age":        0,
# # #                 }

# # #         # Evict cache entries for IDs no longer active this frame
# # #         active = set(ids)
# # #         for tid in list(self._gender_cache.keys()):
# # #             if tid not in active:
# # #                 del self._gender_cache[tid]

# # #         return labels

# # #     # ── HUD ────────────────────────────────────────────────────────────────────

# # #     def _draw_hud(self, output):
# # #         font    = cv2.FONT_HERSHEY_DUPLEX
# # #         pad     = 14
# # #         row_h   = 36
# # #         col_w   = 110
# # #         label_w = 115
# # #         n_zones = len(self.zm.zones_pixel)

# # #         panel_w = label_w + 3 * col_w + 2 * pad
# # #         panel_h = pad + 28 + n_zones * row_h + pad

# # #         draw_filled_rect_alpha(output, 10, 10,
# # #                                10 + panel_w, 10 + panel_h, C_DARK, alpha=0.72)
# # #         cv2.rectangle(output, (10, 10),
# # #                       (10 + panel_w, 10 + panel_h), C_ACCENT, 1)

# # #         hx = 10 + pad
# # #         hy = 10 + pad + 16
# # #         for title, offset in zip(
# # #             ["ZONE", "NOW", "ENTRY", "EXIT"],
# # #             [0, label_w, label_w + col_w, label_w + 2 * col_w],
# # #         ):
# # #             cv2.putText(output, title, (hx + offset, hy),
# # #                         font, 0.42, C_ACCENT, 1, cv2.LINE_AA)

# # #         div_y = 10 + pad + 22
# # #         cv2.line(output, (10 + pad, div_y),
# # #                  (10 + panel_w - pad, div_y), C_ACCENT, 1)

# # #         for i, zone in enumerate(self.zm.zones_pixel):
# # #             ry      = div_y + 8 + (i + 1) * row_h - 6
# # #             inside  = len(self.zm.confirmed_inside[zone])
# # #             entries = self.zm.zone_entry_count[zone]
# # #             exits   = self.zm.zone_exit_count[zone]
# # #             z_color = self.zone_color[zone]

# # #             cv2.circle(output, (hx + 6, ry - 5), 5, z_color, -1)
# # #             cv2.putText(output, zone.upper(),
# # #                         (hx + 18, ry), font, 0.44, z_color, 1, cv2.LINE_AA)

# # #             now_col = C_GREEN if inside > 0 else C_WHITE
# # #             cv2.putText(output, str(inside),
# # #                         (hx + label_w + 30, ry),
# # #                         font, 0.55, now_col, 1, cv2.LINE_AA)
# # #             cv2.putText(output, str(entries),
# # #                         (hx + label_w + col_w + 20, ry),
# # #                         font, 0.55, C_GREEN, 1, cv2.LINE_AA)
# # #             cv2.putText(output, str(exits),
# # #                         (hx + label_w + 2 * col_w + 20, ry),
# # #                         font, 0.55, C_RED, 1, cv2.LINE_AA)

# # #     # ── Zone outlines (no fill) ────────────────────────────────────────────────

# # #     def _draw_zones(self, output):
# # #         for name, poly in self.zm.zones_pixel.items():
# # #             if len(poly) < 3:
# # #                 continue
# # #             pts   = np.array(poly, dtype=np.int32)
# # #             color = self.zone_color[name]
# # #             cv2.polylines(output, [pts], True, color, 2, cv2.LINE_AA)
# # #             cx = int(np.mean([p[0] for p in poly]))
# # #             cy = int(np.mean([p[1] for p in poly]))
# # #             draw_label_with_bg(output, name.upper(), cx - 30, cy,
# # #                                text_color=color, bg_color=C_DARK,
# # #                                font_scale=0.5, thickness=1)

# # #     # ── Per-track drawing ──────────────────────────────────────────────────────

# # #     def _draw_track(self, output, track):
# # #         x1, y1, x2, y2 = track["bbox"]
# # #         gender_label    = track.get("gender", "?")

# # #         # Dark-green thin bbox
# # #         cv2.rectangle(output, (x1, y1), (x2, y2), C_BBOX, 1)

# # #         # Foot dot
# # #         cv2.circle(output, track["foot"], 4, C_BBOX, -1)

# # #         # Black-bg + bright-green text label
# # #         label = f"ID {track['id']} | {gender_label}"
# # #         font  = cv2.FONT_HERSHEY_SIMPLEX
# # #         (tw, th), _ = cv2.getTextSize(label, font, 0.5, 1)
# # #         cv2.rectangle(output,
# # #                       (x1, y1 - th - 8), (x1 + tw + 6, y1),
# # #                       C_BLACK, -1)
# # #         cv2.putText(output, label, (x1 + 3, y1 - 4),
# # #                     font, 0.5, C_LABEL_TEXT, 1, cv2.LINE_AA)

# # #     # ── Floor map ──────────────────────────────────────────────────────────────

# # #     def draw_floor_map(self, tracks):
# # #         floor_map = np.full((self.MAP_H, self.MAP_W, 3),
# # #                             (22, 22, 30), dtype=np.uint8)

# # #         for x in range(0, self.MAP_W, self.MAP_SCALE):
# # #             cv2.line(floor_map, (x, 0), (x, self.MAP_H), (45, 45, 55), 1)
# # #             cv2.putText(floor_map, f"{x // self.MAP_SCALE}m",
# # #                         (x + 3, 13), cv2.FONT_HERSHEY_DUPLEX, 0.3, (80, 80, 100), 1)
# # #         for y in range(0, self.MAP_H, self.MAP_SCALE):
# # #             cv2.line(floor_map, (0, y), (self.MAP_W, y), (45, 45, 55), 1)
# # #             cv2.putText(floor_map, f"{y // self.MAP_SCALE}m",
# # #                         (3, y + 13), cv2.FONT_HERSHEY_DUPLEX, 0.3, (80, 80, 100), 1)

# # #         for name, poly_world in self.zm.zones_world.items():
# # #             if len(poly_world) < 3:
# # #                 continue
# # #             color = self.zone_color[name]
# # #             pts   = np.array(
# # #                 [[int(p[0] * self.MAP_SCALE), int(p[1] * self.MAP_SCALE)]
# # #                  for p in poly_world], dtype=np.int32)
# # #             cv2.polylines(floor_map, [pts], True, color, 2, cv2.LINE_AA)
# # #             cx = int(np.mean(pts[:, 0]))
# # #             cy = int(np.mean(pts[:, 1]))
# # #             cv2.putText(floor_map, name.upper(),
# # #                         (cx - 34, cy - 24), cv2.FONT_HERSHEY_DUPLEX, 0.45, color, 1)
# # #             cv2.putText(floor_map, f"NOW {len(self.zm.confirmed_inside[name])}",
# # #                         (cx - 38, cy), cv2.FONT_HERSHEY_DUPLEX, 0.40, C_GREEN, 1)
# # #             cv2.putText(floor_map, f"E:{self.zm.zone_entry_count[name]}",
# # #                         (cx - 38, cy + 20), cv2.FONT_HERSHEY_DUPLEX, 0.38, (120, 255, 120), 1)
# # #             cv2.putText(floor_map, f"X:{self.zm.zone_exit_count[name]}",
# # #                         (cx + 14, cy + 20), cv2.FONT_HERSHEY_DUPLEX, 0.38, (80, 80, 230), 1)

# # #         for track in tracks:
# # #             wp = self.zm.pixel_to_world(track["foot"][0], track["foot"][1])
# # #             if wp is None:
# # #                 continue
# # #             mx, my = int(wp[0] * self.MAP_SCALE), int(wp[1] * self.MAP_SCALE)
# # #             if not (0 <= mx < self.MAP_W and 0 <= my < self.MAP_H):
# # #                 continue
# # #             dot_col = C_GREEN if track["zones"] else (180, 180, 180)
# # #             cv2.circle(floor_map, (mx, my), 8, dot_col, -1)
# # #             cv2.circle(floor_map, (mx, my), 9, C_WHITE,  1)
# # #             cv2.putText(floor_map, str(track["id"]),
# # #                         (mx + 11, my + 4), cv2.FONT_HERSHEY_DUPLEX, 0.38, dot_col, 1)

# # #         cv2.rectangle(floor_map, (0, 0), (self.MAP_W, 24), (30, 30, 40), -1)
# # #         cv2.line(floor_map, (0, 24), (self.MAP_W, 24), C_ACCENT, 1)
# # #         cv2.putText(floor_map, "STORE FLOOR MAP  —  bird's-eye view",
# # #                     (self.MAP_W // 2 - 155, 17),
# # #                     cv2.FONT_HERSHEY_DUPLEX, 0.46, C_ACCENT, 1)

# # #         lx, ly = self.MAP_W - 140, self.MAP_H - 52
# # #         draw_filled_rect_alpha(floor_map, lx - 8, ly - 14,
# # #                                self.MAP_W - 6, self.MAP_H - 6, C_DARK, alpha=0.70)
# # #         cv2.circle(floor_map, (lx + 6, ly),      5, (180, 180, 180), -1)
# # #         cv2.putText(floor_map, "open area", (lx + 16, ly + 4),
# # #                     cv2.FONT_HERSHEY_DUPLEX, 0.36, (180, 180, 180), 1)
# # #         cv2.circle(floor_map, (lx + 6, ly + 22), 5, C_GREEN, -1)
# # #         cv2.putText(floor_map, "in zone", (lx + 16, ly + 26),
# # #                     cv2.FONT_HERSHEY_DUPLEX, 0.36, C_GREEN, 1)

# # #         return floor_map

# # #     # ── Main per-frame entry-point ─────────────────────────────────────────────

# # #     def process_frame(self, frame):
# # #         now = time.time()

# # #         # ── YOLO tracking ─────────────────────────────────────────────────────
# # #         results = self.model.track(
# # #             frame,
# # #             persist = True,
# # #             classes = 0,
# # #             conf    = 0.1,
# # #             iou     = 0.7,
# # #             tracker = "botsort.yaml",
# # #             verbose = False,
# # #         )

# # #         result     = results[0]
# # #         output     = frame.copy()
# # #         active_ids = set()
# # #         tracks     = []

# # #         if result.boxes is not None and result.boxes.id is not None:
# # #             boxes = result.boxes.xyxy.cpu().numpy()
# # #             ids   = result.boxes.id.cpu().numpy().astype(int)

# # #             # ── Gender (cached batch inference) ───────────────────────────────
# # #             gender_labels = self._resolve_genders(frame, boxes, ids)

# # #             for box, tid, gender in zip(boxes, ids, gender_labels):
# # #                 x1, y1, x2, y2 = box.astype(int)
# # #                 cx, cy          = int((x1 + x2) / 2), int(y2)
# # #                 foot_pixel      = (cx, cy)
# # #                 active_ids.add(tid)
# # #                 world_pt        = self.zm.pixel_to_world(cx, cy)

# # #                 person_zones = []
# # #                 for zone_name in self.zm.zones_pixel:
# # #                     if world_pt is not None and len(self.zm.zones_world[zone_name]) >= 3:
# # #                         raw_inside = (
# # #                             cv2.pointPolygonTest(
# # #                                 np.array(self.zm.zones_world[zone_name], np.float32),
# # #                                 tuple(world_pt), False,
# # #                             ) >= 0
# # #                         )
# # #                     else:
# # #                         raw_inside = (
# # #                             cv2.pointPolygonTest(
# # #                                 np.array(self.zm.zones_pixel[zone_name], np.float32),
# # #                                 foot_pixel, False,
# # #                             ) >= 0
# # #                         )
# # #                     self.zm.apply_hysteresis(tid, zone_name, raw_inside, now, self.event_log)
# # #                     if tid in self.zm.confirmed_inside[zone_name]:
# # #                         person_zones.append(zone_name)

# # #                 tracks.append({
# # #                     "id":     tid,
# # #                     "bbox":   (x1, y1, x2, y2),
# # #                     "foot":   foot_pixel,
# # #                     "zones":  person_zones,
# # #                     "gender": gender,
# # #                 })

# # #         self.zm.cleanup_lost_tracks(active_ids, now, self.event_log)

# # #         # ── Render ────────────────────────────────────────────────────────────
# # #         self._draw_zones(output)
# # #         for track in tracks:
# # #             self._draw_track(output, track)
# # #         self._draw_hud(output)

# # #         # ── Periodic JSON flushes (not every frame) ───────────────────────────
# # #         if now - self.last_events_flush >= EVENTS_FLUSH_INTERVAL:
# # #             with open(EVENTS_FILE, "w") as f:
# # #                 json.dump(self.event_log, f, indent=2, default=int)
# # #             self.last_events_flush = now

# # #         if now - self.last_log_time >= 60:
# # #             log = {"time": self.zm.fmt_ts(now)}
# # #             for zone in self.zm.zones_pixel:
# # #                 log[zone] = {
# # #                     "current": len(self.zm.confirmed_inside[zone]),
# # #                     "entries": self.zm.zone_entry_count[zone],
# # #                     "exits":   self.zm.zone_exit_count[zone],
# # #                 }
# # #             self.metrics_log.append(log)
# # #             with open(METRICS_FILE, "w") as f:
# # #                 json.dump(self.metrics_log, f, indent=2, default=int)
# # #             self.last_log_time = now

# # #         return output, tracks, self.draw_floor_map(tracks)
# # # ---------NEW3-----------------------------
# # import cv2
# # import numpy as np
# # import json
# # import time
# # import threading
# # import queue
# # from ultralytics import YOLO
# # from gender_classifier import GenderClassifier
# # from zone import ZoneManager


# # # ─── CONFIGURATION ─────────────────────────────────────────────────────────────

# # ZONE_FILE    = "/home/keshav/rajan/new_pipeline/zones_runtime.json"
# # YOLO_MODEL   = "/home/keshav/rajan/new_pipeline/models/best.pt"
# # GENDER_MODEL = "/home/keshav/rajan/new_pipeline/models/mobilenetv3_gender_best.pth"
# # METRICS_FILE = "zone_metrics.json"
# # EVENTS_FILE  = "zone_events.json"

# # ENTRY_FRAMES = 4
# # EXIT_FRAMES  = 6

# # GENDER_CACHE_TTL    = 30    # frames before re-inference
# # GENDER_CONF_THRESH  = 0.80  # re-infer if confidence below this

# # EVENTS_FLUSH_INTERVAL  = 5.0   # seconds
# # METRICS_FLUSH_INTERVAL = 60.0  # seconds


# # # ─── PALETTE ───────────────────────────────────────────────────────────────────

# # C_WHITE      = (255, 255, 255)
# # C_BLACK      = (0,   0,   0)
# # C_DARK       = (18,  18,  26)
# # C_ACCENT     = (255, 200,  60)
# # C_GREEN      = ( 60, 220, 120)
# # C_RED        = ( 60,  60, 230)
# # C_BBOX       = (  0, 100,   0)
# # C_LABEL_TEXT = (  0, 255,   0)

# # _ZONE_COLOR_BANK = [
# #     (255, 190,  60),
# #     (100, 220, 100),
# #     ( 60, 160, 255),
# #     (255, 100, 100),
# #     (180,  80, 220),
# #     (  0, 210, 210),
# #     (255, 220,   0),
# #     (255, 140,  40),
# #     (160, 255, 160),
# #     (255, 130, 220),
# # ]


# # # ─── DRAWING HELPERS ───────────────────────────────────────────────────────────

# # def draw_filled_rect_alpha(img, x1, y1, x2, y2, color, alpha=0.55):
# #     x1, y1 = max(0, x1), max(0, y1)
# #     x2, y2 = min(img.shape[1], x2), min(img.shape[0], y2)
# #     if x2 <= x1 or y2 <= y1:
# #         return
# #     sub  = img[y1:y2, x1:x2]
# #     rect = np.full(sub.shape, color, dtype=np.uint8)
# #     cv2.addWeighted(rect, alpha, sub, 1 - alpha, 0, sub)
# #     img[y1:y2, x1:x2] = sub


# # def draw_rounded_rect(img, x1, y1, x2, y2, r, color, thickness=2):
# #     cv2.line(img, (x1+r, y1),   (x2-r, y1),   color, thickness)
# #     cv2.line(img, (x1+r, y2),   (x2-r, y2),   color, thickness)
# #     cv2.line(img, (x1,   y1+r), (x1,   y2-r), color, thickness)
# #     cv2.line(img, (x2,   y1+r), (x2,   y2-r), color, thickness)
# #     cv2.ellipse(img, (x1+r, y1+r), (r,r), 180, 0, 90, color, thickness)
# #     cv2.ellipse(img, (x2-r, y1+r), (r,r), 270, 0, 90, color, thickness)
# #     cv2.ellipse(img, (x1+r, y2-r), (r,r),  90, 0, 90, color, thickness)
# #     cv2.ellipse(img, (x2-r, y2-r), (r,r),   0, 0, 90, color, thickness)


# # def draw_badge(img, text, x, y, bg_color, text_color=C_WHITE,
# #                font_scale=0.48, thickness=1, pad_x=10, pad_y=6):
# #     font = cv2.FONT_HERSHEY_DUPLEX
# #     (tw, th), _ = cv2.getTextSize(text, font, font_scale, thickness)
# #     bx1, by1 = x, y - th - pad_y
# #     bx2, by2 = x + tw + 2*pad_x, y + pad_y
# #     r = max(1, (by2 - by1) // 2)
# #     draw_filled_rect_alpha(img, bx1, by1, bx2, by2, bg_color, alpha=0.80)
# #     draw_rounded_rect(img, bx1, by1, bx2, by2, r, bg_color, thickness=1)
# #     cv2.putText(img, text, (bx1+pad_x, y),
# #                 font, font_scale, text_color, thickness, cv2.LINE_AA)
# #     return bx2 + 6


# # def draw_label_with_bg(img, text, x, y, text_color=C_WHITE,
# #                        bg_color=C_DARK, font_scale=0.5, thickness=1, pad=6):
# #     font = cv2.FONT_HERSHEY_DUPLEX
# #     (tw, th), _ = cv2.getTextSize(text, font, font_scale, thickness)
# #     draw_filled_rect_alpha(img,
# #                            x-pad, y-th-pad, x+tw+pad, y+pad,
# #                            bg_color, alpha=0.75)
# #     cv2.putText(img, text, (x, y), font, font_scale,
# #                 text_color, thickness, cv2.LINE_AA)


# # # ─── DETECTOR ──────────────────────────────────────────────────────────────────

# # class Detector:
# #     """
# #     Threading model
# #     ───────────────
# #     Main thread  — YOLO → zone logic → draw → return frame   (every frame, no waiting)
# #     Gender thread — reads job queue, runs inference, updates gender_cache
# #     I/O thread   — drains io_queue, writes JSON files

# #     The main thread NEVER waits for the gender thread.
# #     It reads whatever label is already in the cache (may be 1-2 frames stale).
# #     That is invisible at ≥25 fps and has zero effect on zone accuracy.
# #     """

# #     def __init__(self, camera_name="cam_entry"):
# #         self.model        = YOLO(YOLO_MODEL)
# #         self.gender_model = GenderClassifier(GENDER_MODEL)

# #         with open(ZONE_FILE) as f:
# #             camera_data = json.load(f)[camera_name]

# #         self.zm = ZoneManager(camera_data,
# #                               entry_frames=ENTRY_FRAMES,
# #                               exit_frames=EXIT_FRAMES)

# #         self.zone_color = {
# #             name: _ZONE_COLOR_BANK[idx % len(_ZONE_COLOR_BANK)]
# #             for idx, name in enumerate(self.zm.zones_pixel)
# #         }

# #         # ── Gender cache (main thread reads, gender thread writes) ────────────
# #         # dict is written by gender thread under _cache_lock,
# #         # read by main thread without a lock (CPython dict reads are atomic).
# #         self._gender_cache      = {}   # tid → {"label", "confidence", "age"}
# #         self._cache_lock        = threading.Lock()

# #         # ── Gender job queue ──────────────────────────────────────────────────
# #         # Main thread puts (frame_copy, boxes, ids) here.
# #         # maxsize=1: if gender thread is busy, we drop the job rather than queue
# #         # up a backlog — stale cache labels are fine for display purposes.
# #         self._gender_queue = queue.Queue(maxsize=1)

# #         # ── I/O queue ─────────────────────────────────────────────────────────
# #         self._io_queue = queue.Queue()

# #         # ── Event / metrics state ─────────────────────────────────────────────
# #         self.event_log          = []
# #         self._flushed_count     = 0
# #         self.metrics_log        = []
# #         self._last_metrics      = 0.0
# #         self._last_events_flush = 0.0

# #         # ── Pre-allocated floor map base (static parts drawn once) ────────────
# #         self.MAP_SCALE     = 150
# #         self.MAP_W         = 900
# #         self.MAP_H         = 750
# #         self._floor_canvas = np.zeros((self.MAP_H, self.MAP_W, 3), dtype=np.uint8)
# #         self._build_floor_base()

# #         # ── Start background threads ──────────────────────────────────────────
# #         threading.Thread(target=self._gender_worker, daemon=True).start()
# #         threading.Thread(target=self._io_worker,     daemon=True).start()

# #     # =========================================================================
# #     # Background thread — gender inference
# #     # =========================================================================

# #     def _gender_worker(self):
# #         """
# #         Waits for a job, runs batched inference for stale/new tracks only,
# #         writes results into _gender_cache under _cache_lock.
# #         Never touches the main thread's frame pipeline.
# #         """
# #         while True:
# #             job = self._gender_queue.get()   # blocks until main thread posts a job
# #             if job is None:
# #                 break

# #             frame, boxes, ids = job

# #             # Separate stale/new from cached
# #             stale_idx, stale_boxes = [], []
# #             with self._cache_lock:
# #                 for i, tid in enumerate(ids):
# #                     cached = self._gender_cache.get(tid)
# #                     if (cached is not None
# #                             and cached["age"] < GENDER_CACHE_TTL
# #                             and cached["confidence"] >= GENDER_CONF_THRESH):
# #                         cached["age"] += 1          # still fresh — just bump age
# #                     else:
# #                         stale_idx.append(i)
# #                         stale_boxes.append(boxes[i])

# #             # Run inference only for stale/new tracks
# #             if stale_boxes:
# #                 preds = self.gender_model.predict(frame, stale_boxes)
# #                 with self._cache_lock:
# #                     for list_pos, orig_i in enumerate(stale_idx):
# #                         tid = ids[orig_i]
# #                         self._gender_cache[tid] = {
# #                             "label":      preds[list_pos]["label"],
# #                             "confidence": preds[list_pos]["confidence"],
# #                             "age":        0,
# #                         }

# #             # Evict tracks no longer visible
# #             active = set(ids)
# #             with self._cache_lock:
# #                 for tid in list(self._gender_cache.keys()):
# #                     if tid not in active:
# #                         del self._gender_cache[tid]

# #             self._gender_queue.task_done()

# #     # =========================================================================
# #     # Background thread — file I/O
# #     # =========================================================================

# #     def _io_worker(self):
# #         while True:
# #             filepath, data = self._io_queue.get()
# #             try:
# #                 with open(filepath, "w") as f:
# #                     json.dump(data, f, indent=2, default=int)
# #             except OSError as e:
# #                 print(f"[WARN] I/O write failed ({filepath}): {e}")
# #             self._io_queue.task_done()

# #     def _enqueue_write(self, filepath, data):
# #         """Post a write job — returns immediately, never blocks."""
# #         self._io_queue.put_nowait((filepath, data))

# #     # =========================================================================
# #     # Floor map — static base built once
# #     # =========================================================================

# #     def _build_floor_base(self):
# #         """Draw grid + zone outlines + title + legend onto _floor_canvas once."""
# #         self._floor_canvas[:] = (22, 22, 30)

# #         for x in range(0, self.MAP_W, self.MAP_SCALE):
# #             cv2.line(self._floor_canvas, (x, 0), (x, self.MAP_H), (45, 45, 55), 1)
# #             cv2.putText(self._floor_canvas, f"{x//self.MAP_SCALE}m",
# #                         (x+3, 13), cv2.FONT_HERSHEY_DUPLEX, 0.3, (80, 80, 100), 1)
# #         for y in range(0, self.MAP_H, self.MAP_SCALE):
# #             cv2.line(self._floor_canvas, (0, y), (self.MAP_W, y), (45, 45, 55), 1)
# #             cv2.putText(self._floor_canvas, f"{y//self.MAP_SCALE}m",
# #                         (3, y+13), cv2.FONT_HERSHEY_DUPLEX, 0.3, (80, 80, 100), 1)

# #         for name, poly_world in self.zm.zones_world.items():
# #             if len(poly_world) < 3:
# #                 continue
# #             color = self.zone_color[name]
# #             pts = np.array([[int(p[0]*self.MAP_SCALE), int(p[1]*self.MAP_SCALE)]
# #                             for p in poly_world], dtype=np.int32)
# #             cv2.polylines(self._floor_canvas, [pts], True, color, 2, cv2.LINE_AA)

# #         cv2.rectangle(self._floor_canvas, (0, 0), (self.MAP_W, 24), (30, 30, 40), -1)
# #         cv2.line(self._floor_canvas, (0, 24), (self.MAP_W, 24), C_ACCENT, 1)
# #         cv2.putText(self._floor_canvas, "STORE FLOOR MAP  —  bird's-eye view",
# #                     (self.MAP_W//2 - 155, 17),
# #                     cv2.FONT_HERSHEY_DUPLEX, 0.46, C_ACCENT, 1)

# #         lx, ly = self.MAP_W - 140, self.MAP_H - 52
# #         draw_filled_rect_alpha(self._floor_canvas,
# #                                lx-8, ly-14, self.MAP_W-6, self.MAP_H-6,
# #                                C_DARK, alpha=0.70)
# #         cv2.circle(self._floor_canvas, (lx+6, ly),    5, (180, 180, 180), -1)
# #         cv2.putText(self._floor_canvas, "open area", (lx+16, ly+4),
# #                     cv2.FONT_HERSHEY_DUPLEX, 0.36, (180, 180, 180), 1)
# #         cv2.circle(self._floor_canvas, (lx+6, ly+22), 5, C_GREEN, -1)
# #         cv2.putText(self._floor_canvas, "in zone",   (lx+16, ly+26),
# #                     cv2.FONT_HERSHEY_DUPLEX, 0.36, C_GREEN, 1)

# #     # =========================================================================
# #     # Drawing — called from main thread every frame
# #     # =========================================================================

# #     def _draw_hud(self, output):
# #         font    = cv2.FONT_HERSHEY_DUPLEX
# #         pad     = 14
# #         row_h   = 36
# #         col_w   = 110
# #         label_w = 115
# #         n_zones = len(self.zm.zones_pixel)
# #         panel_w = label_w + 3*col_w + 2*pad
# #         panel_h = pad + 28 + n_zones*row_h + pad

# #         draw_filled_rect_alpha(output, 10, 10,
# #                                10+panel_w, 10+panel_h, C_DARK, alpha=0.72)
# #         cv2.rectangle(output, (10, 10), (10+panel_w, 10+panel_h), C_ACCENT, 1)

# #         hx, hy = 10+pad, 10+pad+16
# #         for title, offset in zip(
# #             ["ZONE", "NOW", "ENTRY", "EXIT"],
# #             [0, label_w, label_w+col_w, label_w+2*col_w],
# #         ):
# #             cv2.putText(output, title, (hx+offset, hy),
# #                         font, 0.42, C_ACCENT, 1, cv2.LINE_AA)

# #         div_y = 10+pad+22
# #         cv2.line(output, (10+pad, div_y), (10+panel_w-pad, div_y), C_ACCENT, 1)

# #         for i, zone in enumerate(self.zm.zones_pixel):
# #             ry      = div_y + 8 + (i+1)*row_h - 6
# #             inside  = len(self.zm.confirmed_inside[zone])
# #             entries = self.zm.zone_entry_count[zone]
# #             exits   = self.zm.zone_exit_count[zone]
# #             z_color = self.zone_color[zone]

# #             cv2.circle(output, (hx+6, ry-5), 5, z_color, -1)
# #             cv2.putText(output, zone.upper(),
# #                         (hx+18, ry), font, 0.44, z_color, 1, cv2.LINE_AA)
# #             cv2.putText(output, str(inside),
# #                         (hx+label_w+30, ry), font, 0.55,
# #                         C_GREEN if inside > 0 else C_WHITE, 1, cv2.LINE_AA)
# #             cv2.putText(output, str(entries),
# #                         (hx+label_w+col_w+20, ry), font, 0.55, C_GREEN, 1, cv2.LINE_AA)
# #             cv2.putText(output, str(exits),
# #                         (hx+label_w+2*col_w+20, ry), font, 0.55, C_RED, 1, cv2.LINE_AA)

# #     def _draw_zones(self, output):
# #         for name, poly in self.zm.zones_pixel.items():
# #             if len(poly) < 3:
# #                 continue
# #             pts   = np.array(poly, dtype=np.int32)
# #             color = self.zone_color[name]
# #             cv2.polylines(output, [pts], True, color, 2, cv2.LINE_AA)
# #             cx = int(np.mean([p[0] for p in poly]))
# #             cy = int(np.mean([p[1] for p in poly]))
# #             draw_label_with_bg(output, name.upper(), cx-30, cy,
# #                                text_color=color, bg_color=C_DARK)

# #     def _draw_track(self, output, track):
# #         x1, y1, x2, y2  = track["bbox"]
# #         gender_label     = track.get("gender", "?")

# #         cv2.rectangle(output, (x1, y1), (x2, y2), C_BBOX, 1)
# #         cv2.circle(output, track["foot"], 4, C_BBOX, -1)

# #         label = f"ID {track['id']} | {gender_label}"
# #         font  = cv2.FONT_HERSHEY_SIMPLEX
# #         (tw, th), _ = cv2.getTextSize(label, font, 0.5, 1)
# #         cv2.rectangle(output, (x1, y1-th-8), (x1+tw+6, y1), C_BLACK, -1)
# #         cv2.putText(output, label, (x1+3, y1-4),
# #                     font, 0.5, C_LABEL_TEXT, 1, cv2.LINE_AA)

# #     def _draw_floor_map(self, tracks):
# #         """Copy static base then draw only the dynamic elements (person dots + live stats)."""
# #         floor_map = self._floor_canvas.copy()

# #         for name, poly_world in self.zm.zones_world.items():
# #             if len(poly_world) < 3:
# #                 continue
# #             color = self.zone_color[name]
# #             pts   = np.array([[int(p[0]*self.MAP_SCALE), int(p[1]*self.MAP_SCALE)]
# #                               for p in poly_world], dtype=np.int32)
# #             cx, cy = int(np.mean(pts[:,0])), int(np.mean(pts[:,1]))
# #             cv2.putText(floor_map, name.upper(),
# #                         (cx-34, cy-24), cv2.FONT_HERSHEY_DUPLEX, 0.45, color, 1)
# #             cv2.putText(floor_map, f"NOW {len(self.zm.confirmed_inside[name])}",
# #                         (cx-38, cy), cv2.FONT_HERSHEY_DUPLEX, 0.40, C_GREEN, 1)
# #             cv2.putText(floor_map, f"E:{self.zm.zone_entry_count[name]}",
# #                         (cx-38, cy+20), cv2.FONT_HERSHEY_DUPLEX, 0.38, (120,255,120), 1)
# #             cv2.putText(floor_map, f"X:{self.zm.zone_exit_count[name]}",
# #                         (cx+14, cy+20), cv2.FONT_HERSHEY_DUPLEX, 0.38, (80,80,230), 1)

# #         for track in tracks:
# #             wp = self.zm.pixel_to_world(track["foot"][0], track["foot"][1])
# #             if wp is None:
# #                 continue
# #             mx, my = int(wp[0]*self.MAP_SCALE), int(wp[1]*self.MAP_SCALE)
# #             if not (0 <= mx < self.MAP_W and 0 <= my < self.MAP_H):
# #                 continue
# #             dot_col = C_GREEN if track["zones"] else (180, 180, 180)
# #             cv2.circle(floor_map, (mx, my), 8, dot_col, -1)
# #             cv2.circle(floor_map, (mx, my), 9, C_WHITE,  1)
# #             cv2.putText(floor_map, str(track["id"]),
# #                         (mx+11, my+4), cv2.FONT_HERSHEY_DUPLEX, 0.38, dot_col, 1)

# #         return floor_map

# #     # =========================================================================
# #     # Main thread — called every frame by the caller
# #     # =========================================================================

# #     def process_frame(self, frame):
# #         """
# #         Runs entirely on the main thread. Returns every frame without waiting.

# #         Flow:
# #           1. YOLO track
# #           2. Zone hysteresis (must be synchronous — tracker state)
# #           3. Read gender labels from cache (written async by gender thread)
# #           4. Post gender job to background thread (non-blocking drop if busy)
# #           5. Draw zones / tracks / HUD / floor map
# #           6. Post I/O jobs if interval elapsed
# #           7. Return (annotated_frame, tracks, floor_map) immediately
# #         """
# #         now = time.time()

# #         # ── 1. YOLO ───────────────────────────────────────────────────────────
# #         results = self.model.track(
# #             frame,
# #             persist = True,
# #             classes = 0,
# #             conf    = 0.1,
# #             iou     = 0.7,
# #             tracker = "botsort.yaml",
# #             verbose = False,
# #         )

# #         result     = results[0]
# #         output     = frame.copy()
# #         active_ids = set()
# #         tracks     = []

# #         if result.boxes is not None and result.boxes.id is not None:
# #             boxes = result.boxes.xyxy.cpu().numpy()
# #             ids   = result.boxes.id.cpu().numpy().astype(int)

# #             # ── 2. Zone hysteresis ────────────────────────────────────────────
# #             for box, tid in zip(boxes, ids):
# #                 x1, y1, x2, y2 = box.astype(int)
# #                 cx, cy          = int((x1+x2)/2), int(y2)
# #                 foot_pixel      = (cx, cy)
# #                 active_ids.add(tid)
# #                 world_pt        = self.zm.pixel_to_world(cx, cy)

# #                 person_zones = []
# #                 for zone_name in self.zm.zones_pixel:
# #                     if world_pt is not None and len(self.zm.zones_world[zone_name]) >= 3:
# #                         raw_inside = cv2.pointPolygonTest(
# #                             np.array(self.zm.zones_world[zone_name], np.float32),
# #                             tuple(world_pt), False) >= 0
# #                     else:
# #                         raw_inside = cv2.pointPolygonTest(
# #                             np.array(self.zm.zones_pixel[zone_name], np.float32),
# #                             foot_pixel, False) >= 0

# #                     self.zm.apply_hysteresis(tid, zone_name, raw_inside, now, self.event_log)
# #                     if tid in self.zm.confirmed_inside[zone_name]:
# #                         person_zones.append(zone_name)

# #                 # ── 3. Read gender from cache (no lock needed — CPython atomic) ──
# #                 cached = self._gender_cache.get(tid)
# #                 gender = cached["label"] if cached else "?"

# #                 tracks.append({
# #                     "id":     tid,
# #                     "bbox":   (x1, y1, x2, y2),
# #                     "foot":   foot_pixel,
# #                     "zones":  person_zones,
# #                     "gender": gender,
# #                 })

# #             # ── 4. Post gender job — drop if thread is still working ──────────
# #             # This NEVER blocks. If the gender thread is busy the old cache
# #             # labels are used for this frame — completely fine.
# #             try:
# #                 self._gender_queue.put_nowait((frame.copy(), boxes, ids))
# #             except queue.Full:
# #                 pass

# #         self.zm.cleanup_lost_tracks(active_ids, now, self.event_log)

# #         # ── 5. Draw — synchronous, every frame ───────────────────────────────
# #         self._draw_zones(output)
# #         for track in tracks:
# #             self._draw_track(output, track)
# #         self._draw_hud(output)
# #         floor_map = self._draw_floor_map(tracks)

# #         # ── 6. Periodic I/O (background thread, non-blocking) ────────────────
# #         if now - self._last_events_flush >= EVENTS_FLUSH_INTERVAL:
# #             if len(self.event_log) > self._flushed_count:
# #                 self._enqueue_write(EVENTS_FILE, {"events": list(self.event_log)})
# #                 self._flushed_count = len(self.event_log)
# #             self._last_events_flush = now

# #         if now - self._last_metrics >= METRICS_FLUSH_INTERVAL:
# #             log = {"time": self.zm.fmt_ts(now)}
# #             for zone in self.zm.zones_pixel:
# #                 log[zone] = {
# #                     "current": len(self.zm.confirmed_inside[zone]),
# #                     "entries": self.zm.zone_entry_count[zone],
# #                     "exits":   self.zm.zone_exit_count[zone],
# #                 }
# #             self.metrics_log.append(log)
# #             self._enqueue_write(METRICS_FILE, self.metrics_log)
# #             self._last_metrics = now

# #         # ── 7. Return immediately — no waiting ───────────────────────────────
# #         return output, tracks, floor_map
# # ------new4---------------------------------------------------------------------
# import cv2
# import numpy as np
# import json
# import time
# import threading
# import queue
# from ultralytics import YOLO
# from gender_classifier import GenderClassifier
# from zone import ZoneManager


# # ─── CONFIGURATION ─────────────────────────────────────────────────────────────

# ZONE_FILE    = "/home/keshav/rajan/new_pipeline/zones_runtime.json"
# YOLO_MODEL   = "/home/keshav/rajan/new_pipeline/models/best.pt"
# GENDER_MODEL = "/home/keshav/rajan/new_pipeline/models/mobilenetv3_gender_best.pth"
# METRICS_FILE = "zone_metrics.json"
# EVENTS_FILE  = "zone_events.json"

# ENTRY_FRAMES = 4
# EXIT_FRAMES  = 6

# GENDER_CACHE_TTL    = 30    # frames before re-inference
# GENDER_CONF_THRESH  = 0.80  # re-infer if confidence below this

# EVENTS_FLUSH_INTERVAL  = 5.0   # seconds
# METRICS_FLUSH_INTERVAL = 60.0  # seconds


# # ─── PALETTE ───────────────────────────────────────────────────────────────────

# C_WHITE      = (255, 255, 255)
# C_BLACK      = (0,   0,   0)
# C_DARK       = (18,  18,  26)
# C_ACCENT     = (255, 200,  60)
# C_GREEN      = ( 60, 220, 120)
# C_RED        = ( 60,  60, 230)
# C_BBOX       = (  0, 100,   0)
# C_LABEL_TEXT = (  0, 255,   0)

# _ZONE_COLOR_BANK = [
#     (255, 190,  60),
#     (100, 220, 100),
#     ( 60, 160, 255),
#     (255, 100, 100),
#     (180,  80, 220),
#     (  0, 210, 210),
#     (255, 220,   0),
#     (255, 140,  40),
#     (160, 255, 160),
#     (255, 130, 220),
# ]


# # ─── DRAWING HELPERS ───────────────────────────────────────────────────────────

# def draw_filled_rect_alpha(img, x1, y1, x2, y2, color, alpha=0.55):
#     x1, y1 = max(0, x1), max(0, y1)
#     x2, y2 = min(img.shape[1], x2), min(img.shape[0], y2)
#     if x2 <= x1 or y2 <= y1:
#         return
#     sub  = img[y1:y2, x1:x2]
#     rect = np.full(sub.shape, color, dtype=np.uint8)
#     cv2.addWeighted(rect, alpha, sub, 1 - alpha, 0, sub)
#     img[y1:y2, x1:x2] = sub


# def draw_rounded_rect(img, x1, y1, x2, y2, r, color, thickness=2):
#     cv2.line(img, (x1+r, y1),   (x2-r, y1),   color, thickness)
#     cv2.line(img, (x1+r, y2),   (x2-r, y2),   color, thickness)
#     cv2.line(img, (x1,   y1+r), (x1,   y2-r), color, thickness)
#     cv2.line(img, (x2,   y1+r), (x2,   y2-r), color, thickness)
#     cv2.ellipse(img, (x1+r, y1+r), (r,r), 180, 0, 90, color, thickness)
#     cv2.ellipse(img, (x2-r, y1+r), (r,r), 270, 0, 90, color, thickness)
#     cv2.ellipse(img, (x1+r, y2-r), (r,r),  90, 0, 90, color, thickness)
#     cv2.ellipse(img, (x2-r, y2-r), (r,r),   0, 0, 90, color, thickness)


# def draw_badge(img, text, x, y, bg_color, text_color=C_WHITE,
#                font_scale=0.48, thickness=1, pad_x=10, pad_y=6):
#     font = cv2.FONT_HERSHEY_DUPLEX
#     (tw, th), _ = cv2.getTextSize(text, font, font_scale, thickness)
#     bx1, by1 = x, y - th - pad_y
#     bx2, by2 = x + tw + 2*pad_x, y + pad_y
#     r = max(1, (by2 - by1) // 2)
#     draw_filled_rect_alpha(img, bx1, by1, bx2, by2, bg_color, alpha=0.80)
#     draw_rounded_rect(img, bx1, by1, bx2, by2, r, bg_color, thickness=1)
#     cv2.putText(img, text, (bx1+pad_x, y),
#                 font, font_scale, text_color, thickness, cv2.LINE_AA)
#     return bx2 + 6


# def draw_label_with_bg(img, text, x, y, text_color=C_WHITE,
#                        bg_color=C_DARK, font_scale=0.5, thickness=1, pad=6):
#     font = cv2.FONT_HERSHEY_DUPLEX
#     (tw, th), _ = cv2.getTextSize(text, font, font_scale, thickness)
#     draw_filled_rect_alpha(img,
#                            x-pad, y-th-pad, x+tw+pad, y+pad,
#                            bg_color, alpha=0.75)
#     cv2.putText(img, text, (x, y), font, font_scale,
#                 text_color, thickness, cv2.LINE_AA)


# # ─── DETECTOR ──────────────────────────────────────────────────────────────────

# class Detector:
#     """
#     Threading model
#     ───────────────
#     Main thread  — YOLO → zone logic → draw → return frame   (every frame, no waiting)
#     Gender thread — reads job queue, runs inference, updates gender_cache
#     I/O thread   — drains io_queue, writes JSON files

#     The main thread NEVER waits for the gender thread.
#     It reads whatever label is already in the cache (may be 1-2 frames stale).
#     That is invisible at ≥25 fps and has zero effect on zone accuracy.
#     """

#     def __init__(self, camera_name="cam_entry"):
#         self.model        = YOLO(YOLO_MODEL)
#         self.gender_model = GenderClassifier(GENDER_MODEL)

#         with open(ZONE_FILE) as f:
#             camera_data = json.load(f)[camera_name]

#         self.zm = ZoneManager(camera_data,
#                               entry_frames=ENTRY_FRAMES,
#                               exit_frames=EXIT_FRAMES)

#         self.zone_color = {
#             name: _ZONE_COLOR_BANK[idx % len(_ZONE_COLOR_BANK)]
#             for idx, name in enumerate(self.zm.zones_pixel)
#         }

#         # ── Gender cache (main thread reads, gender thread writes) ────────────
#         # dict is written by gender thread under _cache_lock,
#         # read by main thread without a lock (CPython dict reads are atomic).
#         self._gender_cache      = {}   # tid → {"label", "confidence", "age"}
#         self._cache_lock        = threading.Lock()

#         # ── Gender job queue ──────────────────────────────────────────────────
#         # Main thread puts (frame_copy, boxes, ids) here.
#         # maxsize=1: if gender thread is busy, we drop the job rather than queue
#         # up a backlog — stale cache labels are fine for display purposes.
#         self._gender_queue = queue.Queue(maxsize=1)

#         # ── I/O queue ─────────────────────────────────────────────────────────
#         self._io_queue = queue.Queue()

#         # ── Event / metrics state ─────────────────────────────────────────────
#         self.event_log          = []
#         self._flushed_count     = 0
#         self.metrics_log        = []
#         self._last_metrics      = 0.0
#         self._last_events_flush = 0.0

#         # ── Pre-allocated floor map base (static parts drawn once) ────────────
#         self.MAP_SCALE     = 150
#         self.MAP_W         = 900
#         self.MAP_H         = 750
#         self._floor_canvas = np.zeros((self.MAP_H, self.MAP_W, 3), dtype=np.uint8)
#         self._build_floor_base()

#         # ── Start background threads ──────────────────────────────────────────
#         threading.Thread(target=self._gender_worker, daemon=True).start()
#         threading.Thread(target=self._io_worker,     daemon=True).start()

#     # =========================================================================
#     # Background thread — gender inference
#     # =========================================================================

#     def _gender_worker(self):
#         """
#         Waits for a job, runs batched inference for stale/new tracks only,
#         writes results into _gender_cache under _cache_lock.
#         Never touches the main thread's frame pipeline.
#         """
#         while True:
#             job = self._gender_queue.get()   # blocks until main thread posts a job
#             if job is None:
#                 break

#             frame, boxes, ids = job

#             # Snapshot the cache under the lock (fast — just a dict copy)
#             with self._cache_lock:
#                 cache_snapshot = dict(self._gender_cache)

#             # Determine stale/new tracks without holding the lock
#             stale_idx, stale_boxes = [], []
#             for i, tid in enumerate(ids):
#                 cached = cache_snapshot.get(tid)
#                 if (cached is not None
#                         and cached["age"] < GENDER_CACHE_TTL
#                         and cached["confidence"] >= GENDER_CONF_THRESH):
#                     # Still fresh — bump age in the live cache
#                     with self._cache_lock:
#                         if tid in self._gender_cache:
#                             self._gender_cache[tid]["age"] += 1
#                 else:
#                     stale_idx.append(i)
#                     stale_boxes.append(boxes[i])

#             # Run inference only for stale/new tracks
#             if stale_boxes:
#                 preds = self.gender_model.predict(frame, stale_boxes)
#                 with self._cache_lock:
#                     for list_pos, orig_i in enumerate(stale_idx):
#                         tid = ids[orig_i]
#                         self._gender_cache[tid] = {
#                             "label":      preds[list_pos]["label"],
#                             "confidence": preds[list_pos]["confidence"],
#                             "age":        0,
#                         }

#             # Evict tracks no longer visible
#             active = set(ids)
#             with self._cache_lock:
#                 for tid in list(self._gender_cache.keys()):
#                     if tid not in active:
#                         del self._gender_cache[tid]

#             self._gender_queue.task_done()

#     # =========================================================================
#     # Background thread — file I/O
#     # =========================================================================

#     def _io_worker(self):
#         while True:
#             filepath, data = self._io_queue.get()
#             try:
#                 with open(filepath, "w") as f:
#                     json.dump(data, f, indent=2, default=int)
#             except OSError as e:
#                 print(f"[WARN] I/O write failed ({filepath}): {e}")
#             self._io_queue.task_done()

#     def _enqueue_write(self, filepath, data):
#         """Post a write job — returns immediately, never blocks."""
#         self._io_queue.put_nowait((filepath, data))

#     # =========================================================================
#     # Floor map — static base built once
#     # =========================================================================

#     def _build_floor_base(self):
#         """Draw grid + zone outlines + title + legend onto _floor_canvas once."""
#         self._floor_canvas[:] = (22, 22, 30)

#         for x in range(0, self.MAP_W, self.MAP_SCALE):
#             cv2.line(self._floor_canvas, (x, 0), (x, self.MAP_H), (45, 45, 55), 1)
#             cv2.putText(self._floor_canvas, f"{x//self.MAP_SCALE}m",
#                         (x+3, 13), cv2.FONT_HERSHEY_DUPLEX, 0.3, (80, 80, 100), 1)
#         for y in range(0, self.MAP_H, self.MAP_SCALE):
#             cv2.line(self._floor_canvas, (0, y), (self.MAP_W, y), (45, 45, 55), 1)
#             cv2.putText(self._floor_canvas, f"{y//self.MAP_SCALE}m",
#                         (3, y+13), cv2.FONT_HERSHEY_DUPLEX, 0.3, (80, 80, 100), 1)

#         for name, poly_world in self.zm.zones_world.items():
#             if len(poly_world) < 3:
#                 continue
#             color = self.zone_color[name]
#             pts = np.array([[int(p[0]*self.MAP_SCALE), int(p[1]*self.MAP_SCALE)]
#                             for p in poly_world], dtype=np.int32)
#             cv2.polylines(self._floor_canvas, [pts], True, color, 2, cv2.LINE_AA)

#         cv2.rectangle(self._floor_canvas, (0, 0), (self.MAP_W, 24), (30, 30, 40), -1)
#         cv2.line(self._floor_canvas, (0, 24), (self.MAP_W, 24), C_ACCENT, 1)
#         cv2.putText(self._floor_canvas, "STORE FLOOR MAP  —  bird's-eye view",
#                     (self.MAP_W//2 - 155, 17),
#                     cv2.FONT_HERSHEY_DUPLEX, 0.46, C_ACCENT, 1)

#         lx, ly = self.MAP_W - 140, self.MAP_H - 52
#         draw_filled_rect_alpha(self._floor_canvas,
#                                lx-8, ly-14, self.MAP_W-6, self.MAP_H-6,
#                                C_DARK, alpha=0.70)
#         cv2.circle(self._floor_canvas, (lx+6, ly),    5, (180, 180, 180), -1)
#         cv2.putText(self._floor_canvas, "open area", (lx+16, ly+4),
#                     cv2.FONT_HERSHEY_DUPLEX, 0.36, (180, 180, 180), 1)
#         cv2.circle(self._floor_canvas, (lx+6, ly+22), 5, C_GREEN, -1)
#         cv2.putText(self._floor_canvas, "in zone",   (lx+16, ly+26),
#                     cv2.FONT_HERSHEY_DUPLEX, 0.36, C_GREEN, 1)

#     # =========================================================================
#     # Drawing — called from main thread every frame
#     # =========================================================================

#     def _draw_hud(self, output):
#         font    = cv2.FONT_HERSHEY_DUPLEX
#         pad     = 14
#         row_h   = 36
#         col_w   = 110
#         label_w = 115
#         n_zones = len(self.zm.zones_pixel)
#         panel_w = label_w + 3*col_w + 2*pad
#         panel_h = pad + 28 + n_zones*row_h + pad

#         draw_filled_rect_alpha(output, 10, 10,
#                                10+panel_w, 10+panel_h, C_DARK, alpha=0.72)
#         cv2.rectangle(output, (10, 10), (10+panel_w, 10+panel_h), C_ACCENT, 1)

#         hx, hy = 10+pad, 10+pad+16
#         for title, offset in zip(
#             ["ZONE", "NOW", "ENTRY", "EXIT"],
#             [0, label_w, label_w+col_w, label_w+2*col_w],
#         ):
#             cv2.putText(output, title, (hx+offset, hy),
#                         font, 0.42, C_ACCENT, 1, cv2.LINE_AA)

#         div_y = 10+pad+22
#         cv2.line(output, (10+pad, div_y), (10+panel_w-pad, div_y), C_ACCENT, 1)

#         for i, zone in enumerate(self.zm.zones_pixel):
#             ry      = div_y + 8 + (i+1)*row_h - 6
#             inside  = len(self.zm.confirmed_inside[zone])
#             entries = self.zm.zone_entry_count[zone]
#             exits   = self.zm.zone_exit_count[zone]
#             z_color = self.zone_color[zone]

#             cv2.circle(output, (hx+6, ry-5), 5, z_color, -1)
#             cv2.putText(output, zone.upper(),
#                         (hx+18, ry), font, 0.44, z_color, 1, cv2.LINE_AA)
#             cv2.putText(output, str(inside),
#                         (hx+label_w+30, ry), font, 0.55,
#                         C_GREEN if inside > 0 else C_WHITE, 1, cv2.LINE_AA)
#             cv2.putText(output, str(entries),
#                         (hx+label_w+col_w+20, ry), font, 0.55, C_GREEN, 1, cv2.LINE_AA)
#             cv2.putText(output, str(exits),
#                         (hx+label_w+2*col_w+20, ry), font, 0.55, C_RED, 1, cv2.LINE_AA)

#     def _draw_zones(self, output):
#         for name, poly in self.zm.zones_pixel.items():
#             if len(poly) < 3:
#                 continue
#             pts   = np.array(poly, dtype=np.int32)
#             color = self.zone_color[name]
#             cv2.polylines(output, [pts], True, color, 2, cv2.LINE_AA)
#             cx = int(np.mean([p[0] for p in poly]))
#             cy = int(np.mean([p[1] for p in poly]))
#             draw_label_with_bg(output, name.upper(), cx-30, cy,
#                                text_color=color, bg_color=C_DARK)

#     def _draw_track(self, output, track):
#         x1, y1, x2, y2  = track["bbox"]
#         gender_label     = track.get("gender", "?")

#         cv2.rectangle(output, (x1, y1), (x2, y2), C_BBOX, 1)
#         cv2.circle(output, track["foot"], 4, C_BBOX, -1)

#         label = f"ID {track['id']} | {gender_label}"
#         font  = cv2.FONT_HERSHEY_SIMPLEX
#         (tw, th), _ = cv2.getTextSize(label, font, 0.5, 1)
#         cv2.rectangle(output, (x1, y1-th-8), (x1+tw+6, y1), C_BLACK, -1)
#         cv2.putText(output, label, (x1+3, y1-4),
#                     font, 0.5, C_LABEL_TEXT, 1, cv2.LINE_AA)

#     def _draw_floor_map(self, tracks):
#         """Copy static base then draw only the dynamic elements (person dots + live stats)."""
#         floor_map = self._floor_canvas.copy()

#         for name, poly_world in self.zm.zones_world.items():
#             if len(poly_world) < 3:
#                 continue
#             color = self.zone_color[name]
#             pts   = np.array([[int(p[0]*self.MAP_SCALE), int(p[1]*self.MAP_SCALE)]
#                               for p in poly_world], dtype=np.int32)
#             cx, cy = int(np.mean(pts[:,0])), int(np.mean(pts[:,1]))
#             cv2.putText(floor_map, name.upper(),
#                         (cx-34, cy-24), cv2.FONT_HERSHEY_DUPLEX, 0.45, color, 1)
#             cv2.putText(floor_map, f"NOW {len(self.zm.confirmed_inside[name])}",
#                         (cx-38, cy), cv2.FONT_HERSHEY_DUPLEX, 0.40, C_GREEN, 1)
#             cv2.putText(floor_map, f"E:{self.zm.zone_entry_count[name]}",
#                         (cx-38, cy+20), cv2.FONT_HERSHEY_DUPLEX, 0.38, (120,255,120), 1)
#             cv2.putText(floor_map, f"X:{self.zm.zone_exit_count[name]}",
#                         (cx+14, cy+20), cv2.FONT_HERSHEY_DUPLEX, 0.38, (80,80,230), 1)

#         for track in tracks:
#             wp = self.zm.pixel_to_world(track["foot"][0], track["foot"][1])
#             if wp is None:
#                 continue
#             mx, my = int(wp[0]*self.MAP_SCALE), int(wp[1]*self.MAP_SCALE)
#             if not (0 <= mx < self.MAP_W and 0 <= my < self.MAP_H):
#                 continue
#             dot_col = C_GREEN if track["zones"] else (180, 180, 180)
#             cv2.circle(floor_map, (mx, my), 8, dot_col, -1)
#             cv2.circle(floor_map, (mx, my), 9, C_WHITE,  1)
#             cv2.putText(floor_map, str(track["id"]),
#                         (mx+11, my+4), cv2.FONT_HERSHEY_DUPLEX, 0.38, dot_col, 1)

#         return floor_map

#     # =========================================================================
#     # Main thread — called every frame by the caller
#     # =========================================================================

#     def process_frame(self, frame):
#         """
#         Runs entirely on the main thread. Returns every frame without waiting.

#         Flow:
#           1. YOLO track
#           2. Zone hysteresis (must be synchronous — tracker state)
#           3. Read gender labels from cache (written async by gender thread)
#           4. Post gender job to background thread (non-blocking drop if busy)
#           5. Draw zones / tracks / HUD / floor map
#           6. Post I/O jobs if interval elapsed
#           7. Return (annotated_frame, tracks, floor_map) immediately
#         """
#         now = time.time()

#         # ── 1. YOLO ───────────────────────────────────────────────────────────
#         results = self.model.track(
#             frame,
#             persist = True,
#             classes = 0,
#             conf    = 0.1,
#             iou     = 0.7,
#             tracker = "botsort.yaml",
#             verbose = False,
#         )

#         result     = results[0]
#         output     = frame.copy()
#         active_ids = set()
#         tracks     = []

#         if result.boxes is not None and result.boxes.id is not None:
#             boxes = result.boxes.xyxy.cpu().numpy()
#             ids   = result.boxes.id.cpu().numpy().astype(int)

#             # ── 2. Zone hysteresis ────────────────────────────────────────────
#             for box, tid in zip(boxes, ids):
#                 x1, y1, x2, y2 = box.astype(int)
#                 cx, cy          = int((x1+x2)/2), int(y2)
#                 foot_pixel      = (cx, cy)
#                 active_ids.add(tid)
#                 world_pt        = self.zm.pixel_to_world(cx, cy)

#                 person_zones = []
#                 for zone_name in self.zm.zones_pixel:
#                     if world_pt is not None and len(self.zm.zones_world[zone_name]) >= 3:
#                         raw_inside = cv2.pointPolygonTest(
#                             np.array(self.zm.zones_world[zone_name], np.float32),
#                             tuple(world_pt), False) >= 0
#                     else:
#                         raw_inside = cv2.pointPolygonTest(
#                             np.array(self.zm.zones_pixel[zone_name], np.float32),
#                             foot_pixel, False) >= 0

#                     self.zm.apply_hysteresis(tid, zone_name, raw_inside, now, self.event_log)
#                     if tid in self.zm.confirmed_inside[zone_name]:
#                         person_zones.append(zone_name)

#                 # ── 3. Read gender from cache (no lock needed — CPython atomic) ──
#                 cached = self._gender_cache.get(tid)
#                 gender = cached["label"] if cached else "?"

#                 tracks.append({
#                     "id":     tid,
#                     "bbox":   (x1, y1, x2, y2),
#                     "foot":   foot_pixel,
#                     "zones":  person_zones,
#                     "gender": gender,
#                 })

#             # ── 4. Post gender job — drop if thread is still working ──────────
#             # This NEVER blocks. If the gender thread is busy the old cache
#             # labels are used for this frame — completely fine.
#             try:
#                 self._gender_queue.put_nowait((frame.copy(), boxes, ids))
#             except queue.Full:
#                 pass

#         self.zm.cleanup_lost_tracks(active_ids, now, self.event_log)

#         # ── 5. Draw — synchronous, every frame ───────────────────────────────
#         self._draw_zones(output)
#         for track in tracks:
#             self._draw_track(output, track)
#         self._draw_hud(output)
#         floor_map = self._draw_floor_map(tracks)

#         # ── 6. Periodic I/O (background thread, non-blocking) ────────────────
#         # ── Periodic event flush ──────────────────────────────────────────────
#         # Write only the NEW events since the last flush, then trim the in-memory
#         # list so it never grows beyond one flush-interval's worth of entries.
#         if now - self._last_events_flush >= EVENTS_FLUSH_INTERVAL:
#             new_events = self.event_log[self._flushed_count:]
#             if new_events:
#                 self._enqueue_write(EVENTS_FILE, {"events": new_events})
#                 # Trim already-flushed events from memory
#                 del self.event_log[:self._flushed_count]
#                 self._flushed_count = 0
#             self._last_events_flush = now

#         if now - self._last_metrics >= METRICS_FLUSH_INTERVAL:
#             log = {"time": self.zm.fmt_ts(now)}
#             for zone in self.zm.zones_pixel:
#                 log[zone] = {
#                     "current": len(self.zm.confirmed_inside[zone]),
#                     "entries": self.zm.zone_entry_count[zone],
#                     "exits":   self.zm.zone_exit_count[zone],
#                 }
#             self.metrics_log.append(log)
#             self._enqueue_write(METRICS_FILE, self.metrics_log)
#             self._last_metrics = now

#         # ── 7. Return immediately — no waiting ───────────────────────────────
#         return output, tracks, floor_map
# ------new5--------------------------------------------------------------------------------
import cv2
import numpy as np
import json
import time
import threading
import queue
from ultralytics import YOLO
from gender_classifier import GenderClassifier
from zone import ZoneManager


# ─── CONFIGURATION ─────────────────────────────────────────────────────────────

ZONE_FILE    = "/home/keshav/rajan/new_pipeline/zones_runtime.json"
YOLO_MODEL   = "/home/keshav/rajan/new_pipeline/models/best.pt"
GENDER_MODEL = "/home/keshav/rajan/new_pipeline/models/mobilenetv3_gender_best.pth"
METRICS_FILE = "zone_metrics.json"
EVENTS_FILE  = "zone_events.json"

ENTRY_FRAMES = 4
EXIT_FRAMES  = 6

# Gender cache: re-run inference when age >= TTL or confidence < threshold
GENDER_CACHE_TTL    = 30     # frames
GENDER_CONF_THRESH  = 0.80

# Flush intervals
EVENTS_FLUSH_INTERVAL  = 5.0    # seconds
METRICS_FLUSH_INTERVAL = 60.0   # seconds

# Memory bounds
_MAX_EVENT_LOG_FLUSHED  = 500   # trim event_log after this many flushed entries
_MAX_METRICS_LOG        = 120   # ~2 hours at 60 s interval
_IO_QUEUE_MAXSIZE       = 50    # ~4 min backlog at normal write rate


# ─── PALETTE ───────────────────────────────────────────────────────────────────

C_WHITE      = (255, 255, 255)
C_BLACK      = (0,   0,   0)
C_DARK       = (18,  18,  26)
C_ACCENT     = (255, 200,  60)
C_GREEN      = ( 60, 220, 120)
C_RED        = ( 60,  60, 230)
C_BBOX       = (  0, 100,   0)   # dark green bounding box
C_LABEL_TEXT = (  0, 255,   0)   # bright green label text

_ZONE_COLOR_BANK = [
    (255, 190,  60),
    (100, 220, 100),
    ( 60, 160, 255),
    (255, 100, 100),
    (180,  80, 220),
    (  0, 210, 210),
    (255, 220,   0),
    (255, 140,  40),
    (160, 255, 160),
    (255, 130, 220),
]


# ─── DRAWING HELPERS ───────────────────────────────────────────────────────────

def draw_filled_rect_alpha(img, x1, y1, x2, y2, color, alpha=0.55):
    """Blit a solid colour rectangle at the given opacity."""
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(img.shape[1], x2), min(img.shape[0], y2)
    if x2 <= x1 or y2 <= y1:
        return
    sub  = img[y1:y2, x1:x2]
    rect = np.full(sub.shape, color, dtype=np.uint8)
    cv2.addWeighted(rect, alpha, sub, 1 - alpha, 0, sub)
    img[y1:y2, x1:x2] = sub


def draw_rounded_rect(img, x1, y1, x2, y2, r, color, thickness=2):
    """Stroke a rectangle with rounded corners."""
    cv2.line(img, (x1+r, y1),   (x2-r, y1),   color, thickness)
    cv2.line(img, (x1+r, y2),   (x2-r, y2),   color, thickness)
    cv2.line(img, (x1,   y1+r), (x1,   y2-r), color, thickness)
    cv2.line(img, (x2,   y1+r), (x2,   y2-r), color, thickness)
    cv2.ellipse(img, (x1+r, y1+r), (r, r), 180, 0, 90, color, thickness)
    cv2.ellipse(img, (x2-r, y1+r), (r, r), 270, 0, 90, color, thickness)
    cv2.ellipse(img, (x1+r, y2-r), (r, r),  90, 0, 90, color, thickness)
    cv2.ellipse(img, (x2-r, y2-r), (r, r),   0, 0, 90, color, thickness)


def draw_label_with_bg(img, text, x, y, text_color=C_WHITE,
                       bg_color=C_DARK, font_scale=0.5, thickness=1, pad=6):
    """Draw text with a semi-transparent dark backing rectangle."""
    font = cv2.FONT_HERSHEY_DUPLEX
    (tw, th), _ = cv2.getTextSize(text, font, font_scale, thickness)
    draw_filled_rect_alpha(img,
                           x - pad, y - th - pad,
                           x + tw + pad, y + pad,
                           bg_color, alpha=0.75)
    cv2.putText(img, text, (x, y), font, font_scale,
                text_color, thickness, cv2.LINE_AA)


# ─── DETECTOR ──────────────────────────────────────────────────────────────────

class Detector:
    """
    Full tracking pipeline with two background threads.

    Threading model
    ───────────────
    Main thread   — YOLO track → zone hysteresis → read gender cache
                    → draw frame → return result every frame, no waiting.

    Gender thread — receives (frame, boxes, ids) via _gender_queue,
                    runs batched inference for stale/new tracks only,
                    writes results into _gender_cache under _cache_lock.
                    Never touches zone logic or frame drawing.

    I/O thread    — drains _io_queue, writes JSON files to disk.
                    Never blocks the main thread.

    Key invariants
    ──────────────
    - YOLO tracker state is single-threaded (main thread only).
    - Zone entry/exit counts and confirmed_inside are single-threaded.
    - Gender labels are display-only — a 1-frame lag is invisible.
    - All background threads survive exceptions (try/except/finally).
    - No background thread can crash or freeze the main video loop.
    """

    def __init__(self, camera_name="cam_entry"):
        # ── Models ────────────────────────────────────────────────────────────
        self.model        = YOLO(YOLO_MODEL)
        self.gender_model = GenderClassifier(GENDER_MODEL)

        # ── Zone manager ──────────────────────────────────────────────────────
        with open(ZONE_FILE) as f:
            camera_data = json.load(f)[camera_name]

        self.zm = ZoneManager(
            camera_data,
            entry_frames = ENTRY_FRAMES,
            exit_frames  = EXIT_FRAMES,
        )

        # One display colour per zone
        self.zone_color = {
            name: _ZONE_COLOR_BANK[idx % len(_ZONE_COLOR_BANK)]
            for idx, name in enumerate(self.zm.zones_pixel)
        }

        # ── Gender cache ──────────────────────────────────────────────────────
        # Written by gender thread (under _cache_lock).
        # Read by main thread without a lock — CPython dict .get() is atomic.
        self._gender_cache = {}    # tid → {"label": str, "confidence": float, "age": int}
        self._cache_lock   = threading.Lock()

        # ── Queues ────────────────────────────────────────────────────────────
        # maxsize=1: if gender thread is busy, drop the job — cached label is fine.
        self._gender_queue = queue.Queue(maxsize=1)
        # maxsize=_IO_QUEUE_MAXSIZE: bounded so a slow disk can't OOM the process.
        self._io_queue     = queue.Queue(maxsize=_IO_QUEUE_MAXSIZE)

        # ── Event / metrics logs ──────────────────────────────────────────────
        self.event_log          = []
        self._flushed_count     = 0
        self.metrics_log        = []
        self._last_metrics      = 0.0
        self._last_events_flush = 0.0

        # ── Pre-allocated static floor map canvas ─────────────────────────────
        # Grid, zone outlines, title bar and legend are drawn once at startup.
        # Every frame only adds the per-frame dynamic elements on a copy.
        self.MAP_SCALE     = 150
        self.MAP_W         = 900
        self.MAP_H         = 750
        self._floor_canvas = np.zeros((self.MAP_H, self.MAP_W, 3), dtype=np.uint8)
        self._build_floor_base()

        # ── Start background threads ──────────────────────────────────────────
        threading.Thread(target=self._gender_worker, daemon=True).start()
        threading.Thread(target=self._io_worker,     daemon=True).start()

    # =========================================================================
    # Gender thread
    # =========================================================================

    def _gender_worker(self):
        """
        Waits for a (frame, boxes, ids) job.
        Runs batched GPU inference only for stale/new/uncertain tracks.
        Writes results into _gender_cache under _cache_lock.
        task_done() is guaranteed even on exception so the queue never jams.
        """
        while True:
            job = self._gender_queue.get()
            if job is None:                    # shutdown sentinel
                self._gender_queue.task_done()
                break

            try:
                frame, boxes, ids = job

                # Snapshot the cache under the lock (very fast — dict copy)
                with self._cache_lock:
                    cache_snapshot = dict(self._gender_cache)

                # Classify each track: fresh (use cache) or stale (need inference)
                stale_idx, stale_boxes = [], []
                for i, tid in enumerate(ids):
                    cached = cache_snapshot.get(tid)
                    if (cached is not None
                            and cached["age"] < GENDER_CACHE_TTL
                            and cached["confidence"] >= GENDER_CONF_THRESH):
                        # Fresh — increment age in live cache; no GPU work needed
                        with self._cache_lock:
                            if tid in self._gender_cache:
                                self._gender_cache[tid]["age"] += 1
                    else:
                        stale_idx.append(i)
                        stale_boxes.append(boxes[i])

                # One batched forward pass for all stale/new tracks
                if stale_boxes:
                    preds = self.gender_model.predict(frame, stale_boxes)
                    with self._cache_lock:
                        for list_pos, orig_i in enumerate(stale_idx):
                            tid = ids[orig_i]
                            self._gender_cache[tid] = {
                                "label":      preds[list_pos]["label"],
                                "confidence": preds[list_pos]["confidence"],
                                "age":        0,
                            }

                # Evict tracks that are no longer in this job's frame
                active = set(ids)
                with self._cache_lock:
                    for tid in list(self._gender_cache.keys()):
                        if tid not in active:
                            del self._gender_cache[tid]

            except Exception as e:
                # Log but never let the thread die
                print(f"[WARN] gender worker error: {e}")
            finally:
                self._gender_queue.task_done()

    # =========================================================================
    # I/O thread
    # =========================================================================

    def _io_worker(self):
        """
        Drains _io_queue and writes JSON to disk.
        Catches all exceptions so the thread never dies silently.
        task_done() fires in finally so the queue never jams.
        """
        while True:
            filepath, data = self._io_queue.get()
            try:
                with open(filepath, "w") as f:
                    # default=str handles any non-serialisable types gracefully
                    json.dump(data, f, indent=2, default=str)
            except Exception as e:
                print(f"[WARN] I/O write failed ({filepath}): {e}")
            finally:
                self._io_queue.task_done()

    def _enqueue_write(self, filepath, data):
        """
        Post a write job — returns immediately, never blocks, never crashes.
        If the I/O queue is full (disk saturated) the write is silently dropped
        with a warning. A skipped write is always better than a crashed process.
        """
        try:
            self._io_queue.put_nowait((filepath, data))
        except queue.Full:
            print(f"[WARN] I/O queue full — dropping write to {filepath}")

    # =========================================================================
    # Floor map — static base built once at startup
    # =========================================================================

    def _build_floor_base(self):
        """
        Draw the parts of the floor map that never change:
        metric grid, zone outlines, title bar, legend.
        Called once in __init__. Every frame copies this and draws dots on top.
        """
        self._floor_canvas[:] = (22, 22, 30)

        # Metric grid
        for x in range(0, self.MAP_W, self.MAP_SCALE):
            cv2.line(self._floor_canvas, (x, 0), (x, self.MAP_H), (45, 45, 55), 1)
            cv2.putText(self._floor_canvas, f"{x // self.MAP_SCALE}m",
                        (x + 3, 13), cv2.FONT_HERSHEY_DUPLEX, 0.3, (80, 80, 100), 1)
        for y in range(0, self.MAP_H, self.MAP_SCALE):
            cv2.line(self._floor_canvas, (0, y), (self.MAP_W, y), (45, 45, 55), 1)
            cv2.putText(self._floor_canvas, f"{y // self.MAP_SCALE}m",
                        (3, y + 13), cv2.FONT_HERSHEY_DUPLEX, 0.3, (80, 80, 100), 1)

        # Zone outlines (positions never change)
        for name, poly_world in self.zm.zones_world.items():
            if len(poly_world) < 3:
                continue
            color = self.zone_color[name]
            pts   = np.array(
                [[int(p[0] * self.MAP_SCALE), int(p[1] * self.MAP_SCALE)]
                 for p in poly_world], dtype=np.int32)
            cv2.polylines(self._floor_canvas, [pts], True, color, 2, cv2.LINE_AA)

        # Title bar
        cv2.rectangle(self._floor_canvas, (0, 0), (self.MAP_W, 24), (30, 30, 40), -1)
        cv2.line(self._floor_canvas, (0, 24), (self.MAP_W, 24), C_ACCENT, 1)
        cv2.putText(self._floor_canvas, "STORE FLOOR MAP  —  bird's-eye view",
                    (self.MAP_W // 2 - 155, 17),
                    cv2.FONT_HERSHEY_DUPLEX, 0.46, C_ACCENT, 1)

        # Legend
        lx, ly = self.MAP_W - 140, self.MAP_H - 52
        draw_filled_rect_alpha(self._floor_canvas,
                               lx - 8, ly - 14, self.MAP_W - 6, self.MAP_H - 6,
                               C_DARK, alpha=0.70)
        cv2.circle(self._floor_canvas, (lx + 6, ly),     5, (180, 180, 180), -1)
        cv2.putText(self._floor_canvas, "open area", (lx + 16, ly + 4),
                    cv2.FONT_HERSHEY_DUPLEX, 0.36, (180, 180, 180), 1)
        cv2.circle(self._floor_canvas, (lx + 6, ly + 22), 5, C_GREEN, -1)
        cv2.putText(self._floor_canvas, "in zone",   (lx + 16, ly + 26),
                    cv2.FONT_HERSHEY_DUPLEX, 0.36, C_GREEN, 1)

    # =========================================================================
    # Drawing helpers — called from main thread every frame
    # =========================================================================

    def _draw_hud(self, output):
        """Top-left stats panel: ZONE | NOW | ENTRY | EXIT per zone."""
        font    = cv2.FONT_HERSHEY_DUPLEX
        pad     = 14
        row_h   = 36
        col_w   = 110
        label_w = 115
        n_zones = len(self.zm.zones_pixel)
        panel_w = label_w + 3 * col_w + 2 * pad
        panel_h = pad + 28 + n_zones * row_h + pad

        draw_filled_rect_alpha(output, 10, 10,
                               10 + panel_w, 10 + panel_h, C_DARK, alpha=0.72)
        cv2.rectangle(output, (10, 10),
                      (10 + panel_w, 10 + panel_h), C_ACCENT, 1)

        hx, hy = 10 + pad, 10 + pad + 16
        for title, offset in zip(
            ["ZONE", "NOW", "ENTRY", "EXIT"],
            [0, label_w, label_w + col_w, label_w + 2 * col_w],
        ):
            cv2.putText(output, title, (hx + offset, hy),
                        font, 0.42, C_ACCENT, 1, cv2.LINE_AA)

        div_y = 10 + pad + 22
        cv2.line(output, (10 + pad, div_y),
                 (10 + panel_w - pad, div_y), C_ACCENT, 1)

        for i, zone in enumerate(self.zm.zones_pixel):
            ry      = div_y + 8 + (i + 1) * row_h - 6
            inside  = len(self.zm.confirmed_inside[zone])
            entries = self.zm.zone_entry_count[zone]
            exits   = self.zm.zone_exit_count[zone]
            z_color = self.zone_color[zone]

            cv2.circle(output, (hx + 6, ry - 5), 5, z_color, -1)
            cv2.putText(output, zone.upper(),
                        (hx + 18, ry), font, 0.44, z_color, 1, cv2.LINE_AA)
            cv2.putText(output, str(inside),
                        (hx + label_w + 30, ry), font, 0.55,
                        C_GREEN if inside > 0 else C_WHITE, 1, cv2.LINE_AA)
            cv2.putText(output, str(entries),
                        (hx + label_w + col_w + 20, ry),
                        font, 0.55, C_GREEN, 1, cv2.LINE_AA)
            cv2.putText(output, str(exits),
                        (hx + label_w + 2 * col_w + 20, ry),
                        font, 0.55, C_RED, 1, cv2.LINE_AA)

    def _draw_zones(self, output):
        """Zone boundary polylines with name labels. No transparent fill."""
        for name, poly in self.zm.zones_pixel.items():
            if len(poly) < 3:
                continue
            pts   = np.array(poly, dtype=np.int32)
            color = self.zone_color[name]
            cv2.polylines(output, [pts], True, color, 2, cv2.LINE_AA)
            cx = int(np.mean([p[0] for p in poly]))
            cy = int(np.mean([p[1] for p in poly]))
            draw_label_with_bg(output, name.upper(), cx - 30, cy,
                               text_color=color, bg_color=C_DARK)

    def _draw_track(self, output, track):
        """
        Dark-green thin bounding box + foot dot.
        Label above the box (falls back to below if too close to top edge).
        Both left and right label edges are clamped to frame bounds.
        """
        x1, y1, x2, y2 = track["bbox"]
        gender_label    = track.get("gender", "?")

        # Bounding box and foot dot
        cv2.rectangle(output, (x1, y1), (x2, y2), C_BBOX, 1)
        cv2.circle(output, track["foot"], 4, C_BBOX, -1)

        # Label positioning
        label = f"ID {track['id']} | {gender_label}"
        font  = cv2.FONT_HERSHEY_SIMPLEX
        (tw, th), _ = cv2.getTextSize(label, font, 0.5, 1)

        # Place above bbox; if too close to top edge place below instead
        if y1 - th - 8 >= 0:
            lx, ly = x1, y1
        else:
            lx, ly = x1, y2 + th + 8

        # Clamp both horizontal edges to frame bounds
        lx = max(0, lx)
        rx = min(output.shape[1], lx + tw + 6)

        cv2.rectangle(output, (lx, ly - th - 8), (rx, ly), C_BLACK, -1)
        cv2.putText(output, label, (lx + 3, ly - 4),
                    font, 0.5, C_LABEL_TEXT, 1, cv2.LINE_AA)

    def _draw_floor_map(self, tracks):
        """
        Copy the static base canvas and draw per-frame dynamic elements:
        live zone stats (NOW/E/X) and person dots.
        """
        floor_map = self._floor_canvas.copy()

        # Live zone stats
        for name, poly_world in self.zm.zones_world.items():
            if len(poly_world) < 3:
                continue
            color = self.zone_color[name]
            pts   = np.array(
                [[int(p[0] * self.MAP_SCALE), int(p[1] * self.MAP_SCALE)]
                 for p in poly_world], dtype=np.int32)
            cx = int(np.mean(pts[:, 0]))
            cy = int(np.mean(pts[:, 1]))
            cv2.putText(floor_map, name.upper(),
                        (cx - 34, cy - 24),
                        cv2.FONT_HERSHEY_DUPLEX, 0.45, color, 1)
            cv2.putText(floor_map, f"NOW {len(self.zm.confirmed_inside[name])}",
                        (cx - 38, cy),
                        cv2.FONT_HERSHEY_DUPLEX, 0.40, C_GREEN, 1)
            cv2.putText(floor_map, f"E:{self.zm.zone_entry_count[name]}",
                        (cx - 38, cy + 20),
                        cv2.FONT_HERSHEY_DUPLEX, 0.38, (120, 255, 120), 1)
            cv2.putText(floor_map, f"X:{self.zm.zone_exit_count[name]}",
                        (cx + 14, cy + 20),
                        cv2.FONT_HERSHEY_DUPLEX, 0.38, (80, 80, 230), 1)

        # Person dots
        for track in tracks:
            wp = self.zm.pixel_to_world(track["foot"][0], track["foot"][1])
            if wp is None:
                continue
            mx = int(wp[0] * self.MAP_SCALE)
            my = int(wp[1] * self.MAP_SCALE)
            if not (0 <= mx < self.MAP_W and 0 <= my < self.MAP_H):
                continue
            dot_col = C_GREEN if track["zones"] else (180, 180, 180)
            cv2.circle(floor_map, (mx, my), 8, dot_col, -1)
            cv2.circle(floor_map, (mx, my), 9, C_WHITE,  1)
            cv2.putText(floor_map, str(track["id"]),
                        (mx + 11, my + 4),
                        cv2.FONT_HERSHEY_DUPLEX, 0.38, dot_col, 1)

        return floor_map

    # =========================================================================
    # Main per-frame entry point
    # =========================================================================

    def process_frame(self, frame):
        """
        Called from the video loop on every captured frame.
        Runs entirely on the main thread. Returns immediately without waiting
        for any background thread.

        Steps
        -----
        1. YOLO tracking  — produces bounding boxes + tracker IDs
        2. Zone hysteresis — updates entry/exit state and event log
        3. Gender cache read — reads last known label (may be 1 frame stale)
        4. Gender job post — drops job into queue non-blocking (skip if busy)
        5. Gender cache eviction — remove entries for vanished tracks immediately
        6. Draw — zones, tracks, HUD, floor map
        7. Periodic I/O — flush events and metrics to background thread
        8. Return (annotated_frame, tracks, floor_map)
        """
        now = time.time()

        # ── 1. YOLO ───────────────────────────────────────────────────────────
        results = self.model.track(
            frame,
            persist = True,
            classes = 0,
            conf    = 0.1,
            iou     = 0.7,
            tracker = "botsort.yaml",
            verbose = False,
        )

        result     = results[0]
        output     = frame.copy()
        active_ids = set()
        tracks     = []

        if result.boxes is not None and result.boxes.id is not None:
            boxes = result.boxes.xyxy.cpu().numpy()
            ids   = result.boxes.id.cpu().numpy().astype(int)

            for box, tid in zip(boxes, ids):
                x1, y1, x2, y2 = box.astype(int)
                cx, cy          = int((x1 + x2) / 2), int(y2)
                foot_pixel      = (cx, cy)
                active_ids.add(tid)
                world_pt        = self.zm.pixel_to_world(cx, cy)

                # ── 2. Zone hysteresis ────────────────────────────────────────
                person_zones = []
                for zone_name in self.zm.zones_pixel:
                    if world_pt is not None and len(self.zm.zones_world[zone_name]) >= 3:
                        raw_inside = (
                            cv2.pointPolygonTest(
                                np.array(self.zm.zones_world[zone_name], np.float32),
                                tuple(world_pt), False,
                            ) >= 0
                        )
                    else:
                        raw_inside = (
                            cv2.pointPolygonTest(
                                np.array(self.zm.zones_pixel[zone_name], np.float32),
                                foot_pixel, False,
                            ) >= 0
                        )
                    self.zm.apply_hysteresis(tid, zone_name, raw_inside,
                                             now, self.event_log)
                    if tid in self.zm.confirmed_inside[zone_name]:
                        person_zones.append(zone_name)

                # ── 3. Gender cache read (CPython dict.get is atomic) ─────────
                cached = self._gender_cache.get(tid)
                gender = cached["label"] if cached else "?"

                tracks.append({
                    "id":     tid,
                    "bbox":   (x1, y1, x2, y2),
                    "foot":   foot_pixel,
                    "zones":  person_zones,
                    "gender": gender,
                })

            # ── 4. Post gender job — non-blocking, drop if thread is busy ─────
            if not self._gender_queue.full():
                try:
                    self._gender_queue.put_nowait((frame.copy(), boxes, ids))
                except queue.Full:
                    pass   # race between full() check and put_nowait — harmless

        # ── Cleanup lost tracks ───────────────────────────────────────────────
        self.zm.cleanup_lost_tracks(active_ids, now, self.event_log)

        # ── 5. Evict gender cache for vanished tracks (main thread, immediate) ─
        # The gender worker evicts based on the most recent job's ids, which is
        # 1 frame old. This eviction runs on the current frame's active_ids,
        # preventing a reused tracker ID from inheriting a stale cached label.
        with self._cache_lock:
            for tid in list(self._gender_cache.keys()):
                if tid not in active_ids:
                    del self._gender_cache[tid]

        # ── 6. Draw ───────────────────────────────────────────────────────────
        self._draw_zones(output)
        for track in tracks:
            self._draw_track(output, track)
        self._draw_hud(output)
        floor_map = self._draw_floor_map(tracks)

        # ── 7. Periodic I/O ───────────────────────────────────────────────────
        if now - self._last_events_flush >= EVENTS_FLUSH_INTERVAL:
            new_events = self.event_log[self._flushed_count:]
            if new_events:
                self._enqueue_write(EVENTS_FILE, {"events": new_events})
                self._flushed_count = len(self.event_log)
            # Trim the already-flushed prefix to keep memory bounded
            if self._flushed_count > _MAX_EVENT_LOG_FLUSHED:
                del self.event_log[:self._flushed_count]
                self._flushed_count = 0
            self._last_events_flush = now

        if now - self._last_metrics >= METRICS_FLUSH_INTERVAL:
            log = {"time": self.zm.fmt_ts(now)}
            for zone in self.zm.zones_pixel:
                log[zone] = {
                    "current": len(self.zm.confirmed_inside[zone]),
                    "entries": self.zm.zone_entry_count[zone],
                    "exits":   self.zm.zone_exit_count[zone],
                }
            self.metrics_log.append(log)
            if len(self.metrics_log) > _MAX_METRICS_LOG:
                self.metrics_log = self.metrics_log[-_MAX_METRICS_LOG:]
            self._enqueue_write(METRICS_FILE, self.metrics_log)
            self._last_metrics = now

        # ── 8. Return ─────────────────────────────────────────────────────────
        return output, tracks, floor_map