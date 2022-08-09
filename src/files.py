import hashlib
import drive

def getMD5sum(filename, blocksize=65536):
    hash = hashlib.md5()
    with open(filename, "rb") as f:
        for block in iter(lambda: f.read(blocksize), b""):
            hash.update(block)
    return hash.hexdigest()

def compare(local_files, drive_files):
    files = local_files.all()
    for file in files:
        res = drive.find_file(file, drive_files)
        print(res)
        #break