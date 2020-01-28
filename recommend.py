#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 21 12:51:46 2019

@author: brandon

 > All last.fm api methods return song metadate in the format {title:[artist, image_link], ...}
"""

import os
import xml.etree.ElementTree as ET
import requests
import itertools
import eyed3

path = '/home/brandon/MUSIR/songs/'

def recommend(N=5):
    a = artistTopTracks()
    b = similarTracks()
    c = TopTracks()
    z = {**c , **{**a, **b}}
    if len(z) < N:
        return z
    return dict(itertools.islice(z.items(), N))

def load_songs(path=path, only_artists=False):
    metadata = []
    for song in os.listdir(path):
        audiofile = eyed3.load(path + song)
        metadata.append((audiofile.tag.title, audiofile.tag.artist))
    if not only_artists:
        return metadata
    return list(zip(*metadata))[1]
        
def artistTopTracks(num_tracks=2):
    """
    > num_tracks: specifies max number of tracks per artist
    """
    result = {}
    url =  'http://ws.audioscrobbler.com/2.0/'
    artists = load_songs(only_artists=True)
    for artist in artists:
        params = {
                "method": "artist.gettoptracks",
                "artist": artist,
                "limit" : num_tracks,
                "api_key": "6a28ca11484fbda5a88c06d7398c8c55"
                }
        response = requests.get(url, params=params)
        root = ET.fromstring(response.content) #root.tag is always last lfm
        for track in root[0].findall('track'):
            title = track.find('name').text
            img_link = track.findall('image')[2].text
            result[title] = [artist, img_link]
    return result


def similarTracks(limit=1):
    """
    > num_tracks: specifies max number of tracks per artist
    """
    result = {}
    url =  'http://ws.audioscrobbler.com/2.0/'
    songs = load_songs()
    for song in songs:
        params = {
                "method": "track.getsimilar",
                "artist": song[1],
                "track" : song[0],
                "limit" : limit,
                "api_key": "6a28ca11484fbda5a88c06d7398c8c55"
                }
        response = requests.get(url, params=params)
        root = ET.fromstring(response.content) 
        for track in root[0].findall('track'):
            title = track.find('name').text
            artist = track.find('artist').find('name').text
            img_link = track.findall('image')[2]
            result[title] = [artist, img_link]
    return result


def TopTracks(limit=5, country='United States'):
    """
    most popular tracks on Last.fm the previous week by country
    """
    songs = {}
    url =  'http://ws.audioscrobbler.com/2.0/'
    params = {
            "method": "geo.getTopTracks",
            "country": country,
            "limit" : limit,
            "api_key": "6a28ca11484fbda5a88c06d7398c8c55"
            }
    response = requests.get(url, params=params)
    root = ET.fromstring(response.content) 
    for track in root[0].findall('track'):
        title = track.find('name').text
        artist = track.find('artist').find('name').text
        #now get the image
        params2 = {
            "method": "track.getInfo",
            "artist": artist,
            "track" : title,
            "api_key": "6a28ca11484fbda5a88c06d7398c8c55"
            }
    
        r = requests.get(url, params=params2)
        p = ET.fromstring(r.content)
        img_link = p[0].find('album').findall('image')[2].text
        songs[title] = [artist, img_link]
    return songs

