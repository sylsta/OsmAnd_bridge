[![QGIS Version](https://img.shields.io/badge/QGIS-3.x-green)](https://qgis.org) 
[![QGIS.org](https://img.shields.io/badge/QGIS.org-published-green)](https://plugins.qgis.org/plugins/OsmAnd_bridge/#plugin-versions) 
[![OSmAnd](https://img.shields.io/badge/OsmAnd-compatible-orange)](https://osmand.net/)

# OsmAnd bridge

Import tracks, favorites, itinerary and AV notes from OsmAnd on an android device to QGIS 3.x. 
Data are organized by type (point/lines) and audiovisual notes (sounds, pictures and movie) are downloaded and spatialized.
Geographical data are stored in a gpkg file while AV notes are stored in their original file format. 
<p>&nbsp</p>
A direct connexion can be establish with the device, or data can be taken from a copy of OsmAnd directory on an hardrive.  
Supposed to work natively on Linux and Windows. MacOS users needs to use macDroid (even its free version) or similar.  
Feel fre to fork the code and/or to send feedback, especially if something goes wrong with this plugin.
<p>&nbsp</p>

### Credits and acknowledgment
This QGIS extension contains code extracts from the eqip plugin for loading the Comtypes package on Windows.  
- https://plugins.qgis.org/plugins/eqip/#plugin-details
- https://github.com/automaps/eqip
<p>&nbsp</p>
MTP connections under Linux are made using the mtpy package (no more maintained - if you know a recent python module for MTP, please contact me).  

- https://web.archive.org/web/20221206114334/https://github.com/ldo/mtpy/

<p>&nbsp</p>
MTP connections under Windows are made using the "mtp" package. (Thank you Heribert for your kindness and responsiveness in helping me to get to grips with your package ;-)  

- https://github.com/Heribert17/mtp

