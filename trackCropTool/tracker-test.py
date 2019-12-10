import cv2

# const
tracker = 'csrt'
video_path = './test.mp4'
show_video = True
output_path = './track_test.mp4'

fps = 60.
frame_size = (1920, 1080)

OPENCV_OBJECT_TRACKERS = {
    "csrt": cv2.TrackerCSRT_create,
    "kcf": cv2.TrackerKCF_create,
    "boosting": cv2.TrackerBoosting_create,
    "mil": cv2.TrackerMIL_create,
    "tld": cv2.TrackerTLD_create,
    "medianflow": cv2.TrackerMedianFlow_create,
    "mosse": cv2.TrackerMOSSE_create
}

tracker = OPENCV_OBJECT_TRACKERS[tracker]()
initBBox = None

fourcc_str = 'X264'
fourcc = cv2.cv.CV_FOURCC(**list(fourcc_str))
output = cv2.VideoWriter(output_path, fourcc, fps, frame_size)

input = cv2.VideoCapture(video_path)

while True:
    frame = input.read()
    
    if frame == None:
        break

    if initBBox is not None:
        success, bbox = tracker.update(frame)

    if success:
        x, y, w, h = [int(v) for v in bbox]
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    if show_video:
        cv2.imshow('{} - {}'.format(tracker, video_path), frame)

    if output.isOpened():
        output.write(frame)

    key = cv2.waitKey(1) & 0xff

    if key == ord('s'):
        initBBox = cv2.selectROI(
            '{} - {}'.format(tracker, video_path),
            frame,
            fromCenter=False,
            showCrosshair=True
        )

        tracker.init(frame, initBBox)
    elif key == ord('q'):
        break

input.release()
output.release()

cv2.destroyAllWindows()
