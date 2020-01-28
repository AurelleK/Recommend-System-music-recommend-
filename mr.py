#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 27 11:09:26 2019

@author: root
"""
import os
import shutil

import kivy
from kivy.app import App
from kivy.config import Config
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.properties import ObjectProperty, NumericProperty

from pydub import AudioSegment
import simpleaudio as sa

import recommend
import dmedia
import eyed3

kivy.require('1.11.1')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

NEW_SONG = False

class Playlist(Screen):
    """
    TODO: > continuous loop playback
          > playback play & pause
    
    > self.h = height of Gridlayout holding playlist image buttons is incremented each time a button is added.
    > self.h is set as a Property outside __init__ so it is defined from first frame and accessible
      afterwards self i.e play.height can use it to change value. 
      If defined in __init__, a clock cycle needs to be defined to redraw the gridlaylout
      with the new height for every frame to continually repeat self.play.height = self.h
    """
    h = NumericProperty(480)
    def __init__(self, **kwargs):
        super(Playlist, self).__init__(**kwargs)
        playlist = ObjectProperty(None) #reference to Gridlayout
        self.playlist.height = self.h
        self.playback = None
        self.song_playing = False
        self.id_song_playing = None # holds title of current song playing (not in dmedia.titleCase format!)
        self.num_buttons = 0
        self.song_path = '/home/brandon/MUSIR/songs/'
        self.tmp_path = '/home/brandon/MUSIR/tmp/'
        
        Clock.schedule_interval(self.check_new_song, 1/15.0)
        Clock.schedule_once(self.load_songs)
    
    def load_songs(self, dt):
        """
        loads songs in songs/ and calls self.add_song to add each one
        """
        for song in os.listdir(self.song_path):
            self.add_song(song.split('.')[0]) #stripping th .mp3 extension
    
    def play(self, instance):
        if self.song_playing:
            if self.id_song_playing == instance.title:
                self.playback.stop()
                self.song_playing = False
                self.id_song_playing = None
            else:
                self._play(instance.title)
        else:
            self._play(instance.title)
    
    def _play(self, song_name):
        audio_name = dmedia.titleCase(song_name)#All songs are saved with the dmedia.titleCase format
        sound = AudioSegment.from_mp3(self.song_path + audio_name + '.mp3')
        self.playback = sa.play_buffer(
        sound.raw_data, 
        num_channels=sound.channels, 
        bytes_per_sample=sound.sample_width, 
        sample_rate=sound.frame_rate
    )
        self.song_playing = True
        self.id_song_playing = song_name
            
    def load_new_song(self):
        tmp_list = os.listdir(self.tmp_path)
        if len(tmp_list) < 1: raise Exception('No new Song in Found')
        new_song = tmp_list[0]
        shutil.move(self.tmp_path + new_song, self.song_path)
        global NEW_SONG
        NEW_SONG = False
        self.add_song(new_song)
        
    def add_song(self, audio_name):
        """
        Adds song to playlist
        """
        tags = self.get_tags(audio_name)
        button = SongButton(text=tags[1] + ' - ' + tags[0],
                            title=tags[0],
                            artist=tags[1]
                            )
        button.bind(on_release=self.play)
        self.h = self.h + 20 if self.num_buttons > 8 else self.h #bug here. causes app crash without default test button in ScrollView
        self.playlist.height = self.h ## same bug here too. possible fix is to move these lines to after self.playlist.add_widget()
        self.playlist.add_widget(button)
        self.num_buttons += 1
    
    def get_tags(self, song_name):
        # TODO load and return image buffer
        tags = []
        audiofile = eyed3.load(self.song_path + song_name + '.mp3')
        tags.append(audiofile.tag.title)
        tags.append(audiofile.tag.artist)
        return tags
    
    def check_new_song(self, dt):
        global NEW_SONG
        if NEW_SONG:
            self.load_new_song()
  
    

class Recommendations(Screen):
    h = NumericProperty(480)
    def __init__(self, **kwargs):
        super(Recommendations, self).__init__(**kwargs)
        playlist = ObjectProperty(None) #reference to Gridlayout
        self.playlist.height = self.h
        self.num_buttons = 0
        self.tmp_path = '/home/brandon/MUSIR/tmp/'
    
    def recommend(self):
        recoms = recommend.recommend(N=4) # Get recommendations & load to playlist
        for song in recoms:
            button = SongButton(text=song + ' - ' + recoms[song][0],
                                title=song,
                                artist=recoms[song][0],
                                img_link=recoms[song][1]
                            )
            button.bind(on_release=self.download_song)
            self.h = self.h + 20 if self.num_buttons > 8 else self.h
            self.playlist.height = self.h
            self.playlist.add_widget(button)
            self.num_buttons += 1
    
    def download_song(self, instance):
        """
        downloads ands tags file. Then signals main playlist
        """
        tags = []
        audio_name = dmedia.titleCase(instance.title)
        dmedia.download(instance.title)
        
        tags.append(instance.title)
        tags.append(instance.artist)
        tags.append(instance.img_link)
        self.tag(audio_name, tags)
        global NEW_SONG 
        NEW_SONG = True
        
    def tag(self, audio_name, tags):
        audiofile = eyed3.load(self.tmp_path + audio_name + '.mp3')
        audiofile.tag.title = u'{}'.format(tags[0])
        audiofile.tag.artist = u'{}'.format(tags[1])
        audiofile.tag.images.set(type_=3, img_data=None, mime_type=None, img_url=u'{}'.format(tags[2]))
        audiofile.tag.save()

class SongButton(Button):
    pass    
    

class MusicApp(App):
    
    def build(self):
        sm = ScreenManager()
        screens = [Playlist(name='playlist'), Recommendations(name='recomms')]
        for screen in screens:
            sm.add_widget(screen)
        
        return sm

    
if __name__ == '__main__':
    m = MusicApp()
    m.run()