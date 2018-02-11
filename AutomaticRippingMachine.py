import os
import sys
import argparse
import subprocess
import shutil
import logging
from contextlib import redirect_stdout
import imdb

from config import *

class ARM:
    def __init__(self, args):
        self.disc_info = args.disc_info
        self.disc_path = args.disc_path

        if not (os.path.exists(self.disc_info)):
            print('Disc not in drive')
            sys.exit()

        if not (os.path.exists('/opt/arm/log/')):
            os.makedirs('/opt/arm/log/')

    def start(self):
        movie_title = self.getMovieTitle()
        
        movie_title, movie_type = self.verifyViaImdb(movie_title)
        
        movie_title = movie_title.replace(' ', '_')

        logging.basicConfig(filename='/opt/arm/log/{}.txt'.format(movie_title), level=logging.DEBUG)
        
        logging.debug('Found movie: {}'.format(movie_title))
        
        raw_directory = os.path.join(RAWPATH, movie_title)
        logging.debug('Creating {}'.format(raw_directory))
        if not os.path.exists(raw_directory):
            os.makedirs(raw_directory)
            
        rip_string = "makemkvcon mkv {} dev:{} all {} --minlength={} -r >> /opt/arm/log/{}.txt 2>&1".format(MKV_ARGS, self.disc_path, raw_directory, MINLENGTH, movie_title)
        logging.debug("About to run: {}".format(rip_string))
        rip = subprocess.run(rip_string, shell=True)
        
        logging.debug("Ejecting Disc")
        subprocess.call("eject", shell=True)
        
        
        transcoded_directory = os.path.join(ARMPATH, movie_title)
        logging.debug("Path to save HB output: {}".format(transcoded_directory))
        transcoded_directory_extras = os.path.join(transcoded_directory, "Featurettes")
        for file in os.listdir(raw_directory):
            transcoded_string = "{} -i {} -o {} --preset={} {} >> /opt/arm/log/{}.txt 2>&1".format(HANDBRAKE_CLI, os.path.join(raw_directory, file), os.path.join(transcoded_directory_extras, file), HB_PRESET, HB_ARGS, movie_title)
            logging.debug('About to run: {}'.format(transcoded_string))
            subprocess.run(transcoded_string, shell=True)
        
        logging.debug("Removing dir: {}".format(raw_directory))
        shutil.rmtree(raw_directory)
        
        temp = ('',0)
        for file in os.listdir(transcoded_directory_extras):
            filepath = os.path.join(transcoded_directory_extras, file)
            if (os.path.getsize(filepath) > temp[1]):
                temp = (file, os.path.getsize(filepath))
            
            os.system('chmod 777 {}'.format(filepath))
        
        logging.debug("Moving largest file to {}".format(os.path.join(transcoded_directory)))
        shutil.move(os.path.join(transcoded_directory_extras, temp[0]), os.path.join(transcoded_directory, movie_title + ".mkv"))
        
        # movie_directory = os.path.join(MEDIA_DIR, movie_title)
        # if not os.path.exists(movie_directory):
        #     os.makedirs(movie_directory)
        
        logging.debug("Moving all files to {}".format(MEDIA_DIR))
        shutil.move(transcoded_directory, MEDIA_DIR)
        
        logging.debug("Removing {}".format(transcoded_directory))
        shutil.rmtree(transcoded_directory)
    
    def getMovieTitle(self):
        file = open(self.disc_info, 'r')
        disc_data = file.readlines()
        file.close()
        
        title = ''
        for i in disc_data:
            if ("ID_FS_LABEL" in i):
                title = i.split('=')[1]
                break

        if not title:
            print( "No title found. Unlikely this is a DVD" )
            subprocess.call("eject", shell=True)
            sys.exit()
        
        return title
        
    def verifyViaImdb(self, movie_title):
        ia = imdb.IMDb()
        title = movie_title.lower()
        
        search_results = ia.search_movie(title)
        return search_results[0]['title'], search_results[0]['kind']



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("disc_path", help="Path to disc to rip")
    parser.add_argument("disc_info", help="Data about disc to rip")
    args = parser.parse_args()
    print("Can I see this?")
    arm = ARM(args)
    #try:
    arm.start()
    #except Exception as e:
    #    print (e)
        #subprocess.call('eject')
