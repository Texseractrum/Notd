import base64
import requests
import os
from mistralai import Mistral
from google.cloud import texttospeech
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from flask import Flask, request, redirect, url_for, render_template
from oauth2client.file import Storage
from oauth2client.tools import run_flow
from googleapiclient import discovery
import httplib2
from datetime import datetime, timedelta
import pytz
import subprocess
import webbrowser
import requests
import random


import base64
import requests
import os
from mistralai import Mistral
from flask import Flask, request, redirect, render_template
import threading
import time
import webbrowser



file_name = 0
content = 0
flag1 = 0
flag2 = 1
flag3 = 1
file_path = 0
flag4 = 0
title = ""





from flask import Flask, render_template, request, redirect
import os
import webbrowser
import threading
import time

file_path = ""

app = Flask(__name__)
UPLOAD_FOLDER = r'/Users/lv/NoteVids/uploads'  # Change this to your desired upload directory
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    global file_path
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        return redirect(request.url)
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    print(file.filename)
    global file_name
    file_name = file.filename


    post_upload_logic()
    
    return 'File uploaded successfully!'

def post_upload_logic():
    print(f"File has been uploaded to: {file_path}")
    global flag4
    flag4 = 1

def open_browser():
    time.sleep(1)  # Give the server a second to start
    webbrowser.open('http://127.0.0.1:5000')

def start_flask_app():
    app.run(debug=True, use_reloader=False)  # Avoid reloader

if __name__ == '__main__':
    threading.Thread(target=open_browser).start()
    flask_thread = threading.Thread(target=start_flask_app)
    flask_thread.start()
    
    print("Flask app is running in the background. Now running post-flask code!")

while flag3:  # This will run indefinitely; adjust as needed
    if flag4:
        flag3 = 0
        print("Image detection starts")
        def encode_image(image_path):
            """Encode the image to base64."""
            try:
                with open(image_path, "rb") as image_file:
                    return base64.b64encode(image_file.read()).decode('utf-8')
            except FileNotFoundError:
                print(f"Error: The file {image_path} was not found.")
                return None
            except Exception as e:  # Added general exception handling
                print(f"Error: {e}")
                return None

        # Path to your image
        image_path = str(file_path)
        print(file_name)
        print(image_path)

        # Getting the base64 string
        base64_image = encode_image(image_path)

        # Retrieve the API key from environment variables
        api_key = "e1P6Jj7BXAqTQxZHgxdThR0Rsofjokpw"

        # Specify model
        model = "pixtral-12b-2409"

        # Initialize the Mistral client
        client = Mistral(api_key=api_key)

        # Define the messages for the chat
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Use OCR on this image"
                    },
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{base64_image}" 
                    }
                ]
            }
        ]

        # Get the chat response
        chat_response = client.chat.complete(
            model=model,
            messages=messages
        )

        # Print the content of the response

        content = chat_response.choices[0].message.content
        print(content)

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "ignore previous messages. Create a title for a recording with following content:" + content
                    },
                ]
            }
        ]

        # Get the chat response
        chat_response = client.chat.complete(
            model=model,
            messages=messages
        )
        title = chat_response.choices[0].message.content


def getScheduleDateTime(days = 0):
    # Set the publish time to 2 PM Eastern Time (US) on the next day
    eastern_tz = pytz.timezone('America/Los_Angeles')
    publish_time = datetime.now(eastern_tz)
    if days>0:
        publish_time = datetime.now(eastern_tz) + timedelta(days)
    publish_time = publish_time.replace(hour=14, minute=0, second=0, microsecond=0)

    # Set the publish time in the UTC timezone
    publish_time_utc = publish_time.astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    return publish_time_utc

# Start the OAuth flow to retrieve credentials
def authorize_credentials():
    CLIENT_SECRET = 'client_secret.json'
    SCOPE = 'https://www.googleapis.com/auth/youtube'
    STORAGE = Storage('credentials.storage')
    # Fetch credentials from storage
    credentials = STORAGE.get()
    # If the credentials doesn't exist in the storage location then run the flow
    if credentials is None or credentials.invalid:
        flow = flow_from_clientsecrets(CLIENT_SECRET, scope=SCOPE)
        http = httplib2.Http()
        credentials = run_flow(flow, STORAGE, http=http)
    return credentials

def getYoutubeService():
    credentials = authorize_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://www.googleapis.com/discovery/v1/apis/youtube/v3/rest')
    service = discovery.build('youtube', 'v3', http=http, discoveryServiceUrl=discoveryUrl)
    return service

def upload_video(file_path, title, description='', tags=[], privacy_status = 'public',day=0):
    print("Uploading...")
    youtube = getYoutubeService()
    try:
        # Define the video resource object
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
            },
            'status': {
                'privacyStatus': privacy_status
            }
        }

        if privacy_status == 'private':
            body['status']['publishAt'] = getScheduleDateTime(day)

        # Define the media file object
        media_file = MediaFileUpload(file_path)

        # Call the API's videos.insert method to upload the video
        videos = youtube.videos()
        response = videos.insert(
            part='snippet,status',
            body=body,
            media_body=media_file
        ).execute()

        # Print the response after the video has been uploaded
        print('Video uploaded successfully!\n')
        print(f'Title: {response["snippet"]["title"]}')
        print(f'URL: https://www.youtube.com/watch?v={response["id"]}')
        webbrowser.open(f'https://www.youtube.com/watch?v={response["id"]}')


    except HttpError as e:
        # print(f'An HTTP error {error.resp.status} occurred:\n{error.content}')
        raise Exception(f"An HTTP error {e.resp.status} occurred: {e.content.decode('utf-8')}")


flag = 1
while(flag):
    if(content != 0):
        flag = 0
        # Use the path to your service account file directly
        service_account_file = r"/Users/lv/NoteVids/balmy-apogee-437712-k5-45efcd874032.json"

        # Initialize the Text-to-Speech client using the service account file
        client = texttospeech.TextToSpeechClient.from_service_account_file(service_account_file)

        # Set the text input to be synthesizedy
        synthesis_input = texttospeech.SynthesisInput(text = str(content))

        # Build the voice request, select the language code ("en-US") and the ssml
        # voice gender ("neutral")
        voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )

        # Select the type of audio file you want returned
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        # Perform the text-to-speech request on the text input with the selected
        # voice parameters and audio file type
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        # The response's audio_content is binary.
        global tag
        tag = random. randint(1, 100)
        with open("output" + str(tag), "wb") as out:
            # Write the response to the output file.
            out.write(response.audio_content)
            print('Audio content written to file')


        def convert_mp3_to_mp4_with_black_screen(mp3_file_path, output_directory=None):
            # Check if the input file exists
            if not os.path.isfile(mp3_file_path):
                raise FileNotFoundError(f"The file {mp3_file_path} does not exist.")
            
            # Define the output file path
            if output_directory:
                os.makedirs(output_directory, exist_ok=True)  # Create output directory if it doesn't exist
                base_name = os.path.splitext(os.path.basename(mp3_file_path))[0]
                mp4_file_path = os.path.join(output_directory, f"{base_name}.mp4")
            else:
                mp4_file_path = os.path.splitext(mp3_file_path)[0] + '.mp4'
            
            # FFmpeg command to create a video with a black screen and the audio
            command = [
                'ffmpeg',
                '-f', 'lavfi',                     # Use lavfi (FFmpeg's internal filter)
                '-i', 'color=c=black:s=1280x720:d=10',  # Create a black video (width x height x duration in seconds)
                '-i', mp3_file_path,               # Input audio file
                '-c:v', 'libx264',                 # Video codec
                '-tune', 'stillimage',             # Tune for still image
                '-c:a', 'aac',                     # Audio codec
                '-b:a', '192k',                    # Audio bitrate
                '-shortest',                       # Stop encoding when the shortest input ends
                mp4_file_path                       # Output file
            ]
            
            # Run the FFmpeg command
            subprocess.run(command, check=True)
            
            print(f"Successfully converted '{mp3_file_path}' to '{mp4_file_path}' with a black screen.")
            global flag1
            flag1 = 1
            

        # Example usage:
        try:
            convert_mp3_to_mp4_with_black_screen("output"+str(tag))
        except Exception as e:
            print(f"An error occurred: {e}")

        while(flag2 == 1):
            if(flag1 == 1):
                flag2 = 0
                vid_path= str("output"+str(tag)) + '.mp4'
                upload_video(vid_path,str(title))

        
             






