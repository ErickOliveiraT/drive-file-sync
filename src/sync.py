from datetime import datetime
from tabulate import tabulate
from tinydb import TinyDB, Query, where
import drive
import sys

def sync(local_files, drive_files, remote_dir, creds):
    #create non-existing folders on google drive
    File = Query()
    qry = local_files.search((File.type == 'folder') & (File.action == 'upload'))
    for i in range(0, len(qry)):
        qry[i]['paths_count'] = len(qry[i]['relativePath'].split('/')) - 1
    qry = sorted(qry, key=lambda o: o['paths_count'], reverse=False)
    for folder in qry:
        print(f'{datetime.now()}: Creating folder "{folder["name"]}"')
        parents = drive.get_parent_ids(folder['relativePath'], drive_files, remote_dir)
        #print(f'[debug] PARENTS OF {folder["name"]} = ', parents)
        if parents and len(parents) > 0:
            res = drive.create_folder(folder["name"], parents, creds)
            if res and res["id"]:
                print(f'{datetime.now()}: Folder has created with ID "{res["id"]}"')
                #print(f'[debug] res = {res}')
                db_update = {"exists": True, "action": 'skip'}
                local_files.update(db_update, File.relativePath == folder['relativePath'])
                new_folder = {"type": "folder", "relativePath": folder['relativePath']}
                new_folder.update(res)
                #print(f'[debug] db_update = {db_update}')
                drive_files.insert(new_folder)

    #create non-existing files on google drive
    qry = local_files.search((File.type == 'file') & (File.action == 'upload'))
    for file in qry:
        print(f'{datetime.now()}: Uploading {file["name"]}')
        parents = drive.get_parent_ids(file["relativePath"], drive_files, remote_dir)
        #print(f'[debug] parents = {parents}')
        res = drive.upload_basic(file["name"], file["absPath"], parents, creds)
        #print(f'[debug] res = {res}')
        # if not res: 
        #     sys.exit(0)
        if res:
            new_file = {"type": "file", "relativePath": file["relativePath"] }
            new_file.update(res)
            drive_files.insert(new_file)
            db_update = {"exists": True, "samePath": True, "sameHash": True, "action": "skip"}
            local_files.update(db_update, File.relativePath == file["relativePath"])
    print(f'{datetime.now()}: All files uploaded!')

    #update files on google drive (delete/re-upload)
    qry = local_files.search(File.action == 'update')
    print(f'{datetime.now()}: Updating files...')
    for file in qry:
        res = drive.delete(file['remoteFileId'], creds)
        if res:
            print(f'{datetime.now()}: Deleted "{file["name"]}" from Drive')
            drive_files.remove(where('relativePath') == file['relativePath'])
        print(f'{datetime.now()}: Uploading {file["name"]}')
        parents = drive.get_parent_ids(file["relativePath"], drive_files, remote_dir)
        res = drive.upload_basic(file["name"], file["absPath"], parents, creds)
        if res:
            new_file = {"type": "file", "relativePath": file["relativePath"] }
            new_file.update(res)
            db_update = {"exists": True, "samePath": True, "sameHash": True, "action": "skip"}
            local_files.update(db_update, File.relativePath == file["relativePath"])
    print(f'{datetime.now()}: All files updated!')

    #delete remote folders witch doesn't exist
    qry = drive_files.search((File.action == 'delete') & (File.type == 'folder'))
    for folder in qry:
        print(f'{datetime.now()}: Deleting {folder["name"]} ({folder["id"]})')
        res = drive.delete(folder['id'], creds)
        if res["deleted"]:
            print(f'{datetime.now()}: Deleted "{folder["name"]}" from Drive')
            drive_files.remove(where('relativePath') == folder['relativePath'])
        else:
            if res['reason'] and res['reason'] == 'notFound':
                drive_files.remove(where('relativePath') == folder['relativePath'])

    #delete remote files witch doesn't exist   
    qry = drive_files.search((File.action == 'delete') & (File.type == 'file'))
    for file in qry:
        print(f'{datetime.now()}: Deleting {file["name"]} ({file["id"]})')
        res = drive.delete(file['id'], creds)
        if res["deleted"]:
            print(f'{datetime.now()}: Deleted "{file["name"]}" from Drive')
            drive_files.remove(where('relativePath') == file['relativePath'])
        else:
            if res['reason'] and res['reason'] == 'notFound':
                drive_files.remove(where('relativePath') == file['relativePath'])

#Show sync status
def status(profile):
    local_files_db_path = './data/' + profile['profile_name'] + '_local.json'
    drive_files_db_path = './data/' + profile['profile_name'] + '_remote.json'
    local_files = TinyDB(local_files_db_path)
    drive_files = TinyDB(drive_files_db_path)
    table = [['File','Origin','Action']]

    for file in local_files.all():
        local_folder_path = profile['local_folder_path']
        filename = file['absPath'].split(local_folder_path)[1]
        if 'action' in file.keys() and file['action'] != 'skip':
            table.append([filename, 'local', file['action']])
    for file in drive_files.all():
        if 'action' in file.keys() and file['action'] != 'skip':
            table.append([file['relativePath'], 'remote', file['action']])


    print(tabulate(table, headers='firstrow', tablefmt='fancy_grid', showindex=True))
    return print('\n')