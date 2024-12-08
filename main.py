from youtube_transcript_api import YouTubeTranscriptApi
import streamlit as st # type: ignore
import string

import re
from urllib.parse import urlparse, parse_qs

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
    with open("Transcript.txt", "w+") as f:
        for x in videodict:
            f.write("Line: "+clean_string(x["text"])+"\n")

st.header("Youtube URL")
st.write("What")
url = st.text_input(label="Video ID")
go = st.button(label="Get")
if go:
    id = extract_youtube_video_id(url)
    if id:
        id = str(id)
        gotit = GetTranscript(id)
        for x in gotit:
            st.write("Line: "+clean_string(x["text"])+"\n")
        WritePlain(gotit)
    else:
        st.warning("Not a YouTube url")