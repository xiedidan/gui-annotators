import os
from os import path as osp
from pickle import Unpickler

from model import *

class Presenter:
    def __init__(
        self,
        window,
        video_path='',
        metadata_path=''
        ):
        self.window = window
        self.video_path = video_path
        self.metadata_path = metadata_path

        self.video_list = []
        self.current_video = ''

        if osp.exists(self.video_path):
            self.video_list = os.listdir(self.video_path)
        else:
            os.makedirs(self.video_path)

        # TODO : refresh video list

        self.seq_list = []
        self.current_seq = ''

        if osp.exists(self.metadata_path):
            seq_filenames = os.listdir(self.metadata_path)

            for seq_filename in seq_filenames:
                seq_path = osp.join(self.metadata_path, seq_filename)
                self.seq_list.append(Unpickler(seq_path).load())
        else:
            os.makedirs(self.metadata_path)

        # TODO : refresh sequence list


