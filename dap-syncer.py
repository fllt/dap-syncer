
import os
import plistlib
import re
import configparser
#import enum
import urllib.parse
import shutil
#from pathlib import path
import m3u_handler
import unicodedata

from  const import Action
from collections import Counter
config = configparser.ConfigParser()
config.read('config.ini')

file =config['DEFAULT']['itunesmusiclibraryxml']
dap_music_folder = config['DEFAULT']['dapfolder']


def load_itunes_library(itunes_music_library_xml):
    return updating_playlists, updating_tracks

def load_rhythmbox_music_library(music_library_path):
    return updating_playlists, updating_tracks

def load_dap_directory(dap_path):
    return existing_playlists, existing_tracks

def compare_playlists(existing_playlists,existing_tracks,updating_playlists,updating_tracks):
    return additional_playlist

def dap_syncer():
    if True:
        updating_playlists, updating_tracks = load_itunes_library()
    else:
        updating_playlists, updating_tracks = load_rhythmbox_library()

    existing_playlists, existing_tracks = load_dap_directory()

    
