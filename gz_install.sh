#!/bin/bash

# REFERENCES:
# https://gazebosim.org/docs/harmonic/install_ubuntu/
# https://ardupilot.org/dev/docs/ros2.html
# https://ardupilot.org/dev/docs/ros2-sitl.html
# https://ardupilot.org/dev/docs/ros2-gazebo.html
# https://github.com/ArduPilot/SITL_Models/blob/master/Gazebo/docs/AltiTransition.md

# Ask if gazebo and ros are installed already
read -p "Have you already installed Gazebo and ROS2 Humble? (y/n) " yn
case $yn in
    [Yy]* ) echo "Continuing with Gazebo setup...";;
    [Nn]* ) echo "Please install Gazebo and ROS2 Humble first.";
            echo "Follow instructions at: https://gazebosim.org/docs/harmonic/install_ubuntu/ and https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debians.html";
            exit 1;;
    * ) echo "Please answer yes or no."; exit 1;;
esac

# Find simcore base directory
DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"
BASE_DIR="$(pwd)"

# check if basedir is "simcore"
if [[ "$(basename "$BASE_DIR")" != "simcore" ]]; then
    echo "Script could not find simcore."
    echo "Found base directory: $BASE_DIR"
    exit 1
fi

echo "Found simcore base directory: $BASE_DIR"

# Check if ardu_ws directory exists and has ardupilot folder
if [ ! -d "$BASE_DIR/ardu_ws/src/ardupilot" ]; then
    echo "ArduPilot workspace not found in $BASE_DIR/ardu_ws/src/ardupilot"
    exit 1
fi

# Ask to run Ardupilot environment tools setup
read -p "Do you want to setup ArduPilot SITL build environment? (y/n)" yn
case $yn in
    [Yy]* ) echo "Setting up ArduPilot SITL build environment... (respond NO for each prompt)"; sleep 5;
                bash "$BASE_DIR/ardu_ws/src/ardupilot/Tools/environment_install/install-prereqs-ubuntu.sh";. ~/.profile;;
    [Nn]* ) echo "Skipping ArduPilot SITL build environment setup.";;
    * ) echo "Please answer yes or no."; exit 1;;
esac

echo "Setting up Gazebo environment..."

echo "" >> ~/.bashrc
echo "export GZ_VERSION=harmonic" >> ~/.bashrc

# Add gazebo sources to rosdep
sudo wget https://raw.githubusercontent.com/osrf/osrf-rosdep/master/gz/00-gazebo.list -O /etc/ros/rosdep/sources.list.d/00-gazebo.list
rosdep update

cd "$BASE_DIR/ardu_ws"
sudo apt update
rosdep update
source /opt/ros/humble/setup.bash
rosdep install --from-paths src --ignore-src -r -y

# Build Micro XRCE-DDS-Gen
sudo apt install default-jre -y
cd Micro-XRCE-DDS-Gen
./gradlew assemble

# Add stuff to bashrc
echo "Adding ArduPilot Gazebo setup to ~/.bashrc ..."
echo "" >> ~/.bashrc
echo "# ArduPilot Gazebo setup" >> ~/.bashrc
echo "source $BASE_DIR/ardu_ws/src/ardupilot/Tools/completion/completion.bash" >> ~/.bashrc
echo "export ROS_VERSION=2" >> ~/.bashrc
echo "export ROS_PYTHON_VERSION=3" >> ~/.bashrc
echo "export ROS_DISTRO=humble" >> ~/.bashrc
echo "export PATH=\$PATH:$PWD/scripts" >> ~/.bashrc
echo "export PYTHONPATH=\$PYTHONPATH:$BASE_DIR/ardu_ws/install/ardupilot_msgs/local/lib/python3.10/dist-packages" >> ~/.bashrc

# Ask if running inside virtual machine
read -p "Are you running inside a virtual machine? (y/n) " yn
case $yn in
    [Yy]* ) echo "Disabling hardware acceleration"; echo "export LIBGL_DRI3_DISABLE=1" >> ~/.bashrc;;
    [Nn]* ) echo "Coolio, leaving hardware acceleration enabled.";;
    * ) echo "Please answer yes or no."; exit 1;;
esac

# Adding stuff to bash aliases
echo "Adding ArduPilot Gazebo aliases to ~/.bash_aliases ..."
echo "" >> ~/.bash_aliases
echo "# ArduPilot Gazebo aliases" >> ~/.bash_aliases
echo "alias sf='source $BASE_DIR/ardu_ws/install/setup.bash && export PATH=/usr/lib/ccache:$BASE_DIR/ardu_ws/src/ardupilot/Tools/autotest:\$PATH'" >> ~/.bash_aliases
echo "alias runway='sf && ros2 launch ardupilot_gz_bringup iris_runway.launch.py'" >> ~/.bash_aliases