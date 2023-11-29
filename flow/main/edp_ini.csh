#!/bin/tcsh

# The real script is in the some directory as the linked shell script
# ref /home/chenanping/jedp/source/flow/main/edp_ini.py
set srcdir=`readlink -e $0 | xargs dirname`
set srcfile=${srcdir}/edp_ini.py
echo $srcfile

#Execute file
python3 $srcfile $*
