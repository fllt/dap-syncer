import os
import plistlib
import re
#import enum
import urllib.parse
import shutil
#from pathlib import path
file ="/Users/Fumito/Music/iTunes/iTunes Music Library.xml"
destination_music_folder = '/Volumes/UNTITLED/'

#class m3u_controller:
#    def __init__(self):
#
#    def comvert_from_m3u(self,path):
#        
#
#    def Load_m3u(self,path,tracks):
        


class sync_itunes:
 #   path_type = enum.Enum('Source','Destination','Common')

    def __init__(self,itunes_music_library_xml,destination_music_folder):
        self.target_playlist_suffix = '#'
        self.xml = plistlib.readPlist(itunes_music_library_xml)
        self.source_music_folder = urllib.parse.unquote(self.xml['Music Folder']).replace('file://','',1)
        self.destination_music_folder = destination_music_folder
        self.__load_itunes_library()
        self.__load_destination()
        self.__set_result()
    #def convert_path(self,path, convert_type):        
    def __load_itunes_library(self):
        #get updated playkists,tracks

        print('loading ituens ribrary')
        self.updated_playlists ={}
        self.updated_tracks =set()
        
        tracks = self.xml['Tracks']#dictionary
        playlists = self.xml['Playlists']#List
        self.updated_tracks_error = set()
        for playlist in playlists:
            if playlist['Name'][-1] == self.target_playlist_suffix:
                playlist_key = playlist['Name'] + '.m3u'
                self.updated_playlists[playlist_key] = []
                for  playlist_item in playlist['Playlist Items']:
                    track_id = str(playlist_item['Track ID'])
                    track = tracks[track_id]
                    if 'Location' in track.keys() :
                        source_path = urllib.parse.unquote(track['Location']).replace('file://','',1)
                        destination_path = source_path.replace(self.source_music_folder,self.destination_music_folder,1)
                        common_path = source_path.replace(self.source_music_folder,'',1)
                        #add current m3u
                        self.updated_playlists[playlist_key].append(destination_path)
                        # add latest tracks
                        self.updated_tracks.add(common_path)
                    else :
                        self.updated_tracks_error.add(track_id)
                        
 
        print('loaded ' + str(len(self.updated_playlists)) + ' playlists and ' + str(len(self.updated_tracks)) + ' tracks')
        print('error_tracks: ' + str(len(self.updated_tracks_error)))
    def __load_destination(self):
        print('loading destination folder')
        #get preexist playlists, tracks
        if not os.path.exists(self.destination_music_folder) :
            print('not found : ' + self.destination_music_folder)
        self.existing_playlists = {}
        self.existing_tracks= set()
        
        for root,dirs,files in os.walk(self.destination_music_folder):
            for file in files:
                if not file[0] == '.' :
                    path = os.path.join(root,file)
                    ext = os.path.splitext(path)[1]
                    if ext == '.m3u':
                        self.existing_playlists[path] = load_m3u(path)#tracks
                    else :
                        self.existing_tracks.add(path.replace(self.destination_music_folder, '',1))
                                             
        print('loaded ' + str(len(self.existing_playlists)) + ' playlists and ' + str(len(self.existing_tracks)) + ' tracks')
    def __set_result(self):
        self.additional_tracks = self.updated_tracks - self.existing_tracks
        self.skip_tracks = self.updated_tracks & self.existing_tracks
        self.delete_tracks = self.existing_tracks - self.updated_tracks

        print('tracks...addtitional: ' + str(len(self.additional_tracks)) + ' ; skip: ' +str(len(self.skip_tracks)) + ' ; delete:' + str(len(self.delete_tracks)))

    
        
    def execute(self,whatif = False):
        #Delete Tracks
        for track in self.delete_tracks:
            print('delete:' + track)
            destination_path = os.path.join(self.destination_music_folder,track)
            if not os.path.exists( destination_path):
                print('NotFound:' + track)
            else:
                if  not whatif:
                    os.remove(destination_path)
        #Update Tracks
        #SKIP Tracks
    
        # add Tracks
        for track in self.additional_tracks:
            print('Copy :' + track)
            source_path = os.path.join(self.source_music_folder,track)
            destination_path = os.path.join(self.destination_music_folder,track)
            destination_folder = os.path.dirname(destination_path)
            if not os.path.exists(source_path):
                print('NotFound:' + track)
            else:
                if not whatif:
                    os.makedirs(destination_folder,exist_ok =True)
                    shutil.copyfile(source_path, destination_path)
        #Delete empty folder
        
si = sync_itunes(file,destination_music_folder)
