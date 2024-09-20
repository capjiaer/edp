#!/bin/csh

set info = ($_)
set ini_path = `readlink -f $info[2] |xargs dirname`
set env_path = $ini_path/bin
setenv PATH "${env_path}:${PATH}"
