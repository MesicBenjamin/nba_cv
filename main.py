# This code version is designed for prepared masks from Blender
# python main.py --path_data '/Users/benjamin/Documents/data/basketball/2016_finals'
# docker run -v $PWD:/temp/ jrottenberg/ffmpeg:3.2-scratch -framerate 20 -start_number 800 -i temp/%06d.png -vcodec mpeg4 -b 10000k temp/movie.mp4

import argparse

import game
import visual

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--path_data", type=str, help="Path to images, masks, list of frames.", required=True)
    parser.add_argument("--every_nth_frame", type=int, default=1, help="Analyze every n-th frame.", required=False)
    args = parser.parse_args()

    # -------------------------------
    # Load images, masks, etc
    data_loader = game.DataLoader(args.path_data)

    # Handle everything in the game
    game_handler = game.GameHandler()

    # Prepare visulization handler
    visual_handler = visual.VisualizationHandler()

    # -------------------------------
    # Main frame loop
    for f in data_loader.frames:

        if not int(f) % args.every_nth_frame == 0:
            continue

        # if int(f) < 1260:
        #     continue

        print('Frame {}'.format(f))

        # Get all court feature masks for this frame
        game_handler.masks['court'] = data_loader.get_masks_court(f)
        # Compute homography mapping between court on map and image
        game_handler.compute_homography()
        
        # Get person masks and compute position of each person on image
        game_handler.masks['person'] = data_loader.get_masks_person(f)
        game_handler.compute_person_position_on_image(data_loader.frames_person_on_court[f])

        # Compute person court positions given h mapping
        game_handler.compute_person_position_on_court()

        # Ball position
        game_handler.compute_ball_possesion(data_loader.frames_ball_posession[f])

        # -------------------------------------
        # VIZUALIZATION
        # Load image frame and clean copy of court map
        image     = data_loader.get_frame_image(f)
        map_court = data_loader.get_map_court()

        visual_handler.set_image_and_map(image, map_court)
        visual_handler.draw_and_save(f, game_handler.person, game_handler.masks['court'], game_handler.ball_possesion, game_handler.image_keypoints_ordered)

        # --------------------
        game_handler.reset()