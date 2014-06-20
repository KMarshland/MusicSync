#!/usr/bin/env python
# -*- coding: utf-8 -*-

from getpass import getpass
from gmusicapi import *
from pyItunes import *
from sets import Set
from BetterSets import *
from unidecode import unidecode
import base64
import os
import subprocess
import re

itunes_xml_path_windows = "C:\Users\Kai\Music\iTunes\iTunes Music Library.xml"
itunes_path_windows = 'C:\\Program Files (x86)\\iTunes\\iTunes.exe'
artist_folder_path_windows = "C:\\Users\\Kai\\Music\\Artists\\"

env = "windows_desktop"
=======
itunes_xml_path_mac = "/Users/administrator/Music/iTunes/iTunes Music Library.xml"
itunes_path_mac = "/Applications/iTunes.app"
artist_folder_path_mac = "/Users/administrator/Music/Artists"

env = "mac_laptop"

if env == "windows_desktop":
    itunes_xml_path = itunes_xml_path_windows
    itunes_path = itunes_path_windows
    artist_folder_path = artist_folder_path_windows

elif env == "mac_laptop":
    itunes_xml_path = itunes_xml_path_mac
    itunes_path = itunes_path_mac
    artist_folder_path = artist_folder_path_mac

default_email = 'kaimarshland@gmail.com'

def ask_for_credentials():
    """Make an instance of the api and attempts to login with it.
    Return the authenticated api.
    """

    # We're not going to upload anything, so the Mobileclient is what we want.
    api = Mobileclient()

    logged_in = False
    attempts = 0

    while not logged_in and attempts < 3:
        email = raw_input('Email: ')
        password = getpass()

        stuff = api_from_email_and_password(email, password)
        api = stuff[0]
        logged_in = stuff[1]
        attempts += 1

    return api

def api_from_email_and_password(email, password):
    api = Mobileclient()

    logged_in = api.login(email, password)

    return api, logged_in

def get_credentials():
    asking = True
    
    if (asking):
        return ask_for_credentials()
    else:
        return api_from_email_and_password(default_email, 'yeah this isn\'t my real password tough luck')[0]

def google_play_connection():
    """Demonstrate some api features."""

    api = get_credentials()

    if not api.is_authenticated():
        print("""Sorry, those credentials weren't accepted.""")
        return

    print('Successfully logged in.')
    print 

    # Get all of the users songs.
    # library is a big list of dictionaries, each of which contains a single song.
    print 'Loading google play...',
    library = api.get_all_songs()
    print 'done.'

    #print len(library), 'tracks detected.'
    print
    
    return library

def itunes_connection():
    print "Reading iTunes...",
    l = Library(itunes_xml_path)

    library = []

    for id, song in l.songs.items():
        formattedSong = {
            'title': song.name,
            'artist': song.artist,
            'album': song.album,
            'length': song.length
        }
        #print formattedSong['length']
        library.append(formattedSong)
    
    print "done."
    print 
    
    return library

def download_library(library):
    mm = Musicmanager()
    #mm.perform_oauth()
    mm.login()
    
    #for song in library:
    #    download_song(mm, song)
    #download_song(mm, library[0])
    
def download_and_import_library(library):
    mm = Musicmanager()
    #mm.perform_oauth()
    mm.login()
    
    counter = 0
    
    for song in library:
        #try:
        filename = download_song(mm, song)
        import_song(filename)
        counter += 1
        print " (%d remaining)" % (len(library) - counter)
        #except:
        #    print "Error: could not import " + songHash(song)
    
    
def import_song(filename):
    #command = "\"C:\\Program Files (x86)\\iTunes\\iTunes.exe\"" " + filename + ""
    
    subprocess.call([itunes_path, filename])
    
    #print command
    #os.system(command)
    #os.system(filename)
    
    return

def download_song(mm, song):
    print "Downloading " + (song['title'] or "Untitled").encode('utf-8') + "...",
    
    song_id = song['id']
    filename, audio = mm.download_song(song_id)
    #filename = filename.encode('ascii', 'ignore')
    
    
    dirname = artist_folder_path + song['artist'].replace(":", "_")
    dirname = unidecode(dirname)
    dirname = re.sub("\s", " ", dirname).strip()
    
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    
    fullname = dirname + "\\" + filename
    fullname = unidecode(fullname)
    #fullname = fullname.encode('ascii', 'xmlcharrefreplace')
    fullname = re.sub("\s", " ", fullname)
    #print " to " + fullname,
    
    with open(fullname, 'wb') as f:
        f.write(audio)
    print "complete",
        
    try:
        return fullname
    except:
        print "Error: Could not download " + songHash(song)
        return "Error"

def print_library(library):
    for song in library:
        print_song(song)
    
    print "Total length %d" % (len(library))
    
def lib_hash(library):
    res = ""
    for song in library:
        try:
            res += songHash(song) + "\n"
            #str(song['length'])
        except:
            res += "Error on " + songHash(song) + "\n"
    
    res += ("Total length %d" % (len(library)))
    return res;

def compare_libraries(lib1, lib2):
    
    print "Comparing libraries...",
    
    missingFrom1 = []
    missingFrom2 = []
    
    ks1 = KeyedSet(lib1, key=songHash)
    ks2 = KeyedSet(lib2, key=songHash)
    
    inBoth = ks1 & ks2
    #ksBoth = KeyedSet(inBoth, key=songHash)
    
    
    missingFrom1 = list(ks1 - inBoth)
    missingFrom2 = list(ks2 - inBoth)
    
    print "done."
    
    return missingFrom1, missingFrom2

def songsEqual(song1, song2):
    return (song1['title'] == song2['title']) and (song1['artist'] == song2['artist']) and (song1['album'] == song2['album'])

def songHash(song):
    title = (song['title'] or "Untitled").encode('utf-8')
    artist = (song['artist'] or "Unknown Artist").encode('utf-8')
    album = (song['album'] or "Unknown Album").encode('utf-8')
    return "%s by %s on %s" % (title, artist, album)

def print_song(song):
    #print songHash(song)
    return

def write_library(name, library):
    print "Writing to " + name + "...",
    fo = open(name, "wb+")
    
    fo.write(lib_hash(library))
    
    fo.close()
    print "done."

def main():
    #print_library(google_play_connection())
    #print_library(itunes_connection())
    #itunes_connection()
    #import_song("C:\\Users\\Kai\\Music\\Artists\\Ensiferum\\09 - Treacherous Gods.mp3")
    
    not_in_itunes, not_in_play = compare_libraries(google_play_connection(), itunes_connection())
    write_library("not_in_itunes.txt", not_in_itunes)
    write_library("not_in_google_play.txt", not_in_play)
    
    print
    print "%d not in iTunes" % (len(not_in_itunes))
    print "%d not in Google Play" % (len(not_in_play))
    print 
    
    download_and_import_library(not_in_itunes)
    if raw_input("Do you want to download the files? (y/n)") == "y":
        download_and_import_library(not_in_itunes)
    
    
if __name__ == '__main__':
    main()

raw_input("Done")
