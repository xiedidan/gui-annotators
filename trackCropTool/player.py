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

        self.bbox = []
        self.bbox_scale = 1.

        self.grayscale = False

class Player:
    def playerProcess(cmd_q, data_q):
        cmd = PlayerState()
        state = PlayerState()

        frames = []

        original_fps = 0
        actual_fps = 0
        step = 0
        step_time = 0

        while True:
            start_time = timeit.default_timer()

            try:
                # only keep the last cmd
                while not self.cmd_q.empty():
                    cmd = self.cmd_q.get_nowait()
            except:
                pass

            if cmd.video_file != state.video_file:
                # load video file
                state.video_file = cmd.video_file
                cap = cv2.VideoCapture(state.video_file)
                
                # read all frames
                while True:
                    success, frame = cap.read()
                    
                    if not success:
                        break

                    frames.append(frame)

                cap.release()

                state.frame = 0
                state.total_frame = len(frames)

            state.speed = cmd.speed
            state.bbox_scale = cmd.bbox_scale
            state.grayscale = cmd.grayscale

            # TODO : calc parameter

            state.cmd = cmd.cmd

            if state.cmd == 'forward':
                # TODO : track and display

                if state.frame + step < state.total_frame:
                    state.frame += step
            elif state.cmd == 'backward':
                # TODO : track and display

                if state.frame - step > -1:
                    state.frame -= step
            elif state.cmd == 'anchor':
                # TODO : cv2.selectROI()

                state.bbox = roi

            # send state
            try:
                # cancel unsent state
                while not data_q.empty():
                    data_q.get_nowait()

                data_q.put_nowait(state)
            except:
                pass

            end_time = timeit.default_timer()

            # fps control
            frame_time = end_time - start_time
            sleep_time = step_time - frame_time

            if sleep_time > 0:
                cv2.waitKey(sleep_time)
            else:
                cv2.waitKey(1)

    def __init__(self):
        self.cmd = PlayerState()
        self.data = PlayerState()

        self.cmd_q = Queue()
        self.data_q = Queue()

        self.player = Process(
            targe=playerProcess,
            args=(self.cmd_q, self.data_q)
        )
        self.player.start()

    def cmd(self):
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
        except:
            pass
