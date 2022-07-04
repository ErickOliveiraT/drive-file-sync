
from googleapiclient.errors import HttpError
from tinydb import Query

def list_files(parent_id, drive_service, drive_files, parents=None):
    try:
        page_token = None
        while True:
            response = drive_service.files().list(q="'{}' in parents".format(parent_id),
                spaces='drive',
                fields='nextPageToken, files(id, name, parents, md5Checksum, fileExtension, size, createdTime, modifiedTime)',
                pageToken=page_token).execute()
            for file in response.get('files', []):
                if not "fileExtension" in file.keys():
                    file["type"] = 'folder'
                else:
                    file["type"] = 'file'
                if parents:
                    file["parents"] = parents + file["parents"]
                print(f'Checking {file["name"]}')
                drive_files.insert(file)
                if file["type"] == 'folder':
                    list_files(file["id"], drive_service, drive_files, file["parents"])
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
        return True
    except HttpError as error:
        print(f'An error occurred: {error}')

def build_paths(drive_files):
    files = drive_files.all()
    File = Query()
    cache = {}
    for file in files:
        if len(file["parents"]) == 1:
            file["relativePath"] = './' + file["name"]
        else:
            path = './'
            for i in range(1,len(file["parents"])):
                if file["parents"][i] in cache.keys():
                    path += cache[file["parents"][i]] + '/'
                else:
                    match = drive_files.search(File.id == file["parents"][i])
                    path += match[0]["name"] + '/'
                    cache[file["parents"][i]] = match[0]["name"]
            file["relativePath"] = path + file["name"]
        drive_files.update(file, File.id == file['id'])