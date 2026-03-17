# import cv2
# import numpy as np
# import json
# import time
# from ultralytics import YOLO
# from gender_classifier import GenderClassifier


# ZONE_FILE    = "/home/keshav/rajan/new_pipeline/zones_runtime.json"
# METRICS_FILE = "zone_metrics.json"
# EVENTS_FILE  = "zone_events.json"
# DWELL_FILE   = "zone_dwell_summary.json"
# gender_model="/home/keshav/rajan/new_pipeline/models/mobilenetv3_gender_best.pth"
# classifier=GenderClassifier(gender_model)

# ENTRY_FRAMES = 4
# EXIT_FRAMES  = 6

# UNIQUE_ID_GLOBAL = False

# C_WHITE    = (255, 255, 255)
# C_BLACK    = (0,   0,   0)
# C_DARK     = (18,  18,  26)
# C_ACCENT   = (255, 200,  60)
# C_GREEN    = ( 60, 220, 120)
# C_RED      = ( 60,  60, 230)

# _ZONE_COLOR_BANK = [
#     ((255, 190,  60), (200, 140,  40)),
#     ((100, 220, 100), ( 60, 180,  60)),
#     (( 60, 160, 255), ( 40, 120, 220)),
#     ((255, 100, 100), (220,  60,  60)),
#     ((180,  80, 220), (140,  50, 180)),
#     ((  0, 210, 210), (  0, 160, 160)),
#     ((255, 220,   0), (200, 170,   0)),
#     ((255, 140,  40), (200, 100,  20)),
#     ((160, 255, 160), (100, 200, 100)),
#     ((255, 130, 220), (200,  80, 170)),
# ]


# def enhance(frame):
#     gamma    = 1.5
#     invGamma = 1.0 / gamma
#     table    = np.array(
#         [((i / 255.0) ** invGamma) * 255 for i in range(256)]
#     ).astype("uint8")
#     return cv2.LUT(frame, table)


# def point_in_polygon(point, polygon):
#     polygon = np.array(polygon, dtype=np.float32)
#     return cv2.pointPolygonTest(polygon, point, False) >= 0


# def fmt_ts(epoch):
#     return time.strftime("%H:%M:%S", time.localtime(epoch))


# def fmt_duration(secs):
#     secs = int(secs)
#     m, s = divmod(secs, 60)
#     return f"{m}m {s:02d}s" if m else f"{s}s"


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
#     cv2.ellipse(img, (x1+r, y1+r), (r, r), 180,  0, 90, color, thickness)
#     cv2.ellipse(img, (x2-r, y1+r), (r, r), 270,  0, 90, color, thickness)
#     cv2.ellipse(img, (x1+r, y2-r), (r, r),  90,  0, 90, color, thickness)
#     cv2.ellipse(img, (x2-r, y2-r), (r, r),   0,  0, 90, color, thickness)


# def draw_badge(img, text, x, y, bg_color, text_color=C_WHITE,
#                font_scale=0.48, thickness=1, pad_x=10, pad_y=6):
#     font = cv2.FONT_HERSHEY_DUPLEX
#     (tw, th), _ = cv2.getTextSize(text, font, font_scale, thickness)
#     bx1, by1 = x, y - th - pad_y
#     bx2, by2 = x + tw + 2 * pad_x, y + pad_y
#     r = max(1, (by2 - by1) // 2)
#     draw_filled_rect_alpha(img, bx1, by1, bx2, by2, bg_color, alpha=0.80)
#     draw_rounded_rect(img, bx1, by1, bx2, by2, r, bg_color, thickness=1)
#     cv2.putText(img, text, (bx1 + pad_x, y), font,
#                 font_scale, text_color, thickness, cv2.LINE_AA)
#     return bx2 + 6


# def draw_label_with_bg(img, text, x, y, text_color=C_WHITE,
#                        bg_color=C_DARK, font_scale=0.5, thickness=1, pad=6):
#     font = cv2.FONT_HERSHEY_DUPLEX
#     (tw, th), _ = cv2.getTextSize(text, font, font_scale, thickness)
#     draw_filled_rect_alpha(img,
#                            x - pad, y - th - pad,
#                            x + tw + pad, y + pad,
#                            bg_color, alpha=0.75)
#     cv2.putText(img, text, (x, y), font,
#                 font_scale, text_color, thickness, cv2.LINE_AA)


# class Detector:

#     def __init__(self, camera_name="cam_entry"):

#         self.model = YOLO("/home/keshav/rajan/new_pipeline/models/best.pt")

#         with open(ZONE_FILE) as f:
#             data = json.load(f)[camera_name]

#         self.homography = None
#         if data.get("homography") is not None:
#             self.homography = np.array(data["homography"], dtype=np.float32)

#         self.zones_pixel = {}
#         self.zones_world = {}
#         for name, info in data["zones"].items():
#             self.zones_pixel[name] = info["pixel"]
#             self.zones_world[name] = info["world"]

#         self.zone_color_bgr = {}
#         self.zone_color_map = {}
#         for idx, name in enumerate(self.zones_pixel):
#             bright, dark = _ZONE_COLOR_BANK[idx % len(_ZONE_COLOR_BANK)]
#             self.zone_color_bgr[name] = bright
#             self.zone_color_map[name] = dark

#         self.confirmed_inside = {name: set() for name in self.zones_pixel}
#         self.inside_streak    = {}
#         self.outside_streak   = {}

#         self.zone_entry_count = {name: 0 for name in self.zones_pixel}
#         self.zone_exit_count  = {name: 0 for name in self.zones_pixel}

#         self.entry_epoch      = {}
#         self.cumulative_dwell = {}

#         # ── ID management ─────────────────────────────────────────────────
#         # Counter only ever increments — IDs are never reused.
#         # This prevents the ID-collision bug where a new entrant gets the
#         # same local ID as a person who just exited.
#         self.zone_id_counter = {name: 0 for name in self.zones_pixel}
#         # tracker_tid → local display id  (cleared on exit, never recycled)
#         self.zone_id_map     = {name: {} for name in self.zones_pixel}

#         self.event_log     = []
#         self.metrics_log   = []
#         self.last_log_time = time.time()

#         self.MAP_SCALE = 150
#         self.MAP_W     = 900
#         self.MAP_H     = 750

#     # ── ID helpers ─────────────────────────────────────────────────────────

#     def _get_display_id(self, tracker_tid, zone):
#         if UNIQUE_ID_GLOBAL:
#             return tracker_tid
#         if tracker_tid not in self.zone_id_map[zone]:
#             # Always take the next number — never reuse a freed slot
#             self.zone_id_counter[zone] += 1
#             self.zone_id_map[zone][tracker_tid] = self.zone_id_counter[zone]
#         return self.zone_id_map[zone][tracker_tid]

#     def _release_display_id(self, tracker_tid, zone):
#         if UNIQUE_ID_GLOBAL:
#             return
#         # Remove the mapping so memory stays clean,
#         # but do NOT put the number back into any free pool.
#         self.zone_id_map[zone].pop(tracker_tid, None)

#     # ──────────────────────────────────────────────────────────────────────

#     def pixel_to_world(self, x, y):
#         if self.homography is None:
#             return None
#         pt    = np.array([[[x, y]]], dtype=np.float32)
#         world = cv2.perspectiveTransform(pt, self.homography)
#         return world[0][0]

#     def _apply_hysteresis(self, tracker_tid, zone, raw_inside, now):
#         key          = (tracker_tid, zone)
#         confirmed_in = tracker_tid in self.confirmed_inside[zone]

#         if raw_inside:
#             self.outside_streak[key] = 0
#             if not confirmed_in:
#                 self.inside_streak[key] = self.inside_streak.get(key, 0) + 1
#                 if self.inside_streak[key] >= ENTRY_FRAMES:
#                     self.confirmed_inside[zone].add(tracker_tid)
#                     self.inside_streak[key]      = 0
#                     self.zone_entry_count[zone] += 1
#                     display_id             = self._get_display_id(tracker_tid, zone)
#                     dkey                   = (display_id, zone)
#                     self.entry_epoch[dkey] = now
#                     self.event_log.append({
#                         "event":       "ENTRY",
#                         "id":          display_id,
#                         "tracker_id":  int(tracker_tid),
#                         "zone":        zone,
#                         "entry_time":  fmt_ts(now),
#                         "entry_epoch": round(now, 3),
#                         "id_mode":     "global" if UNIQUE_ID_GLOBAL else "zone_local",
#                     })
#                     print(f"[ENTRY] display_id:{display_id}  "
#                           f"tracker:{tracker_tid}  zone:{zone}  {fmt_ts(now)}")
#             else:
#                 self.inside_streak[key] = 0

#         else:
#             self.inside_streak[key] = 0
#             if confirmed_in:
#                 self.outside_streak[key] = self.outside_streak.get(key, 0) + 1
#                 if self.outside_streak[key] >= EXIT_FRAMES:
#                     self.confirmed_inside[zone].discard(tracker_tid)
#                     self.outside_streak[key]    = 0
#                     self.zone_exit_count[zone] += 1
#                     display_id = self._get_display_id(tracker_tid, zone)
#                     dkey       = (display_id, zone)
#                     entry_ep   = self.entry_epoch.pop(dkey, now)
#                     dwell_secs = round(now - entry_ep, 1)
#                     if display_id not in self.cumulative_dwell:
#                         self.cumulative_dwell[display_id] = {}
#                     prev = self.cumulative_dwell[display_id].get(zone, 0.0)
#                     self.cumulative_dwell[display_id][zone] = round(
#                         prev + dwell_secs, 1)
#                     self.event_log.append({
#                         "event":            "EXIT",
#                         "id":               display_id,
#                         "tracker_id":       int(tracker_tid),
#                         "zone":             zone,
#                         "entry_time":       fmt_ts(entry_ep),
#                         "exit_time":        fmt_ts(now),
#                         "entry_epoch":      round(entry_ep, 3),
#                         "exit_epoch":       round(now, 3),
#                         "dwell_secs":       dwell_secs,
#                         "dwell_formatted":  fmt_duration(dwell_secs),
#                         "total_dwell_secs": self.cumulative_dwell[display_id][zone],
#                         "total_dwell_fmt":  fmt_duration(
#                             self.cumulative_dwell[display_id][zone]),
#                         "id_mode":          "global" if UNIQUE_ID_GLOBAL else "zone_local",
#                     })
#                     print(f"[EXIT]  display_id:{display_id}  "
#                           f"tracker:{tracker_tid}  zone:{zone}  "
#                           f"entry:{fmt_ts(entry_ep)}  exit:{fmt_ts(now)}  "
#                           f"dwell:{fmt_duration(dwell_secs)}")
#                     self._release_display_id(tracker_tid, zone)
#                     self._flush_dwell_summary()
#             else:
#                 self.outside_streak[key] = 0

#     def _cleanup_lost_tracks(self, active_ids, now):
#         all_confirmed = set()
#         for zone in self.zones_pixel:
#             all_confirmed |= self.confirmed_inside[zone]

#         for tracker_tid in (all_confirmed - active_ids):
#             for zone in self.zones_pixel:
#                 if tracker_tid not in self.confirmed_inside[zone]:
#                     continue
#                 self.confirmed_inside[zone].discard(tracker_tid)
#                 self.zone_exit_count[zone] += 1
#                 display_id = self._get_display_id(tracker_tid, zone)
#                 dkey       = (display_id, zone)
#                 entry_ep   = self.entry_epoch.pop(dkey, now)
#                 dwell_secs = round(now - entry_ep, 1)
#                 if display_id not in self.cumulative_dwell:
#                     self.cumulative_dwell[display_id] = {}
#                 prev = self.cumulative_dwell[display_id].get(zone, 0.0)
#                 self.cumulative_dwell[display_id][zone] = round(
#                     prev + dwell_secs, 1)
#                 self.event_log.append({
#                     "event":            "EXIT",
#                     "id":               display_id,
#                     "tracker_id":       int(tracker_tid),
#                     "zone":             zone,
#                     "entry_time":       fmt_ts(entry_ep),
#                     "exit_time":        fmt_ts(now),
#                     "entry_epoch":      round(entry_ep, 3),
#                     "exit_epoch":       round(now, 3),
#                     "dwell_secs":       dwell_secs,
#                     "dwell_formatted":  fmt_duration(dwell_secs),
#                     "total_dwell_secs": self.cumulative_dwell[display_id][zone],
#                     "total_dwell_fmt":  fmt_duration(
#                         self.cumulative_dwell[display_id][zone]),
#                     "reason":           "track_lost",
#                     "id_mode":          "global" if UNIQUE_ID_GLOBAL else "zone_local",
#                 })
#                 print(f"[EXIT-LOST] display_id:{display_id}  "
#                       f"tracker:{tracker_tid}  zone:{zone}  "
#                       f"dwell:{fmt_duration(dwell_secs)}")
#                 self._release_display_id(tracker_tid, zone)

#             for zone in self.zones_pixel:
#                 self.inside_streak.pop((tracker_tid, zone),  None)
#                 self.outside_streak.pop((tracker_tid, zone), None)

#         self._flush_dwell_summary()

#     def _flush_dwell_summary(self):
#         summary = {}
#         for did, zones in self.cumulative_dwell.items():
#             summary[f"id_{did}"] = {
#                 zone: {"total_secs": secs, "total_fmt": fmt_duration(secs)}
#                 for zone, secs in zones.items()
#             }
#         with open(DWELL_FILE, "w") as f:
#             json.dump(summary, f, indent=2)

#     def _draw_hud(self, output):
#         font    = cv2.FONT_HERSHEY_DUPLEX
#         pad     = 14
#         row_h   = 36
#         col_w   = 110
#         label_w = 115
#         n_zones = len(self.zones_pixel)

#         panel_w = label_w + 3 * col_w + 2 * pad
#         panel_h = pad + 28 + n_zones * row_h + pad

#         draw_filled_rect_alpha(output, 10, 10,
#                                10 + panel_w, 10 + panel_h,
#                                C_DARK, alpha=0.72)
#         cv2.rectangle(output, (10, 10),
#                       (10 + panel_w, 10 + panel_h), C_ACCENT, 1)

#         mode_text = "ID: GLOBAL" if UNIQUE_ID_GLOBAL else "ID: PER-ZONE"
#         mode_col  = (100, 220, 100) if UNIQUE_ID_GLOBAL else (60, 160, 255)
#         draw_badge(output, mode_text,
#                    10 + panel_w - 115, 10 + 20,
#                    bg_color=mode_col, text_color=C_BLACK,
#                    font_scale=0.36, thickness=1, pad_x=6, pad_y=4)

#         hx = 10 + pad
#         hy = 10 + pad + 16
#         cv2.putText(output, "ZONE",  (hx,                     hy),
#                     font, 0.42, C_ACCENT, 1, cv2.LINE_AA)
#         cv2.putText(output, "NOW",   (hx + label_w,           hy),
#                     font, 0.42, C_ACCENT, 1, cv2.LINE_AA)
#         cv2.putText(output, "ENTRY", (hx + label_w + col_w,   hy),
#                     font, 0.42, C_ACCENT, 1, cv2.LINE_AA)
#         cv2.putText(output, "EXIT",  (hx + label_w + 2*col_w, hy),
#                     font, 0.42, C_ACCENT, 1, cv2.LINE_AA)

#         div_y = 10 + pad + 22
#         cv2.line(output, (10 + pad, div_y),
#                  (10 + panel_w - pad, div_y), C_ACCENT, 1)

#         for i, zone in enumerate(self.zones_pixel):
#             ry      = div_y + 8 + (i + 1) * row_h - 6
#             inside  = len(self.confirmed_inside[zone])
#             entries = self.zone_entry_count[zone]
#             exits   = self.zone_exit_count[zone]
#             z_color = self.zone_color_bgr[zone]

#             cv2.circle(output, (hx + 6, ry - 5), 5, z_color, -1)
#             cv2.putText(output, zone.upper(),
#                         (hx + 18, ry), font, 0.44, z_color, 1, cv2.LINE_AA)

#             now_col = C_GREEN if inside > 0 else C_WHITE
#             cv2.putText(output, str(inside),
#                         (hx + label_w + 30, ry),
#                         font, 0.55, now_col, 1, cv2.LINE_AA)
#             cv2.putText(output, str(entries),
#                         (hx + label_w + col_w + 20, ry),
#                         font, 0.55, C_GREEN, 1, cv2.LINE_AA)
#             cv2.putText(output, str(exits),
#                         (hx + label_w + 2*col_w + 20, ry),
#                         font, 0.55, C_RED, 1, cv2.LINE_AA)

#     def _draw_zones(self, output):
#         for name, poly in self.zones_pixel.items():
#             if len(poly) < 3:
#                 continue
#             pts     = np.array(poly, dtype=np.int32)
#             color   = self.zone_color_bgr[name]
#             overlay = output.copy()
#             cv2.fillPoly(overlay, [pts], color)
#             cv2.addWeighted(overlay, 0.12, output, 0.88, 0, output)
#             cv2.polylines(output, [pts], True, color, 2, cv2.LINE_AA)
#             cx = int(np.mean([p[0] for p in poly]))
#             cy = int(np.mean([p[1] for p in poly]))
#             draw_label_with_bg(output, name.upper(), cx - 30, cy,
#                                text_color=color, bg_color=C_DARK,
#                                font_scale=0.5, thickness=1)

#     def _draw_track(self, output, track):
#         x1, y1, x2, y2 = track["bbox"]
#         tracker_tid     = track["id"]
#         person_zones    = track["zones"]

#         in_zone   = len(person_zones) > 0
#         box_color = C_GREEN if in_zone else (200, 200, 200)

#         blen, t = 18, 2
#         cv2.line(output, (x1, y1), (x1+blen, y1), box_color, t)
#         cv2.line(output, (x1, y1), (x1, y1+blen), box_color, t)
#         cv2.line(output, (x2, y1), (x2-blen, y1), box_color, t)
#         cv2.line(output, (x2, y1), (x2, y1+blen), box_color, t)
#         cv2.line(output, (x1, y2), (x1+blen, y2), box_color, t)
#         cv2.line(output, (x1, y2), (x1, y2-blen), box_color, t)
#         cv2.line(output, (x2, y2), (x2-blen, y2), box_color, t)
#         cv2.line(output, (x2, y2), (x2, y2-blen), box_color, t)

#         cx, cy_foot = track["foot"]
#         cv2.circle(output, (cx, cy_foot), 4, C_ACCENT, -1)

#         if UNIQUE_ID_GLOBAL:
#             draw_badge(output, f"ID {tracker_tid}", x1, y1 - 6,
#                        bg_color=C_DARK, text_color=C_WHITE,
#                        font_scale=0.45, thickness=1)
#         else:
#             if person_zones:
#                 next_x = x1
#                 for zone_name in person_zones:
#                     local_id = self.zone_id_map[zone_name].get(tracker_tid, "?")
#                     z_col    = self.zone_color_bgr.get(zone_name, C_ACCENT)
#                     next_x   = draw_badge(
#                         output,
#                         f"{zone_name[:3].upper()}-{local_id}",
#                         next_x, y1 - 6,
#                         bg_color=z_col, text_color=C_BLACK,
#                         font_scale=0.45, thickness=1
#                     )
#             else:
#                 draw_badge(output, f"T{tracker_tid}", x1, y1 - 6,
#                            bg_color=(50, 50, 60), text_color=(160, 160, 160),
#                            font_scale=0.40, thickness=1)

#     def draw_floor_map(self, tracks):
#         floor_map = np.full((self.MAP_H, self.MAP_W, 3),
#                             (22, 22, 30), dtype=np.uint8)

#         for x in range(0, self.MAP_W, self.MAP_SCALE):
#             cv2.line(floor_map, (x, 0), (x, self.MAP_H), (45, 45, 55), 1)
#         for y in range(0, self.MAP_H, self.MAP_SCALE):
#             cv2.line(floor_map, (0, y), (self.MAP_W, y), (45, 45, 55), 1)
#         for i in range(self.MAP_W // self.MAP_SCALE + 1):
#             cv2.putText(floor_map, f"{i}m",
#                         (i * self.MAP_SCALE + 3, 13),
#                         cv2.FONT_HERSHEY_DUPLEX, 0.3, (80, 80, 100), 1)
#         for i in range(self.MAP_H // self.MAP_SCALE + 1):
#             cv2.putText(floor_map, f"{i}m",
#                         (3, i * self.MAP_SCALE + 13),
#                         cv2.FONT_HERSHEY_DUPLEX, 0.3, (80, 80, 100), 1)

#         for name, poly_world in self.zones_world.items():
#             if len(poly_world) < 3:
#                 continue
#             color = self.zone_color_map[name]
#             pts   = np.array([
#                 [int(p[0] * self.MAP_SCALE), int(p[1] * self.MAP_SCALE)]
#                 for p in poly_world
#             ], dtype=np.int32)
#             overlay = floor_map.copy()
#             cv2.fillPoly(overlay, [pts], color)
#             cv2.addWeighted(overlay, 0.30, floor_map, 0.70, 0, floor_map)
#             cv2.polylines(floor_map, [pts], True, color, 2, cv2.LINE_AA)

#             cx         = int(np.mean(pts[:, 0]))
#             cy         = int(np.mean(pts[:, 1]))
#             inside_now = len(self.confirmed_inside[name])
#             entries    = self.zone_entry_count[name]
#             exits      = self.zone_exit_count[name]

#             cv2.putText(floor_map, name.upper(),
#                         (cx - 34, cy - 24),
#                         cv2.FONT_HERSHEY_DUPLEX, 0.45, color, 1, cv2.LINE_AA)
#             cv2.putText(floor_map, f"NOW {inside_now}",
#                         (cx - 38, cy),
#                         cv2.FONT_HERSHEY_DUPLEX, 0.4, C_GREEN, 1, cv2.LINE_AA)
#             cv2.putText(floor_map, f"E:{entries}",
#                         (cx - 38, cy + 20),
#                         cv2.FONT_HERSHEY_DUPLEX, 0.38,
#                         (120, 255, 120), 1, cv2.LINE_AA)
#             cv2.putText(floor_map, f"X:{exits}",
#                         (cx + 14, cy + 20),
#                         cv2.FONT_HERSHEY_DUPLEX, 0.38,
#                         (80, 80, 230), 1, cv2.LINE_AA)

#         for track in tracks:
#             world_pt = self.pixel_to_world(track["foot"][0], track["foot"][1])
#             if world_pt is None:
#                 continue
#             mx = int(world_pt[0] * self.MAP_SCALE)
#             my = int(world_pt[1] * self.MAP_SCALE)
#             if not (0 <= mx < self.MAP_W and 0 <= my < self.MAP_H):
#                 continue
#             in_zone = bool(track["zones"])
#             dot_col = C_GREEN if in_zone else (180, 180, 180)
#             cv2.circle(floor_map, (mx, my), 8, dot_col, -1)
#             cv2.circle(floor_map, (mx, my), 9, C_WHITE,  1)

#             tracker_tid = track["id"]
#             if not UNIQUE_ID_GLOBAL and track["zones"]:
#                 zone0    = track["zones"][0]
#                 local_id = self.zone_id_map[zone0].get(tracker_tid, tracker_tid)
#                 label    = f"{zone0[:1].upper()}{local_id}"
#             else:
#                 label = str(tracker_tid)
#             cv2.putText(floor_map, label,
#                         (mx + 11, my + 4),
#                         cv2.FONT_HERSHEY_DUPLEX, 0.38, dot_col, 1, cv2.LINE_AA)

#         cv2.rectangle(floor_map, (0, 0), (self.MAP_W, 24), (30, 30, 40), -1)
#         cv2.line(floor_map, (0, 24), (self.MAP_W, 24), C_ACCENT, 1)
#         cv2.putText(floor_map, "STORE FLOOR MAP  —  bird's-eye view",
#                     (self.MAP_W // 2 - 155, 17),
#                     cv2.FONT_HERSHEY_DUPLEX, 0.46, C_ACCENT, 1, cv2.LINE_AA)

#         lx, ly = self.MAP_W - 140, self.MAP_H - 52
#         draw_filled_rect_alpha(floor_map, lx - 8, ly - 14,
#                                self.MAP_W - 6, self.MAP_H - 6,
#                                C_DARK, alpha=0.7)
#         cv2.circle(floor_map, (lx + 6, ly),      5, (180, 180, 180), -1)
#         cv2.putText(floor_map, "open area",
#                     (lx + 16, ly + 4),
#                     cv2.FONT_HERSHEY_DUPLEX, 0.36, (180, 180, 180), 1)
#         cv2.circle(floor_map, (lx + 6, ly + 22), 5, C_GREEN, -1)
#         cv2.putText(floor_map, "in zone",
#                     (lx + 16, ly + 26),
#                     cv2.FONT_HERSHEY_DUPLEX, 0.36, C_GREEN, 1)

#         return floor_map

#     def process_frame(self, frame):
#         frame = enhance(frame)
#         now   = time.time()

#         results = self.model.track(
#             frame,
#             persist=True,
#             classes=0,
#             conf=0.1,
#             iou=0.7,
#             tracker="botsort.yaml",
#             verbose=False
#         )

#         result     = results[0]
#         output     = frame.copy()
#         active_ids = set()
#         tracks     = []

#         if result.boxes is not None and result.boxes.id is not None:
#             boxes = result.boxes.xyxy.cpu().numpy()
#             ids   = result.boxes.id.cpu().numpy().astype(int)

#             for box, tid in zip(boxes, ids):
#                 x1, y1, x2, y2 = box.astype(int)
#                 cx         = int((x1 + x2) / 2)
#                 cy         = int(y2)
#                 foot_pixel = (cx, cy)
#                 active_ids.add(tid)
#                 world_pt = self.pixel_to_world(cx, cy)

#                 person_zones = []
#                 for zone_name in self.zones_pixel:
#                     if world_pt is not None and \
#                             len(self.zones_world[zone_name]) >= 3:
#                         raw_inside = point_in_polygon(
#                             tuple(world_pt), self.zones_world[zone_name])
#                     else:
#                         raw_inside = point_in_polygon(
#                             foot_pixel, self.zones_pixel[zone_name])

#                     self._apply_hysteresis(tid, zone_name, raw_inside, now)

#                     if tid in self.confirmed_inside[zone_name]:
#                         person_zones.append(zone_name)

#                 tracks.append({
#                     "id":    tid,
#                     "bbox":  (x1, y1, x2, y2),
#                     "foot":  foot_pixel,
#                     "zones": person_zones,
#                 })

#         self._cleanup_lost_tracks(active_ids, now)

#         self._draw_zones(output)
#         for track in tracks:
#             self._draw_track(output, track)
#         self._draw_hud(output)

#         with open(EVENTS_FILE, "w") as f:
#             json.dump(self.event_log, f, indent=2)

#         if time.time() - self.last_log_time >= 60:
#             log = {"time": fmt_ts(now)}
#             for zone in self.zones_pixel:
#                 log[zone] = {
#                     "current": len(self.confirmed_inside[zone]),
#                     "entries": self.zone_entry_count[zone],
#                     "exits":   self.zone_exit_count[zone],
#                 }
#             self.metrics_log.append(log)
#             with open(METRICS_FILE, "w") as f:
#                 json.dump(self.metrics_log, f, indent=2)
#             self.last_log_time = time.time()

#         floor_map = self.draw_floor_map(tracks)
#         return output, tracks, floor_map




import cv2
import numpy as np
import json
import time
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
from ultralytics import YOLO


# ─── CONFIGURATION & CONSTANTS ─────────────────────────────────────────

ZONE_FILE    = "/home/keshav/rajan/new_pipeline/zones_runtime.json"
METRICS_FILE = "zone_metrics.json"
EVENTS_FILE  = "zone_events.json"
DWELL_FILE   = "zone_dwell_summary.json"

YOLO_MODEL   = "/home/keshav/rajan/new_pipeline/models/best.pt"
GENDER_MODEL = "/home/keshav/rajan/new_pipeline/models/mobilenetv3_gender_best.pth"

ENTRY_FRAMES = 4
EXIT_FRAMES  = 6
UNIQUE_ID_GLOBAL = True

# Colors
C_WHITE    = (255, 255, 255)
C_BLACK    = (0,   0,   0)
C_DARK     = (18,  18,  26)
C_ACCENT   = (255, 200,  60)
C_GREEN    = ( 60, 220, 120)
C_RED      = ( 60,  60, 230)

_ZONE_COLOR_BANK = [
    ((255, 190,  60), (200, 140,  40)),
    ((100, 220, 100), ( 60, 180,  60)),
    (( 60, 160, 255), ( 40, 120, 220)),
    ((255, 100, 100), (220,  60,  60)),
    ((180,  80, 220), (140,  50, 180)),
    ((  0, 210, 210), (  0, 160, 160)),
    ((255, 220,   0), (200, 170,   0)),
    ((255, 140,  40), (200, 100,  20)),
    ((160, 255, 160), (100, 200, 100)),
    ((255, 130, 220), (200,  80, 170)),
]


# ─── HELPER FUNCTIONS ──────────────────────────────────────────────────

def enhance(frame):
    """Enhance frame visibility using Gamma correction."""
    gamma = 1.5
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255 for i in range(256)]).astype("uint8")
    return cv2.LUT(frame, table)

def point_in_polygon(point, polygon):
    """Check if a point is inside a polygon using OpenCV."""
    polygon = np.array(polygon, dtype=np.float32)
    return cv2.pointPolygonTest(polygon, point, False) >= 0

def fmt_ts(epoch):
    """Format epoch time to HH:MM:SS."""
    return time.strftime("%H:%M:%S", time.localtime(epoch))

def fmt_duration(secs):
    """Format seconds into a readable string (e.g., '1m 05s')."""
    secs = int(secs)
    m, s = divmod(secs, 60)
    return f"{m}m {s:02d}s" if m else f"{s}s"

def draw_filled_rect_alpha(img, x1, y1, x2, y2, color, alpha=0.55):
    """Draw a semi-transparent rectangle."""
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(img.shape[1], x2), min(img.shape[0], y2)
    if x2 <= x1 or y2 <= y1: return
    sub = img[y1:y2, x1:x2]
    rect = np.full(sub.shape, color, dtype=np.uint8)
    cv2.addWeighted(rect, alpha, sub, 1 - alpha, 0, sub)
    img[y1:y2, x1:x2] = sub

def draw_rounded_rect(img, x1, y1, x2, y2, r, color, thickness=2):
    """Draw a rectangle with rounded corners."""
    cv2.line(img, (x1+r, y1),   (x2-r, y1),   color, thickness)
    cv2.line(img, (x1+r, y2),   (x2-r, y2),   color, thickness)
    cv2.line(img, (x1,   y1+r), (x1,   y2-r), color, thickness)
    cv2.line(img, (x2,   y1+r), (x2,   y2-r), color, thickness)
    cv2.ellipse(img, (x1+r, y1+r), (r, r), 180,  0, 90, color, thickness)
    cv2.ellipse(img, (x2-r, y1+r), (r, r), 270,  0, 90, color, thickness)
    cv2.ellipse(img, (x1+r, y2-r), (r, r),  90,  0, 90, color, thickness)
    cv2.ellipse(img, (x2-r, y2-r), (r, r),   0,  0, 90, color, thickness)

def draw_badge(img, text, x, y, bg_color, text_color=C_WHITE, font_scale=0.48, thickness=1, pad_x=10, pad_y=6):
    """Draw a text badge with a background."""
    font = cv2.FONT_HERSHEY_DUPLEX
    (tw, th), _ = cv2.getTextSize(text, font, font_scale, thickness)
    bx1, by1 = x, y - th - pad_y
    bx2, by2 = x + tw + 2 * pad_x, y + pad_y
    r = max(1, (by2 - by1) // 2)
    draw_filled_rect_alpha(img, bx1, by1, bx2, by2, bg_color, alpha=0.80)
    draw_rounded_rect(img, bx1, by1, bx2, by2, r, bg_color, thickness=1)
    cv2.putText(img, text, (bx1 + pad_x, y), font, font_scale, text_color, thickness, cv2.LINE_AA)
    return bx2 + 6

def draw_label_with_bg(img, text, x, y, text_color=C_WHITE, bg_color=C_DARK, font_scale=0.5, thickness=1, pad=6):
    """Draw text with a simple rectangular background block."""
    font = cv2.FONT_HERSHEY_DUPLEX
    (tw, th), _ = cv2.getTextSize(text, font, font_scale, thickness)
    draw_filled_rect_alpha(img, x - pad, y - th - pad, x + tw + pad, y + pad, bg_color, alpha=0.75)
    cv2.putText(img, text, (x, y), font, font_scale, text_color, thickness, cv2.LINE_AA)


# ─── MODELS ────────────────────────────────────────────────────────────

class GenderClassifier:
    """MobileNetV3 model for classifying cropped bounding boxes by gender."""
    def __init__(self, weights_path, device=None):
        self.device = device if device else torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Load & modify MobileNetV3 structure for 2 classes
        self.model = models.mobilenet_v3_small()
        in_features = self.model.classifier[3].in_features
        self.model.classifier[3] = nn.Linear(in_features, 2)

        # Load weights
        state_dict = torch.load(weights_path, map_location=self.device)
        self.model.load_state_dict(state_dict)
        self.model = self.model.to(self.device)
        self.model.eval()

        self.classes = ["F", "M"] # Shortened for tighter UI integration

        # Transforms for inference
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

    def predict(self, frame, boxes):
        """Returns a list of prediction dicts strictly matching the order/length of input boxes."""
        results = []

        for box in boxes:
            x1, y1, x2, y2 = map(int, box)
            
            # Bound crop to frame size to prevent errors
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)
            
            crop = frame[y1:y2, x1:x2]

            # Failsafe: if the box is out of bounds or invalid
            if crop.size == 0 or crop.shape[0] == 0 or crop.shape[1] == 0:
                results.append({"box": [x1, y1, x2, y2], "label": "?", "confidence": 0.0})
                continue

            img = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            img = self.transform(img).unsqueeze(0).to(self.device)

            with torch.no_grad():
                output = self.model(img)
                prob = torch.softmax(output, dim=1)
                conf, pred = torch.max(prob, 1)

            results.append({
                "box": [x1, y1, x2, y2],
                "label": self.classes[pred.item()],
                "confidence": float(conf.item())
            })

        return results


class Detector:
    """Main object tracker and zone manager."""
    def __init__(self, camera_name="cam_entry"):
        self.model = YOLO(YOLO_MODEL)
        self.gender_model = GenderClassifier(GENDER_MODEL)

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

        self.zone_color_bgr = {}
        self.zone_color_map = {}
        for idx, name in enumerate(self.zones_pixel):
            bright, dark = _ZONE_COLOR_BANK[idx % len(_ZONE_COLOR_BANK)]
            self.zone_color_bgr[name] = bright
            self.zone_color_map[name] = dark

        self.confirmed_inside = {name: set() for name in self.zones_pixel}
        self.inside_streak    = {}
        self.outside_streak   = {}

        self.zone_entry_count = {name: 0 for name in self.zones_pixel}
        self.zone_exit_count  = {name: 0 for name in self.zones_pixel}
        self.entry_epoch      = {}
        self.cumulative_dwell = {}

        self.zone_id_counter = {name: 0 for name in self.zones_pixel}
        self.zone_id_map     = {name: {} for name in self.zones_pixel}

        self.event_log     = []
        self.metrics_log   = []
        self.last_log_time = time.time()

        self.MAP_SCALE = 150
        self.MAP_W     = 900
        self.MAP_H     = 750

    # ── ID helpers ──
    def _get_display_id(self, tracker_tid, zone):
        return tracker_tid

    def _release_display_id(self, tracker_tid, zone):
        return

    # ── Geometry & Logic ──
    def pixel_to_world(self, x, y):
        if self.homography is None: return None
        pt = np.array([[[x, y]]], dtype=np.float32)
        world = cv2.perspectiveTransform(pt, self.homography)
        return world[0][0]

    def _apply_hysteresis(self, tracker_tid, zone, raw_inside, now):
        key = (tracker_tid, zone)
        confirmed_in = tracker_tid in self.confirmed_inside[zone]

        if raw_inside:
            self.outside_streak[key] = 0
            if not confirmed_in:
                self.inside_streak[key] = self.inside_streak.get(key, 0) + 1
                if self.inside_streak[key] >= ENTRY_FRAMES:
                    self.confirmed_inside[zone].add(tracker_tid)
                    self.inside_streak[key] = 0
                    self.zone_entry_count[zone] += 1
                    display_id = self._get_display_id(tracker_tid, zone)
                    self.entry_epoch[(display_id, zone)] = now
                    self.event_log.append({
                        "event": "ENTRY", "id": display_id, "tracker_id": int(tracker_tid),
                        "zone": zone, "entry_time": fmt_ts(now), "entry_epoch": round(now, 3),
                        "id_mode": "global" if UNIQUE_ID_GLOBAL else "zone_local",
                    })
            else:
                self.inside_streak[key] = 0
        else:
            self.inside_streak[key] = 0
            if confirmed_in:
                self.outside_streak[key] = self.outside_streak.get(key, 0) + 1
                if self.outside_streak[key] >= EXIT_FRAMES:
                    self.confirmed_inside[zone].discard(tracker_tid)
                    self.outside_streak[key] = 0
                    self.zone_exit_count[zone] += 1
                    display_id = self._get_display_id(tracker_tid, zone)
                    entry_ep = self.entry_epoch.pop((display_id, zone), now)
                    dwell_secs = round(now - entry_ep, 1)
                    
                    if display_id not in self.cumulative_dwell:
                        self.cumulative_dwell[display_id] = {}
                    prev = self.cumulative_dwell[display_id].get(zone, 0.0)
                    self.cumulative_dwell[display_id][zone] = round(prev + dwell_secs, 1)
                    
                    self.event_log.append({
                        "event": "EXIT", "id": display_id, "tracker_id": int(tracker_tid),
                        "zone": zone, "entry_time": fmt_ts(entry_ep), "exit_time": fmt_ts(now),
                        "entry_epoch": round(entry_ep, 3), "exit_epoch": round(now, 3),
                        "dwell_secs": dwell_secs, "dwell_formatted": fmt_duration(dwell_secs),
                        "total_dwell_secs": self.cumulative_dwell[display_id][zone],
                        "total_dwell_fmt": fmt_duration(self.cumulative_dwell[display_id][zone]),
                        "id_mode": "global" if UNIQUE_ID_GLOBAL else "zone_local",
                    })
                    self._release_display_id(tracker_tid, zone)
                    self._flush_dwell_summary()
            else:
                self.outside_streak[key] = 0

    def _cleanup_lost_tracks(self, active_ids, now):
        all_confirmed = set().union(*self.confirmed_inside.values())
        for tracker_tid in (all_confirmed - active_ids):
            for zone in self.zones_pixel:
                if tracker_tid in self.confirmed_inside[zone]:
                    self.confirmed_inside[zone].discard(tracker_tid)
                    self.zone_exit_count[zone] += 1
                    display_id = self._get_display_id(tracker_tid, zone)
                    entry_ep = self.entry_epoch.pop((display_id, zone), now)
                    dwell_secs = round(now - entry_ep, 1)
                    
                    if display_id not in self.cumulative_dwell:
                        self.cumulative_dwell[display_id] = {}
                    prev = self.cumulative_dwell[display_id].get(zone, 0.0)
                    self.cumulative_dwell[display_id][zone] = round(prev + dwell_secs, 1)
                    
                    self.event_log.append({
                        "event": "EXIT", "id": display_id, "tracker_id": int(tracker_tid),
                        "zone": zone, "entry_time": fmt_ts(entry_ep), "exit_time": fmt_ts(now),
                        "dwell_secs": dwell_secs, "reason": "track_lost"
                    })
                    self._release_display_id(tracker_tid, zone)
            
            for zone in self.zones_pixel:
                self.inside_streak.pop((tracker_tid, zone), None)
                self.outside_streak.pop((tracker_tid, zone), None)
        self._flush_dwell_summary()

    def _flush_dwell_summary(self):
        summary = {f"id_{did}": {z: {"total_secs": s, "total_fmt": fmt_duration(s)} for z, s in zs.items()} 
                   for did, zs in self.cumulative_dwell.items()}
        with open(DWELL_FILE, "w") as f:
            json.dump(summary, f, indent=2)

    # ── Visuals ──
    def _draw_hud(self, output):
        font, pad, row_h, col_w, label_w = cv2.FONT_HERSHEY_DUPLEX, 14, 36, 110, 115
        n_zones = len(self.zones_pixel)
        panel_w = label_w + 3 * col_w + 2 * pad
        panel_h = pad + 28 + n_zones * row_h + pad

        draw_filled_rect_alpha(output, 10, 10, 10 + panel_w, 10 + panel_h, C_DARK, alpha=0.72)
        cv2.rectangle(output, (10, 10), (10 + panel_w, 10 + panel_h), C_ACCENT, 1)

        mode_text = "ID: GLOBAL" if UNIQUE_ID_GLOBAL else "ID: PER-ZONE"
        mode_col  = (100, 220, 100) if UNIQUE_ID_GLOBAL else (60, 160, 255)
        draw_badge(output, mode_text, 10 + panel_w - 115, 30, bg_color=mode_col, text_color=C_BLACK, font_scale=0.36, pad_x=6, pad_y=4)

        hx, hy = 10 + pad, 10 + pad + 16
        for title, offset in zip(["ZONE", "NOW", "ENTRY", "EXIT"], [0, label_w, label_w + col_w, label_w + 2*col_w]):
            cv2.putText(output, title, (hx + offset, hy), font, 0.42, C_ACCENT, 1, cv2.LINE_AA)

        div_y = 10 + pad + 22
        cv2.line(output, (10 + pad, div_y), (10 + panel_w - pad, div_y), C_ACCENT, 1)

        for i, zone in enumerate(self.zones_pixel):
            ry = div_y + 8 + (i + 1) * row_h - 6
            inside, entries, exits = len(self.confirmed_inside[zone]), self.zone_entry_count[zone], self.zone_exit_count[zone]
            z_color = self.zone_color_bgr[zone]

            cv2.circle(output, (hx + 6, ry - 5), 5, z_color, -1)
            cv2.putText(output, zone.upper(), (hx + 18, ry), font, 0.44, z_color, 1, cv2.LINE_AA)

            now_col = C_GREEN if inside > 0 else C_WHITE
            cv2.putText(output, str(inside), (hx + label_w + 30, ry), font, 0.55, now_col, 1, cv2.LINE_AA)
            cv2.putText(output, str(entries), (hx + label_w + col_w + 20, ry), font, 0.55, C_GREEN, 1, cv2.LINE_AA)
            cv2.putText(output, str(exits), (hx + label_w + 2*col_w + 20, ry), font, 0.55, C_RED, 1, cv2.LINE_AA)

    def _draw_zones(self, output):
        for name, poly in self.zones_pixel.items():
            if len(poly) < 3: continue
            pts = np.array(poly, dtype=np.int32)
            color = self.zone_color_bgr[name]
            overlay = output.copy()
            cv2.fillPoly(overlay, [pts], color)
            cv2.addWeighted(overlay, 0.12, output, 0.88, 0, output)
            cv2.polylines(output, [pts], True, color, 2, cv2.LINE_AA)
            cx, cy = int(np.mean([p[0] for p in poly])), int(np.mean([p[1] for p in poly]))
            draw_label_with_bg(output, name.upper(), cx - 30, cy, text_color=color, bg_color=C_DARK)

    def _draw_track(self, output, track):

        x1, y1, x2, y2 = track["bbox"]
        tracker_tid = track["id"]
        gender_label = track.get("gender", "?")

        person_zones = track["zones"]

        # thin bbox
        box_color = C_GREEN if person_zones else (180,180,180)

        cv2.rectangle(
            output,
            (x1, y1),
            (x2, y2),
            box_color,
            1   # thin line
        )

        # foot point
        cx, cy = track["foot"]
        cv2.circle(output,(cx,cy),4,C_ACCENT,-1)

        # label text
        label = f"ID {tracker_tid} | {gender_label}"

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        thickness = 1

        (tw,th),_ = cv2.getTextSize(label,font,font_scale,thickness)

        # black background at top of bbox
        cv2.rectangle(
            output,
            (x1, y1-th-8),
            (x1+tw+6, y1),
            (0,0,0),
            -1
        )

        # green text
        cv2.putText(
            output,
            label,
            (x1+3, y1-4),
            font,
            font_scale,
            (0,255,0),
            thickness,
            cv2.LINE_AA
        )

    def draw_floor_map(self, tracks):
        floor_map = np.full((self.MAP_H, self.MAP_W, 3), (22, 22, 30), dtype=np.uint8)

        # Draw Grid
        for x in range(0, self.MAP_W, self.MAP_SCALE): cv2.line(floor_map, (x, 0), (x, self.MAP_H), (45, 45, 55), 1)
        for y in range(0, self.MAP_H, self.MAP_SCALE): cv2.line(floor_map, (0, y), (self.MAP_W, y), (45, 45, 55), 1)
        
        for name, poly_world in self.zones_world.items():
            if len(poly_world) < 3: continue
            color = self.zone_color_map[name]
            pts = np.array([[int(p[0] * self.MAP_SCALE), int(p[1] * self.MAP_SCALE)] for p in poly_world], dtype=np.int32)
            overlay = floor_map.copy()
            cv2.fillPoly(overlay, [pts], color)
            cv2.addWeighted(overlay, 0.30, floor_map, 0.70, 0, floor_map)
            cv2.polylines(floor_map, [pts], True, color, 2, cv2.LINE_AA)

            cx, cy = int(np.mean(pts[:, 0])), int(np.mean(pts[:, 1]))
            cv2.putText(floor_map, name.upper(), (cx - 34, cy - 24), cv2.FONT_HERSHEY_DUPLEX, 0.45, color, 1, cv2.LINE_AA)
            cv2.putText(floor_map, f"NOW {len(self.confirmed_inside[name])}", (cx - 38, cy), cv2.FONT_HERSHEY_DUPLEX, 0.4, C_GREEN, 1)

        # Draw Tracking dots
        for track in tracks:
            world_pt = self.pixel_to_world(track["foot"][0], track["foot"][1])
            if world_pt is None: continue
            mx, my = int(world_pt[0] * self.MAP_SCALE), int(world_pt[1] * self.MAP_SCALE)
            if not (0 <= mx < self.MAP_W and 0 <= my < self.MAP_H): continue
            
            dot_col = C_GREEN if track["zones"] else (180, 180, 180)
            cv2.circle(floor_map, (mx, my), 8, dot_col, -1)
            cv2.circle(floor_map, (mx, my), 9, C_WHITE,  1)

            # Minimalist Map Label
            label = str(track["id"])
            cv2.putText(floor_map, label, (mx + 11, my + 4), cv2.FONT_HERSHEY_DUPLEX, 0.38, dot_col, 1)

        cv2.rectangle(floor_map, (0, 0), (self.MAP_W, 24), (30, 30, 40), -1)
        cv2.putText(floor_map, "STORE FLOOR MAP", (self.MAP_W // 2 - 80, 17), cv2.FONT_HERSHEY_DUPLEX, 0.46, C_ACCENT, 1)

        return floor_map

    # ── Main Processing Loop ──
    def process_frame(self, frame):
        frame = enhance(frame)
        now = time.time()

        results = self.model.track(
            frame, persist=True, classes=0, conf=0.1, iou=0.7, tracker="botsort.yaml", verbose=False
        )

        result = results[0]
        output = frame.copy()
        active_ids = set()
        tracks = []

        if result.boxes is not None and result.boxes.id is not None:
            boxes = result.boxes.xyxy.cpu().numpy()
            ids   = result.boxes.id.cpu().numpy().astype(int)

            # ── GENDER CLASSIFICATION INJECTION ──
            # Run prediction on the whole batch of boxes for this frame
            gender_preds = self.gender_model.predict(frame, boxes)

            # Zip the boxes, tracking IDs, and gender predictions together
            for box, tid, g_pred in zip(boxes, ids, gender_preds):
                x1, y1, x2, y2 = box.astype(int)
                cx, cy = int((x1 + x2) / 2), int(y2)
                foot_pixel = (cx, cy)
                active_ids.add(tid)
                world_pt = self.pixel_to_world(cx, cy)

                person_zones = []
                for zone_name in self.zones_pixel:
                    if world_pt is not None and len(self.zones_world[zone_name]) >= 3:
                        raw_inside = point_in_polygon(tuple(world_pt), self.zones_world[zone_name])
                    else:
                        raw_inside = point_in_polygon(foot_pixel, self.zones_pixel[zone_name])

                    self._apply_hysteresis(tid, zone_name, raw_inside, now)
                    if tid in self.confirmed_inside[zone_name]:
                        person_zones.append(zone_name)

                tracks.append({
                    "id":    tid,
                    "bbox":  (x1, y1, x2, y2),
                    "foot":  foot_pixel,
                    "zones": person_zones,
                    "gender": g_pred["label"]  # Add gender to the track dict
                })

        self._cleanup_lost_tracks(active_ids, now)

        self._draw_zones(output)
        for track in tracks:
            self._draw_track(output, track)
        self._draw_hud(output)

        with open(EVENTS_FILE, "w") as f:
            json.dump(self.event_log, f, indent=2,default=int)

        if time.time() - self.last_log_time >= 60:
            log = {"time": fmt_ts(now)}
            for zone in self.zones_pixel:
                log[zone] = {"current": len(self.confirmed_inside[zone]), "entries": self.zone_entry_count[zone], "exits": self.zone_exit_count[zone]}
            self.metrics_log.append(log)
            with open(METRICS_FILE, "w") as f:
                json.dump(self.metrics_log, f, indent=2,default=int)
            self.last_log_time = time.time()

        floor_map = self.draw_floor_map(tracks)
        return output, tracks, floor_map