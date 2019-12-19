import timeit

import cv2

OPENCV_OBJECT_TRACKERS = {
    "csrt": cv2.TrackerCSRT_create,
    "kcf": cv2.TrackerKCF_create,
    "boosting": cv2.TrackerBoosting_create,
    "mil": cv2.TrackerMIL_create,
    "tld": cv2.TrackerTLD_create,
    "medianflow": cv2.TrackerMedianFlow_create,
    "mosse": cv2.TrackerMOSSE_create
}

class Player:
    def __init__(self):
        self.playing = False
        self.step = False
        self.direction = True # True for forward, False for backward
        
        self.frame = None
        self.frame_pos = 0
        self.total_frame = 0
        self.fps = 0

        self.anchor_frame = 0
        self.anchor = []

        self.bbox_scale = 1.
        self.speed_ratio = 1

        self.calc_start = False
        self.calc_end = False

        self.start_frame = -1
        self.end_frame = -1

        self.video = None
        self.tracker = None

        self.window_name = ''
        self.tracker_name = ''

        self.frame_start_time = 0

    def get_anchor(self):
        try:
            self.anchor_frame = self.frame_pos
            self.anchor = cv2.selectROI(
                self.window_name,
                self.frame,
                fromCenter=False,
                showCrosshair=True
            )

            return True
        except:
            return False

    def load_video(self, video_file):
        try:
            self.video = cv2.VideoCapture(video_file)
            self.total_frame = self.video.get(cv2.CAP_PROP_FRAME_COUNT)
            self.fps = self.video.get(cv2.CAP_PROP_FPS)
            self.frame = self.video.get(cv2.CV_CAP_PROP_POS_FRAMES)

            self.window_name = '{} - {}'.format(video_file, self.tracker_name)

            self.frame = self.video.read()

            cv2.imshow(self.window_name, self.frame)
            cv2.waitKey(1)

            return True
        except:
            return False

    def start_frame(self):
        self.frame_start_time = timeit.default_timer()

    def go(self):
        if self.playing:
            if self.video is not None:
                self.frame_pos = self.video.get(cv2.CV_CAP_PROP_POS_FRAMES)
                success, self.frame = self.video.read()

                if not success:
                    return False
            
                if len(self.anchor) > 0 and self.frame_pos == self.anchor_frame:
                    self.tracker = OPENCV_OBJECT_TRACKERS[self.tracker_name]()
                    self.tracker.init(self.frame, self.anchor)
                elif self.tracker is not None:
                    success, bbox = self.tracker.update(self.frame)

                    if not success:
                        self.tracker = None
                        
                        if self.direction == True and self.calc_end == True:
                            self.end = self.frame - 1
                        
                        if self.direction == False and self.calc_start == True:
                            self.start = self.frame + 1
                    else:
                        x, y, w, h = [int(v) for v in bbox]
                        cv2.rectangle(self.frame, (x, y), (x+w, y+h), (0, 255, 0), 1)

                        if abs(self.bbox_scale - 1.) > 1e-5:
                            d_x = (int(self.bbox_scale * w) - w) // 2
                            d_y = (int(self.bbox_scale * h) - h) // 2
                            cv2.rectangle(self.frame, (x-d_x, y-d_y), (x+w+d_x, y+h+d_y), (255, 255, 0), 1)

                cv2.imshow(self.window_name, self.frame)

                if self.step == True:
                    self.playing = False
                    self.step = False

                # fps control
                actual_fps = self.fps * self.speed_ratio
                frame_time = 1. / actual_fps

                wall_time = timeit.default_timer() - self.frame_start_time
                sleep_time = int((frame_time - wall_time) * 1000)

                if sleep_time > 0:
                    cv2.waitKey(sleep_time)
                else:
                    cv2.waitKey(1)

                return True

        return False
