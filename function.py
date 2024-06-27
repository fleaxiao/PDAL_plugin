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

def record_play(SLICE, step, speed):
    board = pcbnew.GetBoard()
    for track in board.GetTracks():
        track.ClearSelected()
        board.Delete(track)
    for i in range(step):
        for module in board.GetFootprints():
            module.ClearSelected()
        for track in board.GetTracks():
            track.ClearSelected()
        for key, value in SLICE.items():
            if key == 'Module':
                for key, value in value.items():
                    module_ref = key
                    module_x = value['Position X'][i]
                    module_y = value['Position Y'][i]
                    module_angle = value['Angle'][i]
                    place_module(board, module_ref, module_x, module_y, module_angle)
                    if i > 0:
                        module_o = np.array([value['Position X'][i-1], value['Position Y'][i-1], value['Angle'][i-1]])
                        module_p = np.array([value['Position X'][i], value['Position Y'][i], value['Angle'][i]])
                        if not np.array_equal(module_o, module_p):
                            highlight_component = board.FindFootprintByReference(module_ref)
                            highlight_component.SetSelected()

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
                        if i > 0:
                            track_o = np.vstack([value['Start X'][i-1], value['Start Y'][i-1], value['End X'][i-1], value['End Y'][i-1], value['Layer'][i-1], value['Width'][i-1], value['Net'][i-1]])
                            track_p = np.vstack([value['Start X'][i], value['Start Y'][i], value['End X'][i], value['End Y'][i], value['Layer'][i], value['Width'][i], value['Net'][i]])
                            column_is_different = True
                            for k in range(track_o.shape[1]):
                                if np.array_equal(track_p[:,j], track_o[:,k]):
                                    column_is_different = False
                                    break
                            if column_is_different:
                                place_track(board, track_net[j], track_start_x[j], track_start_y[j], track_end_x[j], track_end_y[j], track_width[j], track_layer[j])  
                                highlight_track(board, pcbnew.VECTOR2I(pcbnew.wxPointMM(float(track_p[0,j]), float(track_p[1,j]))), pcbnew.VECTOR2I(pcbnew.wxPointMM(float(track_p[2,j]), float(track_p[3,j]))), track_p[4,j])

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
        time.sleep(speed)
        
def step_play(SLICE):
    board = pcbnew.GetBoard()
    for module in board.GetFootprints():
        module.ClearSelected()
    for track in board.GetTracks():
        track.ClearSelected()
    for key, value in SLICE.items():
        if key == 'Module':
            for key, value in value.items():
                module_ref = key
                module_x = value['Position X'][-1]
                module_y = value['Position Y'][-1]
                module_angle = value['Angle'][-1]
                place_module(board, module_ref, module_x, module_y, module_angle)

                module_o = np.array([value['Position X'][-2], value['Position Y'][-2], value['Angle'][-2]])
                module_p = np.array([value['Position X'][-1], value['Position Y'][-1], value['Angle'][-1]])
                if not np.array_equal(module_o, module_p):
                    highlight_component = board.FindFootprintByReference(module_ref)
                    highlight_component.SetSelected()

        elif key == 'Track':
            track_net = value['Net'][-1]
            track_start_x = value['Start X'][-1]
            track_start_y = value['Start Y'][-1]
            track_end_x = value['End X'][-1]
            track_end_y = value['End Y'][-1]
            track_width = value['Width'][-1]
            track_layer = value['Layer'][-1]
            if track_net == ['None']:
                break
            else:
                for j in range(len(track_net)):
                    track_o = np.vstack([value['Start X'][-2], value['Start Y'][-2], value['End X'][-2], value['End Y'][-2], value['Layer'][-2], value['Width'][-2], value['Net'][-2]])
                    track_p = np.vstack([value['Start X'][-1], value['Start Y'][-1], value['End X'][-1], value['End Y'][-1], value['Layer'][-1], value['Width'][-1], value['Net'][-1]])
                    column_is_different = True
                    for k in range(track_o.shape[1]):
                        if np.array_equal(track_p[:,j], track_o[:,k]):
                            column_is_different = False
                            break
                    if column_is_different:
                        place_track(board, track_net[j], track_start_x[j], track_start_y[j], track_end_x[j], track_end_y[j], track_width[j], track_layer[j])  
                        highlight_track(board, pcbnew.VECTOR2I(pcbnew.wxPointMM(float(track_p[0,j]), float(track_p[1,j]))), pcbnew.VECTOR2I(pcbnew.wxPointMM(float(track_p[2,j]), float(track_p[3,j]))), track_p[4,j])
        elif key == 'Via':
            via_net = value['Net'][-1]
            via_pos_x = value['Position X'][-1]
            via_pos_y = value['Position Y'][-1]
            via_diameter = value['Diameter'][-1]
            if via_net == ['None']:
                break
            else:
                for j in range(len(via_net)):
                    place_via(board, via_net[j], via_pos_x[j], via_pos_y[j], via_diameter[j])
    pcbnew.Refresh()

def label_slice(LABEL_DESIGN, SLICE, step, ID, INSTRUCTION):
    if LABEL_DESIGN == {}:
        LABEL_DESIGN = {'Footprint':{}, 'ID':[], 'Instruction':[], 'Initial State':{'Module':[],'Wire':[]}, 'Action':[],'Slice':[]}
    LABEL_DESIGN['Footprint'] = SLICE['Footprint'] #TODO: Footprint
    LABEL_DESIGN['ID'].append(ID)
    LABEL_DESIGN['Instruction'].append(INSTRUCTION)

    lebal = []
    wire_net = []
    for i in range(len(SLICE['Record']['Track']['Net'])):
        trake_net_o = SLICE['Record']['Track']['Net'][i]
        trake_start_x_o = SLICE['Record']['Track']['Start X'][i]
        trake_start_y_o = SLICE['Record']['Track']['Start Y'][i]
        trake_end_x_o = SLICE['Record']['Track']['End X'][i]
        trake_end_y_o = SLICE['Record']['Track']['End Y'][i]
        trake_width_o = SLICE['Record']['Track']['Width'][i]
        trake_layer_o = SLICE['Record']['Track']['Layer'][i]
        via_net_o = SLICE['Record']['Via']['Net'][i]
        via_pos_x_o = SLICE['Record']['Via']['Position X'][i]
        via_pos_y_o = SLICE['Record']['Via']['Position Y'][i]
        via_diameter_o = SLICE['Record']['Via']['Diameter'][i]
        trake_start_o = np.vstack([trake_start_x_o, trake_start_y_o, trake_layer_o, trake_width_o, trake_net_o])
        trake_end_o = np.vstack([trake_end_x_o, trake_end_y_o, trake_layer_o, trake_width_o, trake_net_o])
        via_o = np.vstack([via_pos_x_o, via_pos_y_o, via_diameter_o])

        number_track = len(trake_net_o)
        trake_start_o = find_via(trake_start_o, via_o)
        trake_end_o = find_via(trake_end_o, via_o)

        wires = []
        lebal = []
        for j in range(len(trake_net_o)):
            if j in lebal:
                continue
            else:
                wire = trake_start_o[:,j].reshape(-1,1)
                wire = np.hstack((wire, trake_end_o[:,j].reshape(-1,1)))
                lebal = lebal + [j]
                wire, lebal = find_connection(wire, number_track, trake_start_o, trake_end_o, lebal)
                wires.append(wire.tolist())
        wire_net.append(wires)

    LABEL_DESIGN['Initial State']['Module'].append({outer_key: {inner_key: inner_value[0] for inner_key, inner_value in outer_value.items() if inner_value} for outer_key, outer_value in SLICE['Record']['Module'].items()})
    LABEL_DESIGN['Initial State']['Wire'].append(wire_net[0])

    action = []
    step_action = []
    last_step_action = []
    for i in range(len(SLICE['Record']['Track']['Net']) - 1):
        for key, value in SLICE['Record']['Module'].items():
            module_ref = key
            module_o = np.array([value['Position X'][i], value['Position Y'][i], value['Angle'][i]])
            module_p = np.array([value['Position X'][i+1], value['Position Y'][i+1], value['Angle'][i+1]])
            if not np.array_equal(module_o, module_p):
               step_action.append([module_ref, (module_p - module_o).tolist()])

        wire_o = wire_net[i]
        wire_p = wire_net[i+1]
        for j in range(len(wire_o)):
            if not wire_o[j] in wire_p and wire_o[j][0] != [None, None]:
                step_action.append(['Delect Wire', wire_o[j]])  
        for j in range(len(wire_p)):
            if not wire_p[j] in wire_o and wire_p[j][0] != [None, None]:
                step_action.append(['Add Wire', wire_p[j]])    

        if not np.array_equal(last_step_action,step_action):
            last_step_action = step_action
        else:
           step_action.append(['None'])

        action.append(step_action)
        step_action = []
        last_step_action = []

    LABEL_DESIGN['Action'].append(action)
    action = []

    SLICE['Record']['Wire'] = wire_net
    LABEL_DESIGN['Slice'].append(SLICE['Record'])
    return LABEL_DESIGN