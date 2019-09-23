#!/bin/sh
#
#    BASH script to generate .json file for YCB Video


##### YCB Video Subsampled 10 -> A1 
#echo "convert A1 to binary"
# python convert_folderYCB_to_binary.py /home/IIT.LOCAL/ebunz/mask_rcnn/syndata-generation/YCB_Video_Train_Subsampled_10/all/ /home/IIT.LOCAL/ebunz/mask_rcnn/syndata-generation/YCB_Video_Train_Subsampled_10/all_coco

echo "convert A1 binary to COCO"
python ycb_to_coco_parallel_py2.py /home/IIT.LOCAL/ebunz/mask_rcnn/syndata-generation/YCB_Video_Train_Subsampled_10/all_coco/ png


##### YCB Video Subsampled 5 -> A 

#echo "convert A to binary"
# python convert_folderYCB_to_binary.py /home/IIT.LOCAL/ebunz/mask_rcnn/syndata-generation/YCB_Video_Train_Subsampled_5/all/ /home/IIT.LOCAL/ebunz/mask_rcnn/syndata-generation/YCB_Video_Train_Subsampled_5/all_coco

echo "convert A binary to COCO"
python ycb_to_coco_parallel_py2.py /home/IIT.LOCAL/ebunz/mask_rcnn/syndata-generation/YCB_Video_Train_Subsampled_5/all_coco/ png
