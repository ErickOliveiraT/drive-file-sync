import json
import sys
import os

#test profile
profile = {
    "local_folder_path": '',
    "remote_folder_id": '',
    "sync_deletions": False,
    "ignored_folders_list": []
}

def create_profile():
    local_path = input('\nInsert local folder path: ')
    if local_path[len(local_path)-1] != '/':
        local_path += '/'
    profile['local_folder_path'] = local_path
    profile['remote_folder_id'] = input('Insert remote folder id: ')
    option = input('Sync deletions? (y/n): ')
    if option == 'y' or option == 'Y':
        profile['sync_deletions'] = True
    else:
        profile['sync_deletions'] = False
    while True:
        option = input('Ignored folders: ')
        if option == '':
            break
        else:
            profile['ignored_folders_list'].append(option)
    option = input('Profile name: ')
    json_string = json.dumps(profile)
    with open('./profiles/' + option + '.json', 'w') as outfile:
        outfile.write(json_string)
    print('')
    return profile

def list_profiles():
    op = 1
    print('')
    profiles = os.listdir('./profiles')
    for x in profiles:
        print(f'[{op}] {x}')
        op += 1
    option = int(input('\nProfile: '))
    if option < 1 or option > op-1:
        print('\nInvalid option')
        sys.exit(0)
    option = profiles[option-1]
    return './profiles' + '/' + option