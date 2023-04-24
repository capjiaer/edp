#!/bin/csh

set info = ($_)
set ini_path = `readlink -f $info[2]`
set env_path = `dirname $ini_path`/bin

setenv PATH "${PATH}:$env_path"
