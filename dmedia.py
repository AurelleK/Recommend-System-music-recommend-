#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 21 13:51:39 2019

@author: brandon
"""
import urllib.request
from bs4 import BeautifulSoup
from os import system

def titleCase(str):
    '''
    A function to convert the given song name to title case.
    '''
    words = []
    for word in str.split():
        if word not in ['in', 'the', 'for', 'of', 'a', 'at', 'an', 'is', 'and']:
            words.append(word.capitalize())
        else:
            words.append(word)
    return ' '.join(words)
   
pathToSave = "/home/brandon/MUSIR/tmp/"

def getVidID(song, URL):
    '''
    This function gets the ID of the Video you have to download.
    '''
    search = song + ' lyrics'
    searchQuery = '+'.join(search.split())
    searchURL = URL + searchQuery
    
    response = urllib.request.urlopen(searchURL)
    soup = BeautifulSoup(response.read(), "html.parser")

    vidID = soup.body.find_all(class_="yt-uix-tile-link")[0]['href']
    return vidID

def download(song):
    print("Downloading " + titleCase(song))
    URL = 'https://www.youtube.com/results?search_query='
    vidID = getVidID(song, URL)
    link = 'https://www.youtube.com' + vidID
    system("youtube-dl -x --audio-format mp3 -q -o \'" + pathToSave + titleCase(song) + ".%(ext)s\' \'" + link + "\'")
    print("Downloaded " + titleCase(song) + "\n") 

