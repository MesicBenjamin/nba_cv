import os
import cv2
import random
import numpy as np
import scipy.ndimage as ndi

import utils

import CONFIG

class DataLoader(object):
    """
    Loading and preparing data for each frame.

    self.frames                 : List of all frame names
    self.frames_person_on_court : Dictionary with frame image name as a key and list of person on the court at this frame.
    self.frames_ball_posession  : Dictionary with frame image name as a key and player name who is in a ball possesion.

    """
    def __init__(self, path_data):
        super(DataLoader, self).__init__()

        self.path_masks     = os.path.join(path_data, 'masks')
        self.path_images    = os.path.join(path_data, 'images')
        self.path_map_court = os.path.join(path_data, 'map_court.png')

        # Load the frames and the list of all players, ball possesions, etc
        with open(os.path.join(self.path_masks, 'frames.txt')) as file:

            data = file.read().splitlines()

            self.frames = [f.split(', ')[0] for f in data]
            self.frames_person_on_court = {f.split(', ')[0]: f.split(', ')[2:] for f in data}
            self.frames_ball_posession  = {f.split(', ')[0]: f.split(', ')[1] for f in data}

    def get_frame_image(self, frame):
        '''
        Returns image for given frame.
        '''
        return cv2.imread(os.path.join(self.path_images, frame + '.jpg'))

    def get_map_court(self):
        '''
        Returns clean map of court.
        '''
        return cv2.imread(self.path_map_court)

    def get_masks_court(self, frame):

        '''
        Returns dictionary with court feature masks for given frame.
        '''

        masks_court = {f: cv2.imread(os.path.join(self.path_masks, 'court', f, 'mask', frame + '.png'))[:,:,0]
            for f in CONFIG.COURT_FEATURES if 'DS' not in f}

        # DIRTY Hack
        if 'line_court_center' in masks_court:

            _,thresh = cv2.threshold(masks_court['line_court_center'], 0.5, 255, cv2.THRESH_BINARY)
            contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            number_of_objects_in_image= len(contours)
            
            if number_of_objects_in_image == 1:
                # print ("The number of objects in this image: ", str(number_of_objects_in_image))
                masks_court['line_court_center'] = np.zeros(masks_court['line_court_center'].shape)

        return masks_court

    def get_masks_person(self, frame):

        '''
        Returns dictionary with person masks for given frame.
        '''

        person = self.frames_person_on_court[frame]

        masks_person = {}
        
        for p in person:

            masks = [f for f in os.listdir(os.path.join(self.path_masks, 'person', p)) if 'DS' not in f]

            for m in masks:

                if not os.path.exists(os.path.join(self.path_masks, 'person', p, m, frame + '.png')):
                    continue

                masks_person['_'.join([p,m])] = cv2.imread(os.path.join(self.path_masks, 'person', p, m, frame + '.png'))[:,:,0]

        return masks_person

class GameHandler(object):
    """
    """
    def __init__(self):
        super(GameHandler, self).__init__()

        self.person = {}

        self.reset()   

    def reset(self):

        '''
        Reset all game states
        '''

        self.masks = {'court':{}, 'person':{}}

        self.ball_possesion = None

        self.homography = None

        for p, p_value in self.person.items():
            p_value.reset()

    def compute_homography(self):
        '''
        Compute homography mapping between court on a map and image
        '''
        
        self.map_keypoints_ordered, self.image_keypoints_ordered = utils.get_matched_keypoints(self.masks['court'], CONFIG.COURT_KEYPOINTS)

        h, status = cv2.findHomography(self.map_keypoints_ordered, self.image_keypoints_ordered)
        
        self.homography = h

    def compute_person_position_on_image(self, person):

        '''
        For a given list of players in this frame computes pose
        '''        

        # Add person if not in the dictionary
        for p in person:

            if p not in self.person:
                self.person[p] = Person(p)

        # Add masks
        for p, p_value in self.person.items():

            # Check who is playing and who is not
            if p not in person and 'REFEREE' not in p:
                p_value.playing = False

            if 'REFEREE' not in p and p_value.playing == False and p in person:
                p_value.playing
            
            # Update pose masks and position
            for m, m_value in self.masks['person'].items():

                if p not in m:
                    continue

                m_name = m.split(p + '_')[1]

                # None if no position
                if np.sum(m_value) == 0:

                    # Assumption that head is there, estimate from head pos (for this scene it is)
                    if m_name == 'pos':
                        x_head, y_head = ndi.center_of_mass(self.masks['person']['{}_pos_head'.format(p)])
                        pos = (1.3*x_head + 42.1, y_head)
                        p_value.positions_image[m_name] = np.array((pos[1], pos[0])).reshape(-1, 1, 2).astype(np.float32)

                else:
                    pos = ndi.center_of_mass(m_value)
                    p_value.positions_image[m_name] = np.array((pos[1], pos[0])).reshape(-1, 1, 2).astype(np.float32)

    def compute_person_position_on_court(self):

        for p, p_value in self.person.items():

            if not 'pos' in p_value.positions_image:
                continue

            p_value.position_court = cv2.perspectiveTransform(p_value.positions_image['pos'], np.linalg.inv(self.homography))

    def compute_ball_possesion(self, possesion):
        
        if 'None' in possesion:
            self.ball_possesion  = None
        else:
            self.ball_possesion  = possesion.replace('ball_', '')

class Person(object):
    """
    """
    def __init__(self, ID):
        super(Person, self).__init__()

        self.reset()

        self.name = ID

        self.number = CONFIG.PERSON_JERSEY_NUMBER[ID]

        # Player section: add team and player color
        if 'REFEREE' in ID:
            self.color = CONFIG.PERSON_REFEREE_COLOR

        else:

            self.playing = True

            self.team, self.name = ID.split('_')
            self.color_unique   = CONFIG.PERSON_PLAYER_COLOR[random.randrange(0,len(CONFIG.PERSON_PLAYER_COLOR))]
            self.color_team     = CONFIG.PERSON_TEAM_COLOR_JERSEY[self.team]
            self.color_number   = CONFIG.PERSON_TEAM_COLOR_NUMBER[self.team]

    def reset(self):

        self.position_court     = None
        # Dictionary with all the masks
        self.masks              = {}
        # Dictionary of image positions for each body part
        self.positions_image    = {}
        
        self.map_keypoints_ordered, self.image_keypoints_ordered = [], []
