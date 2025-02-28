net_osm_path = r"Smini\Espace de stockage interne partagé\Android\data\net.osmand.plus\files\tiles\Microsoft Earth\\"
net_osm_path_element= net_osm_path.split('\\')
path = ''
for element in net_osm_path_element:
    path += element + "/"
    if 'net.osmand' in element:
        break