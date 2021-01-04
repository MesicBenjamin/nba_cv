# Colors are in BGR
# ------------------------

COURT_FEATURES = [
    'basket_left', 'basket_right', 'basket_ball',
    'line_3pt_right', 'line_3pt_left', 
    'line_court_left', 'line_court_right', 'line_court_center', 'line_court_top', 'line_court_bottom',
    'line_foul_bottom', 'line_foul_top', 'line_foul_left', 'line_foul_right'
]

COURT_FEATURES_COLORS = { 
    'basket_left'       : [114, 128, 250],
    'basket_right'      : [114, 128, 250], 
    'basket_ball'       : [0, 69, 255],
    'line_3pt_right'    : [0, 255, 0],
    'line_3pt_left'     : [0, 0, 255], 
    'line_court_left'   : [255, 0, 0],
    'line_court_right'  : [0, 255, 255], 
    'line_court_center' : [255, 255, 0], 
    'line_court_top'    : [255, 0, 255], 
    'line_court_bottom' : [80, 70, 180],
    'line_foul_bottom'  : [250, 80, 190], 
    'line_foul_top'     : [245, 145, 50], 
    'line_foul_left'    : [70, 150, 250], 
    'line_foul_right'   : [50, 190, 190]   
}

COURT_KEYPOINTS = {
    'values' : {
        '01' : [151.5, 82],
        '02' : [151.5, 314.5],
        '03' : [151.5, 535.5],
        '04' : [151.5, 766.5],
        '05' : [415.5, 82],
        '06' : [415.5, 314.5],
        '07' : [415.5, 535.5],
        '08' : [415.5, 766.5],
        '09' : [536.5, 314.5],
        '10' : [536.5, 535.5],
        '11' : [795.5, 82],
        '12' : [795.5, 314.5],
        '13' : [795.5, 535.5],
        '14' : [795.5, 766.5],
        '15' : [1056.5, 314.5],
        '16' : [1056.5, 535.5],
        '17' : [1177.5, 82],
        '18' : [1177.5, 314.5],
        '19' : [1177.5, 535.5],
        '20' : [1177.5, 766.5],
        '21' : [1441.5, 82],
        '22' : [1441.5, 314.5],
        '23' : [1441.5, 535.5],
        '24' : [1441.5, 766.5],
    },

    'pairs' : {
        '01' : ['line_court_top', 'line_court_left'],
        '02' : ['line_foul_top','line_court_left'],
        '03' : ['line_foul_bottom', 'line_court_left'],
        '04' : ['line_court_bottom', 'line_court_left'],
        
        '05' : ['line_court_top', 'line_foul_left'],
        '06' : ['line_foul_top', 'line_foul_left'],
        '07' : ['line_foul_bottom', 'line_foul_left'],
        '08' : ['line_court_bottom', 'line_foul_left'],
        
        '09' : ['line_3pt_left', 'line_foul_top'],
        '10' : ['line_3pt_left', 'line_foul_bottom'], 
        
        '11' : ['line_court_top', 'line_court_center'],
        '12' : ['line_foul_top', 'line_court_center'],
        '13' : ['line_foul_bottom', 'line_court_center'],
        '14' : ['line_court_bottom', 'line_court_center'],
        
        '15' : ['line_3pt_right', 'line_foul_top'],
        '16' : ['line_3pt_right', 'line_foul_bottom'],
        
        '17' : ['line_court_top','line_foul_right'],
        '18' : ['line_foul_top', 'line_foul_right'],        
        '19' : ['line_foul_bottom', 'line_foul_right'],
        '20' : ['line_court_bottom', 'line_foul_right'],

        '21' : ['line_court_top', 'line_court_right'],
        '22' : ['line_foul_top', 'line_court_right'],        
        '23' : ['line_foul_bottom', 'line_court_right'],
        '24' : ['line_court_bottom', 'line_court_right']
        }
}

# ------------------------
PERSON_JERSEY_NUMBER = {
    'CLE_James'     : 23, 
    'CLE_Smith'     : 5, 
    'CLE_Love'      : 0, 
    'CLE_Jefferson' : 24, 
    'CLE_Irving'    : 2, 
    'GS_Barnes'     : 40, 
    'GS_Curry'      : 30, 
    'GS_Green'      : 23, 
    'GS_Iguodala'   : 9, 
    'GS_Thompson'   : 11, 
    'REFEREE_13'    : 13, 
    'REFEREE_24'    : 24, 
    'REFEREE_43'    : 43    
}

PERSON_POSE_CONNECTIONS = {
    'head'              : ['chest'],
    'chest'             : ['shoulder_left', 'shoulder_right', 'hip_left', 'hip_right'],
    'shoulder_left'     : ['elbow_left'],
    'shoulder_right'    : ['elbow_right'],
    'elbow_left'        : ['hand_left'],
    'elbow_right'       : ['hand_right'],
    'hip_left'          : ['knee_left'],
    'hip_right'         : ['knee_right'],
    'knee_left'         : ['foot_left'],
    'knee_right'        : ['foot_right']
}

PERSON_REFEREE_COLOR = [128,128,128]
PERSON_PLAYER_COLOR = [
    [0, 255, 0],
    [0, 0, 255],
    [255, 0, 0],
    [0, 255, 255],
    [255, 255, 0],
    [255, 0, 255],
    [80, 70, 180],
    [250, 80, 190],
    [245, 145, 50],
    [70, 150, 250],
    [50, 190, 190]
]

PERSON_TEAM_COLOR_JERSEY  = {
    'CLE': [51,51,51],
    'GS': [200, 200, 200]
}
PERSON_TEAM_COLOR_NUMBER  = {
    'CLE': [220, 220, 220],
    'GS': [10, 10, 10]
}

# Pose colors https://excelatfinance.com/xlf/xlf-colors-1.php
PERSON_POSE_COLORS = {
    'chest'         :[153, 102, 102],
    'shoulder_left' :[0, 102, 255],
    'shoulder_right':[0, 153, 255],
    'elbow_left'    :[0, 204, 255],
    'elbow_right'   :[0, 204, 153],
    'foot_left'     :[204, 204, 51],
    'foot_right'    :[255, 102, 51],
    'knee_left'     :[153, 204, 255],
    'knee_right'    :[255, 153, 204],
    'hip_left'      :[204, 153, 255],
    'hip_right'     :[255, 204, 153],  
    'hand_left'     :[153, 255, 255],
    'hand_right'    :[204, 255, 204],
    'head'          :[255, 255, 204]
}

# ------------------------
IMAGE_POINT_SIZE = 3
MAP_POINT_SIZE = 10
import cv2
TEXT_FACE = cv2.FONT_HERSHEY_DUPLEX
TEXT_SCALE = 1.0
TEXT_THICKNESS = 1
TEXT_POINT_SIZE = 25