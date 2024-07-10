import re
import isodate
import cv2
import easyocr
import numpy as np
import matplotlib.pyplot as plt
import requests
import os

CONFIDENCE_THRESHOLD = 0.5  
MAX_RESULTS = 2
def get_channel_id_from_url(youtube, url):
    match = re.search(r'(?:https?://)?(?:www\.)?(?:youtube\.com/(?:user/|channel/|c/|@))([a-zA-Z0-9_-]+)', url)
    if not match:
        raise ValueError("Invalid YouTube URL")
    identifier = match.group(1)

    try:
        request = youtube.channels().list(
            part='id',
            forHandle=identifier
        )
        response = request.execute()
        if response['items']:
            return response['items'][0]['id']
    except:
        pass

    request = youtube.search().list(
        part='snippet',
        q=identifier,
        type='channel'
    )
    response = request.execute()
    if response['items']:
        return response['items'][0]['snippet']['channelId']

    raise ValueError("Channel not found")

def get_video_ids(youtube, channel_id):
    request = youtube.search().list(
        part='id',
        channelId=channel_id,
        maxResults=MAX_RESULTS,         # retireve up to 50 videos from the channel
        order='date',                   # order the results by date
        type='video',
        videoDuration='medium',         # only retrieve medium videos
    )
    response = request.execute()
    video_ids = []
    for item in response['items']:
        video_ids.append(item['id']['videoId'])
    return video_ids

def get_statistics(youtube, video_ids):

    # Fetch video data
    stats_request = youtube.videos().list(
        part=['statistics', 'snippet', 'contentDetails'],
        id=','.join(video_ids),

    )
    stats_response = stats_request.execute()

    videos = []
    for item in stats_response['items']:
        if int(item['statistics']['viewCount']) > 10000:
            videos.append({
                'channelId': item['snippet']['channelId'],
                'channelTitle': item['snippet']['channelTitle'],
                'videoId': item['id'],
                'viewCount': item['statistics']['viewCount'],
                'likeCount': item['statistics']['likeCount'],
                'dislikeCount': item['statistics']['dislikeCount'],
                "favoriteCount": item['statistics']['favoriteCount'],
                'commentCount': item['statistics']['commentCount'],
                'durationInSeconds': isodate.parse_duration(item['contentDetails']['duration']).total_seconds(),
                'publishedAt': item['snippet']['publishedAt'],
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
            })
    return videos

def download_thumbnail(youtube, video_title, video_id, save_folder):
    request = youtube.videos().list(
        part='snippet',
        id=video_id
    )
    response = request.execute()

    thumbnail_url = response['items'][0]['snippet']['thumbnails']['high']['url']
    response = requests.get(thumbnail_url)
    if response.status_code == 200:
        with open(os.path.join(save_folder, f'{video_title}.jpg'), 'wb') as f:
            f.write(response.content)
    else:
        print(f"Failed to download thumbnail for video ID: {video_id}")

def face_recognition(save_folder, image_file):

    # Haar Cascade
    cascade_path = save_folder + "/haarcascade_frontalface_default.xml"

    # Haar Cascade
    face_cascade = cv2.CascadeClassifier(cascade_path)

    # Read image
    image = cv2.imread(image_file)
    if image is None:
        print(f"Error: Could not load image from {image_file}")  # Check if image loaded successfully
        return

    gray  = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect face
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Draw a rectangle in the detected face
    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)

    # Show the result
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.axis('off')
    plt.show()

def text_recognition(image_file, lang):
    # Read image
    image = cv2.imread(image_file)
    gray  = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    new_width = 400
    scale_ratio = new_width / image.shape[1]
    new_height = int(image.shape[0] * scale_ratio)
    image = cv2.resize(image, (new_width, new_height))

    reader = easyocr.Reader([lang])
    results = reader.readtext(image)
    texts = []
    for (bbox, text, prob) in results:
        if prob >= CONFIDENCE_THRESHOLD:
            (top_left, top_right, bottom_right, bottom_left) = bbox
            top_left = (int(top_left[0]), int(top_left[1]))
            bottom_right = (int(bottom_right[0]), int(bottom_right[1]))

            print(f"Detected Text: {text} (Confidence: {prob:.2f})")
            cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)

            texts.append(text)

    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.axis('off')
    plt.show()

    return texts