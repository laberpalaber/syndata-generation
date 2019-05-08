import argparse
import glob
import sys
import os
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.dom.minidom
import cv2
import numpy as np
import random
from PIL import Image
import scipy
from multiprocessing import Pool, Manager
from functools import partial
import signal
import time
import json

# Take default values from default file, POISSON_BLENDING_DIR, WIDTH and HEIGHTS
#POISSON_BLENDING_DIR = ''
#WIDTH = 640
#HEIGHT = 480
from defaults import *
sys.path.insert(0, POISSON_BLENDING_DIR)

from pb import *
import math
from pyblur import *
from collections import namedtuple

Rectangle = namedtuple('Rectangle', 'xmin ymin xmax ymax')

def randomAngle(kerneldim):
    """Returns a random angle used to produce motion blurring

    Args:
        kerneldim (int): size of the kernel used in motion blurring

    Returns:
        int: Random angle
    """ 
    kernelCenter = int(math.floor(kerneldim/2))
    numDistinctLines = kernelCenter * 4
    validLineAngles = np.linspace(0,180, numDistinctLines, endpoint = False)
    angleIdx = np.random.randint(0, len(validLineAngles))
    return int(validLineAngles[angleIdx])

def LinearMotionBlur3C(img):
    """Performs motion blur on an image with 3 channels. Used to simulate 
       blurring caused due to motion of camera.

    Args:
        img(NumPy Array): Input image with 3 channels

    Returns:
        Image: Blurred image by applying a motion blur with random parameters
    """
    lineLengths = [3,5,7,9]
    lineTypes = ["right", "left", "full"]
    lineLengthIdx = np.random.randint(0, len(lineLengths))
    lineTypeIdx = np.random.randint(0, len(lineTypes)) 
    lineLength = lineLengths[lineLengthIdx]
    lineType = lineTypes[lineTypeIdx]
    lineAngle = randomAngle(lineLength)
    blurred_img = img
    for i in xrange(3):
        blurred_img[:,:,i] = PIL2array1C(LinearMotionBlur(img[:,:,i], lineLength, lineAngle, lineType))
    blurred_img = Image.fromarray(blurred_img, 'RGB')
    return blurred_img

def overlap(a, b):
    '''Find if two bounding boxes are overlapping or not. This is determined by maximum allowed 
       IOU between bounding boxes. If IOU is less than the max allowed IOU then bounding boxes 
       don't overlap

    Args:
        a(Rectangle): Bounding box 1
        b(Rectangle): Bounding box 2
    Returns:
        bool: True if boxes overlap else False
    '''
    dx = min(a.xmax, b.xmax) - max(a.xmin, b.xmin)
    dy = min(a.ymax, b.ymax) - max(a.ymin, b.ymin)
    
    if (dx>=0) and (dy>=0) and float(dx*dy) > MAX_ALLOWED_IOU*(a.xmax-a.xmin)*(a.ymax-a.ymin):
        return True
    else:
        return False

def get_list_of_images(root_dir, N=1):
    '''Gets the list of images of objects in the root directory. The expected format 
       is root_dir/<object>/<image>.jpg. Adds an image as many times you want it to 
       appear in dataset.

    Args:
        root_dir(string): Directory where images of objects are present
        N(int): Number of times an image would appear in dataset. Each image should have
                different data augmentation
    Returns:
        list: List of images(with paths) that will be put in the dataset
    '''
    img_list = glob.glob(os.path.join(root_dir, '*/*.jpg'))
    img_list_f = []
    for i in xrange(N):
        # sample len(img_list) unique images from the list
        img_list_f = img_list_f + random.sample(img_list, len(img_list))
    return img_list_f

def get_mask_file(img_file):
    '''Takes an image file name and returns the corresponding mask file. The mask represents
       pixels that belong to the object. Default implentation assumes mask file has same path 
       as image file with different extension only. Write custom code for getting mask file here
       if this is not the case.

    Args:
        img_file(string): Image name
    Returns:
        string: Correpsonding mask file path
    '''
    mask_file = img_file.replace('.jpg','.pbm')
    return mask_file

def get_labels(imgs):
    '''Get list of labels/object names. Assumes the images in the root directory follow root_dir/<object>/<image>
       structure. Directory name would be object name.

    Args:
        imgs(list): List of images being used for synthesis 
    Returns:
        list: List of labels/object names corresponding to each image
    '''
    labels = []
    for img_file in imgs:
        label = img_file.split('/')[-2]
        labels.append(label)
    return labels

def get_annotation_from_mask_file(mask_file, scale=1.0):
    '''Given a mask file and scale, return the bounding box annotations

    Args:
        mask_file(string): Path of the mask file
    Returns:
        tuple: Bounding box annotation (xmin, xmax, ymin, ymax)
    '''
    if os.path.exists(mask_file):
        mask = cv2.imread(mask_file)
        if INVERTED_MASK:
            mask = 255 - mask
        rows = np.any(mask, axis=1)
        cols = np.any(mask, axis=0)
        if len(np.where(rows)[0]) > 0:
            ymin, ymax = np.where(rows)[0][[0, -1]]
            xmin, xmax = np.where(cols)[0][[0, -1]]
            return int(scale*xmin), int(scale*xmax), int(scale*ymin), int(scale*ymax)
        else:
            return -1, -1, -1, -1
    else:
        print "%s not found. Using empty mask instead."%mask_file
        return -1, -1, -1, -1

def get_annotation_from_mask(mask):
    '''Given a mask, this returns the bounding box annotations

    Args:
        mask(NumPy Array): Array with the mask
    Returns:
        tuple: Bounding box annotation (xmin, xmax, ymin, ymax)
    '''
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)
    if len(np.where(rows)[0]) > 0:
        ymin, ymax = np.where(rows)[0][[0, -1]]
        xmin, xmax = np.where(cols)[0][[0, -1]]
        return xmin, xmax, ymin, ymax
    else:
        return -1, -1, -1, -1

def write_imageset_file(exp_dir, img_files, anno_files):
    '''Writes the imageset file which has the generated images and corresponding annotation files
       for a given experiment

    Args:
        exp_dir(string): Experiment directory where all the generated images, annotation and imageset
                         files will be stored
        img_files(list): List of image files that were generated
        anno_files(list): List of annotation files corresponding to each image file
    '''
    with open(os.path.join(exp_dir,'train.txt'),'w') as f:
        for i in xrange(len(img_files)):
            f.write('%s %s\n'%(img_files[i], anno_files[i]))

def write_labels_file(exp_dir, labels):
    '''Writes the labels file which has the name of an object on each line

    Args:
        exp_dir(string): Experiment directory where all the generated images, annotation and imageset
                         files will be stored
        labels(list): List of labels. This will be useful while training an object detector
    '''
    unique_labels = ['__background__'] + sorted(set(labels))
    with open(os.path.join(exp_dir,'labels.txt'),'w') as f:
        for i, label in enumerate(unique_labels):
            f.write('%s %s\n'%(i, label))

def write_dataset_json(exp_dir, dataset_dict):
    '''Writes the dataset image dependencies in a JSON file
    Args:
        exp_dir(string): Experiment directory where all the generated images, annotation and imageset
                         files will be stored
        dataset_dict(dict): Dictionary where object dependencies and mask IDs are stored
    '''
    #jsonFormatDataset = json.dumps(dataset_dict)
    with open(os.path.join(exp_dir,'dataset.json'), 'w') as f:
        json.dump(dataset_dict, f)

def write_dataset_info(objects, distractors, backgrounds, scale_augment, rotation_augment, root_dataset_dir):
    '''Writes information relative to the dataset generation to a .txt file
    Args:
        objects: list of objects
        distractors: list of distractor objects
        backgrounds: list of background images
        scale_augment: parameter denoting whether scale augmentation is being applied
        rotation_augment: parameter denoting whether rotation augmentation is being applied
        root_dataset_dir: path to the root directory of the generated dataset
    '''

    info_filename = os.path.join(root_dataset_dir, "info.py")
    with (open(info_filename, "w")) as info_file:

        info_file.write("#DATASET GENERATION INFO\n\n")

        # Write list of objects in txt file
        info_file.write("OBJECTS = " + str(objects) + "\n")

        # Write list of distractors in txt file
        info_file.write("DISTRACTORS = " + str(distractors) + "\n")

        # Write number of background files
        info_file.write("NO_OF_BACKGROUND_IMAGES = " + str(len(backgrounds)) + "\n\n")

        # Write list of generation parameters
        #config_file = open("defaults.py")
        config_file = open(args.settings)        
        config_str = config_file.read()
        info_file.write(config_str)

        info_file.write("AUGMENT_ROTATION = " + str(rotation_augment) + "\n")
        info_file.write("AUGMENT_SCALE = " + str(scale_augment))

def get_labels_dict(labels):
    '''Writes the labels in a dictionary and returns it

    Args:
        labels(list): List of labels. This will be useful while training an object detector
    Returns:
        labels_dict(dict): Dictionary containing an entry for each class label with the corresponding index
    '''
    unique_labels = ['__background__'] + sorted(set(labels))
    labels_dict = {}
    for i, label in enumerate(unique_labels):
        labels_dict[label] = i
    return labels_dict

def keep_selected_labels(img_files, labels):
    '''Filters image files and labels to only retain those that are selected. Useful when one doesn't 
       want all objects to be used for synthesis

    Args:
        img_files(list): List of images in the root directory
        labels(list): List of labels corresponding to each image
    Returns:
        new_image_files(list): Selected list of images
        new_labels(list): Selected list of labels corresponidng to each imahe in above list
    '''
    with open(SELECTED_LIST_FILE) as f:
        selected_labels = [x.strip() for x in f.readlines()]
    new_img_files = []
    new_labels = []
    for i in xrange(len(img_files)):
        if labels[i] in selected_labels:
            new_img_files.append(img_files[i])
            new_labels.append(labels[i])
    return new_img_files, new_labels

def PIL2array1C(img):
    '''Converts a PIL image to NumPy Array

    Args:
        img(PIL Image): Input PIL image
    Returns:
        NumPy Array: Converted image
    '''
    return np.array(img.getdata(),
                    np.uint8).reshape(img.size[1], img.size[0])

def PIL2array3C(img):
    '''Converts a PIL image to NumPy Array

    Args:
        img(PIL Image): Input PIL image
    Returns:
        NumPy Array: Converted image
    '''
    return np.array(img.getdata(),
                    np.uint8).reshape(img.size[1], img.size[0], 3)

def create_image_anno_wrapper(args, dataset_dict, w=WIDTH, h=HEIGHT, scale_augment=False, rotation_augment=False, blending_list=['none'], dontocclude=False):
   ''' Wrapper used to pass params to workers
   '''
   return create_image_anno(*args, dataset_dict=dataset_dict, w=w, h=h, scale_augment=scale_augment, rotation_augment=rotation_augment, blending_list=blending_list, dontocclude=dontocclude)

def create_image_anno(objects, distractor_objects, img_file, anno_file, bg_file, mask_file, root_dataset_dir, dataset_dict,  w=WIDTH, h=HEIGHT, scale_augment=False, rotation_augment=False, blending_list=['none'], dontocclude=False):
    '''Add data augmentation, synthesizes images and generates annotations according to given parameters

    Args:
        objects(list): List of objects whose annotations are also important
        distractor_objects(list): List of distractor objects that will be synthesized but whose annotations are not required
        img_file(str): Synthesized image file name
        anno_file(str): Annotation file name
        bg_file(str): Background image path
        mask_file(str): Output mask file name
        w(int): Width of synthesized image
        h(int): Height of synthesized image
        scale_augment(bool): Add scale data augmentation
        rotation_augment(bool): Add rotation data augmentation
        blending_list(list): List of blending modes to synthesize for each image
        dontocclude(bool): Generate images with occlusion
    '''
    print "Working on root %s" % img_file
    if os.path.exists(anno_file):
        return anno_file
    
    all_objects = objects + distractor_objects
    synthesized_images = 0
    # numbers 0 and 255 are not available for mask IDs
    available_map_ID = range(1, 255)

    object_instances_mask_label = []
    top = Element('annotation')
    background = Image.open(bg_file)
    background = background.resize((w, h), Image.ANTIALIAS)
    backgrounds = []
    #TODO: fix this hack to downsize blending list choice!
    blending_list = [random.choice(blending_list)]
    for i in xrange(len(blending_list)):
        backgrounds.append(background.copy())

    # create a mask map for every image to synthesize
    # masks are not RGB but 8-bit images
    mask_map = Image.new('L', (w,h), color=0)

    if dontocclude:
        already_syn = []
    for idx, obj in enumerate(all_objects):
        foreground = Image.open(obj[0])
        # measure relative size difference between the background image and the source image
        # accounting for width. Height might be used as well
        source_img_scale = float(w) / foreground.size[0]
        xmin, xmax, ymin, ymax = get_annotation_from_mask_file(get_mask_file(obj[0]))
        if xmin == -1 or ymin == -1 or xmax-xmin < MIN_WIDTH or ymax-ymin < MIN_HEIGHT :
            continue
        foreground = foreground.crop((xmin, ymin, xmax, ymax))
        # Just log the dimensions the foreground crop should be resized at. Will perform resizing just once,
        # after augmentation
        orig_w = foreground.size[0] * source_img_scale
        orig_h = foreground.size[1] * source_img_scale
        obj_mask_file =  get_mask_file(obj[0])
        mask = Image.open(obj_mask_file)
        mask = mask.crop((xmin, ymin, xmax, ymax))

        if INVERTED_MASK:
            mask = Image.fromarray(255-PIL2array1C(mask))
        o_w, o_h = orig_w, orig_h
        if scale_augment:
            while True:
                scale = random.uniform(MIN_SCALE, MAX_SCALE)
                o_w, o_h = int(scale*orig_w), int(scale*orig_h)
                if  w-o_w > 0 and h-o_h > 0 and o_w > 0 and o_h > 0:
                    break
        # Resize the image and mask only once (to avoid losing clarity)
        foreground = foreground.resize((int(o_w), int(o_h)), Image.ANTIALIAS)
        mask = mask.resize((int(o_w), int(o_h)), Image.NEAREST)

        if rotation_augment:
            max_degrees = MAX_DEGREES
            while True:
                rot_degrees = random.randint(-max_degrees, max_degrees)
                foreground_tmp = foreground.rotate(rot_degrees, expand=True)
                mask_tmp = mask.rotate(rot_degrees, expand=True)
                o_w, o_h = foreground_tmp.size
                if  w-o_w > 0 and h-o_h > 0:
                    break
            mask = mask_tmp
            foreground = foreground_tmp
        xmin, xmax, ymin, ymax = get_annotation_from_mask(mask)
        attempt = 0

        # find a suitable spot for the crop in the destination image
        # we look for such a space in the user-defined region, if there is none we look in the whole image
        # try to place each one for a max number of times, then scrap the instance
        found = False

        while attempt < MAX_ATTEMPTS_TO_SYNTHESIZE:
            # place the crop somewhere in a rectangular zone at the center of the image
            x = random.randint(int(-MAX_TRUNCATION_FRACTION*o_w + MIN_X_POSITION),
                               int(MAX_X_POSITION-o_w+MAX_TRUNCATION_FRACTION*o_w))
            y = random.randint(int(-MAX_TRUNCATION_FRACTION*o_h + MIN_Y_POSITION),
                               int(MAX_Y_POSITION-o_h+MAX_TRUNCATION_FRACTION*o_h))
            attempt += 1
            if not(dontocclude):
                # if we accept occlusion, there is no need to iterate trying to find unoccluded spots
                found = True
                break
            else:
                # if we don't accept occlusion, look for a suitable space until we run out of trials or we find one
                found = True
                for prev in already_syn:
                    ra = Rectangle(prev[0], prev[2], prev[1], prev[3])
                    rb = Rectangle(x+xmin, y+ymin, x+xmax, y+ymax)
                    if overlap(ra, rb):
                        found = False
                        break

        # if maximum number of attempts of placing an object is reached without finding a suitable position, the
        # instance is dropped
        if (attempt == MAX_ATTEMPTS_TO_SYNTHESIZE) and not found:
            continue

        # log position of the crop
        if dontocclude:
            already_syn.append([x+xmin, x+xmax, y+ymin, y+ymax])
        # paste foreground patch onto background and apply any blending transform if requested
        for i in xrange(len(blending_list)):
            if blending_list[i] == 'none' or blending_list[i] == 'motion':
                backgrounds[i].paste(foreground, (x, y), mask)
            elif blending_list[i] == 'poisson':
                offset = (y, x)
                img_mask = PIL2array1C(mask)
                img_src = PIL2array3C(foreground).astype(np.float64)
                img_target = PIL2array3C(backgrounds[i])
                img_mask, img_src, offset_adj \
                    = create_mask(img_mask.astype(np.float64),
                                  img_target, img_src, offset=offset)
                background_array = poisson_blend(img_mask, img_src, img_target,
                                                 method='normal', offset_adj=offset_adj)
                backgrounds[i] = Image.fromarray(background_array, 'RGB')
            elif blending_list[i] == 'gaussian':
                backgrounds[i].paste(foreground, (x, y), Image.fromarray(cv2.GaussianBlur(PIL2array1C(mask),(5,5),2)))
            elif blending_list[i] == 'box':
                backgrounds[i].paste(foreground, (x, y), Image.fromarray(cv2.blur(PIL2array1C(mask),(3,3))))

        # if the object is a distractor, no need to log it as an instance, and the mask must be background
        if idx >= len(objects):
            foreground_map_color = Image.new('L', foreground.size, 0)
            mask_map.paste(foreground_map_color, (x, y), mask)
            continue

        # paste masks into the mask map
        # make sure the same color is not selected twice
        rand_color = random.choice(available_map_ID)
        foreground_map_color = Image.new('L', foreground.size, rand_color)
        mask_map.paste(foreground_map_color, (x, y), mask)
        available_map_ID.remove(rand_color)

        # log the color and class
        object_instances_mask_label.append((obj[1], rand_color))

        object_root = SubElement(top, 'object')
        object_type = obj[1]
        object_type_entry = SubElement(object_root, 'name')
        object_type_entry.text = str(object_type)
        object_bndbox_entry = SubElement(object_root, 'bndbox')
        x_min_entry = SubElement(object_bndbox_entry, 'xmin')
        x_min_entry.text = '%d'%(max(1,x+xmin))
        x_max_entry = SubElement(object_bndbox_entry, 'xmax')
        x_max_entry.text = '%d'%(min(w,x+xmax))
        y_min_entry = SubElement(object_bndbox_entry, 'ymin')
        y_min_entry.text = '%d'%(max(1,y+ymin))
        y_max_entry = SubElement(object_bndbox_entry, 'ymax')
        y_max_entry.text = '%d'%(min(h,y+ymax))
        difficult_entry = SubElement(object_root, 'difficult')
        difficult_entry.text = '0' # Add heuristic to estimate difficulty later on

    for i in xrange(len(blending_list)):
        if blending_list[i] == 'motion':
            backgrounds[i] = LinearMotionBlur3C(PIL2array3C(backgrounds[i]))
        result_image_filename = img_file + str(blending_list[i]) + '.jpg'
        backgrounds[i].save(os.path.join(root_dataset_dir, result_image_filename))
        synthesized_images += 1

        image_dataset_entry = {
            "MaskPath" : mask_file,
            "Annotations" : anno_file,
            "MaskID" : {item[1] : item[0] for item in object_instances_mask_label}
        }

        dataset_dict[result_image_filename] = image_dataset_entry

    mask_map.save(os.path.join(root_dataset_dir, mask_file), compression=0)

    print "Produced %d images from root %s" % (synthesized_images, img_file)

    xmlstr = xml.dom.minidom.parseString(tostring(top)).toprettyxml(indent="    ")
    with open(os.path.join(root_dataset_dir, anno_file), "w") as f:
        f.write(xmlstr)
   
def gen_syn_data(input_img_files, labels, root_dataset_dir, img_dir, anno_dir, mask_dir, scale_augment, rotation_augment, dontocclude, add_distractors):
    '''Creates list of objects and distractor objects to be pasted on what images.
       Spawns worker processes and generates images according to given params

    Args:
        input_img_files(list): List of image files (input crops)
        labels(list): List of labels for each image
        img_dir(str): Directory where synthesized images will be stored
        anno_dir(str): Directory where corresponding annotations will be stored
        mask_dir(str): Directory where the masks will be stored
        scale_augment(bool): Add scale data augmentation
        rotation_augment(bool): Add rotation data augmentation
        dontocclude(bool): Generate images with occlusion
        add_distractors(bool): Add distractor objects whose annotations are not required 
    '''
    w = WIDTH
    h = HEIGHT
    background_dir = BACKGROUND_DIR
    background_files = glob.glob(os.path.join(background_dir, BACKGROUND_GLOB_STRING)) * BACKGROUND_USES
   
    print "Number of background images : %s"%len(background_files) 
    img_labels = zip(input_img_files, labels)
    random.shuffle(img_labels)

    if add_distractors:
        with open(DISTRACTOR_LIST_FILE) as f:
            distractor_labels = [x.strip() for x in f.readlines()]

        distractor_list = []
        for distractor_label in distractor_labels:
            distractor_list += glob.glob(os.path.join(DISTRACTOR_DIR, distractor_label, DISTRACTOR_GLOB_STRING))

        distractor_files = zip(distractor_list, len(distractor_list)*[None])
        random.shuffle(distractor_files)
    else:
        distractor_files = []
    print "List of distractor files collected: %s" % distractor_files

    manager = Manager()
    dataset_dict = manager.dict()
    idx = 0
    img_files = []
    anno_files = []
    mask_files = []
    params_list = []
    while len(img_labels) > 0:
        # Get list of objects
        objects = []
        n = min(random.randint(MIN_NO_OF_OBJECTS, MAX_NO_OF_OBJECTS), len(img_labels))
        for i in xrange(n):
            objects.append(img_labels.pop())
        # Get list of distractor objects 
        distractor_objects = []
        if add_distractors:
            n = min(random.randint(MIN_NO_OF_DISTRACTOR_OBJECTS, MAX_NO_OF_DISTRACTOR_OBJECTS), len(distractor_files))
            for i in xrange(n):
                distractor_objects.append(random.choice(distractor_files))
            print "Chosen distractor objects: %s" % distractor_objects

        idx += 1
        # Select a random background for the synth image
        bg_file = random.choice(background_files)

        # Generate a root image path, an image for each blending mode will be generated later
        img_file = os.path.join(img_dir, '%i_image_'%(idx))
        anno_file = os.path.join(anno_dir, '%i_annotation.xml'%idx)
        mask_file = os.path.join(mask_dir, '%i_mask.png'%idx)
        params = (objects, distractor_objects, img_file, anno_file, bg_file, mask_file, root_dataset_dir)
        params_list.append(params)
        img_files.append(img_file)
        anno_files.append(anno_file)
        mask_files.append(mask_file)

    print "Setting up %d workers for synthetic image generation" %NUMBER_OF_WORKERS
    partial_func = partial(create_image_anno_wrapper, dataset_dict=dataset_dict, w=w, h=h, scale_augment=scale_augment, rotation_augment=rotation_augment, blending_list=BLENDING_LIST, dontocclude=dontocclude)
    p = Pool(NUMBER_OF_WORKERS, init_worker)
    try:
        p.map(partial_func, params_list)
    except KeyboardInterrupt:
        print "....\nCaught KeyboardInterrupt, terminating workers"
        p.terminate()
    else:
        p.close()
    p.join()

    return img_files, anno_files, dataset_dict.copy()

def init_worker():
    '''
    Catch Ctrl+C signal to terminate workers
    '''
    signal.signal(signal.SIGINT, signal.SIG_IGN)
 
def generate_synthetic_dataset(args):
    ''' Generate synthetic dataset according to given args
    '''
    img_files = get_list_of_images(args.root, args.num) 
    labels = get_labels(img_files)

    if args.selected:
       img_files, labels = keep_selected_labels(img_files, labels)

    if not os.path.exists(args.exp):
        os.makedirs(args.exp)

    if args.add_distractors:
        with open(DISTRACTOR_LIST_FILE) as f:
            distractor_labels = [x.strip() for x in f.readlines()]
    else:
        distractor_labels = []

    with open(SELECTED_LIST_FILE) as f:
        object_labels = [x.strip() for x in f.readlines()]

    # Create directories
    anno_dir = os.path.join(args.exp, 'annotations')
    img_dir = os.path.join(args.exp, 'images')
    mask_dir = os.path.join(args.exp, 'masks')
    if not os.path.exists(anno_dir):
        os.makedirs(anno_dir)
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    if not os.path.exists(mask_dir):
        os.makedirs(mask_dir)

    anno_dir = 'annotations'
    img_dir = 'images'
    mask_dir = 'masks'

    # Synthesize the images and the references
    syn_img_files, anno_files, image_dependencies = gen_syn_data(img_files, labels, args.exp, img_dir, anno_dir, mask_dir, args.scale, args.rotation, args.dontocclude, args.add_distractors)

    # Create a structure with all the dataset references
    # The keys are
    #   Classes - Each training class associated with an integer
    #   Images - Contains each synthesized image path, its associated
    #       annotation file, mask file and mask indexes
    dataset_dict = {}
    dataset_dict['Classes'] = get_labels_dict(labels)
    dataset_dict['Images'] = image_dependencies
    write_dataset_json(args.exp, dataset_dict)

    # Write information about how the dataset was generated
    background_images = [bkg_filename for bkg_filename in os.listdir(BACKGROUND_DIR) if os.path.isfile(os.path.join(BACKGROUND_DIR, bkg_filename))]
    write_dataset_info(object_labels, distractor_labels, background_images, args.scale, args.rotation, args.exp)

def parse_args():
    '''Parse input arguments
    '''
    parser = argparse.ArgumentParser(description="Create dataset with different augmentations")
    parser.add_argument("root",
      help="The root directory which contains objects images and masks.")
    parser.add_argument("exp",
      help="The directory where images, annotations and masks will be created.")
    parser.add_argument("settings",
      help="Name of the defaults.py in the current directory that shall be used")
    parser.add_argument("--selected",
      help="Keep only selected instances in the test dataset. Default is to keep all instances in the root directory", action="store_true")
    parser.add_argument("--scale",
      help="Add scale augmentation. Default is to add scale augmentation.", action="store_true")
    parser.add_argument("--rotation",
      help="Add rotation augmentation. Default is to add rotation augmentation.", action="store_true")
    parser.add_argument("--num",
      help="Number of times each object image will be in dataset", default=1, type=int)
    parser.add_argument("--dontocclude",
      help="Add objects without occlusion. Default is to produce occlusions", action="store_true")
    parser.add_argument("--add_distractors",
      help="Add distractors objects. Default is to not use distractors", action="store_true")
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()
    print args.settings
    m = __import__(args.settings.replace('.py', ''))
    # This is not the preferred way, the variables should be accessed using m.VARIABLE_NAME and then this try: except can be avoided
    try:
        attrlist = m.__all__
    except AttributeError:
        attrlist = dir (m)
    for attr in attrlist:
        globals()[attr] = getattr (m, attr)
    generate_synthetic_dataset(args)

