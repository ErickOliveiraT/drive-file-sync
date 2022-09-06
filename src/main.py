from googleapiclient.discovery import build
from datetime import datetime
from tinydb import TinyDB
import explorer
import profiles
import drive
import files
import time
import json
import auth
import sync
import sys
import os

def run(profile, action):
    start_time = time.time()

    #remote drive files database
    drive_files_db_path = './data/' + profile['profile_name'] + '_remote.json'
    drive_files = TinyDB(drive_files_db_path)
    if action == 'start':
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

    
    if action == 'start':
        #list remote drive files
        print(f'{datetime.now()}: Checking remote files')
        drive.list_files(profile.get('remote_folder_id'), service, drive_files)

        #build path for drive files
        print(f'{datetime.now()}: Building paths for remote files')
        drive.build_paths(drive_files, None)

    #local files database
    local_files_db_path = './data/' + profile['profile_name'] + '_local.json'
    local_files = TinyDB(local_files_db_path)
    if action == 'start':
        print(f'{datetime.now()}: Cleaning database')
        if os.path.isfile(local_files_db_path):
            os.remove(local_files_db_path)
        local_files = TinyDB(local_files_db_path)

        #list local files
        print(f'{datetime.now()}: Checking local files')
        explorer.list_files(profile.get('local_folder_path'), local_files, profile.get('local_folder_path'), drive_files, profile.get('ignored_folders'))

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
        print('[1] Create profile\n[2] Start synchronization\n[3] Delete profile\n[4] Resume synchronization\n[5] Exit\n')
        option = int(input('Option: '))
        if option == 1:
            profiles.create_profile()
        elif option == 2:
            filename = profiles.list_profiles()
            with open(filename) as json_file:
                profile = json.load(json_file)
            print('')
            run(profile, 'start')
        elif option == 3:
            filename = profiles.list_profiles()
            option = input(f'\nAre you sure you want to delete "{files.getProfileName(filename)}"? (y/n): ')
            if option == 'y' or option == 'Y':
                os.remove(filename)
            print('')
        elif option == 4:
            filename = profiles.list_profiles()
            with open(filename) as json_file:
                profile = json.load(json_file)
            print('')
            run(profile, 'resume')
        elif option == 5:
            sys.exit(0)
        else:
            print('\nInvalid option')
            sys.exit(0)