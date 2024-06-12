import pandas as pd
import numpy as np
import json


track_status = {'Start X': ['hhh','aaa'], 'Start Y': [0,1], 'End X': [0,1], 'End Y': [0,1]}
new_track_status = pd.DataFrame(track_status)
new_track_status = new_track_status.sort_values(by = ['Start X']) 

RECORD_DESIGN = {'Module':{},'Track':{'Start X': [], 'Start Y': [], 'End X': [], 'End Y': []}}
RECORD_DESIGN['Track']['Start X'].append(new_track_status['Start X'].tolist())
# RECORD_DESIGN['Track']['Start Y'].append(new_track_status['Start Y'].tolist())
# RECORD_DESIGN['Track']['End X'].append(new_track_status['End X'].tolist())
# RECORD_DESIGN['Track']['End Y'].append(new_track_status['End Y'].tolist)
record_data = json.dumps(RECORD_DESIGN, indent=4)
print(record_data)