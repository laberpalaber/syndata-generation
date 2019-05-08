#!/bin/sh
#
#    BASH script to generate the COCO conform .json for the folders specified in selected.txt (relative to ycb_video_path) 
#    Arguments: ycb_video_data_path selected.txt 
#
#    ycb_video_path:      	path to folder where the binary YCB video sequences are stored
#    selected.txt:      	file containing the folders to convert
echo "here"
filename="$2"
while read -r line; do
    path="$line"
    echo "Name read from file - $path"
    echo "Rename image names to replace - by _"
    cd ${1}/$path/images
    rename  's/-/_/' *.png
    echo "Processing folder $path"
    cd /home/IIT.LOCAL/ebunz/mask_rcnn/syndata-generation
    python ycb_to_coco_parallel_py2.py ${1}/$path png

done < "$filename"

