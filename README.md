***I'm currently rewriting this script from scratch and the actual commit isn't working***

![builds status](https://github.com/wetcork/raiplay-dl/actions/workflows/build.yaml/badge.svg)

# raiplay-dl

raiplay-dl - the most advanced raiplay.it downloader

- [Installation](#installation)
  - [Binaries](#binaries)
  - [Cloning the code](#cloning-the-code)
- [Description](#description)
- [Features](#features)
- [Usage](#usage)
  - [Example usage](#example-usage)
  - [Some things to keep in mind](#some-things-to-keep-in-mind)
- [Problems and limitations](#problems-and-limitations)
- [Donations](#donations)

## Installation

### Binaries
Executables for Windows, MacOS and Linux are available in the [dist](https://github.com/wetcork/raiplay-dl/blob/main/dist/) folder.
They work as standalone executables, don't need Python or external libraries to be installed and can be used by simply calling them from the command line.
Keep in mind that you should run the terminal **in the same folder** as the executable and recall it with the same name as the file, followed by the parameters as in the [Usage](#usage) section of this README.
If you want to call the executables in the terminal from any folder, you should add the executable to the PATH of your system (depends on your OS).

### Cloning the code
Download or clone the repository, then run `pip install -r requirements.txt` and you are set to go.

## Description

**raiplay-dl** is a command-line program to download videos from raiplay.com. It requires the Python interpreter, version 3.4+, and it is not platform specific.

This documentation and the args syntax take ispiration from [youtube-dl](https://github.com/ytdl-org/youtube-dl).
The script is inspired by [raiplay-dl](https://github.com/leoncvlt/raiplay-dl) by [leoncvlt](https://github.com/leoncvlt), but is a complete rewrite.

## Features

- Bypass RaiPlay 720p limit and download up to 1080p
- Download the original mp4 file (not the HLS stream)
- Bulk download tv series
- Selective download seasons and episodes
- No account needed
- Good file naming system

## Usage

```text
usage: raiplay-dl [-h] [-f FORMAT] [-F] [-o PATH] [-v] URL

positional arguments:
  URL                   Content URL

options:
  -h, --help            show this help message and exit
  -f FORMAT, --format FORMAT
                        Video format code
  -F, --list-formats    List all available formats
  -o PATH, --output PATH
                        Set the output directory
  -v, --version         show program's version number and exit
  ```

### Example usage

List avaiable formats by using `-F`
```text
raiplay-dl.py -F https://www.raiplay.it/programmi/thecircle

Formats avaiable for "The Circle (2017)"
5000 - 1080p (4.82 GB)
2400 - 720p (2.06 GB)
1800 - 576p (1.53 GB)
1200 - 414p (1.03 GB)
```
You can filter seasons and episodes by using `-s` and `-e`
```text
raiplay-dl.py -F https://www.raiplay.it/programmi/donmatteo -s 9 -e 3,4

Formats avaiable for "Don Matteo (2000)"

[Season 9]
Ep 3 - "Testimone d'accusa"
5000 - 1080p (2.09 GB)
3200 - 810p (1.36 GB)
2400 - 720p (1.03 GB)
1800 - 576p (796.01 MB)
1200 - 414p (531.93 MB)
700 - 288p (317.92 MB)
400 - 288p (190.9 MB)
250 - 198p (122.41 MB)

Ep 4 - "Prova d'amore"
5000 - 1080p (2.03 GB)
3200 - 810p (1.32 GB)
2400 - 720p (1.01 GB)
1800 - 576p (774.04 MB)
1200 - 414p (517.43 MB)
700 - 288p (309.29 MB)
400 - 288p (185.69 MB)
250 - 198p (119.0 MB)
```
Download the desired quality by using `-f`
```
raiplay-dl.py -f 2400 https://www.raiplay.it/programmi/thecircle

Downloading "The Circle (2017) [720p]"
[##                                                ] 4% of 2.06 GB
```
If `-f` isn't specified the best avaible quality will be automatically selected
```
raiplay-dl.py https://www.raiplay.it/programmi/donmatteo -s 9 -e 3,4

Downloading "Don Matteo - 09x03 - Testimone d'accusa [1080p]"
[##################################################] 100% of 2.09 GB
Downloading "Don Matteo - 09x04 - Prova d'amore [1080p]"
[###############                                   ] 30% of 2.03 GB
```
You can also download directly from the video player url
```
raiplay-dl.py -f 1200 https://www.raiplay.it/video/2016/06/Don-Matteo---S9E3---Testimone-daccusa-872263a6-a947-4d83-9626-000c3127e317.html

Downloading "Don Matteo - 09x03 - Testimone d'accusa (2014) [414p]"
[#########                                         ] 18% of 531.93 MB
```

### Some things to keep in mind
- If you download tv series by specifing the main serie url (example 2) the file path will be *[outdir]\\[serie]\\[season]\\[episode]*
- If you download tv series from the video player url the file path will be *[outdir]\\[episode]*
- If the selected quality is not avaiable the script will download the best quality that will find

## Problems and limitations

- All the RaiPlay contents are georestricted to Italy (a proxy should be able to bypass)
- A few movies/series are DRM protected, this script **can't bypass DRM protection**.
- The metadata system in RaiPlay is so shitty that you need to make different functions to parse metadata for each media type (movies, tv series, tv programs and kids), and in some cases there are differences even between same media type. This makes it difficult for the script to automatically divide for example the seasons or to distinguish if the url given in input is a series or a movie, so in *some rare cases* there could be errors in the naming of the files or in the download. Please report these errors and I will try to fix them.

## Donations

If you appreciate my work and if you can afford it, it would be great if you could give me a small donation!

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/wetcork)
