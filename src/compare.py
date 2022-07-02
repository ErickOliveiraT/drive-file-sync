from tinydb import Query

def build_paths(drive_files):
    files = drive_files.all()
    File = Query()
    for file in files:
        if len(file["parents"]) == 1:
            file["path"] = './' + file["name"]
        else:
            path = './'
            for i in range(1,len(file["parents"])):
                match = drive_files.search(File.id == file["parents"][i])
                path += match[0]["name"] + '/'
            file["path"] = path + file["name"]
        drive_files.update(file, File.id == file['id'])