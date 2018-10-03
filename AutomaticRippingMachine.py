import os
import sys
import argparse
import distutils
import subprocess
import shutil
import logging
import imdb
import pydvdid
import urllib
import xmltodict

import psutil

from config import *

class ARM:
    def __init__(self, args):
        self.disc_info = args.disc_info
        self.disc_path = args.disc_path

        if not (os.path.exists(LOGPATH)):
            os.makedirs(LOGPATH)


    def start(self):

        if not (os.path.exists(self.disc_info)):
            print('Disc not in drive')
            sys.exit()

        movie_title, movie_year = self.getMovieTitle()

        if movie_title is None and movie_year is None:
            return

        try:
            movie_title, movie_year = self.getTitleViaCrc()
        except Exception as e:
            print (e)

        imdb_title, movie_type = self.verifyViaImdb(movie_title, movie_year)
        if not (imdb_title == []):
            movie_title = imdb_title
        else:
            movie_type = 'movie'

        subprocess.run('umount /media/dvd', shell = True)

        movie_title = movie_title.replace(' ', '_')
        for ch in r"/()!@#$%^&*[]{}?'\"":
            movie_title = movie_title.replace(ch, '')

        if(LOG_SINGLE_FILE):
            logging.basicConfig(filename='ARM.txt', level=logging.DEBUG)
        else:
            logging.basicConfig(filename='{}{}-{}.txt'.format(LOGPATH, movie_title, movie_year), level=logging.DEBUG)

        logging.debug('Found movie: {}'.format(movie_title) )
        logging.debug('Movie Year: {}'.format(movie_year) )
        logging.debug('Movie Type: {}'.format(movie_type) )

        raw_directory = os.path.join(RAWPATH, "{}-{}".format( movie_title, movie_year) )
        logging.debug('Creating {}'.format(raw_directory))
        if os.path.exists(raw_directory):
            pass
            shutil.rmtree(raw_directory)
        os.makedirs(raw_directory)

        rip_string = r'makemkvcon mkv {} dev:{} all {} --minlength={} -r '.format( #>> {}{}-{}.txt 2>&1".format(
            MKV_ARGS, 
            self.disc_path, 
            raw_directory, 
            MINLENGTH #, 
            #LOGPATH, 
            #movie_title,
            #movie_year
            )

        log = open("{}{}-{}.txt".format(LOGPATH, movie_title, movie_year), 'a')
        logging.debug("About to run: {}".format(rip_string))
        rip = subprocess.call(rip_string, shell=True, stdout = log, stderr=subprocess.STDOUT)
        #log.close()

        try:
            logging.debug("Result of MakeMKV is: {}".format(rip))

            logging.debug('Return code: {}'.format(rip))
            if rip == 253:
                logging.debug("MakeMKV is out of date.  Need to update.")
                result = supbrocess.call("apt-get install --only-install makemkv-bin")
                rip = subprocess.call(rip_string, shell=True, stdout = log, stderr = subprocess.STDOUT)

            if not (rip == 0):
                logging.debug('Problem detected with makeMKV. Exiting')
                subprocess.call('eject', shell=True)
                sys.exit()
        except Exception as e:
            logging.debug(e)
            logging.debug("There was a problem running MakeMKV.  Aborting.")
            pass
            sys.exit()

        logging.debug("Ejecting Disc")
        logging.debug(subprocess.call("eject", shell=True) )

        logging.debug('MakeMKV finished. Adding job to transcoding queue.')
        logging.debug("Starting thread to run handbrake.")

        import threading
        hb = threading.Thread(target=self.transcode, args=(movie_title, movie_year, raw_directory, movie_type) )
        hb.start()

        logging.debug("Thread started.")


    def transcode(self, movie_title, movie_year, raw_directory, movie_type):

        print("in transcode")

        if(LOG_SINGLE_FILE):
            logging.basicConfig(filename='ARM.txt', level=logging.DEBUG)
        else:
            logging.basicConfig(filename='{}{}-{}.txt'.format(LOGPATH, movie_title, movie_year), level=logging.DEBUG)

        import time
        logging.debug("Current CPU Percentage: {}".format( psutil.cpu_percent() ) )
        while psutil.cpu_percent() > 75:
            time.sleep(60 * 1)

        transcoded_directory = os.path.join(ARMPATH, "{}-{}".format(movie_title, movie_year) )
        logging.debug("Path to save HB output: {}".format(transcoded_directory))
        transcoded_directory_extras = os.path.join(transcoded_directory, "Featurettes")

        counter = 1
        while os.path.exists(transcoded_directory_extras):
            #shutil.rmtree(transcoded_directory_extras)
            counter = counter + 1
            logging.debug("Folder {} already exists. Creating new folder.".format(transcoded_directory_extras) )
            transcoded_directory = os.path.join(ARMPATH, "{}-{}_disc_{}".format(movie_title, movie_year, counter) )

            if('movie' in movie_type):
                transcoded_directory_extras = os.path.join(transcoded_directory, "Featurettes")
            else:
                transcoded_directory_extras = transcoded_directory

        os.makedirs(transcoded_directory_extras)

        logging.debug("raw_directory: {}".format(raw_directory))
        for file in os.listdir(raw_directory):
            #for ch in r'()[]':
            #    file = file.replace(ch, '\\'+ch)

            logging.debug("File found: {}".format(file))

            transcoded_string = "{} -i {} -o {} --preset=\"{}\" {} -x threads={}".format( # >> {}{}-{}.txt 2>&1".format(
                HANDBRAKE_CLI,
                os.path.join(raw_directory, file),
                os.path.join(transcoded_directory_extras, file),
                HB_PRESET,
                HB_ARGS ,
                HB_THREADS
                #LOGPATH,
                #movie_title,
                #movie_year
                )

            log = open("{}{}-{}.txt".format(LOGPATH, movie_title, movie_year), 'a')
            logging.debug('About to run: {}'.format(transcoded_string))
            hb = subprocess.call(transcoded_string, shell=True, stdout = log, stderr = subprocess.STDOUT)
            #log.close()
            logging.debug("Result of transcoding {}: {}".format(file, hb))

        if(DELETE_RAW):
            logging.debug("Removing dir: {}".format(raw_directory))
            shutil.rmtree(raw_directory)

        if('movie' in movie_type):
            temp = ('',0)
            for file in os.listdir(transcoded_directory_extras):
                filepath = os.path.join(transcoded_directory_extras, file)
                if (os.path.getsize(filepath) > temp[1]):
                    temp = (file, os.path.getsize(filepath))

                os.system('chmod 777 {}'.format(filepath))

            logging.debug("Moving largest file to {}".format(os.path.join(transcoded_directory)))
            logging.debug(temp[0])
            shutil.copy(os.path.join(transcoded_directory_extras, temp[0]), os.path.join(transcoded_directory, "{}_({}).{}".format( movie_title, movie_year, DEST_EXT) ) )

            movie_directory = os.path.join(MEDIA_DIR, "Movies",    "{}_({})".format(movie_title, movie_year) )
        else:
            movie_directory = os.path.join(MEDIA_DIR, "TV_Series", "{}_({})".format(movie_title, movie_year) )

        logging.debug("Moving all files to {}".format(movie_directory))

    #        if('movie' in movie_type):
        try:
            if os.path.exists(movie_directory):
                 if 'movie' in movie_path:
                     shutil.rmtree(movie_directory)
                 else:
                     movie_directory = os.path.join(MEDIA_DIR, "{}_({})_disc_{}".format(movie_title, movie_year, counter) )

            shutil.copytree(transcoded_directory, movie_directory)

        except Exception as e:
            logging.debug(e)
            logging.debug("Files already exist.")
            sys.exit()
    #        else:
            #Rename and move TV files here
    #            pass

        if(DELETE_RAW):
            logging.debug("Removing {}".format(transcoded_directory))
            try:
                shutil.rmtree(transcoded_directory)
            except Exception as e:
                logging.debug(e)

            logging.debug("Removing {}".format(self.disc_info))
            try:
                subprocess.run('rm {}'.format(self.disc_info))
            except Exception as e:
                logging.debug(e)

        logging.debug("Successful!")
        #subprocess.call("eject", shell=True)

    def getMovieTitle(self):
        file = open(self.disc_info, 'r')
        disc_data = file.readlines()
        file.close()

        title = ''
        year=''
        for i in disc_data:
            if ("ID_FS_LABEL" in i):
                print (i)
                title = i.split('=')[-1]
                break
            elif ("ID_FS_UUID" in i):
                print (i)
                year = i.split()[-1].split('-')[0]
            elif ("ID_CDROM_MEDIA_TRACK_COUNT_AUDIO" in i):
                subprocess.call(['abcde', '-d', self.disc_path])
                return None, None

        if not title:
            print( "No title found. Unlikely this is a DVD" )
            #subprocess.call("eject", shell=True)
            sys.exit()

        if ('/' in title):
            title = title.replace('/', '-')

        print ("Found Title: {}, year: {}".format(title, year))

        return title.strip(), year.strip()

    def verifyViaImdb(self, movie_title, movie_year):
        ia = imdb.IMDb()
        title = movie_title.lower()
        title = title.replace('_', ' ')
        year = movie_year.strip()

        search_results = ia.search_movie(title)
        while len(search_results) == 0 and len(title) > 0:
            title = title[:-1]
            search_results = ia.search_movie(title)

        for movie in search_results:
            if (movie['year'] == year):
                return movie['title'], movie['kind']

        return [],[]



    def getTitleViaCrc(self):
        #if (os.path.exists('/media/dvd')):
        #    subprocess.run('rm -r /media/dvd')

        try:
            subprocess.run('mkdir -p /media/dvd', shell=True)
            subprocess.run('mount /dev/sr0 /media/dvd', shell=True)
        except Exception as e:
            logging.debug(e)

        crc64 = pydvdid.compute('/media/dvd')

        metadata = urllib.request.urlopen("http://metaservices.windowsmedia.com/pas_dvd_B/template/GetMDRDVDByCRC.xml?CRC={0}".format(crc64)).read()
        metadata_dict = xmltodict.parse(metadata)
        confirmedTitle = metadata_dict['METADATA']['MDR-DVD']['dvdTitle']
        confirmedYear = metadata_dict['METADATA']['MDR-DVD']['releaseDate']
        confirmedYear = confirmedYear.split()[0]

        try:
            subprocess.run('umount /media/dvd', shell=True)
        except:
            pass
        #subprocess.run('rm -r /media/dvd', sshell = True)

        return confirmedTitle, confirmedYear

    def getBlurayTitle(self):
        """ Get's Blu-Ray title by parsing XML in bdmt_eng.xml """
        with open('/media/dvd' + '/BDMV/META/DL/bdmt_eng.xml', "rb") as xml_file:
            doc = xmltodict.parse(xml_file.read())

        bluray_title = doc['disclib']['di:discinfo']['di:title']['di:name']
        
        bluray_modified_timestamp = os.path.getmtime('/media/dvd' + '/BDMV/META/DL/bdmt_eng.xml')
        bluray_year = (datetime.datetime.fromtimestamp(bluray_modified_timestamp).strftime('%Y'))
        
        bluray_title = unicodedata.normalize('NFKD', bluray_title).encode('ascii', 'ignore').decode()
        
        bluray_title = bluray_title.replace(' - Blu-rayTM', '')
        bluray_title = bluray_title.replace(' - BLU-RAYTM', '')
        bluray_title = bluray_title.replace(' - BLU-RAY', '')
        bluray_title = bluray_title.replace(' - Blu-ray', '')
        return bluray_title


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--disc_path", help="Path to disc to rip")
    parser.add_argument("--disc_info", help="Data about disc to rip")
#    parser.add_argument("--f", help='To only transcribe.')
    args = parser.parse_args()
    arm = ARM(args)

#    if arm.transcode_file is None:
    arm.start()
 #   else:
  #      try:
   #         arm.transcode()
    #    except Exception as e:
     #       print (e)
    #subprocess.call('eject')
