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

from config import *

class ARM:
    def __init__(self, args):
        self.disc_info = args.disc_info
        self.disc_path = args.disc_path
        self.transcode_file = args.f

        if not (os.path.exists(LOGPATH)):
            os.makedirs(LOGPATH)

    def start(self):

        if not (os.path.exists(self.disc_info)):
            print('Disc not in drive')
            sys.exit()

        movie_title, movie_year = self.getMovieTitle()
        #movie_year = ''
        try:
            movie_title, movie_year = self.getTitleViaCrc()
        except Exception as e:
            print (e)
            #movie_title = self.getBlurayTitle()
        
        imdb_title, movie_type = self.verifyViaImdb(movie_title, movie_year)
        if not (imdb_title == []):
            movie_title = imdb_title
        else:
            movie_type = 'movie'

        subprocess.run('umount /media/dvd', shell = True)        
        
        #movie_title = movie_title.replace(' ', '_').replace('/', '_').replace('
        for ch in r' /()!@#$%^&*[]{}?':
            movie_title = movie_title.replace(ch, '_')

        if(LOG_SINGLE_FILE):
            logging.basicConfig(filename='ARM.txt', level=logging.DEBUG)
        else:
            logging.basicConfig(filename='{}{}-{}.txt'.format(LOGPATH, movie_title, movie_year), level=logging.DEBUG)
        
        logging.debug('Found movie: {}'.format(movie_title))
        
        raw_directory = os.path.join(RAWPATH, "{}-{}".format( movie_title, movie_year) )
        logging.debug('Creating {}'.format(raw_directory))
        if os.path.exists(raw_directory):
            pass
            shutil.rmtree(raw_directory)
        os.makedirs(raw_directory)
           
        rip_string = "makemkvcon mkv {} dev:{} all {} --minlength={} -r >> {}{}-{}.txt 2>&1".format(
            MKV_ARGS, 
            self.disc_path, 
            raw_directory, 
            MINLENGTH, 
            LOGPATH, 
            movie_title,
            movie_year
            )
        logging.debug("About to run: {}".format(rip_string))
        rip = subprocess.run(rip_string, shell=True)
        
        try:
            logging.debug("Result of MakeMKV is: {}".format(rip))

            logging.debug('Return code: {}'.format(rip.returncode))
            if not (rip.returncode == 0):
                logging.debug('Problem detected with makeMKV. Exiting')
                subprocess.call('eject', shell=True)
                sys.exit()
        except:
            #sys.exit()
            pass
        
        logging.debug("Ejecting Disc")
        subprocess.call("eject", shell=True)
        
        tempPath = os.path.join(ARMPATH, 'temp_{}-{}.tmp'.format(movie_title, movie_year))
        if not os.path.exists(tempPath):
            os.makedirs(ARMPATH)
        with open(tempPath, 'w') as file:
            file.write(movie_title + '\n')
            file.write(movie_year + '\n')
            file.write(raw_directory)
        

        logging.debug('MakeMKV finished. Adding job to transcoding queue.')

        command = 'echo " /usr/bin/python3 /opt/arm/AutomaticRippingMachine.py --f {} " | at -M now'.format(tempPath)
        logging.debug(command)
        subprocess.Popen(command.split(), shell = True)

                 
    def transcode(self):

        print("in transcode")

        file = open(self.transcode_file, 'r')
        lines = file.readlines()
        file.close

        movie_title = lines[0].strip()
        movie_year = lines[1].strip()
        raw_directory = lines[2].strip()

        if(LOG_SINGLE_FILE):
            logging.basicConfig(filename='ARM.txt', level=logging.DEBUG)
        else:
            logging.basicConfig(filename='{}{}-{}.txt'.format(LOGPATH, movie_title, movie_year), level=logging.DEBUG)

        
        transcoded_directory = os.path.join(ARMPATH, "{}-{}".format(movie_title, movie_year) )
        logging.debug("Path to save HB output: {}".format(transcoded_directory))
        transcoded_directory_extras = os.path.join(transcoded_directory, "Featurettes")
        
        if os.path.exists(transcoded_directory_extras):
            shutil.rmtree(transcoded_directory_extras)
        os.makedirs(transcoded_directory_extras)

        for file in os.listdir(raw_directory):
            for ch in r'()[]':
                file = file.replace(ch, '\\'+ch)

            transcoded_string = "{} -i {} -o {} --preset=\"{}\" {} >> {}{}-{}.txt 2>&1".format(
                HANDBRAKE_CLI, 
                os.path.join(raw_directory, file), 
                os.path.join(transcoded_directory_extras, file), 
                HB_PRESET, 
                HB_ARGS, 
                LOGPATH, 
                movie_title,
                movie_year
                )
            logging.debug('About to run: {}'.format(transcoded_string))
            hb = subprocess.call(transcoded_string, shell=True)
            logging.debug("Result of transcoding {}: {}".format(file, hb))
        
        if(DELETE_RAW):
            logging.debug("Removing dir: {}".format(raw_directory))
            shutil.rmtree(raw_directory)
        
        #if('movie' in movie_type):
        temp = ('',0)
        for file in os.listdir(transcoded_directory_extras):
            filepath = os.path.join(transcoded_directory_extras, file)
            if (os.path.getsize(filepath) > temp[1]):
                temp = (file, os.path.getsize(filepath))
            
            os.system('chmod 777 {}'.format(filepath))
        
        logging.debug("Moving largest file to {}".format(os.path.join(transcoded_directory)))
        logging.debug(temp[0])
        shutil.copy(os.path.join(transcoded_directory_extras, temp[0]), os.path.join(transcoded_directory, "{}-{}.{}".format( movie_title, movie_year, DEST_EXT) ) )
        
        movie_directory = os.path.join(MEDIA_DIR, "{}-{}".format(movie_title, movie_year) )

        logging.debug("Moving all files to {}".format(movie_directory))
        
#        if('movie' in movie_type):
        try:
            tempPath = os.path.join(MEDIA_DIR, "{}-{}".format(movie_title, movie_year))
            if os.path.exists( tempPath):
                shutil.rmtree(tempPath)

            shutil.copytree(transcoded_directory, tempPath)
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
                title = i.split('=')[-1]
                break
            elif ("ID_FS_UUID" in i):
                year = i.split('=')[-1].split('-')[0]

        if not title:
            print( "No title found. Unlikely this is a DVD" )
            subprocess.call("eject", shell=True)
            sys.exit()
        
        if ('/' in title):
            title = title.replace('/', '-')

        print ("Found Title: {}, year: {}".format(title, year))

        return title.strip(), year.strip()
        
    def verifyViaImdb(self, movie_title, movie_year):
        ia = imdb.IMDb()
        title = movie_title.lower()
        year = movie_year.strip()
        
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
    parser.add_argument("--f", help='To only transcribe.')
    args = parser.parse_args()
    arm = ARM(args)

    if arm.transcode_file is None:
        arm.start()
    else:
        try:
            arm.transcode()
        except Exception as e:
            print (e)
        #subprocess.call('eject')
