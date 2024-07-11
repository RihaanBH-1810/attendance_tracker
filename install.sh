#!/usr/bin/env bash

unameOut="$(uname -s)"
_uname="$1"
python_path="$2"
case "${unameOut}" in
    Linux*)     machine=Linux;;
    Darwin*)    machine=Mac;;
    CYGWIN*)    machine=Cygwin;;
    MINGW*)     machine=MinGw;;
    *)          machine="UNKNOWN:${unameOut}"
esac



# configuration
if [[ "$machine" = "Mac" ]]; then
    readonly attendance_folder_path="/Users/$_uname/.attendance"
else
    readonly attendance_folder_path="/opt/attendance"
    readonly labtrac_service_path="/etc/systemd/system"
fi





# clone the repo
sudo rm -rf attendance_tracker
git clone --single-branch --branch attendance-tracker-script-fix https://github.com/RihaanBH-1810/attendance_tracker.git
 

# create attendance folder
sudo mkdir -p "$attendance_folder_path"
# remove all old contents if any
sudo rm -rf "$attendance_folder_path"/*
if [[ "$machine" != "Mac" ]]; then
    sudo rm -f "$labtrac_service_path"/labtrac.service
    sudo rm -f "$labtrac_service_path"/labtrac.timer
fi

sudo cp -r attendance_tracker/attendance/. "$attendance_folder_path"/.

sudo chmod +x "$attendance_folder_path"/config "$attendance_folder_path"/get_ssid_names.sh


# fetch creds from user and store them
cd "$attendance_folder_path"
sudo python3 get_and_save_credentials.py
cd ~

# Activate the service
if [[ "$machine" != "Mac" ]]; then
    sudo cp -r attendance_tracker/system/. "$labtrac_service_path"/.
    sudo systemctl enable labtrac.timer
    sudo systemctl start labtrac.service
fi

if [[ "$machine" = "Mac" ]]; then
    cd attendance_tracker
    sudo chmod u+x macinstall.sh
    sudo ./macinstall.sh $_uname $python_path
fi
# delete downloaded files
rm -rf attendance_tracker
rm install.sh

