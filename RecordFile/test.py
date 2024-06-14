import numpy as np 
import pandas as pd
import json
import random

def get_last_level_slice(d, start, step):
    if isinstance(d, dict):
        return {k: get_last_level_slice(v, start, step) for k, v in d.items()}
    else:
        return d[start:start+step]

def record_play(SLICE, step):
    for i in range(step):
        for key, value in SLICE.items():
            if key == 'Module':
                for key, value in value.items():
                    module_ref = key
                    module_x = value['Position X'][i]
                    module_y = value['Position Y'][i]
                    module_angle = value['Angle'][i]
                    print(module_ref, module_x, module_y, module_angle)
            # if key == 'Track':
            #     track_net = value['Net'][i]
            #     track_start_x = value['Start X'][i]
            #     track_start_y = value['Start Y'][i]
            #     track_end_x = value['End X'][i]
            #     track_end_y = value['End Y'][i]
            #     track_width = value['Width'][i]
            #     track_layer = value['Layer'][i]
            #     print(track_net, track_start_x, track_start_y, track_end_x, track_end_y, track_width, track_layer)
            #     if track_net == ['None']:
            #         break
            #     else:
            #         for j in range(len(track_net)):
                        
 
filepath = 'C:/Users/20234635/OneDrive - TU Eindhoven/Desktop/Code/PCB_Design/RecordFile/pcb_record.json'
with open(filepath, 'r') as file:
    data = json.load(file)
RECORD_DESIGN = data

step = 2
items = list(RECORD_DESIGN['Module'].items())
start = random.randrange(0, len(RECORD_DESIGN['Track']['Net']) - step + 1)
SLICE = get_last_level_slice(RECORD_DESIGN, start, step)

# print(SLICE['Via'])
record_play(SLICE,step)



