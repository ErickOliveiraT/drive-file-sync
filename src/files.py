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

#verify if files has to be transfered
def verify_sync(local_files, drive_files, sync_deletions):
    File = Query()
    for local_file in local_files.all():
        if local_file["exists"] and local_file["samePath"]:
            if local_file["type"] == 'file':
                if local_file["sameHash"]:
                    action = 'skip'
                else:
                    action = 'update'
            else:
                action = 'skip'
        elif local_file["exists"] and not local_file["samePath"]:
            action = 'move' #upload and delete
        elif not local_file["exists"]:
            action = 'upload'
        print(f'{datetime.now()}: [local] {local_file["name"]}: {action}')
        db_update = {"action": action}
        local_files.update(db_update, File.relativePath == local_file['relativePath'])
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