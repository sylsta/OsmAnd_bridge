import tempfile

from mtp4windows_win_mtp.access import *
devices = get_portable_devices()
for device in devices:
    device_name, device_desc = device.get_description()
    print(f"{device.get_description()[0]} - {device.get_description()[1]}")

for root, dirs, files in (walk(device, device_name)):
    for directory in dirs:
        root_path = directory.name
        break
    break
potential_paths = ['\\Android\\data\\net.osmand\\files', '\\Android\\data\\net.osmand.plus\\files',
                                           '\\Android\\obb\\net.osmand\\files', '\\Android\\obb\\net.osmand.plus\\files']

path_found = False
for path in potential_paths:
    for root, dirs, files in (walk(device, root_path+path)):
        if len(dirs)>0:
            path_found = True
            print(root_path+path)
            break

    if path_found:
        break
        print(path)
if not path_found:
    # TODO a message box to say no path found
    exit
tmp_dir_name = tempfile.TemporaryDirectory().name

print(f'Copying data to tmp folder: {tmp_dir_name}')
items_list = ['\\avnotes\\', '\\tracks\\rec\\', '\\favorites\\', '\\itinerary.gpx']
os.makedirs(tmp_dir_name + items_list[0])
os.makedirs(tmp_dir_name + items_list[1])
os.makedirs(tmp_dir_name + items_list[2])
cont = device.get_content()
for item in items_list:
    print(path + item)

# try:
    # copy item to tmp dir
    if item == '/itinerary.gpx':  # since it's a file not a dir
        src = root_path + path +item
        dest= tmp_dir_name + item
        content = cont.get_path(src)  # since it's a file not a dir
        content.download_file(dest)
    else:
        pass # common_retrieve_to_folder(item_content, tmp_dir_name + item)
    print(f'Copying {item}')
# except:
#     print(f'Issue copying {item}')
#     pass
    print(tmp_dir_name)








