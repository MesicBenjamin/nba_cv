import cv2
import numpy as np

# ----------------------------------

def get_image_mask_keypoints(masks, map_keypoints):
    """ 
    Returns dictionary of keypoints and their location on image.
    """

    keypoints = {}

    for keypoint, keypoint_mask_pair in map_keypoints['pairs'].items():

        coordinate = None

        if 'line_3pt_left' in keypoint_mask_pair:
            if '3pt' in keypoint_mask_pair[0]:
                coordinate = get_ellipse_line_intersection_mask(masks[keypoint_mask_pair[1]], masks[keypoint_mask_pair[0]], 'left')
            else:
                coordinate = get_ellipse_line_intersection_mask(masks[keypoint_mask_pair[0]], masks[keypoint_mask_pair[1]], 'left')

        elif 'line_3pt_right' in keypoint_mask_pair:

            if '3pt' in keypoint_mask_pair[0]:
                coordinate = get_ellipse_line_intersection_mask(masks[keypoint_mask_pair[1]], masks[keypoint_mask_pair[0]], 'right')
            else:
                coordinate = get_ellipse_line_intersection_mask(masks[keypoint_mask_pair[0]], masks[keypoint_mask_pair[1]], 'right')

        else:

            coordinate = get_two_line_intersection_mask(masks[keypoint_mask_pair[0]], masks[keypoint_mask_pair[1]])

        keypoints.update({keypoint: coordinate})

    return keypoints

def get_matched_keypoints(masks, map_keypoints):
    """ 
    Returns ordered list of keypoint coordinates on a map and image 
    """

    # Extract image keypoints from the list of image court masks
    image_keypoints = get_image_mask_keypoints(masks, map_keypoints)

    # Here comes keypoints image map matching
    map_keypoints_ordered, image_keypoints_ordered = [], []

    for image_keypoint, image_keypoint_value in image_keypoints.items():

        if image_keypoint_value == None:
            continue

        map_keypoints_ordered.append(map_keypoints['values'][image_keypoint])
        image_keypoints_ordered.append(image_keypoints[image_keypoint])

    return np.array([map_keypoints_ordered]), np.array([image_keypoints_ordered])

# ----------------------------------

def get_two_line_intersection_analytical(a1, a2, b1, b2):
    """ 
    Returns the point of intersection of the lines passing through a2,a1 and b2,b1.
    a1: [x, y] a point on the first line
    a2: [x, y] another point on the first line
    b1: [x, y] a point on the second line
    b2: [x, y] another point on the second line
    """
    s = np.vstack([a1,a2,b1,b2])        # s for stacked
    h = np.hstack((s, np.ones((4, 1)))) # h for homogeneous
    l1 = np.cross(h[0], h[1])           # get first line
    l2 = np.cross(h[2], h[3])           # get second line
    x, y, z = np.cross(l1, l2)          # point of intersection
    if z == 0:                          # lines are parallel
        return [float('inf'), float('inf')]
    return [int(x/z), int(y/z)]

def get_two_line_intersection_mask(mask_1, mask_2, min_mask_size=1e4, outlier_mask_thresh=10):
    """ 
    For two masks, fits line and find their intersection.
    """

    # Thresholds should be much higer if predicting masks

    if np.sum(mask_1)<min_mask_size or np.sum(mask_2)<min_mask_size:
        return None

    _,thresh_1 = cv2.threshold(mask_1, 0.5, 255, cv2.THRESH_BINARY)
    _,thresh_2 = cv2.threshold(mask_2, 0.5, 255, cv2.THRESH_BINARY)

    contours_1,_ = cv2.findContours(cv2.convertScaleAbs(thresh_1), 1, 2)
    contours_2,_ = cv2.findContours(cv2.convertScaleAbs(thresh_2), 1, 2)

    contours_1 = np.array([cc for c in contours_1 if cv2.contourArea(c)>outlier_mask_thresh for cc in c])
    contours_2 = np.array([cc for c in contours_2 if cv2.contourArea(c)>outlier_mask_thresh for cc in c])

    if len(contours_1) < 5 or len(contours_2) < 5:
        return None

    [vx_1,vy_1,x_1,y_1] = cv2.fitLine(contours_1, cv2.DIST_L2, 0,0.01,0.01)
    [vx_2,vy_2,x_2,y_2] = cv2.fitLine(contours_2, cv2.DIST_L2, 0,0.01,0.01)

    vx_1,vy_1,x_1,y_1 = vx_1[0],vy_1[0],x_1[0],y_1[0]
    vx_2,vy_2,x_2,y_2 = vx_2[0],vy_2[0],x_2[0],y_2[0]

    p1_0 = [x_1, y_1]
    p1_1 = [x_1 + vx_1, y_1 + vy_1]
    p2_0 = [x_2, y_2]
    p2_1 = [x_2 + vx_2, y_2 + vy_2]

    intersection = get_two_line_intersection_analytical(p1_0, p1_1, p2_0, p2_1)

    return intersection

# ----------------------------------

def get_elipse_line_intersection_analytical(ellipse, line_m, line_n):
    
    # y = m*x + n
    m = line_m
    n = line_n

    (xc, yc), (MA, ma), angle = ellipse
    a = ma/2
    b = MA/2
    angle = angle*np.pi/180 - np.pi/2
    cos = np.cos(angle)
    sin = np.sin(angle)

    E1 = (cos+m*sin)/a
    E2 = ((n-yc)*sin - xc*cos)/a
    E3 = (sin-m*cos)/b
    E4 = ((n-yc)*cos + xc*sin)/b

    A = E1**2 + E3**2
    B = 2*(E1*E2 - E3*E4)
    C = E2**2 + E4**2 - 1

    x1 = (-B + np.sqrt(B**2 - 4*A*C))/(2*A)
    x2 = (-B - np.sqrt(B**2 - 4*A*C))/(2*A)
    y1 = m*x1 + n
    y2 = m*x2 + n    

    return {'left':(x2[0],y2[0]), 'right':(x1[0],y1[0])}

def get_ellipse_line_intersection_mask(mask_1, mask_2, side, min_mask_size=1e4, outlier_mask_thresh_line=10, outlier_mask_thresh_ellipse=10):
    # Thresholds should be much higer if predicting masks

    if np.sum(mask_1)<min_mask_size or np.sum(mask_2)<min_mask_size:
        return None

    _,thresh_1 = cv2.threshold(mask_1, 0.5, 255, cv2.THRESH_BINARY)
    _,thresh_2 = cv2.threshold(mask_2, 0.5, 255, cv2.THRESH_BINARY)

    contours_1,_ = cv2.findContours(cv2.convertScaleAbs(thresh_1), 1, 2)
    contours_2,_ = cv2.findContours(cv2.convertScaleAbs(thresh_2), 1, 2)

    contours_1 = np.array([cc for c in contours_1 if cv2.contourArea(c)>outlier_mask_thresh_line for cc in c])
    contours_2 = np.array([cc for c in contours_2 if cv2.contourArea(c)>outlier_mask_thresh_ellipse for cc in c])

    # ----------------------------
    # Line part
    [vx_1,vy_1,x_1,y_1] = cv2.fitLine(contours_1, cv2.DIST_L2,0,0.01,0.01)

    # y = m*x + n 
    m = vy_1/vx_1
    n = y_1 - m*x_1

    # ----------------------------
    # Ellipse part
    ellipse = cv2.fitEllipse(contours_2)

    # Intersection
    intersections = get_elipse_line_intersection_analytical(ellipse, m, n)

    # DEBUG
    # cv2.ellipse(thresh_2, ellipse, (255,255,0), 1)
    # cv2.ellipse(thresh_2, ellipses[1], (255,255,0), 1)
    # cv2.circle(thresh_2, (int(ellipses[0][0][0]),int(ellipses[0][0][1])), 2, (255,0,0), 25)
    # cv2.circle(thresh_2, (x2,y2), 2, (255,0,0), 25)
    # cv2.circle(thresh_2, (x_l_new,y_l_new), 2, (100,0,0), 5)
    # cv2.line(thresh_2,(cols-1,righty_1),(0,lefty_1),(255,255,0),1)
    # cv2.imwrite('test.png', thresh_2)

    # Take right point of left side
    if side == 'left':
        intersection = intersections['right']
    # Take left point of right side
    elif side == 'right':
        intersection = intersections['left']

    if np.any(np.isnan(intersection)):
        return None
    else:
        return intersection

# ----------------------------------
# NOT USED AT THE MOMENT
# def get_contour_extremes(img):

#     # check if binary mask or color
#     if len(img.shape) == 2:
#       gray = cv2.GaussianBlur(img, (5, 5), 0)
#     else:
#       gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#       gray = cv2.GaussianBlur(gray, (5, 5), 0)

#     # threshold the image, then perform a series of erosions +
#     # dilations to remove any small regions of noise
#     thresh = cv2.threshold(gray, 45, 255, cv2.THRESH_BINARY)[1]
#     thresh = cv2.erode(thresh, None, iterations=2)
#     thresh = cv2.dilate(thresh, None, iterations=2)
     
#     # find contours in thresholded image, then grab the largest one
#     cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
#         cv2.CHAIN_APPROX_SIMPLE)
#     cnts = imutils.grab_contours(cnts)
#     c = max(cnts, key=cv2.contourArea)

#     # determine the most extreme points along the contour
#     extLeft = c[c[:, :, 0].argmin()][0]
#     extRight = c[c[:, :, 0].argmax()][0]
#     extTop = c[c[:, :, 1].argmin()][0]
#     extBot = c[c[:, :, 1].argmax()][0]

#     return (extLeft, extRight, extTop, extBot)

# def get_random_colour_masks(image):
#     colours = [[0, 255, 0],[0, 0, 255],[255, 0, 0],[0, 255, 255],[255, 255, 0],[255, 0, 255],[80, 70, 180],[250, 80, 190],[245, 145, 50],[70, 150, 250],[50, 190, 190]]
#     r = np.zeros_like(image).astype(np.uint8)
#     g = np.zeros_like(image).astype(np.uint8)
#     b = np.zeros_like(image).astype(np.uint8)
#     r[image > 0], g[image > 0], b[image > 0] = colours[random.randrange(0,10)]
#     coloured_mask = np.stack([r, g, b], axis=2)
#     return coloured_mask

# def get_person_position(path_img, mask, person=''):

#     img = cv2.imread(path_img)
 
#     # check if binary mask or color
#     if len(mask.shape) == 2:
#       gray = cv2.GaussianBlur(mask, (5, 5), 0)
#     else:
#       gray = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
#       gray = cv2.GaussianBlur(gray, (5, 5), 0)

#     # threshold the image, then perform a series of erosions +
#     # dilations to remove any small regions of noise
#     thresh = cv2.threshold(gray, 45, 255, cv2.THRESH_BINARY)[1]
#     thresh = cv2.erode(thresh, None, iterations=2)
#     thresh = cv2.dilate(thresh, None, iterations=2)

#     cY, cX = ndi.center_of_mass(thresh)

#     # print(person, cY, np.sum(mask))
    
#     cY = 0.192*cY + 8.57 + cY

#     # print(np.sum(mask))

#     # cv2.circle(img, (int(cX), int(cY)), 5, (255,0,255), -1)
#     # cv2.imwrite("test_{}.png".format(person), img)

#     return (cX, cY)

# # find contours in thresholded image, then grab the largest one
# cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# cnts = imutils.grab_contours(cnts)
# c = max(cnts, key=cv2.contourArea)

# for c in cnts:
#     # compute the center of the contour
#     M = cv2.moments(c)
#     cX = int(M["m10"] / M["m00"])
#     cY = int(M["m01"] / M["m00"])
#     print(cX, cY)

# img = cv2.drawContours(img, cnts, -1, (0,255,0), 3)
