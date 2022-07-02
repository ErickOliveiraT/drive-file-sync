from tinydb import TinyDB, Query
import auth

def compare():
    creds = auth.get_credentials()
    local_files = TinyDB('local_files.json')
    drive_files = TinyDB('drive_files.json')
    files = drive_files.all()
    for file in files:
        if len(file["parents"]) == 1:
            file["path"] = '/'
        else:
            for i in range(1,len(file["parents"])):
                File = Query()
                name = drive_files.search(File.id == file["parents"][i])
                print(f'Name: {name}')
        print(file)
        break

compare()