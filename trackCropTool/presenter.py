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
                self.window.FindElement('DelSeq').Update(
                    disabled=False
                )
            else:
                self.window.FindElement('SeqList').Update(
                    values=self.seqs,
                    disabled=True
                )
                self.window.FindElement('DelSeq').Update(
                    disabled=True
                )

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

    # actions
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
        frame_types
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

        # preview
        self.bbox = []

        self.frame = 0
        self.total_frame = 0

        self.speed = 1.
        self.cmd = 'pause'

        # control
        self.grayscale = False

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

        self.match_metadata()

        self.seq_index = 0
        if len(self.seqs) > 0:
            self.seq = self.seqs[self.seq_index]
        else:
            self.seq = None

    @render_video_list
    @render_seq_list
    @render_seq_detail
    def on_video_list(self, values):
        self.video_index = self.videos.index(values['VideoList'])

        self.match_metadata()

        self.seq_index = 0
        if len(self.seqs) > 0:
            self.seq = self.seqs[self.seq_index]
        else:
            self.seq = None

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

    @render_seq_detail
    def on_seq_list(self, values):
        self.seq_index = self.seqs.index(values['SeqList'])

        if len(self.seqs) > 0:
            self.seq = self.seqs[self.seq_index]
        else:
            self.seq = None

    @render_seq_detail
    def on_seq_detail(self, values):
        self.seq.bbox_scale = float(values['BboxScale'])
        self.seq.label = values['LabelList']
        self.seq.tracker_name = values['Tracker']

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

    def player_dispatch(self):
        pass

    def match_metadata(self):
        if self.metadata_path is not None:
            video = self.videos[self.video_index]
            video_name = video.rsplit('.', 1)[0]

            seq_path = osp.join(self.metadata_path, '{}.meta'.format(video_name))

            if osp.exists(seq_path):
                with open(seq_path, 'rb') as seq_file:
                    self.seqs = Unpickler(seq_file).load()
