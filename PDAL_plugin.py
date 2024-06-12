import pcbnew
import wx
import os
import numpy as np
import pandas as pd
import time
from datetime import datetime
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
        RECORD_DESIGN = {}

        board = pcbnew.GetBoard()
        work_dir, in_pcb_file = os.path.split(board.GetFileName())
        dlg = wx.FileDialog(self.frame, "Choose a record file", work_dir, '', "JSON files (*.json)|*.json", wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK: 
            filepath = dlg.GetPath() 
            with open(filepath, 'r') as file:
                data = json.load(file)
            RECORD_DESIGN = data
            self.text2.SetLabel('File is loaded.')
            self.text3.SetValue(os.path.basename(filepath))
        dlg.Destroy() 

    def play_action(self, event):

        self.text2.SetLabel('Reocrd is finished!')

    def label_action(self, event):

        self.text2.SetLabel('Reocrd is abandoned!')
        
    def Run(self):
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

        self.text2 = wx.StaticText(self.frame, label = 'PDAL is ready', pos = (50,155), size = (100,10), style=wx.ALIGN_CENTER)
        self.text2.SetFont(wx.Font(7, wx.DECORATIVE, wx.NORMAL, wx.BOLD))
        self.text2.SetForegroundColour(wx.RED)
        self.text2.SetWindowStyle(wx.ALIGN_CENTER)

        self.text3 = wx.TextCtrl(self.frame, pos = (180,50), size = (165,25), style = wx.TE_READONLY)

        self.text4 = wx.TextCtrl(self.frame, value="ID", pos = (180,110), size = (20,25))

        self.text5 = wx.TextCtrl(self.frame, value="Instructions", pos = (205,110), size = (135,25))

        # Create slider
        self.slider = wx.Slider(self.frame, value=10, minValue=10, maxValue=50, pos=(220,80), size=(110,25), style=wx.SL_HORIZONTAL)
        self.min_value_text = wx.StaticText(self.frame, label="10", pos=(210, 90))
        self.min_value_text.SetFont(wx.Font(7, wx.DECORATIVE, wx.NORMAL, wx.BOLD))
        self.max_value_text = wx.StaticText(self.frame, label="50", pos=(330, 90))
        self.max_value_text.SetFont(wx.Font(7, wx.DECORATIVE, wx.NORMAL, wx.BOLD))
        self.slider_value = wx.TextCtrl(self.frame, value = str(self.slider.GetValue()), pos=(180,80), size=(20,25), style=wx.TE_READONLY)
        self.slider.Bind(wx.EVT_SLIDER, self.on_slider_change)
        self.slider_value.SetWindowStyle(wx.ALIGN_CENTER)

        # Create button
        self.button1 = wx.Button(self.frame, label = 'Initialization', pos = (180,15), size=(260, 25))
        self.button1.Bind(wx.EVT_BUTTON, self.initialization)

        self.button2 = wx.Button(self.frame, label = 'Load', pos = (350,50), size=(90, 25))
        self.button2.Bind(wx.EVT_BUTTON, self.load_action)

        self.button3 = wx.Button(self.frame, label = 'Play', pos = (350,80), size=(45, 25))
        self.button3.Bind(wx.EVT_BUTTON, self.play_action)

        self.button4 = wx.Button(self.frame, label = 'Replay', pos = (395,80), size=(45, 25))
        self.button4.Bind(wx.EVT_BUTTON, self.play_action)

        self.button5 = wx.Button(self.frame, label = 'Label', pos = (350,110), size=(90, 25))
        self.button5.Bind(wx.EVT_BUTTON, self.label_action)

        self.button6 = wx.Button(self.frame, label = 'Output label file', pos = (180,140), size=(260, 25))
        self.button6.Bind(wx.EVT_BUTTON, self.initialization)

        # Create line
        self.line1 = wx.StaticLine(self.frame, pos=(185, 45), size=(240,1), style=wx.LI_HORIZONTAL)
        self.line2 = wx.StaticLine(self.frame, pos=(40, 172), size=(120,1), style=wx.LI_HORIZONTAL)
        self.line3 = wx.StaticLine(self.frame, pos=(185, 172), size=(240,1), style=wx.LI_HORIZONTAL)

        self.frame.Show()

        return

