#!/bin/bash
DEVNAME=$1
udevadm info --query=env "/dev/$DEVNAME" > /tmp/arm_disc_info_"$DEVNAME"

/usr/bin/python3 /opt/arm/AutomaticRippingMachine.py "/dev/$DEVNAME" /tmp/arm_disc_info_"$DEVNAME" | at -M now
