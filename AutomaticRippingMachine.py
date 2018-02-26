import os
import sys
import argparse
import subprocess
import shutil
import logging
import imdb
import pydvdid
import urllib
import xmltodict

from config import *

class ARM:
    def __init__(self, args):
        self.disc_info = args.disc_info
        self.disc_path = args.disc_path

        if not (os.path.exists(self.disc_info)):
            print('Disc not in drive')
            sys.exit()

        if not (os.path.exists(LOGPATH)):
            os.makedirs('LOGPATH')

    def start(self):
        try:
            movie_title, movie_year = self.getTitleViaCrc()
        except:
            movie_title = self.getBlurayTitle()
        else:
            movie_title = self.getMovieTitle()
        
        
        movie_title = movie_title.replace(' ', '_')

        logging.basicConfig(filename='{}{}.txt'.format(LOGPATH, movie_title), level=logging.DEBUG)
        
        logging.debug('Found movie: {}'.format(movie_title))
        
        raw_directory = os.path.join(RAWPATH, movie_title)
        logging.debug('Creating {}'.format(raw_directory))
        if not os.path.exists(raw_directory):
            os.makedirs(raw_directory)
            
        rip_string = "makemkvcon mkv {} dev:{} all {} --minlength={} -r >> {}{}.txt 2>&1".format(MKV_ARGS, self.disc_path, raw_directory, MINLENGTH, LOGPATH, movie_title)
        logging.debug("About to run: {}".format(rip_string))
        rip = subprocess.run(rip_string, shell=True)
        
        logging.debug("Result of MakeMKV is: {}".format(rip))
        
        logging.debug("Ejecting Disc")
        subprocess.call("eject", shell=True)
        
        
        transcoded_directory = os.path.join(ARMPATH, movie_title)
        logging.debug("Path to save HB output: {}".format(transcoded_directory))
        transcoded_directory_extras = os.path.join(transcoded_directory, "Featurettes")
        
        if not os.path.exists(transcoded_directory_extras):
            os.makedirs(transcoded_directory_extras)

        for file in os.listdir(raw_directory):
            transcoded_string = "{} -i {} -o {} --preset=\"{}\" {} >> {}{}.txt 2>&1".format(HANDBRAKE_CLI, os.path.join(raw_directory, file), os.path.join(transcoded_directory_extras, file), HB_PRESET, HB_ARGS, LOGPATH, movie_title)
            logging.debug('About to run: {}'.format(transcoded_string))
            hb = subprocess.run(transcoded_string, shell=True)
            logging.debug("Result of transcoding {}: {}".format(file, hb))
        
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
        
        movie_directory = os.path.join(MEDIA_DIR, movie_title)
        if not os.path.exists(movie_directory):
            os.makedirs(movie_directory)
        
        logging.debug("Moving all files to {}".format(movie_directory))
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
        
        return title.strip()
        
    def verifyViaImdb(self, movie_title):
        ia = imdb.IMDb()
        title = movie_title.lower()
        
        search_results = ia.search_movie(title)
        return search_results[0]['title'], search_results[0]['kind']

    def getTitleViaCrc(self):
        crc64 = compute(self.disc_path)
        metadata = urlopen("http://metaservices.windowsmedia.com/pas_dvd_B/template/GetMDRDVDByCRC.xml?CRC={0}".format(crc64)).read()
        metadata_dict = xmltodict.parse(metadata)
        confirmedTitle = metadata_dict['METADATA']['MDR-DVD']['dvdTtitle']
        confirmedYear = metadata_dict['METADATA']['MDR-DVD']['releaseDate']
        
        return confirmedTitle, confirmedYear
        
    def getBlurayTitle():
        """ Get's Blu-Ray title by parsing XML in bdmt_eng.xml """
        with open(args.path + '/BDMV/META/DL/bdmt_eng.xml', "rb") as xml_file:
            doc = xmltodict.parse(xml_file.read())
    
    
        bluray_title = doc['disclib']['di:discinfo']['di:title']['di:name']
    
        bluray_modified_timestamp = os.path.getmtime(args.path + '/BDMV/META/DL/bdmt_eng.xml')
        bluray_year = (datetime.datetime.fromtimestamp(bluray_modified_timestamp).strftime('%Y'))
    
        bluray_title = unicodedata.normalize('NFKD', bluray_title).encode('ascii', 'ignore').decode()
    
        bluray_title = bluray_title.replace(' - Blu-rayTM', '')
        bluray_title = bluray_title.replace(' - BLU-RAYTM', '')
        bluray_title = bluray_title.replace(' - BLU-RAY', '')
        bluray_title = bluray_title.replace(' - Blu-ray', '')
        return bluray_title + " (" + bluray_year + ")"


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
