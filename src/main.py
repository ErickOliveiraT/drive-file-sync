from googleapiclient.discovery import build
from datetime import datetime
from tinydb import TinyDB
import explorer
import profiles
import drive
import time
import json
import auth
import sync
import sys
import os

def main(profile):
    start_time = time.time()

    #remote drive files database
    drive_files_db_path = 'drive_files.json'
    print(f'{datetime.now()}: Cleaning database')
    if os.path.isfile(drive_files_db_path):
        os.remove(drive_files_db_path)
    drive_files = TinyDB(drive_files_db_path)

    #start google drive service
    print(f'{datetime.now()}: Starting Google Drive Service')
    creds = auth.get_credentials()
    if not creds:
        print(f'{datetime.now()}: Error while retrieving credentials')
        sys.exit(0)
    service = build('drive', 'v3', credentials=creds)

    #list remote drive files
    print(f'{datetime.now()}: Checking remote files')
    drive.list_files(profile.get('remote_folder_id'), service, drive_files)

    #build path for drive files
    print(f'{datetime.now()}: Building paths for remote files')
    drive.build_paths(drive_files, None)

    #local files database
    local_files_db_path = 'local_files.json'
    print(f'{datetime.now()}: Cleaning database')
    if os.path.isfile(local_files_db_path):
        os.remove(local_files_db_path)
    local_files = TinyDB(local_files_db_path)

    #list local files
    print(f'{datetime.now()}: Checking local files')
    explorer.list_files(profile.get('local_folder_path'), local_files, profile.get('local_folder_path'), drive_files)

    #verify if drive files has to be transfered
    drive.verify_sync(drive_files, local_files, profile.get('sync_deletions'))

    print(f'\nTook {(time.time() - start_time)/60} minutes\n')

    #sync
    print(f'{datetime.now()}: Starting file sync')
    start_time = time.time()
    sync.sync(local_files, drive_files, profile.get('remote_folder_id'), creds)
    print(f'{datetime.now()}: File sync finished\n')

    print(f'\nTook {(time.time() - start_time)/60} minutes\n')


if __name__ == '__main__':
    while True:
        print('[1] Create profile\n[2] Load profile\n[3] Exit\n')
        option = int(input('Option: '))
        if option == 1:
            profiles.create_profile()
        elif option == 2:
            filename = profiles.list_profiles()
            with open(filename) as json_file:
                profile = json.load(json_file)
            print('')
            main(profile)
        elif option == 3:
            sys.exit(0)
        else:
            print('\nInvalid option')
            sys.exit(0)