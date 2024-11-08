import mtpy.mtpy as mtpy
import os
import tempfile
try:
    # see https://bugs.kde.org/show_bug.cgi?id=412257
    # find and kill process by its PID
    pid = os.popen("pgrep -f 'kiod'").read()
    os.system("kill -9 " + pid)
except:
    pass

print('Listing device(s)')
try:
    devices = mtpy.get_raw_devices()
    device_attached = True
except:
    device_attached = False
    print('No device found')
    exit(-1)
print('Connecting device')
try:
    device = mtpy.get_raw_devices()[0].open()
except:
    print('Unable to connect to the device. Try disconnecting and reconnecting. Check that it is unlocked.')
    exit(-1)

print('Looking for Osmand files')
potential_paths = ['/Android/data/net.osmand/files', '/Android/obb/net.osmand/files',
                   '/Android/data/net.osmand.plus/files','/Android/obb/net.osmand.plus/files']
path_found = False
for path in potential_paths:
    if device.get_descendant_by_path(path) is not None:
        path_found = True
        break
if not path_found:
    exit()

# copy data to tmp folder
print('Copying data to tmp folder')
tmp_dir_name = tempfile.TemporaryDirectory().name
items_list = ['/tracks/rec/', '/favourites.gpx', '/itinerary.gpx', '/avnotes/']
for item in items_list:
    print(path+item)
    try:
        # copy item to tmp dir
        item_content = device.get_descendant_by_path(path+item)
        if item_content is not None:
            mtpy.common_retrieve_to_folder(item_content, tmp_dir_name+item)
            print(f'Copying {item}')
        else:
            print(f'No {item}')
    except:
        print(f'Issue copying {item}')
        pass
print(tmp_dir_name)

# device.close()
# children = device.get_children()
# mtpy.common_retrieve_to_folder(children[1], '/tmp/osmand')