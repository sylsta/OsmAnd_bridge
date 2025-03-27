import glob

# Recherche des volumes contenant .AFTVolumes
aft_volumes = glob.glob("/Users/*/.AFTVolumes")

found = False

for volume in aft_volumes:
    # Recherche récursive des répertoires contenant "net.osmand"
    search_path = f"{volume}/**/net.osmand*"
    matching_dirs = glob.glob(search_path, recursive=True)

    if matching_dirs:
        print(f"Des répertoires correspondants trouvés dans {volume} :")
        for match in matching_dirs:
            print(f" - {match}")
        found = True

if not found:
    print("Aucun volume monté ne contient un sous-répertoire avec 'net.osmand' sous .AFTVolumes.")


import os

volumes_path = "/Volumes"
for volume in os.listdir(volumes_path):
    aft_path = os.path.join(volumes_path, volume, ".AFTVolumes")
    if os.path.exists(aft_path):
        print(f"Trouvé : {aft_path}")