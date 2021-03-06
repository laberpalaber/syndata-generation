#!/bin/sh
#
#    BASH script to generate training and validation sets using the synthetic dataset generator
#    as well as a .json file containing the annotations in COCO format
#    Arguments: ycb_video_data_path selected.txt 

source ~/.virtualenvs/ycb_data_gen/bin/activate

# Generate validation dataset
#echo "Generating validation set without augmentation"
#python dataset_generator.py  --dontocclude --selected --scale --rotation --num 8 /home/IIT.LOCAL/ebunz/mask_rcnn/syndata-generation/demo_data_dir/YCB_objects_split_20k/val/ /home/IIT.LOCAL/ebunz/mask_rcnn/syndata-generation/dataset_20k_val

#echo "Generating validation set with augmentation"
#python dataset_generator.py  --dontocclude --selected --num 8 /home/IIT.LOCAL/ebunz/mask_rcnn/syndata-generation/demo_data_dir/YCB_objects_split_20k/val/ /home/IIT.LOCAL/ebunz/mask_rcnn/syndata-generation/dataset_20k_val defaults_20k_val.py

# Convert validation to binary
#echo "Convert validation to binary"
#python convert_dataset_to_binary.py dataset_20k_val

# Convert validation binary to COCO
#echo "Convert validation binary to COCO"
#python ycb_to_coco_parallel_py2.py dataset_20k_val



# Generate training dataset
#echo "Generating training set without augmentation"
#python dataset_generator.py  --dontocclude --selected --scale --rotation --num 8 /home/IIT.LOCAL/ebunz/mask_rcnn/syndata-generation/demo_data_dir/YCB_objects_split_20k/train/ /home/IIT.LOCAL/ebunz/mask_rcnn/syndata-generation/dataset_20k_train

echo "Generating training set with augmentation"
python dataset_generator.py  --dontocclude --selected --num 8 /home/IIT.LOCAL/ebunz/mask_rcnn/syndata-generation/demo_data_dir/YCB_objects_split_20k/train/ /home/IIT.LOCAL/ebunz/mask_rcnn/syndata-generation/dataset_20k_train defaults_20k_train.py

# Convert training to binary
echo "Convert training to binary"
python convert_dataset_to_binary.py dataset_20k_train

# Convert training binary to COCO
echo "Convert training binary to COCO"
python ycb_to_coco_parallel_py2.py dataset_20k_train


