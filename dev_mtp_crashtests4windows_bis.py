import tempfile
import time
import os
from mtp4windows_win_mtp.access import *

# Fonction pour télécharger de manière récursive
def download_recursive(cont, src_path, dest_path):
    """Télécharge de manière récursive les fichiers et répertoires depuis l'appareil MTP."""
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)

    for item in cont.get_children():
        item_name = item.name
        item_src_path = os.path.join(src_path, item_name)
        item_dest_path = os.path.join(dest_path, item_name)

        if item.content_type == WPD_CONTENT_TYPE_DIRECTORY:
            # Si c'est un répertoire, on le crée et on télécharge son contenu
            os.makedirs(item_dest_path, exist_ok=True)
            download_recursive(item, item_src_path, item_dest_path)
        elif item.content_type == WPD_CONTENT_TYPE_FILE:
            # Si c'est un fichier, on le télécharge
            print(f"Téléchargement de {item_src_path} vers {item_dest_path}")
            item.download_file(item_dest_path)

# Récupération des appareils connectés
devices = get_portable_devices()

for device in devices:
    device_name, device_desc = device.get_description()
    print(f"{device_name} - {device_desc}")

    # Construction du point de montage
    mount_point = f"{device_name}\\Espace de stockage interne partagé\\"
    print(f"Point de montage : {mount_point}")

    # Récupération du contenu de l'appareil
    cont = device.get_content()

    # Chemins potentiels à explorer
    potential_paths = [
        'Android\\data\\net.osmand\\files',
        'Android\\data\\net.osmand.plus\\files',
        'Android\\obb\\net.osmand\\files',
        'Android\\obb\\net.osmand.plus\\files'
    ]

    path_found = False
    for path in potential_paths:
        full_path = mount_point + path
        if cont.get_path(full_path) is not None:
            path_found = True
            break

    if not path_found:
        print("Aucun chemin valide trouvé.")
        exit()

    print(f"Chemin trouvé : {full_path}")

    # Création d'un répertoire temporaire pour stocker les fichiers téléchargés
    tmp_dir_name = tempfile.TemporaryDirectory().name
    print(f"Copie des données vers le dossier temporaire : {tmp_dir_name}")

    # Liste des éléments à télécharger
    items_list = ['avnotes\\', 'tracks\\rec\\', 'favorites\\', 'itinerary.gpx']

    # Création des répertoires dans le dossier temporaire
    for item in items_list:
        if item.endswith('\\'):
            os.makedirs(os.path.join(tmp_dir_name, item), exist_ok=True)

    # Téléchargement des éléments
    for item in items_list:
        src = os.path.join(full_path, item)
        dest = os.path.join(tmp_dir_name, item)

        if item == 'itinerary.gpx':  # Fichier
            content = cont.get_path(src)
            if content:
                print(f"Téléchargement de {src} vers {dest}")
                content.download_file(dest)
            else:
                print(f"Le fichier {src} n'existe pas.")
        else:  # Répertoire
            content = cont.get_path(src)
            if content:
                print(f"Téléchargement récursif de {src} vers {dest}")
                download_recursive(content, src, dest)
            else:
                print(f"Le répertoire {src} n'existe pas.")