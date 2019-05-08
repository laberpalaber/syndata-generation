#!/bin/sh
#
#    BASH script to generate training and validation sets using the synthetic dataset generator
#    as well as a .json file containing the annotations in COCO format
#    Arguments: ycb_video_data_path selected.txt 
source ~/.virtualenvs/ycb_data_gen/bin/activate

# Generate training dataset
echo "Generating training set"
python dataset_generator.py  --dontocclude --selected --num 8 /home/IIT.LOCAL/ebunz/mask_rcnn/syndata-generation/demo_data_dir/YCB_objects_split_20k/train/ /home/IIT.LOCAL/ebunz/mask_rcnn/syndata-generation/dataset_20k_train defaults_20k_train.py

# Generate training dataset
echo "Generating validation set"
python dataset_generator.py  --dontocclude --selected --num 8 /home/IIT.LOCAL/ebunz/mask_rcnn/syndata-generation/demo_data_dir/YCB_objects_split_20k/val/ /home/IIT.LOCAL/ebunz/mask_rcnn/syndata-generation/dataset_20k_val defaults_20k_val.py

# Convert training to binary
echo "Convert training to binary"
python convert_dataset_to_binary.py dataset_20k_train

# Convert validation to binary
echo "Convert validation to binary"
python convert_dataset_to_binary.py dataset_20k_val

# Convert training binary to COCO
echo "Convert training binary to COCO"
python ycb_to_coco.py dataset_20k_train

# Convert validation binary to COCO
echo "Convert validation binary to COCO"
python ycb_to_coco.py dataset_20k_val
