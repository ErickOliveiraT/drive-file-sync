from datetime import datetime
from tinydb import Query
import drive
import files
import os

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

#get file sync action
def get_actions(local_files):
    File = Query()
    for file in local_files.all():
        if not file["exists"]:
            action = 'upload'
        else: #file exists on drive
            if file["type"] and file["type"] == 'file':
                if file["samePath"] and file["sameHash"]:
                    action = 'skip'
                elif file["samePath"] and not file["sameHash"]:
                    action = 'update'
                elif not file["samePath"] and file["sameHash"]:
                    action = 'copy'
                else:
                    action = 'unknown'
            else: #folder
                if not file["samePath"]:
                    action = 'upload'
                else:
                    action = 'skip'
        db_update = {'action': action}
        local_files.update(db_update, File.relativePath == file['relativePath'])