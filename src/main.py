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

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def run(profile, action, run_sync):
    start_time = time.time()

    #remote drive files database
    drive_files_db_path = './data/' + profile['profile_name'] + '_remote.json'
    if action == 'start':
        print(f'{datetime.now()}: Cleaning remote files database')
        if os.path.isfile(drive_files_db_path):
            os.remove(drive_files_db_path)
    drive_files = TinyDB(drive_files_db_path)

    #local files database
    local_files_db_path = './data/' + profile['profile_name'] + '_local.json'
    if action == 'start':
        print(f'{datetime.now()}: Cleaning local files database')
        if os.path.isfile(local_files_db_path):
            os.remove(local_files_db_path)
    local_files = TinyDB(local_files_db_path)

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

    if action == 'start':
        #list local files
        print(f'{datetime.now()}: Checking local files')
        explorer.list_files(profile.get('local_folder_path'), local_files, profile.get('local_folder_path'), drive_files, profile.get('ignored_folders'))
        
        #find corresponding local files of remote files
        print(f'{datetime.now()}: Comparing local and remote folders...')
        drive.find_files(drive_files, local_files)

        #get file actions
        print(f'{datetime.now()}: Getting local files actions...')
        explorer.get_actions(local_files)
        print(f'{datetime.now()}: Getting remote files actions...')
        drive.get_actions(drive_files)

        #get duplicated file on drive
        print(f'{datetime.now()}: Searching for duplicated files on remote drive...')
        dup_list = drive.duplicated_files(drive_files)
        print(f'{datetime.now()}: Found {len(dup_list)} duplicated files.')

    print(f'\nTook {(time.time() - start_time)/60} minutes\n')

    #sync
    if run_sync:
        print(f'{datetime.now()}: Starting file sync')
        start_time = time.time()
        sync.sync(local_files, drive_files, profile.get('remote_folder_id'), creds)
        print(f'{datetime.now()}: File sync finished\n')
        print(f'\nTook {(time.time() - start_time)/60} minutes\n')


if __name__ == '__main__':
    while True:
        print('[1] Create profile')
        print('[2] Delete profile')
        print('[3] Check profile')
        print('[4] Start synchronization')
        print('[5] Resume synchronization')
        print('[6] Synchronization status')
        print('[7] Exit\n')
        option = int(input('Option: '))
        if option == 1: #Create profile
            profiles.create_profile()
        elif option == 3: #Check
            filename = profiles.list_profiles()
            with open(filename) as json_file:
                profile = json.load(json_file)
            print('')
            run(profile, 'start', False)
        elif option == 4: #Start sync
            option = input('\nRun check? (y/n): ')
            if option == 'y' or option == 'Y':
                action = 'start'
            else:
                action = 'resume'
            filename = profiles.list_profiles()
            with open(filename) as json_file:
                profile = json.load(json_file)
            print('')
            run(profile, action, True)
        elif option == 2: #Delete profile
            filename = profiles.list_profiles()
            option = input(f'\nAre you sure you want to delete "{files.getProfileName(filename)}"? (y/n): ')
            if option == 'y' or option == 'Y':
                os.remove(filename)
            print('')
        elif option == 5: #Resume sync
            filename = profiles.list_profiles()
            with open(filename) as json_file:
                profile = json.load(json_file)
            print('')
            run(profile, 'resume', True)
        elif option == 6: #Sync status
            filename = profiles.list_profiles()
            with open(filename) as json_file:
                profile = json.load(json_file)
            print('')
            sync.status(profile)
        elif option == 7: #Exit
            sys.exit(0)
        else: #Default
            print('\nInvalid option')
            sys.exit(0)