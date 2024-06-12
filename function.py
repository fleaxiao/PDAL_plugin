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

    ## Import the footprints from the predefinition
    # KICAD_VERSION = pcbnew.Version().split(".")[0]
    # fp_path = os.getenv("KICAD" + KICAD_VERSION + "_FOOTPRINT_DIR", default=None)
    # create_component(board, fp_path, "Capacitor_THT.pretty", "CP_Axial_L37.0mm_D20.0mm_P43.00mm_Horizontal", "C1", "47uF", x1, y1, x2, y2)
    # create_component(board, fp_path, "Capacitor_THT.pretty", "CP_Axial_L37.0mm_D16.0mm_P43.00mm_Horizontal", "C2", "47uF", x1, y1, x2, y2)
    # create_component(board, fp_path, "Diode_THT.pretty", "D_DO-201AE_P15.24mm_Horizontal", "D1", "Diode", x1, y1, x2, y2)
    # create_component(board, fp_path, "inductor_THT.pretty", "L_Radial_D21.0mm_P15.00mm_Vishay_IHB-2", "L1", "110uH", x1, y1, x2, y2)
    # create_component(board, fp_path, "Package_TO_SOT_THT.pretty", "TO-247-3_Vertical", "S1", "TO-247-3", x1, y1, x2, y2)
    # create_component(board, fp_path, "Connector_PinSocket_2.54mm.pretty", "PinSocket_1x05_P2.54mm_Vertical", "P1", "Signal", x1, y1, x2, y2)
    # create_component(board, fp_path, "Connector_Phoenix_GMSTB.pretty", "PhoenixContact_GMSTBVA_2,5_2-G_1x02_P7.50mm_Vertical", "P2", "Power Input", x1, y1, x2, y2)
    # create_component(board, fp_path, "Connector_Phoenix_GMSTB.pretty", "PhoenixContact_GMSTBVA_2,5_2-G_1x02_P7.50mm_Vertical", "P3", "Power Output", x1, y1, x2, y2)

    pcbnew.Refresh()

def random_placement():
    board: pcbnew.BOARD = pcbnew.GetBoard()

    x1 = 40
    y1 = 40
    x2 = 100
    y2 = 100

    for track in board.GetTracks():
        board.Delete(track)

    for module in board.GetFootprints():
        place_component(board, module, x1, y1, x2, y2)

    pcbnew.Refresh()

def pcb_record():
    board: pcbnew.BOARD = pcbnew.GetBoard()

    module_ref = list()
    module_pos_x = np.array([]).reshape(-1, 1)
    module_pos_y = np.array([]).reshape(-1, 1)
    module_angle = np.array([]).reshape(-1, 1)
    for module in board.GetFootprints():   
        module_ref_i, module_pos_x_i, module_pos_y_i, module_angle_i, _, _ = get_module_status(module)
        module_ref.append(module_ref_i)
        module_pos_x = np.append(module_pos_x, module_pos_x_i)
        module_pos_y = np.append(module_pos_y, module_pos_y_i)
        module_angle = np.append(module_angle, module_angle_i)
    module_status = {'Module Reference': module_ref, 'Position X': module_pos_x, 'Position Y': module_pos_y, 'Angle': module_angle}
    new_module_status = pd.DataFrame(module_status)
    new_module_status = new_module_status.sort_values(by = ['Module Reference'])    

    track_net = list()
    track_start_x = np.array([]).reshape(-1, 1)
    track_start_y = np.array([]).reshape(-1, 1)
    track_end_x = np.array([]).reshape(-1, 1)
    track_end_y = np.array([]).reshape(-1, 1)
    track_width = np.array([]).reshape(-1, 1)
    track_layer = list()
    num_tracks = sum(1 for track in board.GetTracks() if isinstance(track, pcbnew.PCB_TRACK) and not isinstance(track, pcbnew.PCB_VIA))
    if num_tracks == 0:
        track_net.append('None')
        track_start_x = np.append(track_start_x, None)
        track_start_y = np.append(track_start_y, None)
        track_end_x = np.append(track_end_x, None)
        track_end_y = np.append(track_end_y, None)
        track_width = np.append(track_width, None)
        track_layer.append('None')
    else:
        for track in board.GetTracks():
            if isinstance(track, pcbnew.PCB_TRACK) and not isinstance(track, pcbnew.PCB_VIA):
                track_net_i, track_start_x_i, track_start_y_i, track_end_x_i, track_end_y_i, track_width_i, track_layer_i = get_track_status(track)
                track_net.append(track_net_i)
                track_start_x = np.append(track_start_x, track_start_x_i)
                track_start_y = np.append(track_start_y, track_start_y_i)
                track_end_x = np.append(track_end_x, track_end_x_i)
                track_end_y = np.append(track_end_y, track_end_y_i)
                track_width = np.append(track_width, track_width_i)
                track_layer.append(track_layer_i)          
    track_status = {'Net':track_net, 'Start X': track_start_x, 'Start Y': track_start_y, 'End X': track_end_x, 'End Y': track_end_y, 'Width': track_width, 'Layer': track_layer}
    new_track_status = pd.DataFrame(track_status)
    new_track_status = new_track_status.sort_values(by = ['Net']) 

    via_net = list()
    via_pos_x = np.array([]).reshape(-1, 1)
    via_pos_y = np.array([]).reshape(-1, 1)
    via_diameter = np.array([]).reshape(-1, 1)
    num_vias = sum(1 for track in board.GetTracks() if isinstance(track, pcbnew.PCB_VIA))
    if num_vias == 0:
        via_net.append('None')
        via_pos_x = np.append(via_pos_x, None)
        via_pos_y = np.append(via_pos_y, None)
        via_diameter = np.append(via_diameter, None)
    else:
        for via in board.GetTracks():
            if isinstance(via, pcbnew.PCB_VIA):
                via_net_i, via_pos_x_i, via_pos_y_i, via_diameter_i = get_via_status(via)
                via_net.append(via_net_i)
                via_pos_x = np.append(via_pos_x, via_pos_x_i)
                via_pos_y = np.append(via_pos_y, via_pos_y_i)
                via_diameter = np.append(via_diameter, via_diameter_i)
    via_status = {'Net':via_net, 'Position X': via_pos_x, 'Position Y': via_pos_y, 'Diameter': via_diameter}
    new_via_status = pd.DataFrame(via_status)
    new_via_status = new_via_status.sort_values(by = ['Net']) 

    return new_module_status, new_track_status, new_via_status