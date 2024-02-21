from moviepy.editor import *
import os
import random
import cv2
from mapvid import generate_map_vid
from moviepy.config import change_settings
import datetime
from pathlib import Path

change_settings({"IMAGEMAGICK_BINARY": "/usr/local/Cellar/imagemagick/7.1.1-21/bin/convert"})
change_settings({"FFMPEG_BINARY":"/usr/local/bin/ffmpeg"})


def with_opencv(filename):
    video = cv2.VideoCapture(filename)

    frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)

    fps = video.get(cv2.CAP_PROP_FPS) 
  
    # calculate duration of the video 
    seconds = round(frame_count / fps) 
    video_time = datetime.timedelta(seconds=seconds) 
    # print(f"duration in seconds: {seconds}") 
    # print(f"video time: {video_time}") 
    return seconds, video_time, frame_count


def process(dir="./",CD=5,title="None",audio_loc=None,final_loc="clip/random.mp4", final_height=1080, final_width=1920):
    clips=[]

    paths = sorted(Path(dir).iterdir(), key=os.path.basename)

    final_time=0
    for path in paths:
        fname=path.parts[-1]
        if ( (fname[-6:].lower()=="_r.mp4") | (fname[-6:].lower()=="_f.mp4") ):
            seconds,_,_=with_opencv(dir+fname)
            if seconds > 10:
                start_time=random.randint(0,seconds-CD)
                end_time=start_time+CD
                generate_map_vid(dir+fname)
                clip = VideoFileClip(dir+fname).volumex(0.0).subclip(start_time,end_time).resize(width=final_width,height=final_height)

                gps_clip = VideoFileClip(dir+fname+"_gps.mp4").resize(width=final_width/4,height=final_height/4).set_pos((0.0,0.75),relative=True).subclip(start_time,end_time)

                speed_clip = VideoFileClip(dir+fname+"_speed.mp4").resize(width=final_width/4,height=final_height/4).set_pos((0.25,0.75),relative=True).subclip(start_time,end_time)

                clips.append(CompositeVideoClip([clip,gps_clip,speed_clip]).crossfadein(1))

                final_time+=CD

    print(final_time)
    final = concatenate_videoclips(clips)

    if title:
        # Generate a text clip. You can customize the font, color, etc.
        txt_clip = TextClip(title,fontsize=70,color='white')
        
        # Say that you want it to appear 10s at the center of the screen
        txt_clip = txt_clip.set_pos('center').set_duration(3).set_start(0)
        
        # Generate a text clip. You can customize the font, color, etc.
        txt_clip2 = TextClip("Thanks for watching",fontsize=70,color='white')
        
        # Say that you want it to appear 10s at the center of the screen
        txt_clip2 = txt_clip2.set_pos('center').set_duration(3).set_start(final_time)
        
        
        # Overlay the text clip on the first video clip
        video = CompositeVideoClip([final, txt_clip,txt_clip2])
    else:
        video = CompositeVideoClip([final])

    if audio_loc:
        audio_clip=AudioFileClip(dir+audio_loc).subclip(0,final_time).audio_fadeout(1)
        video=video.set_audio(audio_clip)
    
    video.write_videofile(dir+final_loc, 
                         codec='libx264', 
                         audio_codec='aac', 
                         temp_audiofile='temp-audio.m4a', 
                         remove_temp=True)
    video.close()



def process_manual(entries,title="None",audio_loc=None,final_loc="clip/select.mp4", final_height=1080, final_width=1920):
    """
    entries: list of dictionary objects with videos and images
         Example: 
              [
                {"type":"video","name":"video1","st":3,"et":10},
                {"type":"video","name":"video2","st":3,"et":10},
                {"type":"video","name":"video3","st":3,"et":10},
                {"type":"image","name":"pic1"},
                {"type":"image","name":"pic2"}
              ]
    """

    clips=[]
    i=0

    iclips=[]
    final_time=0
    for entry in entries:
        print(entry)
        fname=entry['name']
        type=entry['type']
        if (type=="video"):
            seconds,_,_=with_opencv(fname)
            start_time=entry['st']
            end_time=min(entry['et'],seconds)
            clip = VideoFileClip(fname).volumex(0.0).subclip(start_time,end_time).resize(width=final_width,height=final_height).set_start(final_time)
            generate_map_vid(fname)

            gps_clip = VideoFileClip(fname+"_gps.mp4").subclip(start_time,end_time).resize(width=final_width/4,height=final_height/4).set_pos((0.0,0.75),relative=True).set_start(final_time)

            speed_clip = VideoFileClip(fname+"_speed.mp4").subclip(start_time,end_time).resize(width=final_width/4,height=final_height/4).set_pos((0.25,0.75),relative=True).set_start(final_time)

            final_time+=(end_time-start_time)

            #clips.append(clip)
            clips.append(CompositeVideoClip([clip,gps_clip,speed_clip]).crossfadein(1))
        elif (type=="image"):
            iclip = ImageClip(fname).set_pos('center','center').set_duration(3).resize(height=final_height).crossfadein(1).set_start(final_time)
            final_time+=3
            iclips.append(iclip)

    print(final_time)
    #final=concatenate_videoclips(clips)
    
    if title:
        txt_clip = TextClip(title,fontsize=70,color='white')
        txt_clip = txt_clip.set_pos('center').set_duration(3).set_start(0)
        txt_clip2 = TextClip("Thanks for watching",fontsize=70,color='white')
        txt_clip2 = txt_clip2.set_pos('center').set_duration(3).set_start(final_time)
    
    video = CompositeVideoClip(clips+iclips+[txt_clip, txt_clip2])

    if audio_loc:
        audio_clip=AudioFileClip(audio_loc).subclip(0,final_time).audio_fadeout(1)
        video=video.set_audio(audio_clip)
    
    video.write_videofile(final_loc, 
                         codec='libx264', 
                         audio_codec='aac', 
                         temp_audiofile='temp-audio.m4a', 
                         remove_temp=True)

    video.close()

