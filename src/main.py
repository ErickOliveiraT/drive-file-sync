from googleapiclient.discovery import build
from datetime import datetime
from tinydb import TinyDB
import explorer
import drive
import time
import auth
import sys
import os

remote_dir = '1l-sKq0MPteFHFQO_iDUYqLfCe-OcY31n' #teste
#remote_dir = '1nYTt2DpKVjRH1MnKMDHKIt8AcIUf4YYz' #teste2
# local_dir = "C:/Users/erick/Desktop/teste/"
#local_dir = "C:/Users/erick/Desktop/teste2/"
local_dir = "D:/Arquivos/"
sync_deletions = True

def main():
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
    drive.list_files(remote_dir, service, drive_files)

    #build path for drive files
    print(f'{datetime.now()}: Building paths for remote files')
    drive.build_paths(drive_files)

    #local files database
    local_files_db_path = 'local_files.json'
    print(f'{datetime.now()}: Cleaning database')
    if os.path.isfile(local_files_db_path):
        os.remove(local_files_db_path)
    local_files = TinyDB(local_files_db_path)

    #list local files
    print(f'{datetime.now()}: Checking local files')
    explorer.list_files(local_dir, local_files, local_dir, drive_files)

    #verify if drive files has to be transfered
    drive.verify_sync(drive_files, local_files, sync_deletions)

    print(f'\nTook {(time.time() - start_time)/60} minutes')

if __name__ == '__main__':
    main()