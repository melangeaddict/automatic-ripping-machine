# ARM (Automatic Ripping Machine) oonfig file

#################
## ARM Options ##
#################

# Distinguish UDF video discs from UDF data discs.  Requires mounting disc so adds a few seconds to the identify script.
ARM_CHECK_UDF=True

# When enabled if the disc is a DVD use dvdid to calculate a crc64 and query Windows Media Meta Services for the Movie Title.
# For BluRays attempts to extract the title from an XML file on the disc
GET_VIDEO_TITLE=True

# Skip transcoding if you want the original MakeMKV files as your final output
# Thiw will produce the highest quality videos (and use the most storage)
# Note: RIPMETHOD must be set to "mkv" for this feature to work
SKIP_TRANSCODE=False

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
MEDIA_DIR="/media/WDMYCLOUD/Movies/"

# Path to directory to hold log files
# Make sure to include trailing /
LOGPATH="/opt/arm/logs/"

# How long to let log files live before deleting (in days)
LOGLIFE=1

# Set to True if you prefer a single log file for all activity versus a separate log per disc.
LOG_SINGLE_FILE=False 

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
HB_PRESET="Very Fast 1080p30" 

# Extension of the final video file
DEST_EXT="mkv"

# Handbrake binary to call
HANDBRAKE_CLI='"HandBrakeCLI"'

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

#####################
## Emby Parameters ##
#####################

# Parameters to enable automatic library scan in Emby.  This will trigger only if MainFeature is True above.

# Scan emby library after succesful placement of mainfeature (see above)
EMBY_REFRESH=False

# Use subfolders in Emby as described here: https://github.com/MediaBrowser/Wiki/wiki/Movie%20naming#movie-extras
EMBY_SUBFOLDERS=True

# Server parameters
# Server can be ip address or domain name
EMBY_SERVER=""
EMBY_PORT="8096"

# Emby authentication fluff parameters.  These can be anything.
EMBY_CLIENT="ARM"
EMBY_DEVICE="ARM"
EMBY_DEVICEID="ARM"

# Emby authentication parameters.  These are parameters that must be set to a current user in Emby.
EMBY_USERNAME=""

# EMBY_USERID is the user ID associated with the username above.  You can find this by going to the following address on your emby server
# <server>:<port>/Users/Public and getting the ID value for the username above.
EMBY_USERID=""

# This is the SHA1 encrypted password for the username above.  You can generate the SHA1 hash of your password by executing the following at
# the command line: 
# echo -n your-password | sha1sum | awk '{print $1}'
# or using an online generator like the one located at http://www.sha1-online.com/
EMBY_PASSWORD=""

#############################
## Notification Parameters ##
#############################

# Notify after Rip?
NOTIFY_RIP=True

# Notify after transcode?
NOTIFY_TRANSCODE=True

# Pushbullet API Key
# Leave empty or comment out to disable Pushbullet notifications
PB_KEY=""

# IFTTT API KEY
# Leave empty or comment out to disable IFTTT notifications
# IFTTT_KEY=""

# IFTTT Event Name
IFTTT_EVENT="arm_event"

# Pushover API User and Application Key
# Leave User key empty or comment out to disable Pushover notifications
PO_USER_KEY=""
PO_APP_KEY=""

# OMDB_API_KEY
# omdbapi.com API Key
# See README-OMDBAPI for background and info
# This is the API key for omdbapi.com queries.
# More info at http://omdbapi.com/
OMDB_API_KEY=""

# Flag to set for EMail Notification 
# Leave empty or comment out to disable email notifications
# This system uses MUTT to send the emails.  A guide for installing and
# configuraing mutt can be found here:
# https://www.garron.me/en/go2linux/send-mail-gmail-mutt.html
# EMAIL_NOTIFY="user@email.com"


