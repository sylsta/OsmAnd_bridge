[![OSmAnd](https://img.shields.io/badge/OsmAnd-compatible-orange)](https://osmand.net/)
[![QGIS Version](https://img.shields.io/badge/QGIS-3.x-green)](https://qgis.org) 
[![QGIS.org](https://img.shields.io/badge/QGIS.org-published-yellow)](https://plugins.qgis.org/plugins/OsmAnd_bridge/#plugin-versions) 
![license](https://img.shields.io/badge/License-GPL_v3.0-blue) 
![release](https://img.shields.io/badge/release-v2.0-purple.svg)

# OsmAnd bridge

| ![OsmAnd_logo.png](OsmAnd_logo.png) | Import tracks, favorites, itinerary and AV notes from [OsmAnd ](https://osmand.net/)on an **Android device*** to QGIS 3.x. Data are organized by type (point/lines) and audiovisual notes (sounds, pictures and movies) are downloaded and spatialised. Geographical data are stored in a gpkg file while AV notes are stored in their original file format.<br/><br>A direct connexion can be establish with the device, or data can be taken from a copy of OsmAnd directory on an hard drive. Supposed to work natively on Linux and Windows. MacOS users needs to use macDroid (even its free version) or similar. Feel free to fork the code and/or to send feedback, especially if something goes wrong with this plugin. |
|:------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

*Feel free to buy me an Iphone, if you want this plugin to support this device :)

### Credits and acknowledgment
This QGIS extension contains code extracts from the eqip plugin for loading the Comtypes package on Windows.  
- https://plugins.qgis.org/plugins/eqip/#plugin-details
- https://github.com/automaps/eqip

MTP connections under Linux are made using the mtpy package (no more maintained - if you know a recent python module for MTP, please contact me).  

- https://web.archive.org/web/20221206114334/https://github.com/ldo/mtpy/


MTP connections under Windows are made using the "mtp" package. (Thank you Heribert for your kindness and responsiveness in helping me to get to grips with your package ;-)  

- https://github.com/Heribert17/mtp

Device connection under macOS needs macDroid to be be installed (even its free version).

- https://www.macdroid.app/ 
 

Plugin's icon is taken from OsmAnd and licensed under Creative Commons Non-commercial No Derivative Works.

This plugin has been tested with QGIS 3.4x, under:
- GNU/Linux Debian 12 & 13 with KDE, Gnome and XFCE;
- Windows 11;
- macOS Catalina. 

Plesae report any bug or functionality you would like to be implemented. 



