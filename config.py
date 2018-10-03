# ARM (Automatic Ripping Machine) oonfig file

#####################
## Directory setup ##
#####################

# Base directory of ARM media directory
# Ripped and transcoded files end up here
ARMPATH="/mnt/media/ARM/Media/Unidentified/"

# Path to raw MakeMKV directory
# Destination for MakeMKV and source for HandBrake
RAWPATH="/mnt/media/ARM/raw/"

# Path to final media directory
# Destination for final file.  Only used for movies that are positively identified
MEDIA_DIR="/media/WDMYCLOUD/"

# Path to directory to hold log files
# Make sure to include trailing /
LOGPATH="/opt/arm/logs/"

# How long to let log files live before deleting (in days)
LOGLIFE=1

# Set to True if you prefer a single log file for all activity versus a separate log per disc.
LOG_SINGLE_FILE=False 

DELETE_RAW=False

########################
##  File Permissions  ##
########################

# Enabling this seting will allow you to adjust the default file permissions of the outputted files
# The default value is set to 777 for read/write/execute for all users, but can be changed below using the "CHMOD_VALUE" setting
# This setting is helpfuly when storing the data locally on the system
SET_MEDIA_PERMISSIONS=False
CHMOD_VALUE=777
SET_MEDIA_OWNER=False
CHOWN_USER=''
CHOWN_GROUP=''

########################
## MakeMKV Parameters ##
########################

# Minimum length of track for MakeMKV rip (in seconds)
MINLENGTH="600"

# Method of MakeMKV to use for Blu Ray discs.  Options are "mkv" or "backup".
# mkv is the normal method of ripping mkv files directly from the DVD
# backup decrypts the dvd and then copies it to the hard drive.  This allows HandBrake to apply some of it's
# analytical abilities such as the main-feature identification.  This method seems to offer success on bluray 
# discs that fail in "mkv" mode. *** NOTE: MakeMKV only supports the backup method on BluRay discs.  Regular
# DVD's will always default back to the "mkv" mode. If this is set to "backup" then you must also set HandBrake's MAINFEATURE to True. 
RIPMETHOD="mkv" 

# MakeMKV Arguments
# MakeMKV Profile used for controlling Audio Track Selection.
# This is the default profile MakeMKV uses for Audio track selection. Updating this file or changing it is considered
# to be advanced usage of MakeMKV. But this will allow users to alternatively tell makemkv to select HD audio tracks and etc.
# MKV_ARGS="--profile=/opt/arm/default.mmcp.xml"
MKV_ARGS=""

##########################
## HandBrake Parameters ##
##########################

# Handbrake preset profile
# Execute "HandBrakeCLI -z" to see a list of all presets
HB_PRESET="HQ 1080p30 Surround" 

# Extension of the final video file
DEST_EXT="mkv"

# Handbrake binary to call
HANDBRAKE_CLI='"HandBrakeCLI"'

# Number of threads for HB to use
# Use 'auto' if unsure
HB_THREADS="auto"

# Have HandBrake transcode the main feature only.  BluRay discs must have RIPMETHOD="backup" for this to work.
# If MAINFEATURE is True, blurays will be backed up to the HD and then HandBrake will go to work on the backed up
# files.  For normal DVDs, ARM will bypass MakeMKV and hand off the dvd directly to HandBrake.  This will require 
# libdvdcss2 be installed.
# NOTE: For the most part, HandBrake correctly identifies the main feature on movie DVD's, although it is not perfect. 
# However, it does not handle tv shows well at all.  You will likely want this value to be False when ripping tv shows.
MAINFEATURE=False

# Additional HandBrake arguments.  
HB_ARGS="-s 1,2,3,4,5,6,7,8,9"

#####################
## Enable Plex Use ##
#####################

# Set this setting to True, to enable Plex Extras support
PLEX_SUPPORT=False
