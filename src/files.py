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