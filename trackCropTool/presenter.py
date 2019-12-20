import os
from os import path as osp
from pickle import Unpickler
import functools

from model import *

class Presenter:
    # binders
    def render_video_list(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            ret = func(self, *args, **kwargs)

            if len(self.videos) > 0:
                self.window.FindElement('VideoList').Update(
                    values=self.videos,
                    disabled=False,
                    set_to_index=self.video_index,
                    scroll_to_index=self.video_index
                )
            else: 
                self.window.FindElement('VideoList').Update(
                    values=self.videos,
                    disabled=True
                )

            return ret
        return wrapper

    def render_seq_list(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            ret = func(self, *args, **kwargs)

            if len(self.seqs) > 0:
                self.window.FindElement('SeqList').Update(
                    values=self.seqs,
                    disabled=False,
                    set_to_index=self.seq_index,
                    scroll_to_index=self.seq_index
                )
                self.window.FindElement('DelSeq').Update(disabled=False)
            else:
                self.window.FindElement('SeqList').Update(
                    values=self.seqs,
                    disabled=True
                )
                self.window.FindElement('DelSeq').Update(disabled=True)

            if len(self.videos) == 0:
                self.window.FindElement('AddSeq').Update(disabled=True)
            else:
                self.window.FindElement('AddSeq').Update(disabled=False)

            return ret
        return wrapper

    def render_seq_detail(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            ret = func(self, *args, **kwargs)

            if self.seq is not None:
                self.window.FindElement('BboxScale').Update(
                    value=self.seq.bbox_scale,
                    disabled=False
                )
                self.window.FindElement('Grayscale').Update(
                    value=self.seq.grayscale,
                    disabled=False
                )

                self.window.FindElement('StartFrame').Update('Start: {}'.format(self.seq.insert))
                self.window.FindElement('AnchorFrame').Update('Anchor: {}'.format(self.seq.anchor))
                self.window.FindElement('EndFrame').Update('End: {}'.format(self.seq.exit))

                self.window.FindElement('CalcStart').Update(disabled=False)
                self.window.FindElement('CalcEnd').Update(disabled=False)

                self.window.FindElement('SetStart').Update(disabled=False)
                self.window.FindElement('SetAnchor').Update(disabled=False)
                self.window.FindElement('SetEnd').Update(disabled=False)
            else:
                self.window.FindElement('BboxScale').Update(value=1.0, disabled=True)
                self.window.FindElement('Grayscale').Update(disabled=True)

                self.window.FindElement('CalcStart').Update(disabled=True)
                self.window.FindElement('CalcEnd').Update(disabled=True)

                self.window.FindElement('SetStart').Update(disabled=True)
                self.window.FindElement('SetAnchor').Update(disabled=True)
                self.window.FindElement('SetEnd').Update(disabled=True)

                self.window.FindElement('StartFrame').Update('Start: N/A')
                self.window.FindElement('AnchorFrame').Update('Anchor: N/A')
                self.window.FindElement('EndFrame').Update('End: N/A')

            return ret
        return wrapper

    def render_label_list(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            ret = func(self, *args, **kwargs)

            if self.seq is None:
                self.window.FindElement('LabelList').Update(values=self.labels, disabled=True)
            else:
                label_index = self.labels.index(self.seq.label)
                self.window.FindElement('LabelList').Update(
                    values=self.labels,
                    disabled=False,
                    set_to_index=label_index,
                    scroll_to_index=label_index
                )

            return ret
        return wrapper

    def render_tracker(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            ret = func(self, *args, **kwargs)

            if self.seq is None:
                self.window.FindElement('Tracker').Update(values=self.tracker_names, disabled=True)
            else:
                tracker_index = self.tracker_names.index(self.seq.tracker_name)
                self.window.FindElement('Tracker').Update(
                    values=self.tracker_names,
                    disabled=False,
                    set_to_index=tracker_index
                )

            return ret
        return wrapper

    def render_player(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            ret = func(self, *args, **kwargs)

            if len(self.videos) == 0:
                self.window.FindElement('FrameSlider').Update(disabled=True)
                self.window.FindElement('Retreat').Update(disabled=True)
                self.window.FindElement('Backward').Update(disabled=True)
                self.window.FindElement('Pause').Update(disabled=True)
                self.window.FindElement('Forward').Update(disabled=True)
                self.window.FindElement('Advance').Update(disabled=True)
                self.window.FindElement('JumpStart').Update(disabled=True)
                self.window.FindElement('JumpAnchor').Update(disabled=True)
                self.window.FindElement('JumpEnd').Update(disabled=True)
                for i in range(7):
                    radio_name = 'Speed{}'.format(i)
                    self.window.FindElement(radio_name).Update(disabled=True)
            else:
                self.window.FindElement('VideoProgress').Update('Progress: {}/{}'.format(
                    self.player.frame_pos,
                    self.player.total_frame,
                    disabled=False
                ))
                self.window.FindElement('ProgressBar').UpdateBar(
                    self.player.frame_pos,
                    max=self.player.total_frame-1
                )
                self.window.FindElement('FrameSlider').Update(
                    value=self.player.frame_pos,
                    range=(0, self.player.total_frame-1),
                    disabled=False
                )
                self.window.FindElement('Retreat').Update(disabled=False)
                self.window.FindElement('Backward').Update(disabled=False)
                self.window.FindElement('Pause').Update(disabled=False)
                self.window.FindElement('Forward').Update(disabled=False)
                self.window.FindElement('Advance').Update(disabled=False)
                self.window.FindElement('JumpStart').Update(disabled=False)
                self.window.FindElement('JumpAnchor').Update(disabled=False)
                self.window.FindElement('JumpEnd').Update(disabled=False)
                for i in range(7):
                    radio_name = 'Speed{}'.format(i)
                    self.window.FindElement(radio_name).Update(disabled=False)

            return ret
        return wrapper

    # actions
    @render_player
    @render_label_list
    @render_tracker
    @render_seq_detail
    @render_seq_list
    @render_video_list
    def __init__(
        self,
        window,
        player,
        labels,
        tracker_names,
        speeds
        ):
        self.window = window
        self.player = player

        # paths
        self.video_path = None
        self.metadata_path = None
        
        # video list
        self.videos = []
        self.video_index = 0

        # sequence list & detail
        self.seqs = []
        self.seq_index = 0
        self.seq = None

        self.labels = labels
        self.tracker_names = tracker_names
        self.speeds = speeds

        # preview
        self.bbox = []

        self.frame = 0
        self.total_frame = 0

        self.speed = 1.
        self.cmd = 'pause'

        # control
        self.grayscale = False

    @render_player
    @render_video_list
    @render_seq_list
    @render_seq_detail
    def on_video_path(self, values):
        self.video_path = values['VideoPath']

        if osp.exists(self.video_path):
            self.videos = os.listdir(self.video_path)
        else:
            os.makedirs(self.video_path)
            self.videos = []

        self.video_index = 0

        if len(self.videos) > 0:
            video_file = osp.join(self.video_path, self.videos[self.video_index])
            self.player.load_video(video_file)

        self.match_metadata()

        self.seq_index = 0
        if len(self.seqs) > 0:
            self.seq = self.seqs[self.seq_index]
        else:
            self.seq = None

    @render_player
    @render_video_list
    @render_seq_list
    @render_seq_detail
    def on_video_list(self, values):
        # TODO : popup to save

        self.video_index = self.videos.index(values['VideoList'][0])

        self.match_metadata()

        self.seq_index = 0
        if len(self.seqs) > 0:
            self.seq = self.seqs[self.seq_index]
        else:
            self.seq = None

        video_file = osp.join(self.video_path, self.videos[self.video_index])
        self.player.load_video(video_file)

    @render_player
    @render_seq_list
    @render_seq_detail
    def on_metadata_path(self, values):
        self.metadata_path = values['MetaPath']

        self.match_metadata()

        self.seq_index = 0
        if len(self.seqs) > 0:
            self.seq = self.seqs[self.seq_index]
        else:
            self.seq = None

    @render_player
    @render_seq_detail
    def on_seq_list(self, values):
        self.seq_index = self.seqs.index(values['SeqList'][0])

        if len(self.seqs) > 0:
            self.seq = self.seqs[self.seq_index]
        else:
            self.seq = None

    @render_player
    @render_seq_detail
    @render_seq_list
    def on_add_seq(self, values):
        self.seqs.append(Sequence())
        self.seq_index = len(self.seqs) - 1
        self.seq = self.seqs[self.seq_index]

    @render_player
    @render_seq_detail
    @render_seq_list
    def on_del_seq(self, values):
        if len(self.seqs) > 0:
            self.seqs.pop(self.seq_index)

            if self.seq_index >= len(self.seqs):
                self.seq_index = len(self.seqs) - 1

    @render_seq_detail
    def on_seq_detail(self, values):
        self.seq.bbox_scale = float(values['BboxScale'])
        self.seq.label = values['LabelList'][0]
        self.seq.tracker_name = values['Tracker']

    @render_seq_detail
    def on_set_start(self, values):
        self.seq.insert = self.player.frame_pos
        self.player.start_frame = self.player.frame_pos

    @render_seq_detail
    def on_set_anchor(self, values):
        if self.player.get_anchor():
            self.seq.anchor = self.player.anchor_frame
            self.seq.anchor_bbox = self.player.anchor

    @render_seq_detail
    def on_set_end(self, values):
        self.seq.exit = self.player.frame_pos
        self.player.end_frame = self.player.frame_pos

    def on_calc_start(self, values):
        self.player.calc_start = True

    def on_calc_end(self, values):
        self.player.calc_end = True

    @render_player
    def on_frame_slider(self, values):
        self.player.frame_pos = values['FrameSlider']
        self.player.refresh()

    @render_player
    def on_pause(self, values):
        self.player.playing = False

    @render_player
    def on_forward(self, values):
        self.player.playing = True
        self.player.direction = True
        self.player.speed_ratio = self.get_speed_ratio(values)
        self.player.grayscale = values['Grayscale']

    @render_player
    def on_backward(self, values):
        self.player.playing = True
        self.player.direction = False
        self.player.speed_ratio = self.get_speed_ratio(values)
        self.player.grayscale = values['Grayscale']

    @render_player
    def on_advance(self, values):
        self.player.playing = True
        self.player.direction = True
        self.player.step = True
        self.player.grayscale = values['Grayscale']

    @render_player
    def on_retreat(self, values):
        self.player.playing = True
        self.player.direction = False
        self.player.step = True
        self.player.grayscale = values['Grayscale']

    @render_player
    def on_jump_start(self, values):
        if self.player.start_frame > 0:
            self.player.frame_pos = self.player.start_frame
            self.player.refresh()

    @render_player
    def on_jump_end(self, values):
        if self.player.end_frame > 0:
            self.player.frame_pos = self.player.end_frame
            self.player.refresh()

    @render_player
    def on_jump_anchor(self, values):
        if self.player.anchor_frame > 0:
            self.player.frame_pos = self.player.anchor_frame
            self.player.refresh()

    def on_save(self, values):
        if len(self.seqs) > 0:
            video = self.videos[self.video_index]
            video_name = video.rsplit('.', 1)[0]

            meta_file = osp.join(self.metadata_path, '{}.meta'.format(video_name))
            with open(meta_file, 'wb') as file:
                Pickler(file).dump(self.seqs)

    @render_player
    @render_seq_detail
    @render_seq_list
    def on_clear(self, values):
        self.seqs = []
        self.seq_index = 0
        self.seq = None

    # helpers
    def gui_dispatch(self, event, values):
        # we don't handle 'Cancel' here

        if event == 'VideoPath':
            self.on_video_path(values)
        elif event == 'MetaPath':
            self.on_metadata_path(values)
        elif event == 'VideoList':
            self.on_video_list(values)
        elif event == 'SeqList':
            self.on_seq_list(values)
        elif event == 'AddSeq':
            self.on_add_seq(values)
        elif event == 'DelSeq':
            self.on_del_seq(values)
        elif event == 'SetStart':
            self.on_set_start(values)
        elif event == 'SetAnchor':
            self.on_set_anchor(values)
        elif event == 'SetEnd':
            self.on_set_end(values)
        elif event == 'CalcStart':
            self.on_calc_start(values)
        elif event == 'CalcEnd':
            self.on_calc_end(values)
        elif event == 'FrameSlider':
            self.on_frame_slider(values)
        elif event == 'Pause':
            self.on_pause(values)
        elif event == 'Forward':
            self.on_forward(values)
        elif event == 'Backward':
            self.on_backward(values)
        elif event == 'Advance':
            self.on_advance(values)
        elif event == 'Retreat':
            self.on_retreat(values)
        elif event == 'JumpStart':
            self.on_jump_start(values)
        elif event == 'JumpEnd':
            self.on_jump_end(values)
        elif event == 'JumpAnchor':
            self.on_jump_anchor(values)
        elif event == 'Save':
            self.on_save(values)
        elif event == 'Clear':
            self.on_clear(values)

    def match_metadata(self):
        if self.metadata_path is not None:
            video = self.videos[self.video_index]
            video_name = video.rsplit('.', 1)[0]

            seq_path = osp.join(self.metadata_path, '{}.meta'.format(video_name))

            if osp.exists(seq_path):
                with open(seq_path, 'rb') as seq_file:
                    self.seqs = Unpickler(seq_file).load()

    def get_speed_ratio(self, values):
        for key in values.keys():
            if 'Speed' in key and values[key] == True:
                return self.speeds[key]
