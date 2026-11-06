import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

def get_authenticated_service():
    credentials = None

    # The file token.json stores the user's access and refresh tokens.
    if os.path.exists(os.path.join("Youtube", "Config", "token.json")):
        credentials = Credentials.from_authorized_user_file(os.path.join("Youtube", "Config", "token.json"))

    # If credentials are invalid or expired, refresh them
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            raise Exception("No valid credentials available. Please run auth.py to authenticate.")

        # Save the refreshed credentials
        with open(os.path.join("Youtube", "Config", "token.json"), 'w') as token:
            token.write(credentials.to_json())

    return build('youtube', 'v3', credentials=credentials)

def upload_video(service, video_file, title, description, category_id, tags, privacy_status='private'):
    # YouTube rejects < and > and titles longer than 100 characters
    title = title.replace('<', '').replace('>', '')[:100]
    description = description.replace('<', '').replace('>', '')

    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
            'categoryId': category_id
        },
        'status': {
            'privacyStatus': privacy_status,
            'selfDeclaredMadeForKids': False
        }
    }

    # Call the API's videos.insert method to create and upload the video.
    media_body = MediaFileUpload(video_file, chunksize=-1, resumable=True)
    request = service.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=media_body
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print("Uploaded %d%%." % int(status.progress() * 100))
    print("Upload Complete!")
    print("Video ID: %s" % response.get('id'))
    return response.get('id')


def set_thumbnail(service, video_id, image_file):
    # Needs a verified channel, YouTube may not accept it for every Short
    service.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(image_file)).execute()
    print("Thumbnail set.")
