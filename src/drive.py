from __future__ import print_function
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from datetime import datetime
from tinydb import Query
import explorer
import files

def list_files(parent_id, drive_service, drive_files, parents=None):
    try:
        page_token = None
        while True:
            response = drive_service.files().list(q="'{}' in parents".format(parent_id),
                spaces='drive',
                fields='nextPageToken, files(id, name, parents, md5Checksum, fileExtension, size, createdTime, modifiedTime)',
                pageToken=page_token).execute()
            for file in response.get('files', []):
                if not "fileExtension" in file.keys():
                    file["type"] = 'folder'
                else:
                    file["type"] = 'file'
                if parents:
                    file["parents"] = parents + file["parents"]
                print(f'{datetime.now()}: Checking {file["name"]}')
                drive_files.insert(file)
                if file["type"] == 'folder':
                    list_files(file["id"], drive_service, drive_files, file["parents"])
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
        return True
    except HttpError as error:
        print(f'{datetime.now()}: An error occurred: {error}')

def build_paths(drive_files, file_id):
    File = Query()
    if not file_id:
        files = drive_files.all()
    else:
        files = drive_files.search(File.id == file_id)
        if len(files) == 0:
            return
    cache = {}
    for file in files:
        if len(file["parents"]) == 1:
            file["relativePath"] = './' + file["name"]
        else:
            path = './'
            for i in range(1,len(file["parents"])):
                if file["parents"][i] in cache.keys():
                    path += cache[file["parents"][i]] + '/'
                else:
                    match = drive_files.search(File.id == file["parents"][i])
                    path += match[0]["name"] + '/'
                    cache[file["parents"][i]] = match[0]["name"]
            file["relativePath"] = path + file["name"]
        drive_files.update(file, File.id == file['id'])

#Verify local file on google drive
def find_file(file, drive_files):
    File = Query()
    if file["type"] == 'file':
        #Search by MD5 checksum
        match = drive_files.search(File.md5Checksum == file["md5Checksum"])
        if len(match) > 0:
            return {
                "exists": True,
                "sameFilename": file["name"] == match[0]["name"],
                "sameCreateDate": file["createdTime"].split('.')[0] == match[0]["createdTime"].split('.')[0],
                "sameModificationDate": file["modifiedTime"].split('.')[0] == match[0]["modifiedTime"].split('.')[0],
                "samePath": file["relativePath"] == match[0]["relativePath"],
                "sameHash": True,
                "remoteFileId": match[0]['id']
            }
        else:
            match = drive_files.search(File.relativePath == file["relativePath"])
            if len(match) > 0:
                return { 
                    "exists": True,
                    "sameFilename": True,
                    "sameCreateDate": file["createdTime"].split('.')[0] == match[0]["createdTime"].split('.')[0],
                    "sameModificationDate": file["modifiedTime"].split('.')[0] == match[0]["modifiedTime"].split('.')[0],
                    "samePath": True,
                    "sameHash": False,
                    "remoteFileId": match[0]['id']
                }
            else:
                return {"exists": False}
    elif file["type"] == 'folder':
        #Search by relative path
        match = drive_files.search(File.relativePath == file["relativePath"])
        if len(match) > 0:
            return {
                "exists": True,
                "sameFilename": True,
                "sameCreateDate": file["createdTime"].split('.')[0] == match[0]["createdTime"].split('.')[0],
                "sameModificationDate": file["modifiedTime"].split('.')[0] == match[0]["modifiedTime"].split('.')[0],
                "samePath": True,
                "remoteFileId": match[0]['id']
            }
        else:
            return {"exists": False}
    return None

#verify if drive files has to be transfered
def verify_sync(drive_files, local_files, sync_deletions):
    File = Query()
    files = drive_files.all()
    for drive_file in files:
        #Find drive file on local files
        res = explorer.find_file(drive_file, local_files)
        print(f'{datetime.now()}: [drive] {drive_file["name"]} {res}')
        if sync_deletions:
            if not res["exists"]:
                action = 'delete'
            elif res["exists"] and not res["samePath"]:
                action = 'delete'
            else:
                action = 'skip'
            print(f'{datetime.now()}: {drive_file["name"]} action = {action}')
            db_update = {"action": action}
            db_update.update(res)
            drive_files.update(db_update, File.relativePath == drive_file['relativePath'])
        else:
            action = 'skip'
            print(f'{datetime.now()}: [drive] {drive_file["name"]}: {action}')
            db_update = {"action": action}
            db_update.update(res)
            drive_files.update(db_update, File.relativePath == drive_file['relativePath'])

#create folder on google drive
def create_folder(folder_name, parents, creds):
    try:
        # create drive api client
        service = build('drive', 'v3', credentials=creds)
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': parents
        }
        # pylint: disable=maybe-no-member
        file = service.files().create(body=file_metadata,
         fields='id, name, parents, md5Checksum, fileExtension, size, createdTime, modifiedTime').execute()
    except HttpError as error:
        print(F'An error occurred: {error}')
        return None
    return file

#get ids of parents folders of a file
def get_parent_ids(local_file_path, drive_files, remote_dir):
    #print(f'[debug] LOCAL_FILE_PATH = {local_file_path}')
    File = Query()
    match = drive_files.search(File.relativePath == local_file_path)
    #print(f'[debug] LEN(MATCH) = {len(match)}')
    if len(match) > 0:
        #print(f'[debug] FOUND EXACT MATCH')
        return match[0]["parents"]
    parents = local_file_path.split('/')[1:-1]
    if len(parents) == 0:
        return [remote_dir]
    current_path = '.'
    search = list()
    for p in parents:
        current_path += '/' + p
        search.append(current_path)
    for p in search[::-1]:
        #print(f'[debug] SEARCHING {p}')
        match = drive_files.search(File.relativePath == p)
        if len(match) > 0:
            #print(f'[debug] FOUND {p}')
            return [match[0]["id"]]
    return None

#upload file to google drive
def upload_basic(filename, path, parents, creds):
    try:
        service = build('drive', 'v3', credentials=creds)
        file_metadata = {'name': filename, 'parents': parents}
        mime = files.getMIMEType(path)
        media = MediaFileUpload(path, mimetype=mime)
        file = service.files().create(
            body=file_metadata, 
            media_body=media,
            fields='id, name, parents, md5Checksum, fileExtension, size, createdTime, modifiedTime'
        ).execute()
    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None
    return file

#delete a file on google drive
def delete(file_id, creds):
    try:
        service = build('drive', 'v3', credentials=creds)
        service.files().delete(fileId=file_id, fields='id, name').execute()
        return True
    except HttpError as error:
        print(F'An error occurred: {error}')
        return False