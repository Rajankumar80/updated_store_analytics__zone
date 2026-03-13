import cv2
from model import Detector


VIDEO_PATH    = "/home/keshav/rajan/new_pipeline/store.mp4"
OUTPUT_PATH   = "/home/keshav/rajan/new_pipeline/output_videos/output.avi"
CAMERA_NAME   = "cam_entry"

# Tune this between 0.4 and 1.0 to fit your screen
DISPLAY_SCALE = 0.8


def main():

    detector = Detector(camera_name=CAMERA_NAME)

    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        print(f"[ERROR] Cannot open video: {VIDEO_PATH}")
        return

    # Create resizable windows
    cv2.namedWindow("Camera View", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Floor Map",   cv2.WINDOW_NORMAL)

    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out    = None

    print("[INFO] Starting. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[INFO] End of video.")
            break

        processed_frame, tracks, floor_map = detector.process_frame(frame)

        # initialize video writer on first frame (full resolution)
        if out is None:
            h, w = processed_frame.shape[:2]
            out  = cv2.VideoWriter(OUTPUT_PATH, fourcc, 8, (w, h))
            print(f"[INFO] Writing output → {OUTPUT_PATH}  ({w}x{h})")

        # write full-res frame to file
        out.write(processed_frame)

        # scale down for display only
        cam_display = cv2.resize(processed_frame,
                                 (0, 0), fx=DISPLAY_SCALE, fy=DISPLAY_SCALE)
        map_display = cv2.resize(floor_map,
                                 (0, 0), fx=DISPLAY_SCALE, fy=DISPLAY_SCALE)

        cv2.imshow("Camera View", cam_display)
        cv2.imshow("Floor Map",   map_display)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            print("[INFO] Quit by user.")
            break

    cap.release()
    if out is not None:
        out.release()
    cv2.destroyAllWindows()
    print("[INFO] Done.")


if __name__ == "__main__":
    main()