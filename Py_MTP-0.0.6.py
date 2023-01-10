# import os
# from pymtp import Device, LIBMTP_ERROR_NONE
#
# # Connect to the first MTP device found
# device = Device()
# device.connect()
#
# # Get a list of all files on the device
# files = device.get_files()
#
# # Iterate through the files and download the ones that match a certain condition
# for file in files:
#     if file.filename.endswith('.mp3'):
#         filename = os.path.join("C:\\downloads", file.filename)
#         if os.path.isfile(filename):
#             continue
#         ret = device.get_file_to_file(file, filename)
#         if ret != LIBMTP_ERROR_NONE:
#             print("[ERROR]", ret)
#         else:
#             print("[INFO] Downloaded: ", filename)
#
# # Disconnect from the device
# device.disconnect()
import PyMTP.pymtp as pymtp
import os
try:
    # see https://bugs.kde.org/show_bug.cgi?id=412257
    # Trouver un PID en fonction de son nom de processus
    pid = os.popen("pgrep -f 'kiod'").read()
    # Supprimer le processus en utilisant son PID
    print(pid)
    os.system("kill -9 " + pid)
except:
    pass
oMTP = pymtp.MTP()
oMTP.connect()

folder_dic=oMTP.get_folder_list()
files_list=oMTP.get_filelisting()
for key, value in folder_dic.items():
    if 'avnote' in value.name.decode():
        avnote_folder_parentID=value.parent_id
        avnote_folderID=value
        print(f"Avnote folder ID ${avnote_folderID} | parent ${avnote_folder_parentID}")
    if 'net.osmand' in value.name.decode():
        osmand_folderID=value
    if 'files' in value.name.decode() and value.parent_id == osmand_folderID:
        files_folder_parentID = value.parent_id
        files_folderID=value
    if 'tracks' in value.name.decode() and value.parent_id == files_folderID:
        tracks_folder_parent_ID = value.parent_id
        tracks_folderID = value
    if 'rec' in value.name.decode() and value.parent_id == tracks_folderID:
        tracks_folder_parent_ID = value.parent_id
        tracks_folderID = value
if files_folder_parentID != osmand_folderID or avnote_folder_parentID != osmand_folderID:
    for key, value in folder_dic.items():
        if 'avnote' in value.name.decode() and value.parent_id == osmand_folderID:
            avnote_folder_parentID = value.parent_id
            avnote_folderID = value
        if 'files' in value.name.decode() and value.parent_id == osmand_folderID:
            files_folder_parentID = value.parent_id
            files_folderID = value
if tracks_folder_parent_ID != files_folder_parentID:
    for key, value in folder_dic.items():
        if 'tracks' in value.name.decode() and value.parent_id == tracks_folder_parent_ID:
            tracks_folder_parent_ID = value.parent_id
            tracks_folderID = value
oMTP.disconnect()

