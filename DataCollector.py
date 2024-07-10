from youtube_transcript_api import YouTubeTranscriptApi
import googleapiclient.discovery
from Utils import get_channel_id_from_url,  get_video_ids, get_statistics, download_thumbnail, face_recognition, text_recognition
import os
import pandas as pd

CHANNEL_URLS = [                                   
    "https://www.youtube.com/@Lionfield",
    "https://www.youtube.com/@MrBeast",
    "https://www.youtube.com/@tiger_in_translation"
]
api_service_name = "youtube"
api_version      = "v3"
YOUTUBE_API_KEY  = "AIzaSyDasnckxNK0zvrgdk9cqjLPDyR44p7y2WQ"

youtube = googleapiclient.discovery.build(
api_service_name, api_version, developerKey = YOUTUBE_API_KEY)

video_data = []
for url in CHANNEL_URLS:
    CHANNEL_ID = get_channel_id_from_url(youtube, url)
    print(CHANNEL_ID)
    video_ids = get_video_ids(youtube, CHANNEL_ID)
    video_data += get_statistics(youtube, video_ids)

save_folder = "./"
THUMBNAILS_FOLDER = save_folder + 'thumbnails/'
if not os.path.exists(THUMBNAILS_FOLDER):
    os.makedirs(THUMBNAILS_FOLDER)

for data in video_data:
    download_thumbnail(youtube, data['title'], data['videoId'], THUMBNAILS_FOLDER)
    # face_recognition(THUMBNAILS_FOLDER + video_id + '.jpg')
    video_data[video_data.index(data)]['thumbnailText'] = text_recognition(THUMBNAILS_FOLDER + data['title'] + '.jpg', "en")

print(video_data)

