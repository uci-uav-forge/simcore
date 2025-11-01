#!/bin/bash

LOCALPATH=$(pwd)
cd ~/ardu_ws/ || exit 1
echo "colcon building ardu_ws..."
colcon build > /dev/null #hides output, comment out to keep
echo "Finished"
cd "$LOCALPATH" || exit 1
