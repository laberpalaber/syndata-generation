#!/bin/sh
#
#    BASH script to generate training and validation sets using the synthetic dataset generator
#    as well as a .json file containing the annotations in COCO format

###### Validation 2k ################
echo "Generating validation set 2k"
python dataset_generator.py --dontocclude --scale --rotation --selected --num 8 /home/IIT.LOCAL/ebunz/mask_rcnn/syndata-generation/demo_data_dir/YCB_Video_Addditional_Objects/val/ /home/IIT.LOCAL/ebunz/mask_rcnn/syndata-generation/EvalData_2k_dataset_20_obj_val defaults_20objects_val_EvaluationDatasets.py

echo "Convert validation to binary"
python convert_dataset_to_binary.py EvalData_2k_dataset_20_obj_val


echo "Convert validation binary to COCO"
python ycb_to_coco_parallel_py2.py EvalData_2k_dataset_20_obj_val

###### Training 10k ################
echo "Generating training set 10k"
python dataset_generator.py --dontocclude --scale --rotation --selected --num 4 /home/IIT.LOCAL/ebunz/mask_rcnn/syndata-generation/demo_data_dir/YCB_Video_Addditional_Objects/train/ /home/IIT.LOCAL/ebunz/mask_rcnn/syndata-generation/EvalData_10k_dataset_20_obj_train defaults_20objects_train_EvaluationDatasets.py

echo "Convert training set 10k to binary"
python convert_dataset_to_binary.py EvalData_10k_dataset_20_obj_train/

echo "Convert training set 10k binary to COCO"
python ycb_to_coco_parallel_py2.py EvalData_10k_dataset_20_obj_train


###### Training 20k ################
echo "Generating training set 20k"
python dataset_generator.py --dontocclude --scale --rotation --selected --num 8 /home/IIT.LOCAL/ebunz/mask_rcnn/syndata-generation/demo_data_dir/YCB_Video_Addditional_Objects/train/ /home/IIT.LOCAL/ebunz/mask_rcnn/syndata-generation/EvalData_20k_dataset_20_obj_train defaults_20objects_train_EvaluationDatasets.py

echo "Convert training set 20k to binary"
python convert_dataset_to_binary.py EvalData_20k_dataset_20_obj_train/

echo "Convert training set 20k binary to COCO"
python ycb_to_coco_parallel_py2.py EvalData_20k_dataset_20_obj_train
