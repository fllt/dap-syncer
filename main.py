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




class sync_itunes:
 #   path_type = enum.Enum('itunes','dap','Common')

    def __init__(self,itunes_music_library_xml,dap_music_folder):
        self.target_playlist_suffix = '#'
        self.xml = plistlib.readPlist(itunes_music_library_xml)
        self.itunes_music_folder = urllib.parse.unquote(self.xml['Music Folder']).replace('file://','',1)
        self.dap_music_folder = dap_music_folder
        self.__load_itunes_library()
        self.__load_dap()
        self.compare_playlists()
        self.__set_result()
    #def convert_path(self,path, convert_type):        
    def __load_itunes_library(self):
        #get new playkists,tracks

        print('loading ituens ribrary')
        self.new_playlists ={}
        self.new_tracks =set()
        
        tracks = self.xml['Tracks']#dictionary
        playlists = self.xml['Playlists']#List
        self.new_tracks_error = set()
        for playlist in playlists:
            if playlist['Name'][-1] == self.target_playlist_suffix:
                playlist_key = os.path.join(self.dap_music_folder, (playlist['Name'] + '.m3u'))
                self.new_playlists[playlist_key] = []
                for  playlist_item in playlist['Playlist Items']:
                    track_id = str(playlist_item['Track ID'])
                    track = tracks[track_id]
                    if 'Location' in track.keys() :
                        itunes_path = urllib.parse.unquote(track['Location']).replace('file://','',1)
                        dap_path = itunes_path.replace(self.itunes_music_folder,self.dap_music_folder,1)
                        common_path = itunes_path.replace(self.itunes_music_folder,'',1)
                        #add current m3u
                        common_path_nfc = unicodedata.normalize("NFC", common_path)
                        self.new_playlists[playlist_key].append(common_path_nfc)
                        # add latest tracks
                        self.new_tracks.add(common_path)
                    else :
                        self.new_tracks_error.add(track_id)
                if len(self.new_playlists[playlist_key])==0:
                    del self.new_playlists[playlist_key]
                        
 
        print('loaded ' + str(len(self.new_playlists)) + ' playlists and ' + str(len(self.new_tracks)) + ' tracks')
        print('error_tracks: ' + str(len(self.new_tracks_error)))
    def __load_dap(self):
        print('loading dap folder')
        #get preexist playlists, tracks
        if not os.path.exists(self.dap_music_folder) :
            print('not found : ' + self.dap_music_folder)
        self.old_playlists = {}
        self.old_tracks= set()
        
        for root,dirs,files in os.walk(self.dap_music_folder):
            dirs[:] = [d for d in dirs if not d[0] == '.']

            for file in files:
                if not file[0] == '.' :
                    path = os.path.join(root,file)
                    ext = os.path.splitext(path)[1]
                    if ext == '.m3u':
                        self.old_playlists[path] = m3u_handler.read_m3u(path)#tracks
                    else :
                        self.old_tracks.add(path.replace(self.dap_music_folder, '',1))
                                             
        print('loaded ' + str(len(self.old_playlists)) + ' playlists and ' + str(len(self.old_tracks)) + ' tracks')
        
    def compare_playlists(self):
        self.playlists = set(self.new_playlists.keys())|set(self.old_playlists.keys())
        
        self.playlist_action = {}
        for playlist in self.playlists:
            if playlist in self.old_playlists.keys():
                if playlist in self.new_playlists.keys():
                    if self.old_playlists[playlist] == self.new_playlists[playlist]:
                        action = Action.SKIP
                    else:
                        action = Action.UPDATE
                else :
                    action = Action.DELETE
            else :
                action = Action.ADD
            self.playlist_action[playlist] = action
    def __set_result(self):
        playlist_action_counter = Counter(self.playlist_action.values())
        print('playlists...addtitional: ' + str(playlist_action_counter[Action.ADD]))
        print('update: ' + str(playlist_action_counter[Action.UPDATE]))
        print('skip: ' + str(playlist_action_counter[Action.SKIP]))
        print('delete:' + str(playlist_action_counter[Action.DELETE]))
        


        
        self.additional_tracks = self.new_tracks - self.old_tracks
        self.skip_tracks = self.new_tracks & self.old_tracks
        self.delete_tracks = self.old_tracks - self.new_tracks

        print('tracks...addtitional: ' + str(len(self.additional_tracks)) + ' ; skip: ' +str(len(self.skip_tracks)) + ' ; delete:' + str(len(self.delete_tracks)))

    
        
    def execute(self,whatif = False):
        for playlist in self.playlists:
            action = self.playlist_action[playlist]
            if action == Action.ADD:
                print ('ADDING:' + playlist)
                m3u_handler.write_m3u(playlist,self.new_playlists[playlist])
            elif action == Action.DELETE:
                print ('DELETING:' + playlist)
                os.remove(playlist)
            elif action == Action.SKIP:
                print('SKIPPING"' + playlist)
            elif action == Action.UPDATE:
                print ('UPDATING:' + playlist)
                m3u_handler.write_m3u(playlist,self.new_playlists[playlist])

        
        #Delete Tracks
        for track in self.delete_tracks:
            print('delete:' + track)
            dap_path = os.path.join(self.dap_music_folder,track)
            if not os.path.exists( dap_path):
                print('NotFound:' + track)
            else:
                if  not whatif:
                    os.remove(dap_path)
        #Update Tracks
        #SKIP Tracks
    
        # add Tracks
        for track in self.additional_tracks:
            print('Copy :' + track)
            itunes_path = os.path.join(self.itunes_music_folder,track)
            dap_path = os.path.join(self.dap_music_folder,track)
            dap_folder = os.path.dirname(dap_path)
            if not os.path.exists(itunes_path):
                print('NotFound:' + track)
            else:
                if not whatif:
                    os.makedirs(dap_folder,exist_ok =True)
                    shutil.copyfile(itunes_path, dap_path)
        #Delete empty folder
        
si = sync_itunes(file,dap_music_folder)
print('Are you sure to continue sync?')
while True:
    dic = {'Y':True, 'N':False}

    inp = input('[Y]Yes/[N]No? >> ').upper()
    if inp in dic:
        break
    print('Input again.')
if dic[inp]:
    si.execute()
else:
    print('Canceled.')

    
