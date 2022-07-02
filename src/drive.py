
from googleapiclient.errors import HttpError

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
    except HttpError as error:
        print(f'An error occurred: {error}')