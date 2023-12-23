#!/bin/bash

# A script to diff the pip installed serial_packets against the local git repo

#pip_pkg="/c/Users/user/AppData/Roaming/Python/Python311/site-packages/serial_packets"
pip_pkg="/c/Users/user/AppData/Local/Programs/Python/Python312/Lib/site-packages/serial_packets"


git_pkg="./src/serial_packets"

#ls $pip_pkg
#ls $git_pkg

'/c/Program Files/Araxis/Araxis Merge/Compare.exe' "$pip_pkg" "$git_pkg" 

