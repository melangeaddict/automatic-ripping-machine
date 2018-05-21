# Automatic Ripping Machine (ARM)


## Overview

Insert an DVD and rips it.

See https://github.com/melangeaddict/automatic-ripping-machine

## Features

- Detects insertion of disc using udev
  - If video (DVD)
    - Retrieve title from disc or Windows Media MetaServices API to name the folder "movie title (year)" so that Plex or Emby can pick it up
    - Rip using MakeMKV 
    - Eject disc and queue up Handbrake transcoding when done
    - Transcoding jobs are asynchronusly batched from ripping
- Headless, designed to be run from a server
- Can rip from multiple-optical drives in parallel


## Requirements

- Ubuntu Server 16.04 (should work with other Linux distros)
- One or more optical drives to rip 
- Lots of drive space (I suggest using a NAS like FreeNAS) to store your movies

## Install

If you have a  new DVD drive that you haven't used before, some require setting the region before they can play anything.  Be aware most DVD players only let you change the region a handful (4 or 5?) of times then lockout any further changes.  If your region is already set or you have a region free DVD drive you can skip this step.

       sudo apt-get install regionset
       sudo regionset /dev/sr0

    sudo apt-get install git
    sudo add-apt-repository ppa:heyarje/makemkv-beta
    sudo add-apt-repository ppa:stebbins/handbrake-releases
    sudo add-apt-repository ppa:mc3man/xerus-media
    sudo apt update
    sudo apt install makemkv-bin makemkv-oss
    sudo apt install handbrake-cli libavcodec-extra
    sudo apt install abcde flac imagemagick glyrc cdparanoia
    sudo apt install python3 python3-pip
    sudo apt-get install libdvd-pkg
    sudo dpkg-reconfigure libdvd-pkg
    sudo su
    cd /opt
    git clone https://github.com/melangeaddict/automatic-ripping-machine arm
    cd arm
    pip3 install -r requirements.txt
    ln -s /opt/arm/51-automedia.rules /lib/udev/rules.d/
    ln -s /opt/arm/.abcde.conf /root/
    cp /opt/arm/arm@.service /etc/systemd/system/
    cp config.sample config.py

- Edit your "config" file to determine what options you'd like to use
- To rip Blu-Rays after the MakeMKV trial is up you will need to purchase a license key or while MakeMKV is in BETA you can get a free key (which you will need to update from time to time) here:  https://www.makemkv.com/forum2/viewtopic.php?f=5&t=1053 and create /root/.MakeMKV/settings.conf with the contents:

        app_Key = "insertlicensekeyhere"


Optionally if you want something more stable than master you can download the latest release from the releases page.

## Usage

- Insert disc
- Wait for disc to eject
- Repeat

## Troubleshooting

Check /opt/arm/logs to see if you can find where the script failed.  If you need any help feel free to open an issue.

## Contributing

Pull requests are welcome

## License

[MIT License](LICENSE)
