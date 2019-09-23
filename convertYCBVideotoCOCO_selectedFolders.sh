#!/bin/sh
#
#    BASH script that generates binary masks for the specified folders in ycb_video_data_path and saves
#    them in folders in target_dir. Next images are renamed to replace - with _ and then the .json
#    in COCO annotation format is created.
#    Arguments: ycb_video_data_path target_dir selected.txt ycb_video_path
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

    echo "Create binary images for $path" 
    #cd /home/IIT.LOCAL/ebunz/mask_rcnn/syndata-generation
    #python convert_folderYCB_to_binary.py $1$path $2$path
    echo "Rename images in $path" 
    #cd $2$path/images
    #rename  's/-/_/' *.png
    echo "Convert $path to COCO"
    cd /home/IIT.LOCAL/ebunz/mask_rcnn/syndata-generation
    python ycb_to_coco_parallel_py2.py $2$path png


done < "$filename"

