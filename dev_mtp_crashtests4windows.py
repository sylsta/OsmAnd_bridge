import tempfile
import time

from extra_packages.mtp.win_access import *
devices = get_portable_devices()


def display_childs_with_walk(dev, root: str) -> None:
    """Show content of device"""
    pass


for device in devices:
    device_name, device_desc = device.get_description()
    print(f"{device.get_description()[0]} - {device.get_description()[1]}")
    root_path = None
    for root, dirs, files in walk(device, device_name):
       if (len(dirs)) >0:
           root_path = dirs[0].name
           break
    print(root_path)
    if root_path is None:
        print("erreur")
        exit()

cont = device.get_content()
#
potential_paths = ['\\Android\\data\\net.osmand\\files', '\\Android\\data\\net.osmand.plus\\files',
                                           '\\Android\\obb\\net.osmand\\files', '\\Android\\obb\\net.osmand.plus\\files']

path_found = False
for path in potential_paths:
    if cont[0].get_path(root_path+path) is not None:
        print(root_path+path)
        path_found = True
        print(root_path+path)
        break
for path in potential_paths:
    found =False
    # print("**")
    # print(device_name + '\\' + root_path + path)
    # print(str(device))
    for root, dirs, files in walk(device, device_desc + '\\' + root_path + path):
        if (len(dirs)) > 0:
            # found = True
            print("****")
            print(path)
            break
    if found:
        break
if not path_found:
    # TODO a message box to say no path found
    print('not_found')
#     exit()
# exit()
# tmp_dir_name = tempfile.TemporaryDirectory().name
#
# print(f'Copying data to tmp folder: {tmp_dir_name}')
# items_list = ['\\avnotes\\', '\\tracks\\rec\\', '\\favorites\\', '\\itinerary.gpx']
# os.makedirs(tmp_dir_name + items_list[0])
# os.makedirs(tmp_dir_name + items_list[1])
# os.makedirs(tmp_dir_name + items_list[2])
#
# for item in items_list:
#     print(path + item)
#
# # # try:
# #     # copy item to tmp dir
#     if item == '\\itinerary.gpx':  # since it's a file not a dir
#         src = root_path + path +item
#         dest= tmp_dir_name + item
#         print(f'Copying {src} to {dest}')
#         content = cont.get_path(src)  # since it's a file not a dir
#         time.sleep(0.1)
#         content.download_file(dest)
#     else:
#         pass # common_retrieve_to_folder(item_content, tmp_dir_name + item)
#     print(f'Copying {item}')
# # # except:
# # #     print(f'Issue copying {item}')
# # #     pass
# #     print(tmp_dir_name)
# #
# #
# #
# #
# #
# #
# #
# # #
