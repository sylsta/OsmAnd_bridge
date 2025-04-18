
README

mtpy provides access to (some of) the functions of libmtp from Python
3.x. It tries to do this in a high-level, convenient fashion. Examples:

    import mtpy
    mtpy.get_raw_devices()

returns a list of all the recognizable MTP-speaking devices connected
to your host machine, as a list of RawDevice objects.

    dev = mtpy.get_raw_devices()[0].open()

returns a Device object for communicating with the first (or only) MTP
device connected to your system, and saves it in the variable dev.

    dev.get_children()

returns a list of the files and folders at the root directory level
on the Device. (The first such call is liable to take a few seconds,
accompanied by some diagnostic messages from libmtp.)

    p = dev.get_descendant_by_path("/DCIM/Camera")

on my Samsung Galaxy Nexus, returns a Folder object for the location
where the Camera app puts its photos, and saves it in the variable p.

    p.get_children()

returns a list of the photos currently in the /DCIM/Camera folder.

    p.retrieve_to_folder("all_photos")

will download the entire contents of the photos folder into the local
directory “all_photos”, which will be created if it doesn’t exist.

    d1 = dev.create_folder("test")

creates a folder named “test” at the root directory level on the
Device, and saves the returned Folder object describing it in the
variable d1.

    d2 = d1.create_folder("also_test")

creates a folder named “also_test” within the previously-created
“test” folder, and saves the returned Folder object describing it in
the variable d2.

    f3 = d2.send_file("photo.jpeg", "photo.jpg")

sends the file named “photo.jpeg” to the previously-created
“also_test” folder on the device, giving it the full uploaded pathname
of “/test/also_test/photo.jpg”.

    f3.retrieve_to_file("photo-too.jpeg")

downloads the uploaded file under the name “photo-too.jpeg” to the host
system.

    f3.delete()

deletes the uploaded copy of the file. The object in f3 should not
be referenced after this point.

    d1.delete()

will fail, because the folder “test” is not empty (contains the
subfolder “also_test”).

    d1.delete(delete_descendants = True)

will delete the folder “test” and all its descendants (i.e. the Folder
described by d2). The objects in d1 and d2 should not be referenced
after this point.

    dev.close()

closes the connection to the Device when you have finished with it.

Licence: LGPL2+, same as libmtp.

Lawrence D’Oliveiro
2012 June 3


