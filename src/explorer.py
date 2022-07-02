from datetime import datetime
from tinydb import TinyDB
import files
import os

path = "C:\\Users\\Érick\\Pictures\\"

def check():
    db = TinyDB('local_files.json')
    for x in os.listdir(path):
        stats = os.stat(path+x)
        is_file = True if len(x.split('.')) > 1 else False
        file = {
            "name": x,
            "createdTime": str(datetime.fromtimestamp(stats.st_ctime)).replace(' ','T'),
            "modifiedTime": str(datetime.fromtimestamp(stats.st_mtime)).replace(' ','T'),
            "type": "file" if is_file else "folder",
            "path": path + x,
            "fileExtension": x.split('.')[1] if is_file else '',
            "md5Checksum": files.getMD5sum(path+x) if is_file else ''
        }
        print(file)
        db.insert(file)

check()