from youtube_transcript_api import YouTubeTranscriptApi
import streamlit as st # type: ignore
import string
import math
import re
from urllib.parse import urlparse, parse_qs
import zipfile
from io import BytesIO
import os

def extract_youtube_video_id(url):
    """
    Extracts the video ID from a YouTube URL.

    Parameters:
        url (str): The YouTube URL.

    Returns:
        str or None: The video ID if found, otherwise None.
    """
    # Check if it's a standard YouTube URL
    parsed_url = urlparse(url)
    if parsed_url.netloc in ['www.youtube.com', 'youtube.com']:
        query_params = parse_qs(parsed_url.query)
        return query_params.get('v', [None])[0]

    # Check if it's a shortened YouTube URL
    if parsed_url.netloc in ['youtu.be']:
        return parsed_url.path.lstrip('/')

    # Try regex as a fallback
    match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})', url)
    if match:
        return match.group(1)

    return None

def GetTranscript(videoID):
    return YouTubeTranscriptApi.get_transcript(video_id=videoID, languages=['en'])

def clean_string(text):
    printable = set(string.printable)
    return ''.join(filter(lambda x: x in printable, text))

def WritePlain(videodict):
    with open("./PlainTranscript.txt", "w+") as f:
        for x in videodict:
            f.write(clean_string(x["text"])+"\n")

def ConvertSRTTime(time):
    if(time < 60):
        rounded = math.floor(time)
        ms = math.floor((time - rounded)*1000)
        if rounded < 10:
            rounded = "0"+str(rounded)
        else: rounded = str(rounded)
        if ms < 100:
            ms = "0"+str(ms)
        else: ms = str(ms)
        return("00:00:"+rounded+","+ms)
    elif ((time < 3600) and (time >= 60)):
        mins = math.floor(time/60)
        
        rounded = math.floor(time-mins*60)
        ms = math.floor((time-mins*60 - rounded)*1000)
        if mins < 10:
            mins = "0"+str(mins)
        else: mins = str(mins)
        if rounded < 10:
            rounded = "0"+str(rounded)
        else: rounded = str(rounded)
        if ms < 100:
            ms = "0"+str(ms)
        else: ms = str(ms)
        return("00:"+mins+":"+rounded+","+ms)
    else:
        hours = math.floor(time/3600)
        nohour = time - hours*3600
        mins = math.floor(nohour/60)
        rounded = math.floor(time-mins*60)
        ms = math.floor((time - hours*3600 - mins*60-rounded)*1000)
        if hours < 10:
            hours = "0"+str(hours)
        else: hours = str(hours)
        if mins < 10:
            mins = "0"+str(mins)
        else: mins = str(mins)
        if rounded < 10:
            rounded = "0"+str(rounded)
        else: rounded = str(rounded)
        if ms < 100:
            ms = "0"+str(ms)
        else: ms = str(ms)
        return(hours+":"+mins+":"+rounded+","+ms)

def FormatToSRT(videodict):
    print("started SRT")
    if(text_timed):
        f = open("./SRT_Transcript.txt", "w+")
        for x in videodict:
            f.write(ConvertSRTTime(x["start"])+" --> "+ConvertSRTTime(x["start"]+x["duration"])+" "+clean_string(x["text"])+"\n")
        f.close()
        
    if(srtfile):
        with open("./SRT_Transcript.srt", "w+") as f:
            for x in videodict:
                f.write(ConvertSRTTime(x["start"])+" --> "+ConvertSRTTime(x["start"]+x["duration"])+" "+clean_string(x["text"])+"\n")

file_dict = []

def AddtoDict():
    if(plaintxt):
        file_dict.append("./PlainTranscript.txt")
    if(srtfile):
        file_dict.append("./SRT_Transcript.srt")
    if(text_timed):
        file_dict.append("./SRT_Transcript.txt")

st.header("Youtube URL")
st.write("Desired Formats:")

col1, col2, col3 = st.columns([1,1,1])

with col1:
    text_timed = st.toggle("TXT file with time stamps", value=True)
with col2:
    srtfile = st.toggle("SRT file")
with col3:
    plaintxt = st.toggle("Plain TXT file")
inline = st.toggle("Show Captions")
url = st.text_input(label="Video url")
go = st.button(label="Get")
if(not srtfile and not text_timed and not plaintxt):
        st.warning("A file format must be chosen!")
        
if go:
    AddtoDict()
    print(file_dict)
    id = extract_youtube_video_id(url)
    if id:
        id = str(id)
        gotit = GetTranscript(id)
        if inline:
            for x in gotit:
                st.write(x)
                st.write("Line: "+clean_string(x["text"])+"\n")
        FormatToSRT(gotit)
        if(plaintxt):
            WritePlain(gotit)
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for file_path in file_dict:
                zip_file.write(file_path)
        zip_buffer.seek(0)
        st.download_button(label="Download FIles", data=zip_buffer, file_name="Transcripts.zip", mime="application/zip")
    else:
        st.warning("Not a YouTube url")