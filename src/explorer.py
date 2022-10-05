from datetime import datetime
from tinydb import Query
import files
import drive
import os
import sys

def list_files(path, local_files, root_dir, drive_files, ignore=[]):
    if root_dir[len(root_dir)-1] == '\\' or root_dir[len(root_dir)-1] == '/':
        root_dir = root_dir[:-1]
    for x in os.listdir(path):
        print(f'{datetime.now()}: Checking {x}')
        stats = os.stat(path+'\\'+x)
        is_file = os.path.isfile(path+'\\'+x)
        if not is_file and x in ignore:
            continue
        file = {
            "name": x,
            "createdTime": str(datetime.fromtimestamp(stats.st_ctime)).replace(' ', 'T'),
            "modifiedTime": str(datetime.fromtimestamp(stats.st_mtime)).replace(' ', 'T'),
            "type": "file" if is_file else "folder",
            "absPath": path + x,
            "fileExtension": x.split('.')[1] if is_file and len(x.split('.')) > 1 else '',
            "md5Checksum": files.getMD5sum(path+x) if is_file else ''
        }
        file["relativePath"] = '.' + file["absPath"].split(root_dir)[1].replace('\\','/')
        if not is_file:
            list_files(path+x+'/', local_files, root_dir, drive_files, ignore)
        try:
            #Find file on google drive
            res = drive.find_file(file, drive_files)
            file.update(res)
            print(f'{datetime.now()}: {file["name"]} {res}')

            #verify if files has to be transfered
            if file["exists"] and file["samePath"]:
                if file["type"] == 'file':
                    if file["sameHash"]:
                        action = 'skip'
                    else:
                        action = 'update'
                else:
                    action = 'skip'
            elif file["exists"] and not file["samePath"]:
                remote_file = drive.get_file(file["remoteFileId"], drive_files)
                if remote_file and 'action' in remote_file.keys():
                    if remote_file['action'] != 'skip':
                        action = 'move'
                    else:
                        action = 'upload'
            elif not file["exists"]:
                action = 'upload'

            print(f'{datetime.now()}: {file["name"]} action = {action}')
            file["action"] = action
            local_files.insert(file)
        except:
            pass
    return True

#Verify google drive file in local files
def find_file(file, local_files):
    File = Query()
    if file["type"] == 'file':
        #Search by MD5 checksum
        match = local_files.search(File.md5Checksum == file["md5Checksum"])
        if len(match) > 0:
            for local_file in match:
                if file["relativePath"] == local_file["relativePath"]: 
                    return {
                        "exists": True,
                        "sameFilename": file["name"] == local_file["name"],
                        "sameCreateDate": file["createdTime"].split('.')[0] == local_file["createdTime"].split('.')[0],
                        "sameModificationDate": file["modifiedTime"].split('.')[0] == local_file["modifiedTime"].split('.')[0],
                        "samePath": True,
                        "sameHash": True
                    }
            return {
                "exists": True,
                "sameFilename": file["name"] == local_file["name"],
                "sameCreateDate": file["createdTime"].split('.')[0] == local_file["createdTime"].split('.')[0],
                "sameModificationDate": file["modifiedTime"].split('.')[0] == local_file["modifiedTime"].split('.')[0],
                "samePath": False,
                "sameHash": True
            }
        else:
            match = local_files.search(File.relativePath == file["relativePath"])
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
        match = local_files.search(File.relativePath == file["relativePath"])
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