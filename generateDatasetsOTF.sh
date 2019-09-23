#!/bin/sh
#
#    BASH script to generate training and validation sets using the synthetic dataset generator
#    as well as a .json file containing the annotations in COCO format

###### D - Training 20k 20objs* ################
echo "Generating training set D 20k 20objs*"
python dataset_generator.py --dontocclude --scale --rotation --selected --num 8 /home/IIT.LOCAL/ebunz/mask_rcnn/syndata-generation/demo_data_dir/YCB_Video_Addditional_Objects/train/ /home/IIT.LOCAL/ebunz/mask_rcnn/syndata-generation/D_20k_dataset_20_obj*_train defaults_20objects_train_datasetD.py

echo "Convert training set 20k to binary"
python convert_dataset_to_binary.py D_20k_dataset_20_obj*_train/

echo "Convert training set 20k binary to COCO"
python ycb_to_coco_parallel_py2_20obj*.py D_20k_dataset_20_obj*_train


###### E - Training 20k 20obj + 20 obj* ################
echo "Generating training set E 20k 40 obj"
python dataset_generator.py --dontocclude --scale --rotation --selected --num 4 /home/IIT.LOCAL/ebunz/mask_rcnn/syndata-generation/demo_data_dir/YCB_Video_Addditional_Objects/train/ /home/IIT.LOCAL/ebunz/mask_rcnn/syndata-generation/E_20k_dataset_40_obj_simplifiedBG_train defaults_20objects_train_simplifiedPretrain.py

echo "Convert training set 10k to binary"
python convert_dataset_to_binary.py E_20k_dataset_40_obj_simplifiedBG_train/

echo "Convert training set 10k binary to COCO"
python ycb_to_coco_parallel_py2.py E_20k_dataset_40_obj_simplifiedBG_train
