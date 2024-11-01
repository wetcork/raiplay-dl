# Created by WetCork
# Version 1.0.3 - August 2024
# https://github.com/wetcork/raiplay-dl

import argparse
import json
import math
import os
import pathlib
import sys

import requests
from natsort import natsorted, ns

# GLOBAL SETTINGS #

debug = False # Print debug output in the console
url_root = 'https://www.raiplay.it'
override = '&overrideUserAgentRule=mp4-'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:116.0) Gecko/20100101 Firefox/116.0'}
formats = ['5000', '3200', '2401', '2400', '1800', '1200', '0', '800', '700', '400', '250']
resolutions = ['1080p', '810p', '720p', '720p', '576p', '414p', '396p','288p', '288p', '288p', '198p']

# END GLOBAL SETTINGS #

def main(args):
    if check_url(args.url):
        data = get_json(args.url)
        if check_drm(data):
            serie = is_serie(data)
            if args.list_formats:
                if serie:
                    list_formats_serie(data, args.seasons, args.episodes)
                else:
                    list_formats(data)
            elif serie:
                pre_download_serie(data, args.seasons, args.episodes, args.format, args.out_dir)
            else:
                pre_download(data, args.format, args.out_dir)

def check_url(url): # Check if given url is valid
    if debug: print('[debug] Checking URL')
    
    if url_root in url:
        try:
            if requests.get(url).status_code == 404:
                sys.exit('[error] Can\'t connect to the url.')
            else:
                return True
        except:
            sys.exit('[error] Connection error.')
    else:
        sys.exit('[error] Invalid url.')

def check_drm(data): # Check if the content is DRM protected
    if debug: print('[debug] Checking DRM...')
    
    if 'ContentItem' in data['id']:
        data = get_json(url_root + data['program_info']['path_id'])
        
    try:
        if data['program_info']['rights_management']['rights']['drm']['VOD']:
            print('[drm error] "%s" is DRM protected.' % (data['name']))
    except:
        return True
    else:
        sys.exit('[drm error] This script can\'t bypass DRM protection.')

def get_json(url): # Input the RaiPlay url and output the associated JSON
    if debug: print('[debug] Getting JSON...')
    
    url = url.rstrip('/')
    if url.endswith('.html'):
        url = url.replace('.html', '.json')
    elif not url.endswith('.json'):
        url = url + '.json'

    if debug: print('[debug] Url: ' + url)
    data = json.loads(requests.get(url).content)
    return data

def is_serie(data): # Check if the media is a tv serie or a movie
    if debug: print('[debug] Checking SERIE...')
    
    layout = data['program_info']['layout']
    if layout == 'single':
        return False
    elif layout == 'multi':
        return True
    else:
        sys.exit('Error while defining serie.')

def get_override_url(data, format): # Generate the mp4 video url
    if debug:
        print('[debug] Getting OVERRIDE URL...')
        print('[debug] ' + format)
    
    url = data['video']['content_url']
    if format == 'best':
        for format in formats:
            url_override = url + override + format
            
            if debug:
                    print('[debug] Format: ' + format)
                    print('[debug] Url: ' + url_override)
            try:    
                if requests.get(url_override, stream=True, headers=headers).headers['Content-Type'] == 'video/mp4':
                    return url_override
            except:
                sys.exit('[error] Connection error, or the title has Verimatrix DRM protection.')
        print('[error] No format has been found for the given title.')
    else:
        url_override = url + override + format
        try:    
            if requests.get(url_override, stream=True, headers=headers).headers['Content-Type'] == 'video/mp4':
                return url_override
            else:
                #print('[info] Selected format is not avaiable, fallback to the best avaible format')
                for format in formats:
                    url_override = url + override + format
                    
                    if debug:
                            print('[debug] Format: ' + format)
                            print('[debug] Url: ' + url_override)
                            
                    if requests.get(url_override, stream=True, headers=headers).headers['Content-Type'] == 'video/mp4':
                        return url_override 
        except:
            sys.exit('[error] Connection error, or the title has Verimatrix DRM protection.')
        

def get_definition(format): # Retrive the video quality
    if debug: print('[debug] Getting DEFINITION...')
    
    for bit in range(len(formats)):
        if formats[bit] == format:
            if debug: print('[debug] ' + resolutions[bit])
            return resolutions[bit]

def convert_size(size_bytes): # Covert file size from bytes to the best readable option
    if size_bytes == 0:
        return '0B'
    size_name = ('B', 'KB', 'MB', 'GB')
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return '%s %s' % (s, size_name[i])

def path_and_down(url, out_dir, file_name): # Check output file path and start the download
    
    out_dir = out_dir[2:].replace(':', ' -').replace('<', ' ').replace('>', '<').replace('|', '').replace('*', '').replace('?', '').replace('"', '')
    file_name = file_name.replace(':', ' -').replace('<', ' ').replace('>', '<').replace('|', '').replace('*', '').replace('?', '').replace('"', '').replace('/', '_').replace('\\', '_')
    file_path = os.path.join(out_dir, file_name)
    
    if debug:
        print('[debug] Checking PATH...')
        print('[debug] ' + out_dir)
        print('[debug] ' + file_name)
        print()
    
    
    if not os.path.isfile(file_path):
            if not os.path.isdir(out_dir):
                os.makedirs(out_dir)
            print('Downloading "%s"' % (file_name.strip('.mp4')))
            download(url, file_path)
    else:
        print('%s has already been downloaded.' % file_name)
        if debug: print()

def pre_download(data, format, out_dir): # Get all the infos to start the download
    if debug: print('[debug] Starting PRE-DOWNLOAD...')
    
    if 'Page' in data['id']:
        data = get_json(url_root + data['first_item_path'])
        
    if debug: print('[debug] Defining METADATA...')
    title = data['program_info']['name']
    year = data['program_info']['year']
    url = get_override_url(data, format)

    if url: # Thanks to drego85
        definition = get_definition(url[url.find('-') + 1:])
        file_name = '%s (%s) [%s].mp4' % (title.strip(), year, definition)
        path_and_down(url, out_dir, file_name)

def pre_download_serie(data, def_seasons, def_episodes, format, out_dir): # Get all the infos to start the download
    if debug: print('[debug] Starting SERIE PRE-DOWNLOAD...\n')

    if 'ContentItem' in data['id']:
        if debug: print('[debug] Defining METADATA...')
        
        serie = data['program_info']['name']
        season = data['season']
        episode = data['episode']
        episode_title = data['episode_title']
        year = data['track_info']['edit_year']
        url = get_override_url(data, format)

        if url: # Thanks to drego85
            definition = get_definition(url[url.find('-') + 1:])
            file_name = '%s - %sx%s - %s (%s) [%s].mp4' % (serie, season.zfill(2), episode.zfill(2), episode_title.strip(), year, definition)
            path_and_down(url, out_dir, file_name)
    elif 'Page' in data['id']:
        def_seasons = [x.strip() for x in def_seasons.split(',')]
        def_episodes = [x.strip() for x in def_episodes.split(',')]
        
        fn_serie = data['name']
        fn_year = data['program_info']['year']
        print('Downloading "%s (%s)".\n' % (fn_serie.strip(), fn_year))
        
        for block in range(len(data['blocks'])):
            blocks_name = data['blocks'][block]['name'].strip()
            if 'Episodi' == blocks_name or 'Puntate' == blocks_name or 'Lingua italiana' == blocks_name:
                        seasons = []

                        if debug: print('[debug] Sorting SEASONS...')
                        # This function stores the season name and the rispective json path
                        # in one array, separated by a custom word, then natsort the season
                        # for a better output in the console (it was to difficult to organize things for RAI)
                        for season in range(len(data['blocks'][block]['sets'])):
                            seasons.append(data['blocks'][block]['sets'][season]['name'] + '_SEP_' + data['blocks'][block]['sets'][season]['path_id'])
                        seasons = natsorted(seasons, alg=ns.IGNORECASE)

                        if debug: print('[debug] Getting custom SEASONS...')
                        if def_seasons[0] != 'all':
                            temp = []
                            for i in def_seasons:
                                temp.append(seasons[int(i)-1])
                            seasons = temp
                        
                        for sor_season in seasons:
                            season_data = get_json(url_root + sor_season.split('_SEP_')[1])
                            
                            if debug: print('[debug] Defining seasons METADATA...\n')
                            fn_season = season_data['items'][0]['season']
                            sub_dir = '%s (%s)\\Season %s' % (fn_serie.strip(), fn_year, fn_season)
                            out_sub_dir = os.path.join(out_dir, sub_dir)
                            
                            print('[Season %s]' % (season_data['items'][0]['season']))
                            
                            episodes = []
                            for episode in range(len(season_data['items'])):
                                if not season_data['items'][episode]['episode'] == '':
                                    episodes.append(season_data['items'][episode]['episode'])
                                else:
                                    episodes.append(episode+1)
                            
                            if def_episodes[0] != 'all':
                                if debug:
                                    print('\n[debug] Getting SELECTED EPISODES...')
                                    print('[debug] ' + str(def_episodes))
                                    
                                for def_episode in def_episodes:
                                    for episode in range(len(episodes)):
                                        if def_episode == episodes[episode]:
                                            
                                            if debug: print('[debug] Defining episode METADATA...')
                                            fn_episode = season_data['items'][episode]['episode']
                                            fn_episode_title = season_data['items'][episode]['episode_title']
                                            url = get_override_url(get_json(url_root + season_data['items'][episode]['weblink']), format)

                                            if url: # Thanks to drego85
                                                definition = get_definition(url[url.find('-') + 1:])
                                                file_name = '%s - %sx%s - %s [%s].mp4' % (fn_serie, fn_season.zfill(2), fn_episode.zfill(2), fn_episode_title.strip(), definition)
                                                path_and_down(url, out_sub_dir, file_name)
                            else:   
                                if debug:
                                    print('\n[debug] Getting ALL EPISODES...')
                                    print('[debug] ' + str(episodes))
                                
                                for episode in range(len(episodes)):
                                    fn_episode = season_data['items'][episode]['episode']
                                    fn_episode_title = season_data['items'][episode]['episode_title']
                                    url = get_override_url(get_json(url_root + season_data['items'][episode]['weblink']), format)

                                    if url: # Thanks to drego85
                                        definition = get_definition(url[url.find('-') + 1:])
                                        file_name = '%s - %sx%s - %s [%s].mp4' % (fn_serie, fn_season.zfill(2), fn_episode.zfill(2), fn_episode_title.strip(), definition)
                                        path_and_down(url, out_sub_dir, file_name)
                            print()

def list_formats(data): # List the formats
    try:
        if 'Page' in data['id']:
            data = get_json(url_root + data['first_item_path'])
            
        if debug: print('[debug] Listing FORMATS...\n')

        title = data['program_info']['name']
        year = data['program_info']['year']
        url = data['video']['content_url']

        print('Formats avaiable for "%s (%s)"' % (title.strip(), year))

        for format in range(len(formats)):
            url_override = url + override + formats[format]
            r = requests.get(url_override, stream=True, headers=headers)
            if r.headers['Content-Type'] == 'video/mp4':
                print('%s - %s (%s)' % (formats[format], resolutions[format], convert_size(int(r.headers['Content-Length']))))
    except KeyboardInterrupt:
        sys.exit('\n[info] Format listing interrupted.')

def list_formats_serie(data, def_seasons, def_episodes): # List the formats
    if debug: print('[debug] Listing SERIE FORMATS...\n')
    try:
        if 'ContentItem' in data['id']:
            serie = data['program_info']['name']
            season = data['season']
            episode = data['episode']
            episode_title = data['episode_title']
            year = data['track_info']['edit_year']
            url = data['video']['content_url']
            
            print('Formats avaiable for "%s - %sx%s - %s (%s)"' % (serie.strip(), season.zfill(2), episode.zfill(2), episode_title.strip(), year))
            
            for format in range(len(formats)):
                override_url = url + override + formats[format]
                r = requests.get(override_url, stream=True, headers=headers)
                if r.headers['Content-Type'] == 'video/mp4':
                    print('%s - %s (%s)' % (formats[format], resolutions[format], convert_size(int(r.headers['Content-Length']))))
        elif 'Page' in data['id']:
            def_seasons = [x.strip() for x in def_seasons.split(',')]
            def_episodes = [x.strip() for x in def_episodes.split(',')]
            
            fn_serie = data['name']
            fn_year = data['program_info']['year']
            
            print('Formats avaiable for "%s (%s)"\n' % (fn_serie.strip(), fn_year))
            if debug: print('[debug] Getting SEASONS...')
            for block in range(len(data['blocks'])):
                if 'Episodi' == data['blocks'][block]['name'] or 'Puntate' == data['blocks'][block]['name']:
                            seasons = []
                            if debug: print('[debug] Sorting SEASONS...')
                            # This function stores the season name and the rispective json path
                            # in one array, separated by a custom word, then natsort the season
                            # for a better output in the console (it was to difficult to organize things for RAI)
                            for season in range(len(data['blocks'][block]['sets'])):
                                seasons.append(data['blocks'][block]['sets'][season]['name'] + '_SEP_' + data['blocks'][block]['sets'][season]['path_id'])
                            seasons = natsorted(seasons, alg=ns.IGNORECASE)

                            if def_seasons[0] != 'all':
                                if debug: print('[debug] Getting custom SEASONS...')
                                temp = []
                                for i in def_seasons:
                                    temp.append(seasons[int(i)-1])
                                seasons = temp
                            
                            for sor_season in seasons:
                                season_data = get_json(url_root + sor_season.split('_SEP_')[1])
                                
                                if debug: print()
                                print('[Season %s]' % (season_data['items'][0]['season']))
                                
                                episodes = []
                                for episode in range(len(season_data['items'])):
                                    if not season_data['items'][episode]['episode'] == '':
                                        episodes.append(season_data['items'][episode]['episode'])
                                    else:
                                        episodes.append(episode+1)
                                
                                if def_episodes[0] != 'all':
                                    if debug:
                                        print('\n[debug] Getting SELECTED EPISODES...')
                                        print('[debug] ' + str(def_episodes))
                                        print()
                                        
                                    for def_episode in def_episodes:
                                        for episode in range(len(episodes)):
                                            if def_episode == episodes[episode]:
                                                fn_episode = season_data['items'][episode]['episode']
                                                fn_episode_title = season_data['items'][episode]['episode_title']
                                                
                                                print('Ep %s - "%s"' % (fn_episode, fn_episode_title.strip()))
                                                url = season_data['items'][episode]['video_url']
                                                for format in range(len(formats)):
                                                    override_url = url + override + formats[format]
                                                    r = requests.get(override_url, stream=True, headers=headers)
                                                    if r.headers['Content-Type'] == 'video/mp4':
                                                        print('%s - %s (%s)' % (formats[format], resolutions[format], convert_size(int(r.headers['Content-Length']))))
                                                print()
                                        
                                else:   
                                    if debug:
                                        print('\n[debug] Getting ALL EPISODES...')
                                        print('[debug] ' + str(episodes))
                                        print()
                                    
                                    for episode in range(len(episodes)):
                                        fn_episode = season_data['items'][episode]['episode']
                                        fn_episode_title = season_data['items'][episode]['episode_title']
                                        
                                        print('Ep %s - "%s"' % (fn_episode, fn_episode_title.strip()))
                                        url = season_data['items'][episode]['video_url']
                                        for format in range(len(formats)):
                                            override_url = url + override + formats[format]
                                            r = requests.get(override_url, stream=True, headers=headers)
                                            if r.headers['Content-Type'] == 'video/mp4':
                                                print('%s - %s (%s)' % (formats[format], resolutions[format], convert_size(int(r.headers['Content-Length']))))
                                        print()
    except KeyboardInterrupt:
        sys.exit('\n[info] Format listing interrupted.')
        
def download(url, file_path): # yeah this pretty much download
    if debug: print('\n[debug] Starting DOWNLOAD...')
    try:
        with open(file_path, 'wb') as f:
            r = requests.get(url, stream=True, headers=headers)
            total_length = r.headers['Content-Length']
            if debug: print('[debug] ' + total_length + '\n')
            if total_length is None:
                f.write(r.content)
            else:
                dl = 0
                total_length = int(total_length)
                for data in r.iter_content(chunk_size=4096):
                    dl += len(data)
                    f.write(data)
                    done = int(50 * dl / total_length)
                    percent = int(100 * dl / total_length)
                    sys.stdout.write('\r[%s%s] %s%% of %s' % ('#' * done, ' ' * (50 - done), percent, convert_size(int(total_length))))
                    sys.stdout.flush()
                print()
    except KeyboardInterrupt:
        os.remove(file_path)
        sys.exit('\n\n[info] Download cancelled.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='raiplay-dl', description='Downloader for RaiPlay')
    parser.add_argument('url', metavar='URL', help='Content URL')
    parser.add_argument('-f', '--format', metavar='FORMAT', dest='format', default='best', help='Video format code')
    parser.add_argument('-F', '--list-formats', dest='list_formats', help='List all available formats', action='store_true')
    parser.add_argument('-s', '--season', metavar='SEASON', dest='seasons', default='all', help='Season')
    parser.add_argument('-e', '--episode', metavar='EPISODE', dest='episodes', default='all', help='Episode')
    parser.add_argument('-o', '--output', metavar='PATH', dest='out_dir', default=str(pathlib.Path(__file__).parent.resolve()), help='Set the output directory')
    args = parser.parse_args()
    main(args)
