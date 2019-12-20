import os
import sys
import io
import base64
import math
import time

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageColor
import pandas as pd
import PySimpleGUI as sg

from presenter import Presenter
from player import Player

# global
class_file = './predefined_classes.txt'
classes = []
image_files = []
annos = {}
THUMB_SIZE = (120, 120)
GRID_SIZE = (8, 8)
pageNo = 0
pageCount = 0
pageOffset = -1 # index in page
batch_images = []
INFO_COLOR = '#66CC66'
HIGHLIGHT_COLOR = '#FF6666'
CLASS_COLORS = ['#666699', '#99CC66', '#FF99CC', '#FF9999', '#FFCC99', '#FFCC00']
play = False
tracker_names = [
    "csrt",
    "kcf",
    "boosting",
    "mil",
    "tld",
    "medianflow",
    "mosse"
]
speeds = {
    'Speed0': 1./8,
    'Speed1': 1./4,
    'Speed2': 1./2,
    'Speed3': 1.,
    'Speed4': 2.,
    'Speed5': 4.,
    'Speed6': 8.
}

batch_size = GRID_SIZE[0] * GRID_SIZE[1]

# label reader
def read_class(class_file):
    classes = []

    with open(class_file) as f:
        classes = [line.rstrip('\n') for line in f]

    return classes

classes = read_class(class_file)

# background
def read_img(file_path, size=THUMB_SIZE):
    img = open(file_path, 'rb+')
    img = base64.b64encode(img.read())

    return img

img = read_img('./bg-batch.png')

# GUI
sg.ChangeLookAndFeel('Dark')

img_grid = []

for i in range(GRID_SIZE[0]):
    img_row = []

    for j in range(GRID_SIZE[1]):
        img_row.append(sg.Image(
            data=img,
            key='Image-{}-{}'.format(i, j),
            background_color='white',
            size=(120,120),
            pad=(1,1),
            enable_events=True)
        )

    img_grid.append(img_row)

layout = [
    [
        sg.Column(img_grid),
        sg.VerticalSeparator(pad=None),
        sg.Column([
            [sg.Frame('Paths', [
                [sg.In('Video Directory', key='VideoPath', enable_events=True), sg.FolderBrowse()],
                [sg.In('Metadata Directory', key='MetaPath', enable_events=True), sg.FolderBrowse()]
            ])],
            [sg.Frame('Video Files', [
                [sg.Listbox(values=[], key='VideoList', enable_events=True, size=(51, 6))]
            ])],
            [sg.Frame('Sequences', [
                [sg.Listbox(values=[], key='SeqList', enable_events=True, size=(51, 6))],
                [
                    sg.Button('Add', key='AddSeq'),
                    sg.Button('Del', key='DelSeq'),
                    sg.Button('Save', key='Save'),
                    sg.Button('Clear', key='Clear')
                ]
            ])],
            [sg.Frame('Sequence', [
                [
                    sg.Combo(tracker_names, default_value='kcf', key='Tracker'),
                    sg.VerticalSeparator(pad=None),
                    sg.Text('BBox Scale:'),
                    sg.In('1.0', key='BboxScale', size=(5, 1)),
                    sg.VerticalSeparator(pad=None),
                    sg.Checkbox('Grayscale', key='Grayscale'),
                ],
                [sg.Listbox(values=classes, key='LabelList', enable_events=True, size=(51, len(classes)))],
                [
                    sg.Text('Start: {}', key='StartFrame'), sg.Button('Calc', key='CalcStart'),
                    sg.VerticalSeparator(pad=None),
                    sg.Text('Anchor: {}', key='AnchorFrame'),
                    sg.VerticalSeparator(pad=None),
                    sg.Text('End: {}', key='EndFrame'), sg.Button('Calc', key='CalcEnd')
                ],
                [
                    sg.Text('Set:'),
                    sg.Button('  {  ', key='SetStart'),
                    sg.Button('  ⌂  ', key='SetAnchor'),
                    sg.Button('  }  ', key='SetEnd'),
                ]
            ])],
            [sg.Frame('Preview', [
                [sg.T('Progress: 0/0', key='VideoProgress', size=(30, 1), auto_size_text=True)],
                [sg.ProgressBar(100, orientation='h', size=(48, 5), key='ProgressBar')],
                [sg.Slider(key='FrameSlider', orientation='h', size=(48, 15), disable_number_display=True, enable_events=True)],
                [
                    sg.Button(' ← ', key='Retreat'),
                    sg.Button(' ◄ ', key='Backward'),
                    sg.Button('   ‖   ', key='Pause'),
                    sg.Button(' ► ', key='Forward'),
                    sg.Button(' → ', key='Advance'),
                    sg.VerticalSeparator(pad=None),
                    sg.Button('  {  ', key='JumpStart'),
                    sg.Button('  ⌂  ', key='JumpAnchor'),
                    sg.Button('  }  ', key='JumpEnd'),
                ],
                [
                    sg.Radio('⅛', 'SpeedRadio', key='Speed0'),
                    sg.Radio('¼', 'SpeedRadio', key='Speed1'),
                    sg.Radio('½', 'SpeedRadio', key='Speed2'),
                    sg.Radio('1', 'SpeedRadio', default=True, key='Speed3'),
                    sg.Radio('2', 'SpeedRadio', key='Speed4'),
                    sg.Radio('4', 'SpeedRadio', key='Speed5'),
                    sg.Radio('8', 'SpeedRadio', key='Speed6')
                ]
            ])],
            [sg.Frame('Crops', [
                [
                    sg.Text('Crop Page: {} / {}'),
                    sg.VerticalSeparator(pad=None),
                    sg.Button('Crop'),
                    sg.VerticalSeparator(pad=None),
                    sg.Checkbox('Tag', key='Tag')
                ],
                [
                    sg.Button(' ◄ '),
                    sg.Slider(key='CropSlider', orientation='h', size=(38, 24), disable_number_display=True),
                    sg.Button(' ► '),
                ]
            ])]
        ])
    ]
]

if __name__ == '__main__':
    # finalize window so presenter could init ASAP
    window = sg.Window('Track Label Tool', layout, finalize=True)
    player = Player()

    # MVP Presenter
    presenter = Presenter(
        window,
        player,
        classes,
        tracker_names,
        speeds,
    )

    # main loop
    while True:
        player.frame_start()

        # GUI handler
        event, values = window.read(timeout=0)

        if event in (None, 'Cancel'):
            break
        elif event == sg.TIMEOUT_KEY:
            pass
        else:
            presenter.gui_dispatch(event, values)

        presenter.render_player()

        play_flag = player.go()

        if not play_flag:
            time.sleep(0.005)

    window.close()
