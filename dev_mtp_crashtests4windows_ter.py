
from extra_packages.win_mtp.access import *
dev = get_portable_devices()
cont = dev[0].get_content()
name=".\\itinerary.gpx"
content = cont.get_path("Espace de stockage interne partagé\\Android\\data\\net.osmand.plus\\files\\itinerary.gpx")
outp = open(name, "wb")
content.download_stream(outp)
outp.close()



# Traceback (most recent call last):
#   File "<input>", line 1, in <module>
#   File "C:\Users\SylTer\PycharmProjects\OsmAnd_bridge\extra_packages\win_mtp\access.py", line 626, in download_file
#     self.download_stream(output_stream)
#     ~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^
#   File "C:\Users\SylTer\PycharmProjects\OsmAnd_bridge\extra_packages\win_mtp\access.py", line 602, in download_stream
#     buf, length = filestream.RemoteRead(buf, ctypes.c_ulong(blocksize))
#                   ~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# TypeError: ISequentialStream.RemoteRead() takes 2 positional arguments but 3 were given
