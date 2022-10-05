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
    try:
        mime = magic.Magic(mime=True)
        #print('[debug] filepath = ', filepath)
        mimetype = mime.from_file(filepath)
        #print(f'[debug] mimetype = {mimetype}')
        if mimetype.startswith('cannot open'):
            splitted = filepath.split('.')
            ext = splitted[len(splitted)-1]
            #print('[debug] ext = ', ext)
            return genericMimeType(ext)
        return mimetype
    except: 
        return None

def getProfileName(path):
    return path.split('./profiles/')[1].split('.json')[0]

def genericMimeType(ext):
    ext = ext.lower()
    if ext == 'aac':
        return 'audio/aac'
    elif ext == 'abw':
        return 'application/x-abiword'
    elif ext == 'arc':
        return 'application/x-freearc'
    elif ext == 'avi':
        return 'video/x-msvideo'
    elif ext == 'azw':
        return 'application/vnd.amazon.ebook'
    elif ext == 'bin':
        return 'application/octet-stream'
    elif ext == 'bmp':
        return 'image/bmp'
    elif ext == 'bz':
        return 'application/x-bzip'
    elif ext == 'bz2':
        return 'application/x-bzip2'
    elif ext == 'csh':
        return 'application/x-csh'
    elif ext == 'css':
        return 'text/css'
    elif ext == 'csv':
        return 'text/csv'
    elif ext == 'doc':
        return 'application/msword'
    elif ext == 'docx':
        return 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    elif ext == 'eot':
        return 'application/vnd.ms-fontobject'
    elif ext == 'epub':
        return 'application/epub+zip'
    elif ext == 'gz':
        return 'application/gzip'
    elif ext == 'gif':
        return 'image/gif'
    elif ext == 'htm':
        return 'text/html'
    elif ext == 'html':
        return 'text/html'
    elif ext == 'ico':
        return 'image/vnd.microsoft.icon'
    elif ext == 'ics':
        return 'text/calendar'
    elif ext == 'jar':
        return 'application/java-archive'
    elif ext == 'jpeg':
        return 'image/jpeg'
    elif ext == 'jpg':
        return 'image/jpeg'
    elif ext == 'js':
        return 'text/javascript'
    elif ext == 'json':
        return 'application/json'
    elif ext == 'jsonld':
        return 'application/ld+json'
    elif ext == 'mid':
        return 'audio/midi audio/x-midi'
    elif ext == 'midi':
        return 'audio/midi audio/x-midi'
    elif ext == 'mjs':
        return 'text/javascript'
    elif ext == 'mp3':
        return 'audio/mpeg'
    elif ext == 'mpeg':
        return 'video/mpeg'
    elif ext == 'mpkg':
        return 'application/vnd.apple.installer+xml'
    elif ext == 'odp':
        return 'application/vnd.oasis.opendocument.presentation'
    elif ext == 'ods':
        return 'application/vnd.oasis.opendocument.spreadsheet'
    elif ext == 'odt':
        return 'application/vnd.oasis.opendocument.text'
    elif ext == 'oga':
        return 'audio/ogg'
    elif ext == 'ogv':
        return 'video/ogg'
    elif ext == 'ogx':
        return 'application/ogg'
    elif ext == 'opus':
        return 'audio/opus'
    elif ext == 'otf':
        return 'font/otf'
    elif ext == 'png':
        return 'image/png'
    elif ext == 'pdf':
        return 'application/pdf'
    elif ext == 'php':
        return 'application/x-httpd-php'
    elif ext == 'ppt':
        return 'application/vnd.ms-powerpoint'
    elif ext == 'pptx':
        return 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    elif ext == 'rar':
        return 'application/vnd.rar'
    elif ext == 'rtf':
        return 'application/rtf'
    elif ext == 'sh':
        return 'application/x-sh'
    elif ext == 'svg':
        return 'image/svg+xml'
    elif ext == 'swf':
        return 'application/x-shockwave-flash'
    elif ext == 'tar':
        return 'application/x-tar'
    elif ext == 'tif':
        return 'image/tiff'
    elif ext == 'tiff':
        return 'image/tiff'
    elif ext == 'ts':
        return 'video/mp2t'
    elif ext == 'ttf':
        return 'font/ttf'
    elif ext == 'txt':
        return 'text/plain'
    elif ext == 'vsd':
        return 'application/vnd.visio'
    elif ext == 'wav':
        return 'audio/wav'
    elif ext == 'weba':
        return 'audio/webm'
    elif ext == 'webm':
        return 'video/webm'
    elif ext == 'webp':
        return 'image/webp'
    elif ext == 'woff':
        return 'font/woff'
    elif ext == 'woff2':
        return 'font/woff2'
    elif ext == 'xhtml':
        return 'application/xhtml+xml'
    elif ext == 'xls':
        return 'application/vnd.ms-excel'
    elif ext == 'xlsx':
        return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    elif ext == 'xml':
        return 'application/xml'
    elif ext == 'xul':
        return 'application/vnd.mozilla.xul+xml'
    elif ext == 'zip':
        return 'application/zip'
    elif ext == '3gp':
        return 'video/3gpp'
    elif ext == '3g2':
        return 'video/3gpp2'
    elif ext == '7z':
        return 'application/x-7z-compressed'
    return 'application/binary'