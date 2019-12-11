import time
import cv2

# const
tracker_name = 'mosse'
video_path = '../../../dl_data/warframe/export/2019-12-09_23-44-31_4.mp4'
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

initBBox = None

fourcc_str = 'H264'
fourcc = cv2.VideoWriter_fourcc(*fourcc_str)
output = cv2.VideoWriter(output_path, fourcc, fps, frame_size, True)

input = cv2.VideoCapture(video_path)

# read all frames
while True:
    success, frame = input.read()
    
    if not success:
        break

    if initBBox is not None:
        success, bbox = tracker.update(frame)

        if success:
            x, y, w, h = [int(v) for v in bbox]
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        if output.isOpened():
            output.write(frame)

    window_name = '{} - {}'.format(tracker_name, video_path)
    cv2.imshow(window_name, frame)

    key = cv2.waitKey(1) & 0xff

    if key == ord('s'):
        initBBox = cv2.selectROI(
            window_name,
            frame,
            fromCenter=False,
            showCrosshair=True
        )

        tracker = OPENCV_OBJECT_TRACKERS[tracker_name]()
        tracker.init(frame, initBBox)
    elif key == ord('q'):
        break

input.release()
output.release()

cv2.destroyAllWindows()
