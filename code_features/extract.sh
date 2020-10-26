#!/bin/bash
# Damir Pulatov
# extract and save software features 

while getopts ":f:p:d:s:" arg; do
	case $arg in
		f) soft=$OPTARG;;
		p) parser=$OPTARG;;
		d) dir=$OPTARG;;
		s) save=$OPTARG;;
	esac
done

#Gather metrics
python "$soft" collect --std.code.lines.code --std.general.size --std.code.complexity.cyclomatic --std.code.complexity.maxindent -- $dir

#Save metrics in log file
python "$soft" view > metrix.log

#Parse log file with awk
$parser metrix.log >> "$save" 
