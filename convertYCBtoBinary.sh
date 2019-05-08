#!/bin/sh
#
#    BASH script to generate binary masks for all folders in ycb_video_data_path and saves
#    in folders in target_dir
#    Arguments: ycb_video_data_path target_dir 
#
#    ycb_video_data_path:      	path to folder where the YCB video sequences are stored (/data) 
#    target_dir:        	directory where the results shall be saved to

mkdir $2

cd $1
for i in `ls`
do
	echo "Processing folder $i" 
	cd /home/IIT.LOCAL/ebunz/mask_rcnn/syndata-generation
	python convert_folderYCB_to_binary.py $1$i $2$i 
done

