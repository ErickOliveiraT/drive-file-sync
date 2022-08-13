
from googleapiclient.errors import HttpError
from datetime import datetime
from tinydb import Query

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

def build_paths(drive_files):
    files = drive_files.all()
    File = Query()
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
                "sameHash": True
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
                    "sameHash": False
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
                "samePath": True
            }
        else:
            return {"exists": False}
    return None

#verify if drive files has to be transfered
def verify_sync(drive_files, sync_deletions):
    File = Query()
    if sync_deletions:
        for drive_file in drive_files.all():
            if not drive_file["exists"]:
                action = 'delete'
            elif drive_file["exists"] and not drive_file["samePath"]:
                action = 'delete'
            else:
                action = 'skip'
            print(f'{datetime.now()}: [drive] {drive_file["name"]}: {action}')
            db_update = {"action": action}
            drive_files.update(db_update, File.relativePath == drive_file['relativePath'])
    else:
        for drive_file in drive_files.all():
            action = 'skip'
            print(f'{datetime.now()}: [drive] {drive_file["name"]}: {action}')
            db_update = {"action": action}
            drive_files.update(db_update, File.relativePath == drive_file['relativePath'])