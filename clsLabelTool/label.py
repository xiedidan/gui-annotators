import os
import sys
import io
import base64

from PIL import Image
import pandas as pd
import PySimpleGUI as sg

# global
class_file = './predefined_classes.txt'
classes = []
image_files = []
annos = {}

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

def jpg_2_png(file_path):
    img_data = Image.open(file_path)
    png_buffer = io.BytesIO()

    img_data.save(png_buffer, format='PNG')

    return png_buffer.getvalue()

def read_img(file_path):
    img = open(file_path, 'rb+')
    img = base64.b64encode(img.read())

    return img

img = read_img('./bg.png')

sg.ChangeLookAndFeel('Dark')

layout = [
    [
        sg.Image(data=img, key='Image', size=(512,512)),
        sg.VerticalSeparator(pad=None),
        sg.Column([
            [sg.Frame('Paths:', [
                [sg.In('Image Directory', key='ImagePath', enable_events=True), sg.FolderBrowse()],
                [sg.In('Anno File', key='AnnoPath', enable_events=True), sg.FileBrowse(file_types=(('ALL Files', '*.*'), ('CSV', '*.csv')),)]
            ])],
            [sg.Frame('Image Files:', [
                    [sg.Listbox(values=[], key='ImageList', enable_events=True, size=(51, 8))]
            ])],
            [sg.Frame('Select Label:', [
                    [sg.Listbox(values=classes, key='LabelList', size=(51, 8))]
            ])],
            [sg.Frame('Control:', [
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
            window.FindElement('ImageList').SetValue([image_files[0]])

            # select recorded label
            selected_image = image_files[0]
            if image_files[0] in annos.keys():
                window.FindElement('LabelList').SetValue([annos[selected_image]])
            else:
                window.FindElement('LabelList').SetValue([classes[0]])

            # show selected image
            image_file = os.path.join(values['ImagePath'], image_files[0])
            img = jpg_2_png(image_file)

            window.FindElement('Image').Update(data=img, size=(512, 512))
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
        except:
            sg.Popup(sys.exc_info())
    elif event == 'ImageList':
        try:
            # show selected image
            image_file = os.path.join(values['ImagePath'], values['ImageList'][0])
            img = jpg_2_png(image_file)

            window.FindElement('Image').Update(data=img, size=(512, 512))

            # select recorded label
            selected_image = values['ImageList'][0]
            if selected_image in annos.keys():
                window.FindElement('LabelList').SetValue([annos[selected_image]])
        except:
            sg.Popup(sys.exc_info())
    elif event == 'Next' or event == 'Prev' or event == 'Save':
        try:
            current_image = values['ImageList'][0]
            current_class = values['LabelList'][0]
            current_index = image_files.index(current_image)
            incoming_index = 0

            if event != 'Save':
                if event == 'Next':
                    if current_index != len(image_files)-1:
                        incoming_index = current_index + 1
                    else:
                        incoming_index = current_index
                elif event == 'Prev':
                    if current_index != 0:
                        incoming_index = current_index - 1
                    else:
                        incoming_index = current_index

                incoming_image = image_files[incoming_index]

                # select incoming image
                window.FindElement('ImageList').SetValue([incoming_image])
                window.FindElement('ImageList').Update(scroll_to_index=incoming_index)

                # show selected image
                image_file = os.path.join(values['ImagePath'], incoming_image)
                img = jpg_2_png(image_file)

                window.FindElement('Image').Update(data=img, size=(512, 512))

                # select recorded label
                selected_image = incoming_image
                if selected_image in annos.keys():
                    window.FindElement('LabelList').SetValue([annos[selected_image]])

            # update annos
            annos[current_image] = current_class

            # save current
            auto_save = values['AutoSave']

            if auto_save or event == 'Save':
                csv_file = values['AnnoPath']

                save_anno(annos, csv_file)
        except:
            sg.Popup(sys.exc_info())

    # sg.Popup(event, values)

window.close()
