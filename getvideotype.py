#!/usr/bin/python

import sys
import argparse
import urllib
import os
#import xmltodict
import json
import re
import imdb

def entry():
    """ Entry to program, parses arguments"""
    parser = argparse.ArgumentParser(description='Get type of dvd--movie or tv series')
    parser.add_argument('-t', '--title', help='Title', required=True)
    parser.add_argument('-k', '--key', help='API_Key', dest='omdb_api_key', required=True)
    parser.add_argument('-f', '--full_title', help='Get the full title from IMDB', required=False, default=False)

    return parser.parse_args()

def getdvdtype():

    title = args.title
    title = title.lower()
    head, sep, tail = re.sub(r'\W+', ' ', title).partition('season')

    #print(args.full_title)
    if (args.full_title == False):
	    ia = imdb.IMDb()
	    search_results = ia.search_movie(head)
	    try:
		if (search_results[0]['kind'] == 'tv series'):
		    return 'tv'
		elif (search_results[0]['kind'] == 'movie'):
		    return 'movie'
		else:
		    return 'fail'
	    except IndexError:
		return 'fail'
    else:
        return head


    """ Queries OMDbapi.org for title information and parses if it's a movie
        or a tv series """
    dvd_title = args.title
    needs_new_year = "false"
    omdb_api_key = args.omdb_api_key

    try:
        year = dvd_title[(dvd_title.rindex('(')):len(dvd_title)]
    except:
        year = ""
    else:
        year = re.sub('[()]','', year)

    try:
        dvd_title = dvd_title[0:(dvd_title.rindex('('))].strip()
    except:
        dvd_title_clean = cleanupstring(dvd_title)
    else:
        dvd_title_clean = cleanupstring(dvd_title)

    if year is None:
        year = ""

    dvd_type = callwebservice(omdb_api_key, dvd_title_clean, year)
    # print (dvd_type)

    # handle failures
    # this is kind of kludgy, but it kind of work...
    if (dvd_type == "fail"):

        # first try submitting without the year
        dvd_type = callwebservice(omdb_api_key, dvd_title_clean, "")
        # print (dvd_type)

        if (dvd_type != "fail"):
            #that means the year is wrong. 
            needs_new_year = "true"

        if (dvd_type == "fail"):
            # second see if there is a hyphen and split it
            if (dvd_title.find("-") > -1):
                dvd_title_slice = dvd_title[:dvd_title.find("-")]
                dvd_title_slice =cleanupstring(dvd_title_slice)
                dvd_type = callwebservice(omdb_api_key, dvd_title_slice)
                
            # if still fail, then try slicing off the last word in a loop
            while dvd_type == "fail" and dvd_title_clean.count('+') > 0:
                dvd_title_clean = dvd_title_clean.rsplit('+', 1)[0]
                dvd_type = callwebservice(omdb_api_key, dvd_title_clean)
        
    if needs_new_year == "true":
        #pass the new year back to bash to handle
        global new_year
        return dvd_type + "#" + new_year
    else:
        return dvd_type

def cleanupstring(string):
    # clean up title string to pass to OMDbapi.org
    string = string.strip()
    return re.sub('[_ ]',"+",string)

def callwebservice(omdb_api_key, dvd_title, year=""):
    """ Queries OMDbapi.org for title information and parses if it's a movie
        or a tv series """
    # print (dvd_title)
    # print (year)
    # print (omdb_api_key)

    try:
        dvd_title_info_json = urllib.request.urlopen("http://www.omdbapi.com/?t={1}&y={2}&plot=short&r=json&apikey={0}".format(omdb_api_key, dvd_title, year)).read()
    except:
        return "fail"
    else:
        doc = json.loads(dvd_title_info_json.decode())
        if doc['Response'] == "False":
            return "fail"
        else:
            global new_year 
            new_year = doc['Year']
            return doc['Type']

args = entry()

dvd_type = getdvdtype()
print(dvd_type)
