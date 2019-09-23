# From the folder in YCB Video /data create two new folder
# 1) IMAGE_DIR containing all the color images
# 2) OUTPUT_DIR containing the created binary masks, naming convention
#    imageNumber_className_objectNumber.png
# FOLDER_PATH and TARGET_PATH have to be given as absolute paths

import os
from read_mat_file import return_classes
import re
import shutil
import cv2
import sys

if len(sys.argv) > 1:
        FOLDER_PATH = sys.argv[1]
if len(sys.argv) > 2:
        TARGET_PATH = sys.argv[2]

#FOLDER_PATH = '/home/elsa/Desktop/Masterthesis/YCB_dataset/YCB_Video/0000'
#TARGET_PATH = '/home/elsa/Desktop/Masterthesis/YCB_dataset/YCB_Video/test0'

# where to save the binary masks to (relative to FOLDER_PATH)
ANNOTATION_DIR = 'annotations_coco'
# where to save the color images to (relative to FOLDER_PATH)
IMAGE_DIR = 'images'

# Dictionaries that contains the correspondance between object names and labels
CATEGORIES = {
        '1': 'master_chef_can',
        '2': 'cracker_box',
        '3': 'sugar_box',
        '4': 'tomato_soup_can',
        '5': 'mustard_bottle',
        '6': 'tuna_fish_can',
        '7': 'pudding_box',
        '8': 'gelatin_box',
        '9': 'potted_meat_can',
        '10': 'banana',
        '11': 'pitcher_base',
        '12': 'bleacher_cleanser',
        '13': 'bowl',
        '14': 'mug',
        '15': 'power_drill',
        '16': 'wood_block',
        '17': 'scissors',
        '18': 'large_marker',
        '19': 'large_clamp',
        '20': 'extra_large_clamp',
        '21': 'foam_brick',
}

# generate the two
if not os.path.exists(TARGET_PATH):
    os.mkdir(TARGET_PATH)
# Go into the correct folder
os.chdir(TARGET_PATH)
# Create the directory if it does not exist yet
if not os.path.exists(ANNOTATION_DIR):
    os.mkdir(ANNOTATION_DIR)

if not os.path.exists(IMAGE_DIR):
    os.mkdir(IMAGE_DIR)

# List all files in FOLDER_PATH
files = os.listdir(FOLDER_PATH)
# regular expression to filter the files which end with color.png
file_name_prefix = ".*\color.png$"
# loop through all images and copy them into IMAGE_DIR
for f in files:
    if re.match(file_name_prefix, os.path.basename(f)):
        file_complete_path = os.path.join(FOLDER_PATH, f)
        if os.path.isfile(file_complete_path):
            shutil.copy2(file_complete_path, IMAGE_DIR)

# Get list of all images
os.chdir(IMAGE_DIR)
image_files = os.listdir('.')
# change back to FOLDER_PATH
os.chdir(FOLDER_PATH)
# Loop through all images
for image in image_files:

    # save image ID
    img_ID = image.split('-')[0]
    # Get the mask imagepath
    mask_path = img_ID + '-label.png'

    # load the mask image
    cv2.CV_LOAD_IMAGE_GRAYSCALE = 0
    im_mask = cv2.imread(mask_path, cv2.CV_LOAD_IMAGE_GRAYSCALE)

    mat_filepath = img_ID + "-meta.mat"
    # get the classes using the mat file
    classes_present = return_classes(mat_filepath)
    # loop through all objects in this image
    annotation_ID = 0
    for object in classes_present:
        # exclude wood block
        if(CATEGORIES[str(object)] == 'wood_block'):
            continue
        # extract object names with corresponding pixel values
        pixel_value = int(object)
        int_ID = int(object)
        object_class = CATEGORIES[str(int(object))]

        # generate the binary mask
        mask_bin = cv2.inRange(im_mask, pixel_value, pixel_value)
        # save the mask as imageNumber_className_annotation_ID.png
        filename = TARGET_PATH + '/' + ANNOTATION_DIR + '/' + img_ID + '_' + object_class + '_' + str(annotation_ID) + '.png'
        cv2.imwrite(filename, mask_bin)
        # increase the annotation ID
        annotation_ID = annotation_ID + 1




