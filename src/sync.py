from datetime import datetime
from tinydb import Query
import drive

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
        print(f'[debug] PARENTS OF {folder["name"]} = ', parents)
        if parents and len(parents) > 0:
            res = drive.create_folder(folder["name"], parents, creds)
            if res and res["id"]:
                #print(f'[debug] res = {res}')
                db_update = {"exists": True}
                local_files.update(db_update, File.relativePath == folder['relativePath'])
                new_folder = {"type": "folder", "relativePath": folder['relativePath']}
                new_folder.update(res)
                #print(f'[debug] db_update = {db_update}')
                drive_files.insert(new_folder)