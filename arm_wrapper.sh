#!/bin/bash
DEVNAME=$1
udevadm info --query=env "/dev/$DEVNAME" > /tmp/arm_disc_info_"$DEVNAME"

echo "Devname: $DEVNAME"

/usr/bin/python3 /opt/arm/AutomaticRippingMachine.py --disc_path "/dev/$DEVNAME" --disc_info /tmp/arm_disc_info_"$DEVNAME"

echo "Exiting arm_wrapper"
