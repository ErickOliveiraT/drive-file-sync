from datetime import datetime
from tinydb import Query
import explorer
import hashlib
import drive

def getMD5sum(filename, blocksize=65536):
    try:
        hash = hashlib.md5()
        with open(filename, "rb") as f:
            for block in iter(lambda: f.read(blocksize), b""):
                hash.update(block)
        return hash.hexdigest()
    except:
        return ''

def compare(local_files, drive_files):
    File = Query()
    #Find local files on drive
    files = local_files.all()
    for file in files:
        res = drive.find_file(file, drive_files)
        local_files.update(res, File.absPath == file['absPath'])
        print(f'{datetime.now()}: {file["name"]} {res}')

    #Find drive files on local files
    files = drive_files.all()
    for file in files:
        res = explorer.find_file(file, local_files)
        drive_files.update(res, File.relativePath == file['relativePath'])
        print(f'{datetime.now()}: {file["name"]} {res}')