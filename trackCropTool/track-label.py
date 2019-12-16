import os
import sys
import io
import base64
import math

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageColor
import pandas as pd
import PySimpleGUI as sg

from model import *

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

def read_class(class_file):
    classes = []

    with open(class_file) as f:
        classes = [line.rstrip('\n') for line in f]

    return classes

classes = read_class(class_file)

def read_annos(anno_file):
    anno_df = pd.read_csv(anno_file)

    id_list = list(anno_df['filename'])
    class_list = list(anno_df['class'])
    anno_dict = {}

    for id, cls in zip(id_list, class_list):
        anno_dict[id] = cls

    return anno_dict

def save_anno(annos, anno_path):
    id_list = annos.keys()
    cls_list = annos.values()

    anno_df = pd.DataFrame(zip(id_list, cls_list), columns=['filename', 'class'])
    anno_df.to_csv(anno_path, index=False)

def read_img(file_path, size=THUMB_SIZE):
    img = open(file_path, 'rb+')
    img = base64.b64encode(img.read())

    return img

img = read_img('./bg-batch.png')

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
                    sg.Button('Add'),
                    sg.Button('Del'),
                ]
            ])],
            [sg.Frame('Sequence', [
                [
                    sg.Combo(tracker_names, default_value='kcf'),
                    sg.VerticalSeparator(pad=None),
                    sg.Text('BBox Scale:'),
                    sg.In('1.0', key='BboxScale', size=(5, 1))
                ],
                [sg.Listbox(values=classes, key='LabelList', enable_events=True, size=(51, len(classes)))],
                [
                    sg.Text('Start: {}', key='StartFrame'), sg.Button('Calc'),
                    sg.VerticalSeparator(pad=None),
                    sg.Text('Anchor: {}', key='AnchorFrame'),
                    sg.VerticalSeparator(pad=None),
                    sg.Text('End: {}', key='EndFrame'), sg.Button('Calc')
                ],
                [
                    sg.Text('Set:'),
                    sg.Button('  {  '),
                    sg.Button('  ⌂  '),
                    sg.Button('  }  '),
                ]
            ])],
            [sg.Frame('Preview', [
                [sg.T('Progress: {}/{}'.format(pageNo, pageCount), key='ProgressText', size=(30, 1), auto_size_text=True)],
                [sg.ProgressBar(pageCount, orientation='h', size=(48, 5), key='ProgressBar')],
                [sg.Slider(key='FrameSlider', orientation='h', size=(48, 15), disable_number_display=True)],
                [
                    
                    sg.Button(' ◄ '),
                    sg.Button('   ‖   '),
                    sg.Button(' ► '),
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

window = sg.Window('Track Label Tool', layout)

# frame (event) loop
while True:
    # tracker

    # video player
    if play:
        pass

    # GUI handler
    event, values = window.read()

    if event in (None, 'Cancel'):
        break
    elif event == 'ImagePath':
        try:
            # list image files
            image_path = values['ImagePath']
            image_files = os.listdir(image_path)
            window.FindElement('ImageList').Update(image_files)

            # calc page info
            pageNo = 0
            pageCount = math.ceil(len(image_files) / batch_size)

            pageOffset = 0

            page_nav()
        except:
            sg.Popup(sys.exc_info())
    elif event == 'AnnoPath':
        try:
            annos = read_annos(values['AnnoPath'])

            # select recorded label
            if len(values['ImageList']) > 0:
                selected_image = values['ImageList'][0]
                if image_files[0] in annos.keys():
                    window.FindElement('LabelList').SetValue([annos[selected_image]])
                else:
                    window.FindElement('LabelList').SetValue([classes[0]])
            
            # refresh grid
            for i in range(GRID_SIZE[0]):
                for j in range(GRID_SIZE[1]):
                    refresh_image(i, j)
        except:
            sg.Popup(sys.exc_info())
    elif event == 'ImageList':
        try:
            # we do NOT allow to select from ImageList
            img_offset = pageNo * batch_size + pageOffset
            img_filename = image_files[img_offset]

            window.FindElement('ImageList').SetValue([img_filename])
            window.FindElement('ImageList').Update(scroll_to_index=img_offset)
        except:
            sg.Popup(sys.exc_info())
    elif event.split('-')[0] == 'Image':
        if pageCount != 0:
            prevPageOffset = pageOffset

            _, i, j = event.split('-')

            pageOffset = GRID_SIZE[1] * int(i) + int(j)
            img_offset = pageNo * batch_size + pageOffset

            img_filename = image_files[img_offset]

            # refresh previously selected image
            if prevPageOffset != -1:
                prev_i = prevPageOffset // GRID_SIZE[1]
                prev_j = prevPageOffset % GRID_SIZE[1]

                refresh_image(prev_i, prev_j)

            # select image in ImageList
            window.FindElement('ImageList').SetValue([img_filename])
            window.FindElement('ImageList').Update(scroll_to_index=img_offset)

            # select recorded label, or apply current label
            selected_image = img_filename

            if selected_image in annos.keys():
                window.FindElement('LabelList').SetValue([annos[selected_image]])
            elif len(values['LabelList']) > 0:
                annos[selected_image] = values['LabelList'][0]

            # refresh selected image
            i = pageOffset // GRID_SIZE[1]
            j = pageOffset % GRID_SIZE[1]

            refresh_image(i, j)
    elif event == 'LabelList':
        img_offset = pageNo * batch_size + pageOffset
        img_filename = image_files[img_offset]

        # update internal status
        annos[img_filename] = values['LabelList'][0]

        # refresh
        i = pageOffset // GRID_SIZE[1]
        j = pageOffset % GRID_SIZE[1]

        refresh_image(i, j)
    elif event == 'Next' or event == 'Prev' or event == 'Save':
        try:
            # nav
            if event != 'Save':
                if event == 'Next':
                    if pageNo < pageCount-1:
                        pageNo += 1
                elif event == 'Prev':
                    if pageNo > 0:
                        pageNo -= 1

                pageOffset = 0

                page_nav()

            # save
            auto_save = values['AutoSave']

            if auto_save or event == 'Save':
                csv_file = values['AnnoPath']
                save_anno(annos, csv_file)
        except:
            sg.Popup(sys.exc_info())
    elif event == 'Expand':
        if len(values['LabelList']) > 0:
            ret = sg.PopupOKCancel(
                'Current label will be expanded to all unlabeled samples in this page. Are you sure?',
                title='Expand Comfirm'
            )
            
            if ret == 'OK':
                page_start = pageNo * batch_size
                page_filenames = image_files[page_start:page_start+batch_size]

                current_label = values['LabelList'][0]

                for filename in page_filenames:
                    if filename not in annos.keys():
                        annos[filename] = current_label

                page_nav()
    elif event == 'Clear':
            ret = sg.PopupOKCancel(
                'All label will be cleared in this page. Are you sure?',
                title='Clear Comfirm'
            )
            
            if ret == 'OK':
                page_start = pageNo * batch_size
                page_filenames = image_files[page_start:page_start+batch_size]

                for filename in page_filenames:
                    if filename in annos.keys():
                        annos.pop(filename)
                        
                page_nav()
    elif event == 'Statistics':
        total_count = len(image_files)
        class_count = {}

        for filename in annos.keys():
            if annos[filename] in class_count.keys():
                class_count[annos[filename]] += 1
            else:
                class_count[annos[filename]] = 1

        sg.Popup('total: {}\nclass: {}'.format(total_count, class_count), title='Statistics')

window.close()