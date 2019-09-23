#!/bin/sh
mkdir $1

for ycb_dir in 0*/
do
	#cd "$ycb_dir"
#echo "$ycb_dir"
	for file in "${ycb_dir}"0*
	do
		#echo "$PWD/$file"
		#echo "$1/$(basename "$ycb_dir")_$(basename "$file")"
		ln -s $PWD/$file $1/$(basename "$ycb_dir")$(basename "$file")
	
	done
done
