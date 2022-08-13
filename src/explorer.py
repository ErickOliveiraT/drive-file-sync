from datetime import datetime
from tinydb import Query
import files
import drive
import os

def list_files(path, local_files, root_dir, drive_files):
    if root_dir[len(root_dir)-1] == '\\' or root_dir[len(root_dir)-1] == '/':
        root_dir = root_dir[:-1]
    for x in os.listdir(path):
        print(f'{datetime.now()}: Checking {x}')
        stats = os.stat(path+'\\'+x)
        is_file = os.path.isfile(path+'\\'+x)
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
            list_files(path+x+'/', local_files, root_dir, drive_files)
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
                action = 'move' #upload and delete
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
            return {
                "exists": True,
                "sameFilename": file["name"] == match[0]["name"],
                "sameCreateDate": file["createdTime"].split('.')[0] == match[0]["createdTime"].split('.')[0],
                "sameModificationDate": file["modifiedTime"].split('.')[0] == match[0]["modifiedTime"].split('.')[0],
                "samePath": file["relativePath"] == match[0]["relativePath"],
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