"""
zone_drawer.py — Interactive Zone + Homography Tool
====================================================

Step 1 — Calibration (optional but recommended)
  Click exactly 4 known floor points on the image.
  Enter their real-world (X, Y) coordinates in metres when prompted.
  This computes a homography for pixel → world mapping.
  Press SPACE to skip calibration entirely.

Step 2 — Draw zones
  Switch zone with 1 / 2 / 3, then left-click to add polygon vertices.
  Right-click or Z to undo the last point.
  Press ENTER or F to close (finish) the current polygon.
  Press C to clear the current zone entirely.
  Press Q to save and exit.

Keys at a glance
----------------
  1 / 2 / 3     — switch active zone (billing / cashier / security)
  Left-click    — add vertex to current zone
  Right-click   — undo last vertex
  Z             — undo last vertex (keyboard)
  ENTER / F     — close current polygon
  C             — clear current zone
  SPACE         — skip calibration / confirm calibration done
  R             — reset ALL zones and recalibrate
  Q             — save zones_runtime.json and exit
  ESC           — exit without saving
"""

import cv2
import json
import os
import numpy as np

# ---------------------------------------------------------------------------
# Config — edit these before running
# ---------------------------------------------------------------------------
CAMERA_NAME       = "cam_entry"
SOURCE            = "/home/keshav/rajan/new_pipeline/store.mp4"
TARGET_RESOLUTION = (1280, 720)   # resolution zones are drawn at
OUTPUT_FILE       = "zones_runtime.json"

ZONE_NAMES = ["billing", "cashier", "security"]

# ---------------------------------------------------------------------------
# Colours (BGR)
# ---------------------------------------------------------------------------
ZONE_COLORS = {
    "billing":  (255,   0,   0),
    "cashier":  (  0, 165, 255),
    "security": (  0,   0, 255),
}
CALIB_COLOR    = (0, 255, 255)    # yellow
CURSOR_COLOR   = (200, 200, 200)  # grey preview line
FINISHED_ALPHA = 0.20             # fill opacity for closed polygons


# ===========================================================================
# State
# ===========================================================================
zones        = {z: [] for z in ZONE_NAMES}   # pixel points per zone
closed       = {z: False for z in ZONE_NAMES}  # whether polygon is closed
current_zone = ZONE_NAMES[0]

# Calibration
pixel_ref = []
world_ref = []
homography = None
calib_done = False   # True once 4 points collected (or user pressed SPACE)

# Mouse cursor position (for live preview line)
cursor_pos = (0, 0)


# ===========================================================================
# Homography helpers
# ===========================================================================

def compute_homography():
    global homography
    src = np.array(pixel_ref, dtype=np.float32)
    dst = np.array(world_ref, dtype=np.float32)
    homography, _ = cv2.findHomography(src, dst)
    print("[Calib] Homography computed:")
    print(homography)


def pixel_to_world(x, y):
    if homography is None:
        return None
    pt    = np.array([[[float(x), float(y)]]], dtype=np.float32)
    world = cv2.perspectiveTransform(pt, homography)
    return [round(float(world[0][0][0]), 4), round(float(world[0][0][1]), 4)]


# ===========================================================================
# Mouse callback
# ===========================================================================

def mouse_cb(event, x, y, flags, param):
    global calib_done, cursor_pos

    cursor_pos = (x, y)

    # ── Calibration phase ──────────────────────────────────────────────────
    if not calib_done:
        if event == cv2.EVENT_LBUTTONDOWN:
            if len(pixel_ref) < 4:
                pixel_ref.append([x, y])
                print(f"[Calib] Point {len(pixel_ref)}: pixel=({x},{y})")
                if len(pixel_ref) == 4:
                    print("[Calib] 4 points collected.")
                    print("        Enter real-world coords (metres) in terminal.")
                    _collect_world_coords()
                    compute_homography()
                    calib_done = True
                    print("[Calib] Done. You can now draw zones.")
        return

    # ── Zone drawing phase ─────────────────────────────────────────────────
    if event == cv2.EVENT_LBUTTONDOWN:
        if not closed[current_zone]:
            zones[current_zone].append([x, y])
            world = pixel_to_world(x, y)
            w_str = f"  world={world}" if world else ""
            print(f"[{current_zone}] point {len(zones[current_zone])}: "
                  f"pixel=({x},{y}){w_str}")

    elif event == cv2.EVENT_RBUTTONDOWN:
        _undo_last()


def _collect_world_coords():
    """Block in terminal to read 4 world-coordinate pairs."""
    for i in range(4):
        while True:
            try:
                X = float(input(f"  Point {i+1} → X (metres): "))
                Y = float(input(f"  Point {i+1} → Y (metres): "))
                world_ref.append([X, Y])
                break
            except ValueError:
                print("  Invalid — enter a number.")


def _undo_last():
    pts = zones[current_zone]
    if pts:
        removed = pts.pop()
        closed[current_zone] = False   # re-open if it was closed
        print(f"[{current_zone}] Undo — removed {removed}, "
              f"{len(pts)} points remain")
    else:
        print(f"[{current_zone}] Nothing to undo.")


def _close_current():
    if len(zones[current_zone]) >= 3:
        closed[current_zone] = True
        print(f"[{current_zone}] Polygon closed ({len(zones[current_zone])} points).")
    else:
        print(f"[{current_zone}] Need at least 3 points to close "
              f"(have {len(zones[current_zone])}).")


# ===========================================================================
# Drawing helpers
# ===========================================================================

def draw_state(base_frame):
    img = base_frame.copy()
    h, w = img.shape[:2]

    # ── Calibration points ─────────────────────────────────────────────────
    for i, p in enumerate(pixel_ref):
        cv2.circle(img, tuple(p), 7, CALIB_COLOR, -1)
        cv2.putText(img, f"C{i+1}", (p[0]+8, p[1]-6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, CALIB_COLOR, 1)

    # ── Zones ─────────────────────────────────────────────────────────────
    for zone_name, pts in zones.items():
        if not pts:
            continue
        color = ZONE_COLORS.get(zone_name, (0, 255, 0))
        arr   = np.array(pts, dtype=np.int32)

        # filled polygon for closed zones
        if closed[zone_name] and len(pts) >= 3:
            overlay = img.copy()
            cv2.fillPoly(overlay, [arr], color)
            cv2.addWeighted(overlay, FINISHED_ALPHA, img, 1 - FINISHED_ALPHA,
                            0, img)
            cv2.polylines(img, [arr], True, color, 2)
            # label at centroid
            cx = int(arr[:, 0].mean())
            cy = int(arr[:, 1].mean())
            cv2.putText(img, zone_name, (cx - 30, cy),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        else:
            # draw edges between placed points
            for i in range(len(pts) - 1):
                cv2.line(img, tuple(pts[i]), tuple(pts[i+1]), color, 2)
            # dashed preview line from last point to cursor
            if zone_name == current_zone and pts and not closed[zone_name]:
                _draw_dashed_line(img, tuple(pts[-1]), cursor_pos,
                                  CURSOR_COLOR)

        # draw vertex dots
        for i, p in enumerate(pts):
            cv2.circle(img, tuple(p), 5, color, -1)
            cv2.putText(img, str(i + 1), (p[0] + 6, p[1] - 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

    # ── HUD ────────────────────────────────────────────────────────────────
    phase = "CALIBRATION (click 4 floor points)" if not calib_done else \
            f"ZONE: {current_zone.upper()}"
    cv2.rectangle(img, (0, 0), (w, 40), (30, 30, 30), -1)
    cv2.putText(img, phase, (10, 27),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

    # point count badge
    n = len(zones[current_zone])
    st = "closed" if closed[current_zone] else f"{n} pts"
    cv2.putText(img, st, (w - 120, 27),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

    # legend bottom-left
    legend = [
        "1/2/3: switch zone",
        "LClick: add point",
        "RClick / Z: undo",
        "Enter/F: close polygon",
        "C: clear zone   R: reset all",
        "SPACE: skip calib   Q: save   ESC: quit",
    ]
    y_leg = h - len(legend) * 18 - 5
    cv2.rectangle(img, (0, y_leg - 5), (310, h), (30, 30, 30), -1)
    for line in legend:
        cv2.putText(img, line, (6, y_leg),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (200, 200, 200), 1)
        y_leg += 18

    # zone status row
    y_s = 60
    for zn in ZONE_NAMES:
        color  = ZONE_COLORS.get(zn, (0, 255, 0))
        n_pts  = len(zones[zn])
        status = "✓" if closed[zn] else f"{n_pts}p"
        prefix = "► " if zn == current_zone else "  "
        cv2.putText(img, f"{prefix}{zn}: {status}", (10, y_s),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)
        y_s += 24

    return img


def _draw_dashed_line(img, pt1, pt2, color, dash=10, gap=6):
    """Draw a dashed line between pt1 and pt2."""
    dx = pt2[0] - pt1[0]
    dy = pt2[1] - pt1[1]
    dist = max(1, int((dx**2 + dy**2) ** 0.5))
    steps = dist // (dash + gap)
    for i in range(steps + 1):
        s = (dash + gap) * i / dist
        e = min(1.0, s + dash / dist)
        x1 = int(pt1[0] + dx * s);  y1 = int(pt1[1] + dy * s)
        x2 = int(pt1[0] + dx * e);  y2 = int(pt1[1] + dy * e)
        cv2.line(img, (x1, y1), (x2, y2), color, 1)


# ===========================================================================
# Main
# ===========================================================================

cap = cv2.VideoCapture(SOURCE)
ret, frame = cap.read()
cap.release()

if not ret:
    raise RuntimeError(f"Cannot read source: {SOURCE}")

frame = cv2.resize(frame, TARGET_RESOLUTION)

cv2.namedWindow("Draw Zones", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Draw Zones", TARGET_RESOLUTION[0], TARGET_RESOLUTION[1])
cv2.setMouseCallback("Draw Zones", mouse_cb)

print(__doc__)

saved = False

while True:
    cv2.imshow("Draw Zones", draw_state(frame))
    key = cv2.waitKey(20) & 0xFF

    # ── Zone switch ───────────────────────────────────────────────────────
    if key == ord('1'):
        current_zone = ZONE_NAMES[0]
        print(f"[Switch] Active zone → {current_zone}")
    elif key == ord('2'):
        current_zone = ZONE_NAMES[1]
        print(f"[Switch] Active zone → {current_zone}")
    elif key == ord('3'):
        current_zone = ZONE_NAMES[2]
        print(f"[Switch] Active zone → {current_zone}")

    # ── Undo ──────────────────────────────────────────────────────────────
    elif key == ord('z'):
        _undo_last()

    # ── Close polygon ─────────────────────────────────────────────────────
    elif key in (13, ord('f')):    # ENTER or F
        _close_current()

    # ── Clear current zone ────────────────────────────────────────────────
    elif key == ord('c'):
        zones[current_zone] = []
        closed[current_zone] = False
        print(f"[{current_zone}] Cleared.")

    # ── Reset everything ──────────────────────────────────────────────────
    elif key == ord('r'):
        zones   = {z: [] for z in ZONE_NAMES}
        closed  = {z: False for z in ZONE_NAMES}
        pixel_ref.clear()
        world_ref.clear()
        homography  = None
        calib_done  = False
        print("[Reset] All zones and calibration cleared.")

    # ── Skip calibration ──────────────────────────────────────────────────
    elif key == ord(' '):
        if not calib_done:
            calib_done = True
            print("[Calib] Skipped — no world-coordinate mapping.")

    # ── Save & exit ───────────────────────────────────────────────────────
    elif key == ord('q'):
        # auto-close any open polygon with >= 3 points
        for zn in ZONE_NAMES:
            if not closed[zn] and len(zones[zn]) >= 3:
                closed[zn] = True
                print(f"[{zn}] Auto-closed on save.")

        # build per-zone world coords
        world_zones = {}
        for zn, pts in zones.items():
            world_pts = [pixel_to_world(x, y) for x, y in pts]
            world_zones[zn] = {
                "pixel": pts,
                "world": [wp for wp in world_pts if wp is not None],
            }

        # merge with existing file (other cameras untouched)
        all_zones = {}
        if os.path.exists(OUTPUT_FILE):
            with open(OUTPUT_FILE, "r") as f:
                all_zones = json.load(f)

        all_zones[CAMERA_NAME] = {
            "homography": homography.tolist() if homography is not None else None,
            "zones": world_zones,
        }

        with open(OUTPUT_FILE, "w") as f:
            json.dump(all_zones, f, indent=2)

        saved = True
        print(f"[Save] Zones written to {OUTPUT_FILE}")
        break

    # ── Exit without saving ───────────────────────────────────────────────
    elif key == 27:    # ESC
        print("[Exit] No changes saved.")
        break

cv2.destroyAllWindows()

if saved:
    print("\nSummary:")
    for zn in ZONE_NAMES:
        n = len(zones[zn])
        st = "closed" if closed[zn] else "open"
        print(f"  {zn:12s}: {n} points  ({st})")