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
from player import PlayerState, Player

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
frame_types = [
    'Auto',
    'Specified'
]

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
                ]
            ])],
            [sg.Frame('Sequence', [
                [
                    sg.Combo(tracker_names, default_value='kcf', key='Tracker'),
                    sg.VerticalSeparator(pad=None),
                    sg.Text('BBox Scale:'),
                    sg.In('1.0', key='BboxScale', size=(5, 1))
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
                [sg.ProgressBar(pageCount, orientation='h', size=(48, 5), key='ProgressBar')],
                [sg.Slider(key='FrameSlider', orientation='h', size=(48, 15), disable_number_display=True)],
                [
                    sg.Button(' ← '),
                    sg.Button(' ◄ '),
                    sg.Button('   ‖   '),
                    sg.Button(' ► '),
                    sg.Button(' → '),
                    sg.VerticalSeparator(pad=None),
                    sg.Button('  {  '),
                    sg.Button('  ⌂  '),
                    sg.Button('  }  '),
                ],
                [
                    sg.Radio('⅛', 'SpeedRadio'),
                    sg.Radio('¼', 'SpeedRadio'),
                    sg.Radio('½', 'SpeedRadio'),
                    sg.Radio('1', 'SpeedRadio', default=True),
                    sg.Radio('2', 'SpeedRadio'),
                    sg.Radio('4', 'SpeedRadio'),
                    sg.Radio('8', 'SpeedRadio')
                ]
            ])],
            [sg.Frame('Crops', [
                [
                    sg.Text('Crop Page: {} / {}'),
                    sg.VerticalSeparator(pad=None),
                    sg.Button('Crop'),
                    sg.VerticalSeparator(pad=None),
                    sg.Checkbox('Tag')
                ],
                [
                    sg.Button(' ◄ '),
                    sg.Slider(key='FrameSlider', orientation='h', size=(38, 24), disable_number_display=True),
                    sg.Button(' ► '),
                ]
            ])],
            [sg.Frame('Misc.', [
                [sg.Checkbox('Grayscale')],
                [
                    sg.Button('Save'),
                    sg.Button('Save All'),
                    sg.VerticalSeparator(pad=None),
                    sg.Button('Clear'),
                    sg.Button('Clear All')]
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
        frame_types
    )

    # main loop
    while True:
        # GUI handler
        event, values = window.read(timeout=0)

        if event in (None, 'Cancel'):
            break
        elif event == sg.TIMEOUT_KEY:
            pass
        else:
            presenter.gui_dispatch(event, values)

        if player.read():
            presenter.player_dispatch()

        time.sleep(0.005)

    window.close()
