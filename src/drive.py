from __future__ import print_function
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from datetime import datetime
from tinydb import Query
from uuid import uuid4
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
                file["uid"] = str(uuid4())
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
        del file["uid"]
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
            for remote_file in match:
                if file["relativePath"] == remote_file["relativePath"]:
                    return {
                        "exists": True,
                        "sameFilename": file["name"] == remote_file["name"],
                        "sameCreateDate": file["createdTime"].split('.')[0] == remote_file["createdTime"].split('.')[0],
                        "sameModificationDate": file["modifiedTime"].split('.')[0] == remote_file["modifiedTime"].split('.')[0],
                        "samePath": True,
                        "sameHash": True,
                        "remoteFileId": remote_file['id']
                    }
            return {
                "exists": True,
                "sameFilename": file["name"] == remote_file["name"],
                "sameCreateDate": file["createdTime"].split('.')[0] == remote_file["createdTime"].split('.')[0],
                "sameModificationDate": file["modifiedTime"].split('.')[0] == remote_file["modifiedTime"].split('.')[0],
                "samePath": False,
                "sameHash": True,
                "remoteFileId": remote_file['id']
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
        if not mime:
            return None
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
        return {'deleted': True}
    except HttpError as error:
        print(F'An error occurred: {error}')
        return {'deleted': False, 'reason': error.error_details[0]['reason']}

#Copy a file to another location
def copy_file(file_id, parents, creds):
  service = build('drive', 'v3', credentials=creds)
  copied_file = {'parents': parents}
  try:
    file = service.files().copy(
        fileId=file_id,
        body=copied_file
    ).execute()
    return file
  except HttpError as error:
    print(F'An error occurred: {error}')
    return None

#Get remote file object from database
def get_file(file_id, drive_files):
    File = Query()
    qry = drive_files.search(File.id == file_id)
    if len(qry) > 0:
        return qry[0]
    return None

#get file sync action
def get_actions(drive_files):
    File = Query()
    for file in drive_files.all():
        if not file["exists"]:
            action = 'delete'
        else: #exists local file
            if file["samePath"]:
                action = 'skip'
            else:
                action = 'delete'
        db_update = {'action': action}
        drive_files.update(db_update, File.relativePath == file['relativePath'])

#search corresponding files on local storage
def find_files(drive_files, local_files):
    File = Query()
    for file in drive_files.all():
        res = explorer.find_file(file, local_files)
        if res:
            file.update(res)
            del file['uid']
            drive_files.update(file, File.relativePath == file['relativePath'])
    return True

#get duplicated files
def duplicated_files(drive_files):
    File = Query()
    dup_list = []
    for file in drive_files.all():
        if file["relativePath"] in dup_list:
            continue
        qry = drive_files.search(File.relativePath == file["relativePath"])
        if len(qry) > 1:
            for i in range(1,len(qry)):
                dup = qry[i]
                if not dup["relativePath"] in dup_list:
                    dup_list.append("relativePath")
                    db_update = {'action': 'delete', 'duplicated': True}
                    drive_files.update(db_update, File.uid == file['uid'])
    return dup_list