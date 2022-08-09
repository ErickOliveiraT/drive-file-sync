from datetime import datetime
from logging import root
from tinydb import TinyDB, where
import files
import os

def list_files(path, local_files, root_dir):
    if root_dir[len(root_dir)-1] == '\\' or root_dir[len(root_dir)-1] == '/':
        root_dir = root_dir[:-1]
    for x in os.listdir(path):
        stats = os.stat(path+'\\'+x)
        is_file = True if len(x.split('.')) > 1 else False
        file = {
            "name": x,
            "createdTime": str(datetime.fromtimestamp(stats.st_ctime)).replace(' ', 'T'),
            "modifiedTime": str(datetime.fromtimestamp(stats.st_mtime)).replace(' ', 'T'),
            "type": "file" if is_file else "folder",
            "absPath": path + x,
            "fileExtension": x.split('.')[1] if is_file else '',
            "md5Checksum": files.getMD5sum(path+x) if is_file else ''
        }
        file["relativePath"] = '.' + file["absPath"].split(root_dir)[1].replace('\\','/')
        print(f'Checking {file["name"]}')
        if not is_file:
            list_files(path+x+'\\', local_files, root_dir)
        try:
            local_files.insert(file)
        except:
            pass
    return True