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

class PDAL_plugin(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "PCB Design Action Labeler"
        self.category = "Import PCB actions"
        self.description = "Label the actions when designing PCB"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), 'icon.png')

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

    def play_action(self, event):
        global RECORD_DESIGN, SLICE

        if RECORD_DESIGN == {}:
            self.text2.SetLabel('Please load record file.')
            return
        self.step = int(self.slider.GetValue())
        if self.step > len(RECORD_DESIGN['Track']['Net']):
            self.step = len(RECORD_DESIGN['Track']['Net'])
        start = random.randrange(0, len(RECORD_DESIGN['Track']['Net']) - self.step + 1)
        SLICE = random_tailor(RECORD_DESIGN, start, self.step)
        self.text2.SetLabel('Playing...')
        record_play(SLICE, self.step)

        self.text2.SetLabel('Play is end.')

    def replay_action(self, event):
        global RECORD_DESIGN, SLICE

        if RECORD_DESIGN == {}:
            self.text2.SetLabel('Please load record file.')
            return
        self.text2.SetLabel('Replaying...')
        record_play(SLICE, self.step)

        self.text2.SetLabel('Replay is end.')

    def label_action(self, event):
        global SLICE, LABEL_DESIGN

        ID = int(self.text4.GetValue())
        INSTRUCTION = str(self.text5.GetValue())
        LABEL_DESIGN = label_slice(LABEL_DESIGN, SLICE, ID, INSTRUCTION)

        self.text2.SetLabel('Slice is labeled.')
    
    def save_action(self, event):
        global LABEL_DESIGN

        label_data = json.dumps(LABEL_DESIGN, indent=4)
        exist_filenname = os.path.basename(self.filepath)
        filename = exist_filenname.replace("record", "label")
        with open(filename, 'w') as file:
            file.write(label_data)

        LABEL_DESIGN = {}

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
        self.frame.SetSize(0,0,500,200)
        self.frame.SetBackgroundColour(wx.WHITE)

        displaySize = wx.DisplaySize()
        self.frame.SetPosition((10, displaySize[1] - self.frame.GetSize()[1]-100))

        # Set icon
        icon = wx.Icon(os.path.join(os.path.dirname(__file__), 'icon.ico'), wx.BITMAP_TYPE_ICO)
        self.frame.SetIcon(icon)

        # Set image
        image = wx.Image(os.path.join(os.path.dirname(__file__), 'tue.png'), wx.BITMAP_TYPE_ANY)
        image = image.Scale(100, 100, wx.IMAGE_QUALITY_HIGH)
        bitmap = wx.Bitmap(image)
        wx.StaticBitmap(self.frame, -1, bitmap, (50, 20))

        # Create text
        self.text1 = wx.StaticText(self.frame, label = 'PCB Design Action Labeler   Copyright \u00A9 fleaxiao', pos = (130,180))
        self.text1.SetFont(wx.Font(6, wx.DECORATIVE, wx.NORMAL, wx.BOLD))
        self.text1.SetForegroundColour(wx.LIGHT_GREY)

        self.text2 = wx.StaticText(self.frame, label = 'PDAL is ready', pos = (40,155), size = (120,10), style=wx.ALIGN_CENTER)
        self.text2.SetFont(wx.Font(7, wx.DECORATIVE, wx.NORMAL, wx.BOLD))
        self.text2.SetForegroundColour(wx.RED)
        self.text2.SetWindowStyle(wx.ALIGN_CENTER)

        self.text3 = wx.TextCtrl(self.frame, pos = (180,50), size = (165,25), style = wx.TE_READONLY)

        self.text4 = wx.TextCtrl(self.frame, value="ID", pos = (180,110), size = (30,25), style = wx.TE_CENTRE)

        self.text5 = wx.TextCtrl(self.frame, value="Instructions", pos = (212,110), size = (135,25))

        # Create slider
        self.slider = wx.Slider(self.frame, value=20, minValue=10, maxValue=50, pos=(229,80), size=(100,25), style=wx.SL_HORIZONTAL) #? MaxValue should be the length of the record file
        self.min_value_text = wx.StaticText(self.frame, label=str(self.slider.GetMin()), pos=(215, 90))
        self.min_value_text.SetFont(wx.Font(7, wx.DECORATIVE, wx.NORMAL, wx.BOLD))
        self.max_value_text = wx.StaticText(self.frame, label=str(self.slider.GetMax()), pos=(330, 90))
        self.max_value_text.SetFont(wx.Font(7, wx.DECORATIVE, wx.NORMAL, wx.BOLD))
        self.slider_value = wx.TextCtrl(self.frame, value = str(self.slider.GetValue()), pos=(180,80), size=(30,25), style=wx.TE_READONLY)
        self.slider.Bind(wx.EVT_SLIDER, self.on_slider_change)
        self.slider_value.SetWindowStyle(wx.ALIGN_CENTER)

        # Create button
        self.button1 = wx.Button(self.frame, label = 'Initialization', pos = (180,15), size=(272, 25))
        self.button1.Bind(wx.EVT_BUTTON, self.initialization)

        self.button2 = wx.Button(self.frame, label = 'Load', pos = (350,50), size=(102, 25))
        self.button2.Bind(wx.EVT_BUTTON, self.load_action)

        self.button3 = wx.Button(self.frame, label = 'Play', pos = (350,80), size=(50, 25))
        self.button3.Bind(wx.EVT_BUTTON, self.play_action)

        self.button4 = wx.Button(self.frame, label = 'Replay', pos = (402,80), size=(50, 25))
        self.button4.Bind(wx.EVT_BUTTON, self.replay_action)

        self.button5 = wx.Button(self.frame, label = 'Label', pos = (350,110), size=(102, 25))
        self.button5.Bind(wx.EVT_BUTTON, self.label_action)

        self.button6 = wx.Button(self.frame, label = 'Save label file', pos = (180,140), size=(272, 25))
        self.button6.Bind(wx.EVT_BUTTON, self.save_action)

        # Create line
        self.line1 = wx.StaticLine(self.frame, pos=(195, 45), size=(240,1), style=wx.LI_HORIZONTAL)
        self.line2 = wx.StaticLine(self.frame, pos=(40, 172), size=(120,1), style=wx.LI_HORIZONTAL)
        self.line3 = wx.StaticLine(self.frame, pos=(195, 172), size=(240,1), style=wx.LI_HORIZONTAL)

        self.frame.Show()

        return

