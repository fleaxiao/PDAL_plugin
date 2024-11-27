import pcbnew
import wx
import os
import numpy as np
import pandas as pd
import random
import time
import threading
import json

from .function import *
from .tool import *
from .constant import *


class PDAL_plugin(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "PCB Design Action Labeler"
        self.category = "Import PCB actions"
        self.description = "Label the actions when designing PCB"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), 'images/icon.png')

    def initialization(self, event):
        pcb_init()
        self.text2.SetLabel('Environment is ready.')

    def on_slider_change(self, event):
        slider_value = self.slider.GetValue()
        self.slider_value.SetValue(str(slider_value))
    
    def load_action(self, event):
        global RECORD_DESIGN

        board = pcbnew.GetBoard()
        work_dir, in_pcb_file = os.path.split(board.GetFileName())
        dlg = wx.FileDialog(self.frame, "Choose a record file", work_dir, '', "JSON files (*.json)|*.json", wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK: 
            self.filepath = dlg.GetPath() 
            with open(self.filepath, 'r') as file:
                data = json.load(file)
            RECORD_DESIGN = data
            self.text2.SetLabel('File is loaded.')
            self.text3.SetValue(os.path.basename(self.filepath))
        dlg.Destroy() 

    def on_check_change(self, event):
        if self.new_check.IsChecked():
            print("Checkbox is checked.")

    def play_action(self, event):
        global RECORD_DESIGN, SLICE

        if RECORD_DESIGN == {}:
            self.text2.SetLabel('Please load record file.')
            return
        self.step = int(self.slider.GetValue())
        if self.step >= len(RECORD_DESIGN['Record']['Module']['C1']['Position X']):
            self.step = len(RECORD_DESIGN['Record']['Module']['C1']['Position X'])
        if self.checkbox1.IsChecked():
            # self.start = random.randrange(0, 10)
            self.start = 0
        else:
            self.start = random.randrange(0, len(RECORD_DESIGN['Record']['Module']['C1']['Position X']) - self.step + 1)
        SLICE = {'Record':{}, 'Footprint':{}, 'Constraint':{}}
        SLICE['Record'] = random_tailor(RECORD_DESIGN['Record'], self.start, self.step)
        SLICE['Footprint'] = RECORD_DESIGN['Footprint']
        SLICE['Constraint'] = {
            "Power Module": sorted(RECORD_DESIGN['Constraint']["Power Module"]),
            "Sensitive Module": sorted(RECORD_DESIGN['Constraint']["Sensitive Module"])
        }

        if self.checkbox2.IsChecked():
            self.speed = 1
        else:
            self.speed = 0.5
        self.text2.SetLabel('Playing...')
        record_play(SLICE['Record'], self.step, self.speed)

        self.text2.SetLabel(f'Play is end. {self.step} steps')

    def next_action(self, event):
        global RECORD_DESIGN, SLICE

        if self.step >= len(RECORD_DESIGN['Record']['Module']['C1']['Position X']) - self.start:
            self.text2.SetLabel('No more steps!')
        else:
            self.step = self.step + 1
            SLICE['Record'] = random_tailor(RECORD_DESIGN['Record'], self.start, self.step)
            step_play(SLICE['Record'])

            self.text2.SetLabel(f'Next step is shown. {self.step} steps')
    
    def back_action(self, event):
        global RECORD_DESIGN, SLICE

        if self.step == 2:
            self.text2.SetLabel('No more steps!')
        else:
            self.step = self.step - 1
            SLICE['Record'] = random_tailor(RECORD_DESIGN['Record'], self.start, self.step)
            step_play(SLICE['Record'])

            self.text2.SetLabel(f'Last step is shown. {self.step} steps')

    def replay_action(self, event):
        global RECORD_DESIGN, SLICE

        if RECORD_DESIGN == {}:
            self.text2.SetLabel('Please load record file.')
            return
        self.text2.SetLabel('Replaying...')

        if self.checkbox2.IsChecked():
            self.speed = 1
        else:
            self.speed = 0.5
        record_play(SLICE['Record'], self.step, self.speed)

        self.text2.SetLabel('Replay is end.')

    def label_action(self, event):
        global SLICE, LABEL_DESIGN

        ID = self.text4.GetValue()
        INSTRUCTION = self.text5.GetValue()
        LABEL_DESIGN = label_slice(LABEL_DESIGN, SLICE, ID, INSTRUCTION)

        self.number_label = int(self.text6.GetValue())
        self.number_label += 1
        self.text6.SetValue(str(self.number_label))
        self.text2.SetLabel('Slice is labeled.')
    
    def save_action(self, event):
        global LABEL_DESIGN
        
        exist_filenname = os.path.basename(self.filepath)
        base_filename = os.path.splitext(exist_filenname)[0]
        circuit_name = base_filename.split('_')[0]

        # json file
        label_data = json.dumps(LABEL_DESIGN, indent=4)
        filename = exist_filenname.replace("record", "label")
        with open(filename, 'w') as file:
            file.write(label_data)

        # image file
        if not os.path.exists(os.path.join(circuit_name,'Condition')):
            os.makedirs(os.path.join(circuit_name,'Condition'))
        if not os.path.exists(os.path.join(circuit_name,'Target')):
            os.makedirs(os.path.join(circuit_name,'Target'))
        save_image(LABEL_DESIGN, exist_filenname)

        LABEL_DESIGN = {}
        self.number_label = 0
        self.text6.SetValue(str(self.number_label))
        self.text2.SetLabel('Label file is saved.')
        
    def Run(self):
        global RECORD_DESIGN, LABEL_DESIGN
        RECORD_DESIGN = {}
        LABEL_DESIGN = {}

        board = pcbnew.GetBoard()
        work_dir, in_pcb_file = os.path.split(board.GetFileName())
        os.chdir(work_dir) # Change the working directory to the directory of the PCB file

        self.frame = wx.Frame(None, -1, style=wx.STAY_ON_TOP)
        self.frame.SetTitle("Design PCB Action Labeler")
        self.frame.SetSize(0,0,500,230)
        self.frame.SetBackgroundColour(wx.WHITE)

        displaySize = wx.DisplaySize()
        self.frame.SetPosition((10, displaySize[1] - self.frame.GetSize()[1]-100))

        # Set icon
        icon = wx.Icon(os.path.join(os.path.dirname(__file__), 'images/icon.ico'), wx.BITMAP_TYPE_ICO)
        self.frame.SetIcon(icon)

        # Set image
        image = wx.Image(os.path.join(os.path.dirname(__file__), 'images/tue.png'), wx.BITMAP_TYPE_ANY)
        image = image.Scale(100, 100, wx.IMAGE_QUALITY_HIGH)
        bitmap = wx.Bitmap(image)
        wx.StaticBitmap(self.frame, -1, bitmap, (50, 20))

        # Create text
        self.text1 = wx.StaticText(self.frame, label = 'PCB Design Action Labeler   Copyright \u00A9 fleaxiao', pos = (130,210))
        self.text1.SetFont(wx.Font(6, wx.DECORATIVE, wx.NORMAL, wx.BOLD))
        self.text1.SetForegroundColour(wx.LIGHT_GREY)

        self.text2 = wx.StaticText(self.frame, label = 'PDAL is ready', pos = (40,185), size = (120,10), style=wx.ALIGN_CENTER)
        self.text2.SetFont(wx.Font(7, wx.DECORATIVE, wx.NORMAL, wx.BOLD))
        self.text2.SetForegroundColour(wx.RED)
        self.text2.SetWindowStyle(wx.ALIGN_CENTER)

        self.text3 = wx.TextCtrl(self.frame, pos = (180,52), size = (202,25), style = wx.TE_READONLY)

        self.text4 = wx.TextCtrl(self.frame, value="ID", pos = (180,144), size = (66,25), style = wx.TE_CENTRE)

        self.text5 = wx.TextCtrl(self.frame, value="Instruction", pos = (248,144), size = (134,25), style = wx.TE_CENTRE)

        self.text6 = wx.TextCtrl(self.frame, value="0", pos = (180,172), size = (30,25), style = wx.TE_READONLY)
        self.text6.SetWindowStyle(wx.ALIGN_CENTER)

        # Create slider
        self.slider = wx.Slider(self.frame, value=50, minValue=1, maxValue=50, pos=(229,80), size=(200,25), style=wx.SL_HORIZONTAL) #? MaxValue should be the length of the record file
        self.min_value_text = wx.StaticText(self.frame, label=str(self.slider.GetMin()), pos=(220, 90))
        self.min_value_text.SetFont(wx.Font(7, wx.DECORATIVE, wx.NORMAL, wx.BOLD))
        self.min_value_text.SetWindowStyle(wx.ALIGN_CENTER)
        self.max_value_text = wx.StaticText(self.frame, label=str(self.slider.GetMax()), pos=(430, 90))
        self.max_value_text.SetFont(wx.Font(7, wx.DECORATIVE, wx.NORMAL, wx.BOLD))
        self.slider_value = wx.TextCtrl(self.frame, value = str(self.slider.GetValue()), pos=(180,80), size=(30,25), style=wx.TE_READONLY)
        self.slider.Bind(wx.EVT_SLIDER, self.on_slider_change)
        self.slider_value.SetWindowStyle(wx.ALIGN_CENTER)

        # Create button
        self.button1 = wx.Button(self.frame, label = 'Initialization', pos = (180,15), size=(272, 25))
        self.button1.Bind(wx.EVT_BUTTON, self.initialization)

        self.button2 = wx.Button(self.frame, label = 'Load', pos = (384,52), size = (66, 25))
        self.button2.Bind(wx.EVT_BUTTON, self.load_action)

        self.checkbox1 = wx.CheckBox(self.frame, label="Fix start", pos = (50, 131), size = (130, 18))
        self.checkbox1.SetFont(wx.Font(8, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))

        self.checkbox2 = wx.CheckBox(self.frame, label="Slow play", pos = (50, 152), size = (130, 18))
        self.checkbox2.SetFont(wx.Font(8, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))

        self.button3 = wx.Button(self.frame, label = 'Play', pos = (180,108), size=(66, 25))
        self.button3.Bind(wx.EVT_BUTTON, self.play_action)
        
        self.button4 = wx.Button(self.frame, label = 'Next', pos = (248,108), size=(66, 25))
        self.button4.Bind(wx.EVT_BUTTON, self.next_action)

        self.button5 = wx.Button(self.frame, label = 'Back', pos = (316,108), size=(66, 25))
        self.button5.Bind(wx.EVT_BUTTON, self.back_action)

        self.button6 = wx.Button(self.frame, label = 'Replay', pos = (384,108), size=(66, 25))
        self.button6.Bind(wx.EVT_BUTTON, self.replay_action)

        self.button7 = wx.Button(self.frame, label = 'Label', pos = (384,144), size=(66, 25))
        self.button7.Bind(wx.EVT_BUTTON, self.label_action)

        self.button8 = wx.Button(self.frame, label = 'Save label file', pos = (212,172), size=(240, 25))
        self.button8.Bind(wx.EVT_BUTTON, self.save_action)

        # Create line
        self.line1 = wx.StaticLine(self.frame, pos=(40, 202), size=(120,1), style=wx.LI_HORIZONTAL)
        self.line2 = wx.StaticLine(self.frame, pos=(195, 45), size=(240,1), style=wx.LI_HORIZONTAL)
        self.line3 = wx.StaticLine(self.frame, pos=(195, 138), size=(240,1), style=wx.LI_HORIZONTAL)
        self.line4 = wx.StaticLine(self.frame, pos=(195, 202), size=(240,1), style=wx.LI_HORIZONTAL)

        self.frame.Show()

        return