#!/bin/bash
#
#    BASH script to quickly split a YCB object directory tree into a train and validation
#    sets.
#
#    Arguments: object_dir_YCB target_dir
#
#    object_dir_ycb:    directory where the YCB object lies. Assumes object directories 
#                       have names in the form xxx_object_name_directory
#    target_dir:        where to put the extracted files

mkdir $2
mkdir $2/train
mkdir $2/val

# {} to specify where the parameter ends
# % to get parameter without the /  
for object_dir in ${1%/}/*
do
    # ## to get the basepath
    object_name=${object_dir##*/}
    # to remove the first 4 characters
    #object_name=${object_name:4}
    echo "Creating training set for $object_name"
    mkdir $2/train/$object_name
    for angle in {0..357..9}
    do
        cp $object_dir/*_"$angle".jpg $2/train/$object_name
        cp $object_dir/masks/*_"$angle"_mask.pbm $2/train/$object_name
        # deletes _mask from all files with extension .pbm
        rename 's/_mask//' $2/train/$object_name/*.pbm
    done
    echo "Creating validation set for $object_name"
    mkdir $2/val/$object_name
    for angle in {0..357..30}
    do
        cp $object_dir/*_"$angle".jpg $2/val/$object_name
        cp $object_dir/masks/*_"$angle"_mask.pbm $2/val/$object_name
        rename 's/_mask//' $2/val/$object_name/*.pbm
    done
done

 

