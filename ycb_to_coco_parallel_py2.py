#!/usr/bin/env python3

################################################################################
# Script that reads the binary annotations masks in ANNOTATION_DIR and creates
# a .json file in the COCO format. Adapted to the synthetic datasets created
# using syndata-generation (https://github.com/fbottarel/syndata-generation).
# Annotations need to be converted to binary masks by using
# convert_dataset_to_binary.py
# Make sure to adapt to your version of python and your objects
################################################################################

# @authors: Elsa Bunz <elsa.bunz@iit.it>
# Adapted from shapes_to_coco.py (https://github.com/waspinator/pycococreator)

import datetime
import json
import os
import re
import fnmatch
from PIL import Image
import numpy as np
from pycococreatortools import pycococreatortools
import multiprocessing
import itertools # for python 2 use itertools.izip instead of zip
import time
import sys

format_jpg = 0
format_png = 0

if len(sys.argv) > 1:
        ROOT_DIR = sys.argv[1]

if len(sys.argv) > 2:
        image_type = sys.argv[2]

        if image_type == 'jpg' or image_type == 'jpeg':
                format_jpg = 1
        elif image_type == 'png':
                format_png = 1
        else:
                print("Requested image format not supported")
                sys.exit()
# without argument the assumed format is jpeg
else:
        format_jpg = 1
        format_png = 0

#ROOT_DIR = 'dataset_sanity_test'
IMAGE_DIR = os.path.join(ROOT_DIR, "images")
ANNOTATION_DIR = os.path.join(ROOT_DIR, "annotations_coco")

print ("Dataset directory: ", ROOT_DIR)

INFO = {
    "description": "Synthetic dataset generated from YCB",
    "url": "https://github.com/fbottarel/syndata-generation",
    "version": "0.1.0",
    "year": 2018,
    "contributor": "laberpalaber",
    "date_created": datetime.datetime.utcnow().isoformat(' ')
}

LICENSES = [
    {
        "id": 1,
        "name": "Attribution-NonCommercial-ShareAlike License",
        "url": "http://creativecommons.org/licenses/by-nc-sa/2.0/"
    }
]

CATEGORIES = [
    {
        'id': 1,
        'name': 'master_chef_can',
        'supercategory': 'YCB_video',
    },
    {
        'id': 2,
        'name': 'cracker_box',
        'supercategory': 'YCB_video',
    },
    {
        'id': 3,
        'name': 'sugar_box',
        'supercategory': 'YCB_video',
    },
    {
        'id': 4,
        'name': 'tomato_soup_can',
        'supercategory': 'YCB_video',
    },
    {
        'id': 5,
        'name': 'mustard_bottle',
        'supercategory': 'YCB_video',
    },
    {
        'id': 6,
        'name': 'tuna_fish_can',
        'supercategory': 'YCB_video',
    },
    {
        'id': 7,
        'name': 'pudding_box',
        'supercategory': 'YCB_video',
    },
    {
        'id': 8,
        'name': 'gelatin_box',
        'supercategory': 'YCB_video',
    },
    {
        'id': 9,
        'name': 'potted_meat_can',
        'supercategory': 'YCB_video',
    },
    {
        'id': 10,
        'name': 'banana',
        'supercategory': 'YCB_video',
    },
    {
        'id': 11,
        'name': 'pitcher_base',
        'supercategory': 'YCB_video',
    },
    {
        'id': 12,
        'name': 'bleacher_cleanser',
        'supercategory': 'YCB_video',
    },
    {
        'id': 13,
        'name': 'bowl',
        'supercategory': 'YCB_video',
    },
    {
        'id': 14,
        'name': 'mug',
        'supercategory': 'YCB_video',
    },
    {
        'id': 15,
        'name': 'power_drill',
        'supercategory': 'YCB_video',
    },
    {
        'id': 16,
        'name': 'scissors',
        'supercategory': 'YCB_video',
    },
    {
        'id': 17,
        'name': 'large_marker',
        'supercategory': 'YCB_video',
    },
    {
        'id': 18,
        'name': 'extra_large_clamp',
        'supercategory': 'YCB_video',
    },
    {
        'id': 19,
        'name': 'large_clamp',
        'supercategory': 'YCB_video',
    },
    {
        'id': 20,
        'name': 'foam_brick',
        'supercategory': 'YCB_video',
    },
    {
        'id': 21,
        'name': 'chips_can',
        'supercategory': 'ycb',
    },
    {
        'id': 22,
        'name': 'apple',
        'supercategory': 'ycb',
    },
    {
        'id': 23,
        'name': 'lemon',
        'supercategory': 'ycb',
    },
    {
        'id': 24,
        'name': 'pear',
        'supercategory': 'ycb',
    },
    {
        'id': 25,
        'name': 'mini_soccer_ball',
        'supercategory': 'ycb',
    },
    {
        'id': 26,
        'name': 'orange',
        'supercategory': 'ycb',
    },
    {
        'id': 27,
        'name': 'softball',
        'supercategory': 'ycb',
    },
    {
        'id': 28,
        'name': 'baseball',
        'supercategory': 'ycb',
    },
    {
        'id': 29,
        'name': 'tennis_ball',
        'supercategory': 'ycb',
    },
    {
        'id': 30,
        'name': 'a_cups',
        'supercategory': 'ycb',
    },
    {
        'id': 31,
        'name': 'e_cups',
        'supercategory': 'ycb',
    },
    {
        'id': 32,
        'name': 'f_cups',
        'supercategory': 'ycb',
    },
    {
        'id': 33,
        'name': 'h_cups',
        'supercategory': 'ycb',
    },
    {
        'id': 34,
        'name': 'i_cups',
        'supercategory': 'ycb',
    },
    {
        'id': 35,
        'name': 'j_cups',
        'supercategory': 'ycb',
    },
    {
        'id': 36,
        'name': 'b_lego_duplo',
        'supercategory': 'ycb',
    },
    {
        'id': 37,
        'name': 'c_lego_duplo',
        'supercategory': 'ycb',
    },
    {
        'id': 38,
        'name': 'm_lego_duplo',
        'supercategory': 'ycb',
    },
    {
        'id': 39,
        'name': 'timer',
        'supercategory': 'ycb',
    },
    {
        'id': 40,
        'name': 'rubiks_cube',
        'supercategory': 'ycb',
    },
]
def filter_for_jpeg(root, files):
    file_types = ['*.jpeg', '*.jpg']
    file_types = r'|'.join([fnmatch.translate(x) for x in file_types])
    files = [os.path.join(root, f) for f in files]
    files = [f for f in files if re.match(file_types, f)]
    
    return files

def filter_for_png(root, files):
    file_types = [ '*.png']
    file_types = r'|'.join([fnmatch.translate(x) for x in file_types])
    files = [os.path.join(root, f) for f in files]
    files = [f for f in files if re.match(file_types, f)]
    
    return files

def filter_for_annotations(root, files, image_filename):
    #file_types = ['*.png']
    #file_types = r'|'.join([fnmatch.translate(x) for x in file_types])
    basename_no_extension = os.path.splitext(os.path.basename(image_filename))[0]
    # Adapted here to our naming convention
    basename_onlyID = basename_no_extension.split('_')[0]
    file_name_prefix = "^" + basename_onlyID + "_.*\.png$"
    files = [os.path.join(root, f) for f in files]
    #files = [f for f in files if re.match(file_types, f)]
    files = [f for f in files if re.match(file_name_prefix, os.path.basename(f))]
    # newlist = []
    # for f in files:
    #     if re.match(file_name_prefix, os.path.splitext(os.path.basename(f))[0]):
    #         newlist.append(f)

    return files

def main():

    coco_output = {
        "info": INFO,
        "licenses": LICENSES,
        "categories": CATEGORIES,
        "images": [],
        "annotations": []
    }

    image_id = 1
    segmentation_id = 1
    cnt = 0

    parallel_bunches_nr = 1000
    nr_cpu_cores = 1000

    segmentation_id_list = []
    image_id_list = []
    category_info_list = []
    binary_mask_list = []
    image_size_list = []
    tolerance_list = []

    start = time.time()
    print("Start")
    for root, _, files in os.walk(ANNOTATION_DIR):
    
        # filter for jpeg images
        for root_imagedir, _, files_imagedir in os.walk(IMAGE_DIR):
            if format_jpg:
                image_files = filter_for_jpeg(root_imagedir, files_imagedir)
                print ("jpeg filter applied")
            elif format_png:
                image_files = filter_for_png(root_imagedir, files_imagedir)
                print ("png filter applied")
            num_files = float(len(image_files))
            percent = 0
            start_converting = time.time()

            # go through each image
            for image_filename in image_files:
                #print(str(image_id/num_files * 100), str(percent))
                #print(str(int(image_id/num_files * 100.0)), str(percent))
                if int(image_id/num_files * 100) > percent:
                    percent = int(image_id/num_files * 100)
                    curr_time = time.time()
                    total_time = (curr_time - start_converting)/(image_id/num_files)
                    remain_time = total_time - (curr_time - start_converting)
                    print(str(percent) + "%, Remaining time " +  time.strftime('%H:%M:%S', time.gmtime(remain_time)))

                if cnt == 0:
                    segmentation_id_list = []
                    image_id_list = []
                    category_info_list = []
                    binary_mask_list = []
                    image_size_list = []
                    tolerance_list = []


                image = Image.open(image_filename)
                image_info = pycococreatortools.create_image_info(
                    image_id, os.path.basename(image_filename), image.size)
                coco_output["images"].append(image_info)

                # filter for associated png annotations

                annotation_files = filter_for_annotations(root, files, image_filename)
		#print (annotation_files)
                # go through each associated annotation
                for annotation_filename in annotation_files:

                    #print(annotation_filename)
                    # large_clamp needs to be after extra_large_clamp to have correct mapping
                    class_id = [x['id'] for x in CATEGORIES if x['name'] in annotation_filename][0]
                    #print(class_id)
                    category_info = {'id': class_id, 'is_crowd': 'crowd' in image_filename}
                    binary_mask = np.asarray(Image.open(annotation_filename)
                        .convert('1')).astype(np.uint8)

                    segmentation_id_list.append(segmentation_id)
                    image_id_list.append(image_id)
                    category_info_list.append(category_info)
                    binary_mask_list.append(binary_mask)
                    image_size_list.append(image.size)
                    tolerance_list.append(2)

                    cnt = cnt+1
                    #print (cnt)

                    segmentation_id = segmentation_id + 1

                image_id = image_id + 1

                if cnt >= parallel_bunches_nr:
                    print("compute polygons in parallel")
                    pool = multiprocessing.Pool(nr_cpu_cores)
                    # TODO parallelize
                    # annotation_infos = zip(*pool.map(pycococreatortools.create_annotation_info,
                    #     segmentation_id_list, image_id_list, category_info_list, binary_mask_list,
                    #     image_size_list, tolerance_list))
                    # for python 2 use itertools.izip instead of zip
                    annotation_infos = pool.map(multi_run_wrapper, itertools.izip(segmentation_id_list, image_id_list, category_info_list, binary_mask_list,
                        image_size_list, tolerance_list))

                    pool.close()

                    for annotation_info in annotation_infos:
                        if annotation_info is not None:
                            coco_output["annotations"].append(annotation_info)

                    cnt = 0

    # Compute the polygons also for the remaining files if any
    if cnt > 0:
        pool = multiprocessing.Pool(nr_cpu_cores)
        # TODO parallelize
        # annotation_infos = zip(*pool.map(pycococreatortools.create_annotation_info,
        #     segmentation_id_list, image_id_list, category_info_list, binary_mask_list,
        #     image_size_list, tolerance_list))
        # for python 2 use itertools.izip instead of zip
        annotation_infos = pool.map(multi_run_wrapper, itertools.izip(segmentation_id_list, image_id_list, category_info_list, binary_mask_list, image_size_list, tolerance_list))

        pool.close()

        for annotation_info in annotation_infos:
            if annotation_info is not None:
                coco_output["annotations"].append(annotation_info)


    with open('{}/instances_ycb.json'.format(ROOT_DIR), 'w') as output_json_file:
        json.dump(coco_output, output_json_file)

    end = time.time()
    print(end - start)

def multi_run_wrapper(args):
    return pycococreatortools.create_annotation_info(*args)

if __name__ == "__main__":
    main()
