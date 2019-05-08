#!/bin/sh
#
#    BASH script to generate binary masks for  for the folders specified in selected.txt (relative to ycb_video_data_path) and saves
#    in folders in target_dir
#    Arguments: ycb_video_data_path target_dir selected.txt 
#
#    ycb_video_data_path:      	path to folder where the YCB video sequences are stored (/data) 
#    target_dir:        	directory where the results shall be saved to
#    selected.txt:      	file containing the folders to convert

mkdir $2

filename="$3"
while read -r line; do
    path="$line"
    echo "Name read from file - $path"
    #path = $line
    #number of directory
    #cd /$path && for i in `ls `; do echo "Path - $i"; done

    echo "Processing folder $path" 
    cd /home/IIT.LOCAL/ebunz/mask_rcnn/syndata-generation
    python convert_folderYCB_to_binary.py $1$path $2$path 

done < "$filename"

