import cv2
import json
import os
import numpy as np

CAMERA_NAME       = "cam_entry"
SOURCE            = "/home/keshav/rajan/new_pipeline/input/shopping.mp4"
TARGET_RESOLUTION = (1280, 720)
OUTPUT_FILE       = "zones_runtime.json"

COLOR_BANK = [
    (255,  60,  60),
    ( 60, 200,  60),
    ( 60,  60, 230),
    (255, 165,   0),
    (180,   0, 180),
    (  0, 200, 200),
    (255, 255,   0),
    (  0, 128, 255),
    (128, 255, 128),
    (255, 128, 255),
]

CALIB_COLOR    = (0, 255, 255)
CURSOR_COLOR   = (200, 200, 200)
FINISHED_ALPHA = 0.18

zone_names  = []
zone_pts    = {}
zone_closed = {}
zone_color  = {}
current_idx = 0

pixel_ref  = []
world_ref  = []
homography = None
calib_done = False
cursor_pos = (0, 0)


def _color_for(idx):
    return COLOR_BANK[idx % len(COLOR_BANK)]


def add_zone(name):
    name = name.strip().lower().replace(" ", "_")
    if not name:
        return False
    if name in zone_names:
        print(f"[Zone] '{name}' already exists.")
        return False
    idx = len(zone_names)
    zone_names.append(name)
    zone_pts[name]    = []
    zone_closed[name] = False
    zone_color[name]  = _color_for(idx)
    print(f"[Zone] Added '{name}'")
    return True


def delete_current_zone():
    global current_idx
    if not zone_names:
        return
    name = zone_names[current_idx]
    zone_names.pop(current_idx)
    del zone_pts[name]
    del zone_closed[name]
    del zone_color[name]
    current_idx = min(current_idx, max(0, len(zone_names) - 1))
    print(f"[Zone] Deleted '{name}'.")


def current_zone():
    if not zone_names:
        return None
    return zone_names[current_idx]


def compute_homography():
    global homography
    src = np.array(pixel_ref, dtype=np.float32)
    dst = np.array(world_ref, dtype=np.float32)
    homography, _ = cv2.findHomography(src, dst)
    print("[Calib] Homography computed.")


def pixel_to_world(x, y):
    if homography is None:
        return None
    pt    = np.array([[[float(x), float(y)]]], dtype=np.float32)
    world = cv2.perspectiveTransform(pt, homography)
    return [round(float(world[0][0][0]), 4), round(float(world[0][0][1]), 4)]


def _collect_world_coords():
    for i in range(4):
        while True:
            try:
                X = float(input(f"  Point {i+1} → X (metres): "))
                Y = float(input(f"  Point {i+1} → Y (metres): "))
                world_ref.append([X, Y])
                break
            except ValueError:
                print("  Invalid — enter a number.")


def mouse_cb(event, x, y, flags, param):
    global calib_done, cursor_pos
    cursor_pos = (x, y)

    if not calib_done:
        if event == cv2.EVENT_LBUTTONDOWN and len(pixel_ref) < 4:
            pixel_ref.append([x, y])
            print(f"[Calib] Point {len(pixel_ref)}: pixel=({x},{y})")
            if len(pixel_ref) == 4:
                print("[Calib] 4 points collected.")
                _collect_world_coords()
                compute_homography()
                calib_done = True
                print("[Calib] Done. Draw your zones.")
        return

    zn = current_zone()
    if zn is None:
        return

    if event == cv2.EVENT_LBUTTONDOWN:
        if not zone_closed[zn]:
            zone_pts[zn].append([x, y])
            world = pixel_to_world(x, y)
            w_str = f"  world={world}" if world else ""
            print(f"[{zn}] point {len(zone_pts[zn])}: pixel=({x},{y}){w_str}")

    elif event == cv2.EVENT_RBUTTONDOWN:
        _undo_last()


def _undo_last():
    zn = current_zone()
    if zn is None:
        return
    pts = zone_pts[zn]
    if pts:
        removed = pts.pop()
        zone_closed[zn] = False
        print(f"[{zn}] Undo — removed {removed}, {len(pts)} points remain")
    else:
        print(f"[{zn}] Nothing to undo.")


def _close_current():
    zn = current_zone()
    if zn is None:
        return
    if len(zone_pts[zn]) >= 3:
        zone_closed[zn] = True
        print(f"[{zn}] Polygon closed ({len(zone_pts[zn])} points).")
    else:
        print(f"[{zn}] Need at least 3 points (have {len(zone_pts[zn])}).")


def _draw_dashed_line(img, pt1, pt2, color, dash=10, gap=6):
    dx   = pt2[0] - pt1[0]
    dy   = pt2[1] - pt1[1]
    dist = max(1, int((dx**2 + dy**2) ** 0.5))
    for i in range(dist // (dash + gap) + 1):
        s  = (dash + gap) * i / dist
        e  = min(1.0, s + dash / dist)
        x1 = int(pt1[0] + dx * s);  y1 = int(pt1[1] + dy * s)
        x2 = int(pt1[0] + dx * e);  y2 = int(pt1[1] + dy * e)
        cv2.line(img, (x1, y1), (x2, y2), color, 1)


def draw_state(base_frame):
    img  = base_frame.copy()
    h, w = img.shape[:2]

    for i, p in enumerate(pixel_ref):
        cv2.circle(img, tuple(p), 7, CALIB_COLOR, -1)
        cv2.putText(img, f"C{i+1}", (p[0]+8, p[1]-6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, CALIB_COLOR, 1)

    zn_active = current_zone()
    for zn in zone_names:
        pts       = zone_pts[zn]
        color     = zone_color[zn]
        is_active = (zn == zn_active)
        if not pts:
            continue
        arr = np.array(pts, dtype=np.int32)

        if zone_closed[zn] and len(pts) >= 3:
            overlay = img.copy()
            cv2.fillPoly(overlay, [arr], color)
            cv2.addWeighted(overlay, FINISHED_ALPHA, img, 1 - FINISHED_ALPHA, 0, img)
            cv2.polylines(img, [arr], True, color, 3 if is_active else 2, cv2.LINE_AA)
            cx    = int(arr[:, 0].mean())
            cy    = int(arr[:, 1].mean())
            label = zn.upper()
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_DUPLEX, 0.6, 1)
            cv2.rectangle(img,
                          (cx - tw//2 - 6, cy - th - 6),
                          (cx + tw//2 + 6, cy + 6),
                          (20, 20, 20), -1)
            cv2.putText(img, label, (cx - tw//2, cy),
                        cv2.FONT_HERSHEY_DUPLEX, 0.6, color, 1, cv2.LINE_AA)
        else:
            for i in range(len(pts) - 1):
                cv2.line(img, tuple(pts[i]), tuple(pts[i+1]), color, 2)
            if is_active and pts and not zone_closed[zn]:
                _draw_dashed_line(img, tuple(pts[-1]), cursor_pos, CURSOR_COLOR)

        for i, p in enumerate(pts):
            cv2.circle(img, tuple(p), 5, color, -1)
            cv2.putText(img, str(i+1), (p[0]+6, p[1]-4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.38, color, 1)

    cv2.rectangle(img, (0, 0), (w, 44), (25, 25, 30), -1)
    if not calib_done:
        cv2.putText(img,
                    "STEP 1 — CALIBRATION  (click 4 floor points, or SPACE to skip)",
                    (10, 28), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 220, 220), 1, cv2.LINE_AA)
    else:
        if zn_active:
            color = zone_color[zn_active]
            cv2.putText(img, "ACTIVE ZONE:", (10, 28),
                        cv2.FONT_HERSHEY_DUPLEX, 0.5, (180, 180, 180), 1, cv2.LINE_AA)
            cv2.putText(img, zn_active.upper(), (140, 28),
                        cv2.FONT_HERSHEY_DUPLEX, 0.6, color, 1, cv2.LINE_AA)
            n  = len(zone_pts[zn_active])
            st = "CLOSED" if zone_closed[zn_active] else f"{n} pts"
            cv2.putText(img, f"[{st}]", (300, 28),
                        cv2.FONT_HERSHEY_DUPLEX, 0.48, (200, 200, 200), 1, cv2.LINE_AA)
        else:
            cv2.putText(img, "No zones — press A to add one", (10, 28),
                        cv2.FONT_HERSHEY_DUPLEX, 0.5, (100, 100, 100), 1, cv2.LINE_AA)

    panel_x = w - 220
    cv2.rectangle(img, (panel_x - 6, 48),
                  (w, 48 + len(zone_names) * 26 + 10), (25, 25, 30), -1)
    for i, zn in enumerate(zone_names):
        color  = zone_color[zn]
        n_pts  = len(zone_pts[zn])
        status = "closed" if zone_closed[zn] else f"{n_pts} pts"
        prefix = ">" if zn == zn_active else " "
        y_pos  = 68 + i * 26
        cv2.putText(img, f"{prefix} {zn} [{status}]", (panel_x, y_pos),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.44,
                    color if zn == zn_active else (130, 130, 130),
                    2 if zn == zn_active else 1, cv2.LINE_AA)

    legend = [
        "TAB/N: next zone    B: prev zone",
        "A: add zone         D: delete zone",
        "Click: add vertex   Z/RClick: undo",
        "Enter/F: close poly C: clear zone",
        "SPACE: skip calib   R: reset all",
        "Q: save & exit      ESC: quit",
    ]
    ly = h - len(legend) * 17 - 8
    cv2.rectangle(img, (0, ly - 4), (310, h), (25, 25, 30), -1)
    for line in legend:
        cv2.putText(img, line, (6, ly),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (160, 160, 160), 1)
        ly += 17

    return img


def collect_initial_zones():
    print("\n" + "="*55)
    print("  ZONE SETUP — enter zone names one by one.")
    print("  Leave blank or type DONE to finish.")
    print("="*55)
    while True:
        name = input("  Zone name (or DONE to finish): ").strip()
        if name.upper() in ("DONE", ""):
            if zone_names:
                break
            print("  Enter at least one zone name.")
            continue
        add_zone(name)
    print(f"\n  Zones: {zone_names}")
    print("="*55 + "\n")


collect_initial_zones()

cap = cv2.VideoCapture(SOURCE)
ret, frame = cap.read()
cap.release()
if not ret:
    raise RuntimeError(f"Cannot read source: {SOURCE}")

frame = cv2.resize(frame, TARGET_RESOLUTION)

cv2.namedWindow("Draw Zones", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Draw Zones", TARGET_RESOLUTION[0], TARGET_RESOLUTION[1])
cv2.setMouseCallback("Draw Zones", mouse_cb)

saved = False

while True:
    cv2.imshow("Draw Zones", draw_state(frame))
    key = cv2.waitKey(20) & 0xFF

    if key in (9, ord('n')):
        if zone_names:
            current_idx = (current_idx + 1) % len(zone_names)
            print(f"[Switch] → {current_zone()}")

    elif key == ord('b'):
        if zone_names:
            current_idx = (current_idx - 1) % len(zone_names)
            print(f"[Switch] → {current_zone()}")

    elif key == ord('a'):
        name = input("[Add Zone] Zone name: ").strip()
        if add_zone(name):
            current_idx = len(zone_names) - 1

    elif key == ord('d'):
        zn = current_zone()
        if zn:
            confirm = input(f"[Delete] Delete '{zn}'? (y/N): ").strip().lower()
            if confirm == 'y':
                delete_current_zone()

    elif key == ord('z'):
        _undo_last()

    elif key in (13, ord('f')):
        _close_current()

    elif key == ord('c'):
        zn = current_zone()
        if zn:
            zone_pts[zn]    = []
            zone_closed[zn] = False
            print(f"[{zn}] Cleared.")

    elif key == ord('r'):
        for zn in zone_names:
            zone_pts[zn]    = []
            zone_closed[zn] = False
        pixel_ref.clear()
        world_ref.clear()
        homography = None
        calib_done = False
        print("[Reset] All zones and calibration cleared.")

    elif key == ord(' '):
        if not calib_done:
            calib_done = True
            print("[Calib] Skipped.")

    elif key == ord('q'):
        for zn in zone_names:
            if not zone_closed[zn] and len(zone_pts[zn]) >= 3:
                zone_closed[zn] = True
                print(f"[{zn}] Auto-closed on save.")

        world_zones = {}
        for zn in zone_names:
            pts       = zone_pts[zn]
            world_pts = [pixel_to_world(x, y) for x, y in pts]
            world_zones[zn] = {
                "pixel": pts,
                "world": [wp for wp in world_pts if wp is not None],
            }

        all_data = {}
        if os.path.exists(OUTPUT_FILE):
            with open(OUTPUT_FILE, "r") as f:
                all_data = json.load(f)

        all_data[CAMERA_NAME] = {
            "homography": homography.tolist() if homography is not None else None,
            "zones": world_zones,
        }

        with open(OUTPUT_FILE, "w") as f:
            json.dump(all_data, f, indent=2)

        saved = True
        print(f"[Save] Written to {OUTPUT_FILE}")
        break

    elif key == 27:
        print("[Exit] No changes saved.")
        break

cv2.destroyAllWindows()

if saved:
    print("\n── Summary ──────────────────────────────────")
    for zn in zone_names:
        n  = len(zone_pts[zn])
        st = "closed" if zone_closed[zn] else "open"
        print(f"  {zn:20s}: {n} points  ({st})")
    print("─────────────────────────────────────────────")