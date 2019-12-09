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

def resize_with_pad(image, height=THUMB_SIZE[1], width=THUMB_SIZE[0], fill=[255, 255, 255]):

    def get_padding_size(image):
        h, w, _ = image.shape
        longest_edge = max(h, w)
        top, bottom, left, right = (0, 0, 0, 0)
        if h < longest_edge:
            dh = longest_edge - h
            top = dh // 2
            bottom = dh - top
        elif w < longest_edge:
            dw = longest_edge - w
            left = dw // 2
            right = dw - left
        else:
            pass
        return top, bottom, left, right

    top, bottom, left, right = get_padding_size(image)
    constant = cv2.copyMakeBorder(image, top , bottom, left, right, cv2.BORDER_CONSTANT, value=fill)

    resized_image = cv2.resize(constant, (height, width))

    return resized_image 

def jpg_2_png(file_path, size=THUMB_SIZE, highlight_color=None, class_name=None, class_color=None):
    img_data = Image.open(file_path).convert('RGB')

    # original size
    w, h = img_data.size
    
    img_arr = np.array(img_data)
    img_arr = resize_with_pad(img_arr, height=size[1], width=size[0])
    img_data = Image.fromarray(img_arr)

    draw = ImageDraw.Draw(img_data)

    if highlight_color:
        h_color = ImageColor.getrgb(highlight_color)
        draw.rectangle([0, 0, size[0]-1, size[1]-1], outline=h_color, width=2)

    if class_name:
        draw.text((2, 2), class_name, fill=class_color)

    draw.text((2, size[1]-12), '({},{})'.format(w, h), fill=INFO_COLOR)

    png_buffer = io.BytesIO()
    img_data.save(png_buffer, format='PNG')

    return png_buffer.getvalue()

def refresh_image(i, j):
    batch_offset = i * GRID_SIZE[1] + j
    overall_offset = pageNo * batch_size + batch_offset

    if overall_offset < len(image_files):
        # highlight selected
        if batch_offset == pageOffset:
            highlight_color = HIGHLIGHT_COLOR
        else:
            highlight_color = None

        # class label
        image_filename = image_files[overall_offset]
        if image_filename in annos.keys():
            class_name = annos[image_filename]
            color_index = classes.index(class_name)
            class_color = CLASS_COLORS[color_index]
        else:
            class_name = None
            class_color = None

        image = jpg_2_png(
            os.path.join(values['ImagePath'], image_filename),
            highlight_color=highlight_color,
            class_name=class_name,
            class_color=class_color
        )
        window.FindElement('Image-{}-{}'.format(i, j)).Update(data=image, size=THUMB_SIZE)
    else:
        window.FindElement('Image-{}-{}'.format(i, j)).Update(data=img, size=THUMB_SIZE)
    
def page_nav():
    img_offset = pageNo * batch_size + pageOffset
    img_filename = image_files[img_offset]

    # update progress bar
    window.FindElement('ProgressText').Update('Progress: {}/{}'.format(pageNo, pageCount-1))
    window.FindElement('ProgressBar').UpdateBar(pageNo, max=pageCount-1)

    # select in ImageList
    window.FindElement('ImageList').SetValue([img_filename])
    window.FindElement('ImageList').Update(scroll_to_index=img_offset)

    # refresh grid
    for i in range(GRID_SIZE[0]):
        for j in range(GRID_SIZE[1]):
            refresh_image(i, j)

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
            [sg.Frame('Paths:', [
                [sg.In('Image Directory', key='ImagePath', enable_events=True), sg.FolderBrowse()],
                [sg.In('Anno File', key='AnnoPath', enable_events=True), sg.FileBrowse(file_types=(('ALL Files', '*.*'), ('CSV', '*.csv')),)]
            ])],
            [sg.Frame('Image Files:', [
                [sg.Listbox(values=[], key='ImageList', enable_events=True, size=(51, 15))]
            ])],
            [sg.Frame('Select Label:', [
                [sg.Button('Expand'), sg.Button('Clear'), sg.Button('Statistics')],
                [sg.Listbox(values=classes, key='LabelList', enable_events=True, size=(51, len(classes)))]
            ])],
            [sg.Frame('Control:', [
                [sg.T('Progress: {}/{}'.format(pageNo, pageCount), key='ProgressText', size=(30, 1), auto_size_text=True)],
                [sg.ProgressBar(pageCount, orientation='h', size=(48, 20), key='ProgressBar')],
                [sg.Checkbox('Auto Save (ONLY for Prev / Next)', key='AutoSave', default=True)],
                [sg.Button('Prev'), sg.Button('Save'), sg.Button('Next')]
            ])]
        ])
    ]
]

window = sg.Window('CLS Label Tool', layout)

while True:
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
