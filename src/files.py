import hashlib
import magic

def getMD5sum(filename, blocksize=65536):
    try:
        hash = hashlib.md5()
        with open(filename, "rb") as f:
            for block in iter(lambda: f.read(blocksize), b""):
                hash.update(block)
        return hash.hexdigest()
    except:
        return ''

def getMIMEType(filepath):
    mime = magic.Magic(mime=True)
    mimetype = mime.from_file(filepath)
    if mimetype.startswith('cannot open'):
        return None
    return mimetype

def getProfileName(path):
    return path.split('./profiles/')[1].split('.json')[0]