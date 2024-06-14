import pcbnew
import os
import numpy as np
import pandas as pd
import wx
import random
import pyautogui
import pygetwindow as gw
import time
from .tool import *

def pcb_init():
    board: pcbnew.BOARD = pcbnew.GetBoard()

    x1 = 40
    y1 = 40
    x2 = 100
    y2 = 100
    margin = 5
    originX = pcbnew.FromMM(x1-margin)  
    originY = pcbnew.FromMM(y1-margin)  
    endX = pcbnew.FromMM(x2+margin) 
    endY = pcbnew.FromMM(y2+margin)

    # Initialize the board
    for item in list(board.GetDrawings()):
        if isinstance(item, pcbnew.PCB_SHAPE) and item.GetLayer() == pcbnew.Edge_Cuts:
            board.Remove(item)
    rectmodule_angle = pcbnew.PCB_SHAPE(board)
    rectmodule_angle.SetShape(pcbnew.SHAPE_T_RECT)
    rectmodule_angle.SetStartX(originX)
    rectmodule_angle.SetStartY(originY)
    rectmodule_angle.SetEndX(endX)
    rectmodule_angle.SetEndY(endY)
    rectmodule_angle.SetLayer(pcbnew.Edge_Cuts)
    board.Add(rectmodule_angle)

    # Initialize the components
    ## Import the footprints from the schematic
    windows = gw.getWindowsWithTitle('PCB Editor')
    pcb_editor_window = None
    for window in windows:
        if window.title.endswith('PCB Editor'):
            pcb_editor_window = window
            break
    if pcb_editor_window:
        pcb_editor_window.activate()
    else:
        wx.MessageBox('Window is not found', 'Error', wx.OK | wx.ICON_ERROR)
    time.sleep(0.1)
    pyautogui.press('f8')
    time.sleep(0.1)
    pyautogui.press('enter')
    time.sleep(0.1)
    pyautogui.press('enter')
    time.sleep(0.1)
    pyautogui.press('enter')
    time.sleep(0.1)
    pyautogui.press('esc')

    pcbnew.Refresh()

def random_tailor(RECORD_DESIGN, start, step):
    if isinstance(RECORD_DESIGN, dict):
        return {k: random_tailor(v, start, step) for k, v in RECORD_DESIGN.items()}
    else:
        if len(RECORD_DESIGN) < step:
            return RECORD_DESIGN
        else:
            return RECORD_DESIGN[start:start+step]

def record_play(SLICE, step):
    board = pcbnew.GetBoard()
    for i in range(step):
        for track in board.GetTracks():
            board.Delete(track)
        for key, value in SLICE.items():
            if key == 'Module':
                for key, value in value.items():
                    module_ref = key
                    module_x = value['Position X'][i]
                    module_y = value['Position Y'][i]
                    module_angle = value['Angle'][i]
                    place_module(board, module_ref, module_x, module_y, module_angle)
            elif key == 'Track':
                track_net = value['Net'][i]
                track_start_x = value['Start X'][i]
                track_start_y = value['Start Y'][i]
                track_end_x = value['End X'][i]
                track_end_y = value['End Y'][i]
                track_width = value['Width'][i]
                track_layer = value['Layer'][i]
                if track_net == ['None']:
                    break
                else:
                    for j in range(len(track_net)):
                        place_track(board, track_net[j], track_start_x[j], track_start_y[j], track_end_x[j], track_end_y[j], track_width[j], track_layer[j])
            elif key == 'Via':
                via_net = value['Net'][i]
                via_pos_x = value['Position X'][i]
                via_pos_y = value['Position Y'][i]
                via_diameter = value['Diameter'][i]
                if via_net == ['None']:
                    break
                else:
                    for j in range(len(via_net)):
                        place_via(board, via_net[j], via_pos_x[j], via_pos_y[j], via_diameter[j])
        pcbnew.Refresh()
        time.sleep(0.5)

def label_slice(LABEL_DESIGN, SLICE, ID, INSTRUCTION):
    if LABEL_DESIGN == {}:
        LABEL_DESIGN = {'ID': [], 'Instruction': [], 'Slice': []}
    LABEL_DESIGN['ID'].append(ID)
    LABEL_DESIGN['Instruction'].append(INSTRUCTION)
    LABEL_DESIGN['Slice'].append(SLICE)
    return LABEL_DESIGN