from camera_manager import MultiCameraManager

if __name__ == "__main__":
    cameras = [
        "rtsp://10.64.36.13:554/rtsp/streaming?channel=01&subtype=1",
        "rtsp://10.64.36.14:554/rtsp/streaming?channel=01&subtype=1",
    ]

    manager = MultiCameraManager(cameras=cameras, buffer_size=2, fps=15, img_size=(640, 640))
    manager.display_streams()