import cv2
import numpy as np
import random

import CONFIG

class VisualizationHandler(object):
    """
    Handler for drawing

    """
    def __init__(self):
        super(VisualizationHandler, self).__init__()
        
        self.image      = None
        self.map_court  = None
        self.dashboard  = {}

    def set_image_and_map(self, image, map_court):
        '''
        Used for (re)loading image and map

        '''

        self.image      = image
        self.map_court  = map_court

    def draw_court_masks_on_image(self, court_masks, image_draw_court_mask, image_keypoints):

        for m, m_value in court_masks.items():

            # if 'basket' in m and image_draw_basket:        
            #     rgb_mask = self.get_color_mask(m_value, CONFIG.COURT_FEATURES_COLORS[m])
            #     self.image = cv2.addWeighted(self.image.astype(float), 1, rgb_mask.astype(float), 0.5, 0)

            if not 'basket' in m and image_draw_court_mask:
                rgb_mask = self.get_color_mask(m_value, CONFIG.COURT_FEATURES_COLORS[m])
                self.image = cv2.addWeighted(self.image.astype(np.float), 1, rgb_mask.astype(np.float), 1, 0)

        for k in image_keypoints[0]:
            x,y = k.astype(int)
            cv2.circle(self.image, tuple([x,y]), CONFIG.IMAGE_POINT_SIZE, (255,255,255), -1)

    def draw_person_on_image(self, person, color_person):

        for p,p_value in person.items():

            # Draw lines
            for l, l_value in CONFIG.PERSON_POSE_CONNECTIONS.items():

                for ll in l_value:

                    l_pos = 'pos_' + l
                    ll_pos = 'pos_' + ll

                    if l_pos in p_value.positions_image and ll_pos in p_value.positions_image:

                        x_l, y_l = p_value.positions_image[l_pos][0][0].astype(np.int)
                        x_ll, y_ll = p_value.positions_image[ll_pos][0][0].astype(np.int)
                        
                        # Choose color
                        if color_person == 'team':
                            cv2.line(self.image, (x_l, y_l), (x_ll, y_ll), p_value.color_team, 2)
                        elif color_person == 'random':
                            temp_color = CONFIG.PERSON_PLAYER_COLOR[random.randrange(0,len(CONFIG.PERSON_PLAYER_COLOR))]
                            cv2.line(self.image, (x_l, y_l), (x_ll, y_ll), temp_color, 2)
                        else:
                            cv2.line(self.image, (x_l, y_l), (x_ll, y_ll), p_value.color_unique, 2)

            # Draw dots
            for c, c_value in CONFIG.PERSON_POSE_COLORS.items():

                c_pos = 'pos_' + c

                if c_pos in p_value.positions_image:
                    x, y = p_value.positions_image[c_pos][0][0].astype(np.int)
                    cv2.circle(self.image, tuple([x,y]), CONFIG.IMAGE_POINT_SIZE, c_value, -1)

    def draw_person_on_map(self, person, color_person):

        # Draw players on map
        for p,p_value in person.items():

            if p_value.position_court is None:
                continue

            x, y = p_value.position_court[0][0].astype(np.int)

            center = tuple([x,y])

            # Only players draw text, https://stackoverflow.com/questions/55904418/draw-text-inside-circle-opencv
            if not 'REFEREE' in p:

                if color_person == 'team':
                    color_jersey = p_value.color_team
                elif color_person == 'unique':
                    color_jersey = p_value.color_unique
                else:
                    continue

                cv2.circle(self.map_court, center, CONFIG.TEXT_POINT_SIZE, color_jersey, -1)

                text = str(p_value.number)
                text_size, _ = cv2.getTextSize(text, CONFIG.TEXT_FACE, CONFIG.TEXT_SCALE, CONFIG.TEXT_THICKNESS)
                text_origin = (int(center[0] - text_size[0] / 2), int(center[1] + text_size[1] / 2))

                cv2.putText(self.map_court, text, text_origin, CONFIG.TEXT_FACE, CONFIG.TEXT_SCALE, p_value.color_number, CONFIG.TEXT_THICKNESS, cv2.LINE_AA)

            else:
                cv2.circle(self.map_court, center, CONFIG.MAP_POINT_SIZE, CONFIG.PERSON_REFEREE_COLOR, -1)

    def draw_basket_on_image(self, court_masks):
        
        rgb_mask = self.get_color_mask(court_masks['basket_ball'], CONFIG.COURT_FEATURES_COLORS['basket_ball'])
        self.image = cv2.addWeighted(self.image.astype(np.float), 1, rgb_mask.astype(np.float), 1, 0)  

    def draw_basket_on_map(self, person, possesion):

        if possesion is None:
            return

        if person[possesion].position_court is None:
            return

        x, y = person[possesion].position_court[0][0].astype(np.int)
        cv2.circle(self.map_court, (x,y), CONFIG.TEXT_POINT_SIZE + 1, CONFIG.COURT_FEATURES_COLORS['basket_ball'], 5)

    def draw_and_save(self, frame, person, court_masks, ball_possesion, image_keypoints,
        layout='image_map',
        image_draw_black_background=False, image_draw_court_mask=False, image_draw_basket=True, image_draw_person=True,
        color_person='team'):
        '''
        Save current frame as png.

        layout                      : str, ['image_map', 'image', 'map']

        image_draw_court_mask       : bool, if True draw court lines on image
        image_draw_black_background : bool, if True draw black background
        image_draw_basket           : bool, if True draw basket on image
        image_draw_person           : bool, if True draw person on image
        color_person                : str, ['random', 'player', 'team', ]
    
        '''

        # -------
        # Draw without rgb image
        if image_draw_black_background:
            self.image = np.zeros(self.image.shape)#.astype(int)

        # ------------------------------
        # Layouts
        if layout == 'image':

            if image_draw_court_mask:
                self.draw_court_masks_on_image(court_masks, image_draw_court_mask, image_keypoints)

            if image_draw_basket:
                self.draw_basket_on_image(court_masks)

            if image_draw_person:
                self.draw_person_on_image(person, color_person)

            out_image = self.image

        elif layout == 'map':

            if image_draw_basket:
                self.draw_basket_on_map(person, ball_possesion)

            if image_draw_person:
                self.draw_person_on_map(person, color_person)

            out_image = self.map_court
        
        else:

            if image_draw_court_mask:
                self.draw_court_masks_on_image(court_masks, image_draw_court_mask, image_keypoints)

            if image_draw_basket:
                self.draw_basket_on_image(court_masks)
                self.draw_basket_on_map(person, ball_possesion)

            if image_draw_person:
                self.draw_person_on_image(person, color_person)
                self.draw_person_on_map(person, color_person)

            # Prepare map court layout
            scale_percent = 40 # percent of original size
            width = int(self.map_court.shape[1] * scale_percent / 100)
            height = int(self.map_court.shape[0] * scale_percent / 100)
            map_court = cv2.resize(self.map_court, (width, height), interpolation = cv2.INTER_AREA)

            # Final layout is defined by image and map size
            h1, w1, c1 = self.image.shape
            h2, w2, c2 = map_court.shape
            h, w = h1+h2, max(w1, w2)
            w_shift = int((w-min(w1, w2))/2)

            out_image = np.zeros((h,w,c1))
            out_image[:h1,:w1, ] = self.image
            out_image[h1:h1+h2,w_shift:w2+w_shift, ] = map_court


        cv2.imwrite("../tmp/{}.png".format(frame), out_image)  

    def get_color_mask(self, mask, color):

        r = np.zeros_like(mask).astype(np.float)
        g = np.zeros_like(mask).astype(np.uint8)
        b = np.zeros_like(mask).astype(np.uint8)

        b[mask > 0], g[mask > 0], r[mask > 0] = color
        
        coloured_mask = np.stack([b, g, r], axis=2)
        
        return coloured_mask
