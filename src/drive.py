from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from tinydb import TinyDB
import auth
import sys
import os

def main():
    try:
        db = TinyDB('drive_files.json')
        creds = auth.get_credentials()
        if not creds:
            print('Error while retrieving credentials')
            sys.exit(0)
        service = build('drive', 'v3', credentials=creds)
        page_token = None
        while True:
            response = service.files().list(q="'{}' in parents".format('1rkSVumNLsAuD-F-anTHGzBly2D43Qyye'),
                spaces='drive',
                fields='nextPageToken, files(id, name, parents, md5Checksum, fileExtension, size, createdTime, modifiedTime)',
                pageToken=page_token).execute()
            for file in response.get('files', []):
                file["type"] = 'file'
                if not "fileExtension" in file.keys():
                    file["type"] = 'folder'
                print(file)
                db.insert(file)
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
    except HttpError as error:
        print(f'An error occurred: {error}')

if __name__ == '__main__':
    main()