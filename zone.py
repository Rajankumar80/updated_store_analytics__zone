import cv2
import numpy as np
import json
import time

class ZoneManager:
    def __init__(self, camera_data, entry_frames=4, exit_frames=6, dwell_file="zone_dwell_summary.json"):
        self.ENTRY_FRAMES = entry_frames
        self.EXIT_FRAMES = exit_frames
        self.DWELL_FILE = dwell_file
        
        # Initialize Homography
        self.homography = np.array(camera_data["homography"], dtype=np.float32) if camera_data.get("homography") else None
        
        # Load Zones
        self.zones_pixel = {k: v["pixel"] for k, v in camera_data["zones"].items()}
        self.zones_world = {k: v["world"] for k, v in camera_data["zones"].items()}
        
        # State Tracking
        self.confirmed_inside = {name: set() for name in self.zones_pixel}
        self.inside_streak = {}
        self.outside_streak = {}
        self.zone_entry_count = {name: 0 for name in self.zones_pixel}
        self.zone_exit_count = {name: 0 for name in self.zones_pixel}
        self.entry_epoch = {}
        self.cumulative_dwell = {}

    def fmt_ts(self, epoch): 
        return time.strftime("%H:%M:%S", time.localtime(epoch))

    def fmt_duration(self, secs):
        secs = int(secs)
        m, s = divmod(secs, 60)
        return f"{m}m {s:02d}s" if m else f"{s}s"

    # --- THE MISSING METHOD ---
    def pixel_to_world(self, x, y):
        """Converts pixel coordinates to world coordinates using the homography matrix."""
        if self.homography is None: 
            return None
        pt = np.array([[[float(x), float(y)]]], dtype=np.float32)
        world_pt = cv2.perspectiveTransform(pt, self.homography)
        return world_pt[0][0]

    def apply_hysteresis(self, tid, zone, raw_inside, now, event_log):
        key = (tid, zone)
        confirmed_in = tid in self.confirmed_inside[zone]

        if raw_inside:
            self.outside_streak[key] = 0
            if not confirmed_in:
                self.inside_streak[key] = self.inside_streak.get(key, 0) + 1
                if self.inside_streak[key] >= self.ENTRY_FRAMES:
                    self.confirmed_inside[zone].add(tid)
                    self.inside_streak[key] = 0
                    self.zone_entry_count[zone] += 1
                    self.entry_epoch[key] = now
                    event_log.append({
                        "event": "ENTRY", "id": tid, "tracker_id": int(tid),
                        "zone": zone, "entry_time": self.fmt_ts(now), "entry_epoch": round(now, 3)
                    })
        else:
            self.inside_streak[key] = 0
            if confirmed_in:
                self.outside_streak[key] = self.outside_streak.get(key, 0) + 1
                if self.outside_streak[key] >= self.EXIT_FRAMES:
                    self.process_exit(tid, zone, now, event_log)

    def process_exit(self, tid, zone, now, event_log, reason=None):
        key = (tid, zone)
        if tid in self.confirmed_inside[zone]:
            self.confirmed_inside[zone].discard(tid)
            self.outside_streak[key] = 0
            self.zone_exit_count[zone] += 1
            entry_ep = self.entry_epoch.pop(key, now)
            dwell_secs = round(now - entry_ep, 1)
            
            if tid not in self.cumulative_dwell: 
                self.cumulative_dwell[tid] = {}
            prev = self.cumulative_dwell[tid].get(zone, 0.0)
            total = round(prev + dwell_secs, 1)
            self.cumulative_dwell[tid][zone] = total
            
            evt = {
                "event": "EXIT", "id": tid, "tracker_id": int(tid),
                "zone": zone, "entry_time": self.fmt_ts(entry_ep), "exit_time": self.fmt_ts(now),
                "dwell_secs": dwell_secs, "dwell_formatted": self.fmt_duration(dwell_secs),
                "total_dwell_secs": total, "total_dwell_fmt": self.fmt_duration(total)
            }
            if reason: 
                evt["reason"] = reason
            event_log.append(evt)
            self.flush_dwell_summary()

    def cleanup_lost_tracks(self, active_ids, now, event_log):
        all_confirmed = set().union(*self.confirmed_inside.values())
        for tid in (all_confirmed - active_ids):
            for zone in self.zones_pixel:
                if tid in self.confirmed_inside[zone]:
                    self.process_exit(tid, zone, now, event_log, reason="track_lost")
            for zone in self.zones_pixel:
                self.inside_streak.pop((tid, zone), None)
                self.outside_streak.pop((tid, zone), None)

    def flush_dwell_summary(self):
        summary = {f"id_{did}": {z: {"total_secs": s, "total_fmt": self.fmt_duration(s)} 
                   for z, s in zs.items()} for did, zs in self.cumulative_dwell.items()}
        with open(self.DWELL_FILE, "w") as f:
            json.dump(summary, f, indent=2)