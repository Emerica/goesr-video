#!/usr/bin/python3
# Simple script to turn a bunch of photos into a video
import os, sys, glob, subprocess
from datetime import datetime

#sys.argv[2]
userhome = os.path.expanduser('~')          
USER = os.path.split(userhome)[-1]  

FRAMES = 15*24*2 # 2 days of data
SRC =  '/home/' + USER + '/goesr/truecolor-thumb-*.jpg'
DEST = '/home/' + USER + '/goesr/video-{}.webm'
FRAMES = {'day':     24*4-1,
          'two-day': 24*4*2-1,
          'week':    24*4*7-1,
          'month':   31,
          'year':    365}

# frames per second (real time is four frames per hour)
RATE   = {'day':     '8',
          'two-day': '8',
          'week':    '16',
          'month':   '4',
          'year':    '8'}


def main():
    files = sorted(glob.glob(SRC))

    # for month and year settings, use daily pictures instead of 15-minutes.
    # This uses some cleverness to find the file closest to noon for each day.
    if sys.argv[1] in ['month', 'year']:
        # Build a sorted list of file mtime and path
        files = [(os.path.getmtime(f), f) for f in files]
        files_daily = []
        noon = datetime.utcnow().replace(hour=16, minute=40, second=0).timestamp()
        for index in range(FRAMES[sys.argv[1]]):
            ideal_time = noon - 3600*24*index
            file       = min(files, key=lambda f: abs(f[0] - ideal_time))[1]
            # Insist that "noon" imagery be +/- an hour of noon.
            if abs(os.path.getmtime(file) - ideal_time) > 3600: continue
            files_daily.insert(0, file)
        files = files_daily
    else:
        files = files[-FRAMES[sys.argv[1]]:]

    print('Encoding the following', len(files), 'files:', files)

    ffmpeg = subprocess.Popen(('ffmpeg',
        '-framerate', RATE[sys.argv[1]], # Framerate from RATE
        '-y',                          # Overwrite output path
        '-f', 'image2pipe', '-i', '-', # Read images from stdin
        '-c:v', 'libx264', '-c:a', 'aac',
        '-pix_fmt', 'yuv420p',
	'-qscale', '0',
	'-y',
	'-movflags', 'faststart',
	DEST.format(sys.argv[1]).replace('webm', 'mp4') 
       ), stdin=subprocess.PIPE)      # Write to a tempfile

    for path in files:
        with open(path, 'rb') as image:
            ffmpeg.stdin.write(image.read())
    ffmpeg.stdin.close()
    ffmpeg.wait()

main()
