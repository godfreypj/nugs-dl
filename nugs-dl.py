'''
Docstring explaining this module blah blah
'''
import json
import os
import platform
import re
import sys
import time
import urllib
import requests
from mutagen.flac import FLAC
from mutagen.mp4 import MP4


def get_os_type():
    '''
    blah
    '''
    os_platform = platform.system()
    return bool(os_platform=='Windows')

def os_commands(command):
    '''
    blah
    '''
    if command == "p":
        if get_os_type():
            os.system('pause')
        else:
            os.system("read -rsp $\"\"")
    elif command == "c":
        if get_os_type():
            os.system('cls')
        else:
            os.system("clear")
    else:
        if get_os_type():
            os.system('title nugs-dl R1 (by godfrey)')
        else:
            sys.stdout.write("\x1b]2;nugs-dl R1 (by godfrey)\x07")

def clean_json(jsonf):
    '''
    blah
    '''
    try:
        return json.loads(jsonf.rstrip()[21:-2])
    except json.decoder.JSONDecodeError:
        return json.loads(jsonf.rstrip()[20:-2])

def login(user_email, user_pwd):
    '''
    blah
    '''
    login_get_req = session.get(\
        f"https://streamapi.nugs.net/secureapi.aspx?orgn=nndesktop&callback=angular.\
            callbacks._3&method=user.site.login&pw={user_pwd}&username={user_email}")
    if login_get_req.status_code != 200:
        print(f"Sign in failed. Response from API: {login_get_req.text}")
        os_commands("p")
    elif "USER_NOT_FOUND" in login_get_req.text:
        print("Sign in failed. Bad credentials.")
        os_commands("p")

def fetch_sub_info():
    '''
    blah
    '''
    sub_info_get_req = session.get(\
        "https://streamapi.nugs.net/secureapi.aspx?orgn=nndesktop&callback=angular.\
            callbacks._0&method=user.site.getSubscriberInfo")
    if sub_info_get_req.status_code != 200:
        print(f"Failed to fetch sub info. Response from API: {sub_info_get_req.text}")
    elif not clean_json(sub_info_get_req.text)['Response']:
        print("Failed to fetch sub info. Bad credentials.")	
        os_commands("p")
    else:
        print(f"Signed in successfully - {clean_json(sub_info_get_req.text)['Response']['subscriptionInfo']['planName'][9:]} account\n")
        
def fetch_track_url(trackId, x):
    '''
    blah
    '''
    track_url_get_resp = session.get(\
        f"https://streamapi.nugs.net/bigriver/subplayer.aspx?\
            orgn=nndesktop&HLS=1&callback=angular.callbacks._h&platformID=\
            {x}&trackID={trackId}")
    if track_url_get_resp.status_code != 200:
        print(f"Failed to fetch track URL. Response from API: {track_url_get_resp.text}")
        os_commands("p")
    else:
        return clean_json(track_url_get_resp.text)["streamLink"]

def wrap(track_title, track_num, track_total):
    '''
    blah
    '''
    def reporthook(blocknum, blocksize, totalsize):
        if quality == "1":
            dl_quality = f"Downloading track \
                {track_num} of {track_total}: {track_title} - 16-bit / 44.1 kHz FLAC"
        elif quality == "2":
            dl_quality = f"Downloading track \
                {track_num} of {track_total}: {track_title} - ALAC"
        else:
            dl_quality = f"Downloading track \
                {track_num} of {track_total}: {track_title} - VBR L4 AAC"
        readsofar = blocknum * blocksize
        if totalsize > 0:
            percent = readsofar * 1e2 / totalsize
            sys.stderr.write(f"{dl_quality}{percent:5.0f}%\r")
            if readsofar >= totalsize:
                sys.stderr.write("\n")
    return reporthook

def fetch_track(track_url, track_title, track_num, track_total, f_ext):
    '''
    blah
    '''
    urllib.request.urlretrieve(track_url, f"{track_num,}{f_ext}", wrap(track_title, track_num, track_total))

def fetch_meta_data(album_id):
    '''
    blah
    '''
    metadata_get_resp = session.get(\
        f"https://streamapi.nugs.net/api.aspx?orgn=nndesktop&callback=\
            angular.callbacks._4&containerID=\
            {album_id}&method=catalog.container&nht=1", verify = False)
    if metadata_get_resp.status_code != 200:
        print(f"Failed to fetch metadata. Response from API: {metadata_get_resp.text}")
        os_commands("p")
    else:
        return clean_json(metadata_get_resp.text)

def write_tags(file_name, album_title, track_num, track_total):
    '''
    blah
    '''
    if file_name.endswith("c"):
        audio = FLAC(file_name)
        audio['album'] = album_title
        audio['tracktotal'] = str(track_total)
    else:
        audio = MP4(file_name)
        audio["\xa9alb"] = album_title
        audio["trkn"] = [(track_num, track_total)]
    audio.save()

def rename_files(track_title, track_num, f_ext):
    '''
    blah
    '''
    if not str(track_num).startswith("0"):
        if int(track_num) < 10:
            final_file_name = f"0{track_num}. {track_title}{f_ext}"
        else:
            final_file_name = f"{track_num}. {track_title}{f_ext}"
    else:
        final_file_name = f"{track_num}. {track_title}{f_ext}"
    if get_os_type():
        final_file_name = re.sub(r'[\\/:*?"><|]', '-', final_file_name)
    else:
        final_file_name = re.sub('/', '-', final_file_name)
    if os.path.isfile(final_file_name):
        os.remove(final_file_name)
    os.rename(f"{track_num}{f_ext}", final_file_name)

def album_dir_prep(album_dir):
    '''
    blah
    '''
    if get_os_type():
        album_dir = re.sub(r'[\\/:*?"><|]', '-', album_dir)
    else:
        album_dir = re.sub('/', '-', album_dir)
    if not os.path.isdir("nugs-dl Downloads"):
        os.mkdir("nugs-dl Downloads")
    os.chdir("nugs-dl Downloads")
    if not os.path.isdir(album_dir):
        os.mkdir(album_dir)	
    os.chdir(album_dir)

def main(track_quality):
    '''
    blah
    '''
    url = input("Input Nugs URL: ")
    try:
        if not url.strip():
            os_commands("c")
            return
        elif url.split('/')[-2] != "recording":
            print("Invalid URL.")
            time.sleep(1)
            os_commands("c")
        else:
            os_commands("c")
            metaj = fetch_meta_data(url.split('/')[-1])
            album_artist = metaj["Response"]["artistName"]
            album_title = metaj['Response']['containerInfo'].rstrip()
            print(f"{album_artist} - {album_title}\n")
            album_dir_prep(f"{album_artist} - {album_title}")
            track_total = len([x for x in metaj["Response"]["tracks"]])
            if track_quality == "1":
                f_ext = ".flac"
                num = "1"
            elif track_quality == "2":
                f_ext = ".m4a"
                num = "0"
            else:
                f_ext = ".m4a"
                num = ""
            i = 0
            for item in metaj["Response"]["tracks"]:
                i += 1
                track_url = fetch_track_url(item["trackID"], num)
                fetch_track(track_url, item["songTitle"], i, track_total, f_ext)
                write_tags(f"{i}{f_ext}", album_title, i, track_total)
                rename_files(item["songTitle"], i, f_ext)
            os.remove("cover.jpg")
            os.chdir("....")
            print("Returning to URL input screen...")
            time.sleep(1)
            os_commands("c")
    except IndexError:
        print("Invalid URL.")
        time.sleep(1)
        os_commands("c")

if __name__ == '__main__':
    os_commands("t")
    session = requests.session()
    with open("config.json", encoding=json) as file:
        config = json.load(file)
        email, pwd, quality = config["email"], config["password"], config["quality"]
    login(email, pwd)
    fetch_sub_info()
    while True:
        main(quality)
