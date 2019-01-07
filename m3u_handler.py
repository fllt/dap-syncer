from enum import Enum
import const
import unicodedata


def read_m3u(path):
        with open(path,"r",encoding='utf-8') as file:
                playlist = file.readlines()
        return playlist                
def write_m3u(path,tracks):
        with open(path,'w',encoding='utf-8' ) as file:
                file.write('\n'.join(tracks))
