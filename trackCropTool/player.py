from multiprocessing import Process, Queue
import timeit

import cv2

class PlayerState:
    def __init__(self):
        self.video_file = ''

        self.frame = 0
        self.total_frame = 0

        self.cmd = 'pause' # forward or backward or pause or anchor
        self.speed = 1.

        self.anchor = []
        self.bbox_scale = 1.

        self.tracker_name = 'kcf'

FSM_STATUS = [
    'idle',
    'pause',
    'forward',
    'backward',
    'advance',
    'retreat',
    
]

def playerProcess(cmd_q, data_q):
    cmd = PlayerState()
    state = PlayerState()

    while True:
        start_time = timeit.default_timer()

        try:
            # only keep the last cmd
            while not cmd_q.empty():
                cmd = cmd_q.get_nowait()
        except:
            pass

        if cmd.video_file != state.video_file:
            # load video file
            state.video_file = cmd.video_file
            cap = cv2.VideoCapture(state.video_file)
            
            state.total_frame = cap.get(cv2.CAP_PROP_FRAME_COUNT)

        state.cmd = cmd.cmd
        state.speed = cmd.speed
        state.bbox_scale = cmd.bbox_scale
        state.tracker_name = cmd.tracker_name
        state.anchor = cmd.anchor

        # calc parameter
        state.frame = cap.get(cv2.CV_CAP_PROP_POS_FRAMES)
        frame_time = 1. / (cap.get(cv2.CV_CAP_PROP_FPS) * state.speed)

        if state.cmd != 'pause':
            success, frame = cap.read()

            if not success:
                state.cmd = 'pause'

            window_name = '{} - {}'.format(state.video_file, state.tracker_name)
            cv2.imshow(window_name, frame)

            if state.cmd != 'anchor':
                if state.anchor is not None:
                    success, bbox = tracker.update(frame)
                    
                    if success:
                        x, y, w, h = [int(v) for v in bbox]
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 1)
                        # TODO : scaled bbox

                    window_name = '{} - {}'.format(state.video_file, state.tracker_name)
                    cv2.imshow(window_name, frame)

                    if state.cmd == 'forward' or state.cmd == 'advance':
                        if cap.get(cv2.CV_CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT) - 1:
                            state.cmd = 'pause'
                        else:
                            cap.set(cv2.CV_CAP_PROP_POS_FRAMES, cap.get(cv2.CV_CAP_PROP_POS_FRAMES)+1)
                            if state.cmd == 'advance':
                                state.cmd = 'pause'
                    elif state.cmd == 'backward' or state.cmd == 'retreat':
                        if cap.get(cv2.CV_CAP_PROP_POS_FRAMES) == 0:
                            state.cmd = 'pause'
                        else:
                            cap.set(cv2.CV_CAP_PROP_POS_FRAMES, cap.get(cv2.CV_CAP_PROP_POS_FRAMES)-1)
                            if state.cmd == 'retreat':
                                state.cmd = 'pause'

                    # send state
                    try:
                        # cancel unsent state
                        while not data_q.empty():
                            data_q.get_nowait()

                        data_q.put_nowait(state)
                    except:
                        pass

                    # fps control
                    end_time = timeit.default_timer()
                    wall_time = end_time - start_time
                    sleep_time = frame_time - wall_time

                    if sleep_time > 0:
                        cv2.waitKey(sleep_time)
                    else:
                        cv2.waitKey(1)
            else:
                window_name = '{} - {}'.format(state.video_file, state.tracker_name)
                cv2.imshow(window_name, frame)

                anchor = cv2.selectROI(
                    window_name,
                    frame,
                    fromCenter=False,
                    showCrosshair=True
                )

                state.anchor = anchor

                # send state
                try:
                    # cancel unsent state
                    while not data_q.empty():
                        data_q.get_nowait()

                    data_q.put_nowait(state)
                except:
                    pass

                cv2.waitKey(1)

    cap.release()

class Player:
    def __init__(self):
        self.cmd = PlayerState()
        self.data = PlayerState()

        self.cmd_q = Queue()
        self.data_q = Queue()

        self.player = Process(
            target=playerProcess,
            args=(self.cmd_q, self.data_q)
        )
        self.player.start()

    def write(self):
        try:
            # cancel unsent cmd
            while not self.cmd_q.empty():
                self.cmd_q.get_nowait()

            self.cmd_q.put_nowait(self.cmd)
        except:
            pass

    def read(self):
        try:
            # only keep the last data
            while not self.data_q.empty():
                self.data = self.data_q.get_nowait()

            return True
        except:
            return False
