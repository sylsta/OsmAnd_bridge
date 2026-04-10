# OsmAnd bridge — Documentation utilisateur

> Plugin QGIS pour importer les traces, favoris, itinéraires et notes audiovisuelles depuis [OsmAnd](https://osmand.net/)
>
> **Auteur :** Sylvain Théry — UMR 5281 ART-Dev (CNRS)
> **Licence :** GPL v2 ou ultérieure
> **Documentation en ligne :** https://osmand-bridge.readthedocs.io/

---

## Table des matières

1. [Présentation](#1-présentation)
2. [Prérequis et installation](#2-prérequis-et-installation)
3. [Interface du plugin](#3-interface-du-plugin)
4. [Sources de données : appareil ou répertoire local](#4-sources-de-données--appareil-ou-répertoire-local)
   - [4.1 Depuis un répertoire local](#41-depuis-un-répertoire-local)
   - [4.2 Depuis un appareil connecté (MTP)](#42-depuis-un-appareil-connecté-mtp)
5. [Données importables](#5-données-importables)
   - [5.1 Traces GPX](#51-traces-gpx)
   - [5.2 Favoris](#52-favoris)
   - [5.3 Itinéraire](#53-itinéraire)
   - [5.4 Notes audiovisuelles](#54-notes-audiovisuelles)
6. [Dossier de destination](#6-dossier-de-destination)
7. [Résultat dans QGIS](#7-résultat-dans-qgis)
   - [7.1 Fichiers produits](#71-fichiers-produits)
   - [7.2 Structure des couches](#72-structure-des-couches)
   - [7.3 Fond de carte OpenStreetMap](#73-fond-de-carte-openstreetmap)
8. [Menu du plugin](#8-menu-du-plugin)
9. [Notes par système d'exploitation](#9-notes-par-système-dexploitation)
   - [9.1 Linux](#91-linux)
   - [9.2 Windows](#92-windows)
   - [9.3 macOS](#93-macos)
10. [Dépannage](#10-dépannage)
11. [Compatibilité](#11-compatibilité)

---

## 1. Présentation

**OsmAnd bridge** est un plugin QGIS qui permet de rapatrier dans un projet QGIS les données collectées sur le terrain avec l'application mobile [OsmAnd](https://osmand.net/) (Android / iOS).

Il prend en charge quatre types de données :

| Type | Fichier source dans OsmAnd | Couches créées dans QGIS |
|---|---|---|
| **Traces GPX** | `tracks/rec/*.gpx` | Waypoints, Routes, Traces, Points de route, Points de trace |
| **Favoris** | `favorites/favorites.gpx` | Même structure que les traces GPX |
| **Itinéraire** | `itinerary.gpx` | Même structure que les traces GPX |
| **Notes AV** | `avnotes/*.3gp / .mp3 / .mp4 / .jpg / .tif` | Notes audio, Notes vidéo, Notes photo |

Toutes les données sont converties et sauvegardées dans un fichier **GeoPackage** (`.gpkg`) unique, ce qui garantit leur pérennité et leur portabilité.

---

## 2. Prérequis et installation

### Versions supportées

| Logiciel | Version minimale |
|---|---|
| QGIS | 3.x (Qt5 / PyQt5) |
| QGIS | 4.x (Qt6 / PyQt6) |

### Installation

1. Dans QGIS, ouvrez **Extensions → Installer/Gérer les extensions**.
2. Recherchez **OsmAnd bridge** dans l'onglet *Toutes*.
3. Cliquez sur **Installer**.

Le plugin apparaît alors dans le menu **Extensions → OsmAnd bridge** et une icône est ajoutée à la barre d'outils.

### Dépendance spécifique à Windows

La connexion directe à un appareil Android via USB (protocole MTP) requiert sous Windows la bibliothèque Python **comtypes**. Si elle n'est pas présente, le plugin propose de l'installer automatiquement au premier lancement. Un redémarrage de QGIS est ensuite nécessaire.

Si l'installation automatique échoue, installez `comtypes` manuellement via OSGeo4W Shell :

```
pip install comtypes
```

### Dépendance spécifique à macOS

La connexion directe à un appareil Android nécessite l'application **MacDroid** (la version gratuite suffit). Téléchargez-la depuis [macdroid.app](https://www.macdroid.app/fr/downloads/). MacDroid doit être lancée avant d'utiliser le plugin.

---

## 3. Interface du plugin

Cliquez sur l'icône OsmAnd dans la barre d'outils ou sélectionnez **Extensions → OsmAnd bridge → Import tracks, favorites, itinerary and AV notes**.

> **Note :** Un avertissement s'affiche au premier lancement pour signaler que les bibliothèques d'accès MTP peuvent être instables et, dans de rares cas, provoquer un crash de QGIS. Vous pouvez cocher **"Ne plus afficher ce message"** pour le masquer définitivement.

La fenêtre d'import est divisée en plusieurs zones :

```
┌─────────────────────────────────────────────────────────┐
│  [Logo]   Import OsmAnd data from:                      │
│           ◉ Device    ○ Local directory                  │
│  ─────────────────────────────────────────────────────  │
│  [Label source / sélecteur de répertoire ou appareil]   │
│  ─────────────────────────────────────────────────────  │
│  Select the track(s) you want to download:              │
│  ┌─────────────────────────────────────┐  [✓] [✗]      │
│  │  Nom          │ Taille │ Modifié    │               │
│  │  ...          │ ...    │ ...        │               │
│  └─────────────────────────────────────┘               │
│  ─────────────────────────────────────────────────────  │
│  Select the point feature(s) you want to download:      │
│  ☐ Favorites    ☐ Itinerary    ☐ AVnotes               │
│  ─────────────────────────────────────────────────────  │
│  Choose the destination folder on your computer:        │
│  [____________________________________________] [...]   │
│                                                         │
│                      [  Cancel  ]  [   OK   ]           │
└─────────────────────────────────────────────────────────┘
```

Le bouton **OK** ne s'active que lorsque toutes les conditions sont remplies :
- une source valide est sélectionnée,
- un dossier de destination valide est choisi,
- au moins un élément à importer est coché ou sélectionné.

---

## 4. Sources de données : appareil ou répertoire local

### 4.1 Depuis un répertoire local

Sélectionnez le bouton radio **Local directory**, puis choisissez le **répertoire racine OsmAnd** sur votre ordinateur.

Ce répertoire correspond au dossier `files` d'OsmAnd sur l'appareil, selon l'emplacement habituel :

```
/Android/data/net.osmand/files/
    ou
/Android/data/net.osmand.plus/files/
```

Si vous avez copié manuellement les fichiers depuis votre appareil, pointez directement vers ce dossier copié.

Dès qu'un répertoire valide est sélectionné, le plugin :
- liste automatiquement les traces GPX disponibles dans le tableau,
- active les cases à cocher **Favorites**, **Itinerary** et **AVnotes** si les fichiers correspondants existent.

### 4.2 Depuis un appareil connecté (MTP)

Sélectionnez le bouton radio **Device**. Le plugin liste les appareils détectés dans la liste déroulante.

Deux boutons sont disponibles :

| Bouton | Action |
|---|---|
| **↺** (Rafraîchir) | Actualise la liste des appareils connectés |
| **→** (Chercher) | Parcourt l'appareil sélectionné pour localiser les fichiers OsmAnd et les copier dans un dossier temporaire |

> **Important :** L'opération de copie depuis un appareil peut prendre **plusieurs minutes**, en particulier sous Linux. QGIS peut sembler bloqué pendant cette période ; c'est normal.

Le plugin recherche les fichiers OsmAnd dans les emplacements suivants sur l'appareil :

```
/Android/data/net.osmand/files
/Android/data/net.osmand.plus/files
/Android/media/net.osmand/files
/Android/media/net.osmand.plus/files
/Android/obb/net.osmand/files
/Android/obb/net.osmand.plus/files
```

Une fois la copie effectuée, le tableau des traces et les cases à cocher se remplissent automatiquement, exactement comme pour un répertoire local.

---

## 5. Données importables

### 5.1 Traces GPX

Le tableau central liste toutes les traces enregistrées dans `tracks/rec/` sur l'appareil OsmAnd. Pour chaque trace sont affichés :
- le **nom** du fichier,
- la **taille** (formatée en octets / Ko / Mo…),
- la **date de dernière modification**.

Le tableau est **triable** par colonne (clic sur l'en-tête).

**Sélection des traces :**

| Bouton | Action |
|---|---|
| **✓** (Tout sélectionner) | Sélectionne toutes les traces du tableau |
| **✗** (Tout désélectionner) | Désélectionne toutes les traces |
| Clic simple / Ctrl+clic / Maj+clic | Sélection manuelle individuelle ou multiple |

Seules les traces **sélectionnées** seront importées.

Pour chaque trace GPX, le plugin extrait les sous-couches non vides parmi :

| Sous-couche GPX | Type de géométrie | Groupe QGIS |
|---|---|---|
| `waypoints` | Points | *Waypoints* |
| `routes` | Lignes | *Routes* |
| `tracks` | Lignes | *Tracks* |
| `route_points` | Points | *Route points* |
| `track_points` | Points | *Track points* |

### 5.2 Favoris

La case **Favorites** est activée automatiquement si le fichier `favorites/favorites.gpx` est présent dans le répertoire source. Elle est cochée par défaut.

Les favoris sont importés avec la même structure de sous-couches que les traces GPX et regroupés sous le groupe **favorites**.

### 5.3 Itinéraire

La case **Itinerary** est activée automatiquement si le fichier `itinerary.gpx` est présent à la racine du répertoire source. Elle est cochée par défaut.

L'itinéraire est importé avec la même structure de sous-couches que les traces GPX et regroupé sous le groupe **Itinerary**.

### 5.4 Notes audiovisuelles

La case **AVnotes** est activée automatiquement si au moins un fichier multimédia est présent dans le sous-dossier `avnotes/`. Elle est cochée par défaut.

Les formats pris en charge sont :

| Format | Type | Couche créée |
|---|---|---|
| `.3gp` | Audio | *Audio notes* |
| `.mp3` | Audio | *Audio notes* |
| `.mp4` | Vidéo | *Video notes* |
| `.jpg` | Photo | *Picture notes* |
| `.tif` | Photo | *Picture notes* |

Chaque note est positionnée sur la carte grâce aux coordonnées géographiques encodées dans le nom du fichier par OsmAnd (format shortcode). Les fichiers multimédias sont **copiés** dans un sous-dossier `avnotes/` à l'intérieur du dossier de destination choisi.

Les couches de notes disposent des fonctionnalités suivantes :
- **Icônes SVG** distinctives par type (haut-parleur pour l'audio, caméra pour la vidéo, appareil photo pour les photos).
- **Action "Ouvrir le fichier"** accessible depuis la table attributaire ou la carte : ouvre le fichier multimédia avec l'application par défaut du système.
- **Info-bulle cartographique** pour les photos : survole un point avec la souris (après activation des info-bulles dans QGIS) pour afficher un aperçu de la photo directement sur la carte.

---

## 6. Dossier de destination

Le champ **"Choose the destination folder on your computer"** permet de choisir où seront enregistrés les fichiers produits par le plugin.

À l'issue de l'import, ce dossier contiendra :

```
<dossier_destination>/
├── AAAAMMJJ-HHhMMmSSs_OsmAnd_bridge.qgz   ← projet QGIS (sauvegardé automatiquement)
├── AAAAMMJJ-HHhMMmSSs_OsmAnd_bridge.gpkg  ← toutes les couches vecteur
└── avnotes/                                ← copie des fichiers multimédias (si AVnotes importées)
    ├── photo1.jpg
    ├── video1.mp4
    └── ...
```

> **Si un projet QGIS est déjà ouvert** au moment de l'import, les couches y sont ajoutées et le projet existant est sauvegardé. Aucun nouveau fichier `.qgz` n'est créé dans ce cas.

> **Si aucun projet n'est ouvert**, un nouveau projet est créé automatiquement avec un nom horodaté.

Le **système de coordonnées de référence** (SCR) du projet est automatiquement défini en **WGS 84 (EPSG:4326)**.

---

## 7. Résultat dans QGIS

### 7.1 Fichiers produits

Tous les vecteurs importés sont consolidés dans un **GeoPackage unique** (`.gpkg`). Ce format standard OGC présente plusieurs avantages :

- un seul fichier regroupe toutes les couches,
- compatible avec tous les SIG majeurs,
- pas de limite de taille de champ ni de nom.

### 7.2 Structure des couches

À la fin de l'import, le panneau des couches de QGIS est organisé en **groupes** :

```
📁 Map background
   └── OpenStreetMap (fond de carte XYZ)
📁 Audiovisual notes          ← si AVnotes importées
   ├── 🔊 Audio notes
   ├── 🎥 Video notes
   └── 📷 Picture notes
📁 favorites                  ← si Favorites importés
   ├── favorites_waypoints
   └── ...
📁 Itinerary                  ← si Itinéraire importé
   ├── itinerary_tracks
   └── ...
📁 Tracks                     ← par type de géométrie GPX
📁 Waypoints
📁 Routes
   ├── NomTrace1_tracks
   ├── NomTrace2_tracks
   └── ...
```

> Seules les sous-couches **non vides** sont créées. Une trace sans waypoints ne génère pas de couche *waypoints*.

### 7.3 Fond de carte OpenStreetMap

Si une connexion Internet est disponible au moment de l'import, le plugin ajoute automatiquement un **fond de carte OpenStreetMap** (tuiles XYZ) au projet. Si aucune connexion n'est détectée, un avertissement est affiché dans la barre de messages de QGIS mais l'import continue normalement.

À la fin de l'import, la vue cartographique est automatiquement **zoomée sur l'étendue** de toutes les données importées.

---

## 8. Menu du plugin

Le menu **Extensions → OsmAnd bridge** contient trois entrées :

| Entrée | Description |
|---|---|
| **Import tracks, favorites, itinerary and AV notes** | Lance la fenêtre d'import (également accessible via la barre d'outils) |
| **Reset saved settings** | Efface toutes les préférences mémorisées (cases "Ne plus afficher", etc.) |
| **Help** | Ouvre la documentation en ligne dans le navigateur web par défaut |

La langue de la documentation en ligne est choisie automatiquement en fonction de la langue de l'interface QGIS. Les langues disponibles sont : anglais, espagnol, italien, japonais, portugais, finnois et français. Si la langue de QGIS n'est pas supportée, la documentation s'affiche en anglais.

---

## 9. Notes par système d'exploitation

### 9.1 Linux

- La connexion MTP est réalisée via la bibliothèque **libmtp** (encapsulée dans le module `mtpy` fourni avec le plugin). Cette bibliothèque doit être installée sur le système :
  ```
  sudo apt install libmtp9        # Debian / Ubuntu
  sudo dnf install libmtp         # Fedora
  ```
- Certains gestionnaires de bureau (KDE, GNOME) verrouillent l'accès USB aux appareils MTP. Le plugin tente de résoudre ce conflit en terminant automatiquement les processus `kio*` et `gvfs*` avant d'accéder à l'appareil.
- La copie des fichiers depuis un appareil Android est **particulièrement lente** sous Linux en raison des limitations du protocole MTP. Comptez plusieurs minutes pour un volume de données important.
- Il est recommandé de **déverrouiller** l'écran de l'appareil Android avant de connecter et d'accéder à l'appareil.

### 9.2 Windows

- La connexion MTP nécessite la bibliothèque **comtypes** (voir [section 2](#2-prérequis-et-installation)).
- L'appareil doit être configuré en mode **Transfert de fichiers (MTP)** dans les options USB Android (la notification qui apparaît lors de la connexion du câble USB).
- Si l'appareil n'est pas détecté, essayez de débrancher et rebrancher le câble USB, puis cliquez sur le bouton **Rafraîchir**.

### 9.3 macOS

- La connexion MTP nécessite **MacDroid** (voir [section 2](#2-prérequis-et-installation)).
- MacDroid monte l'appareil Android comme un volume du système de fichiers, ce qui évite toute copie temporaire : le plugin accède directement aux fichiers.
- Assurez-vous que MacDroid est **lancé et que l'appareil est monté** avant d'utiliser le plugin.

---

## 10. Dépannage

### Le bouton OK reste grisé

Vérifiez que :
- le répertoire source est valide (contient bien la structure attendue d'OsmAnd),
- le dossier de destination est sélectionné et accessible en écriture,
- au moins une trace est sélectionnée dans le tableau **ou** au moins une case (Favorites, Itinerary, AVnotes) est cochée.

### Aucun appareil n'est détecté

- Vérifiez que le câble USB est bien connecté.
- Déverrouillez l'écran de l'appareil Android.
- Sélectionnez le mode **Transfert de fichiers (MTP)** dans la notification USB Android.
- Cliquez sur le bouton **Rafraîchir**.
- Sous Linux, essayez de débrancher et rebrancher le câble, puis relancez la détection.

### Les fichiers OsmAnd ne sont pas trouvés sur l'appareil

OsmAnd peut stocker ses données à différents emplacements selon la version (OsmAnd gratuit ou OsmAnd+) et les paramètres de stockage Android. Si le plugin ne trouve pas les fichiers automatiquement, copiez manuellement le dossier `files` d'OsmAnd depuis l'explorateur de fichiers de votre système, puis utilisez l'option **Local directory**.

### QGIS se bloque pendant la copie MTP

C'est un comportement attendu lors de la copie de gros volumes de données via MTP, en particulier sous Linux. Attendez la fin de l'opération. En cas de crash, relancez QGIS et utilisez l'option **Local directory** après avoir copié les fichiers manuellement.

### Les notes audiovisuelles ne s'affichent pas correctement

Vérifiez que les fichiers multimédias ont bien été copiés dans le sous-dossier `avnotes/` du dossier de destination. Le champ `full_path` de la table attributaire indique le chemin absolu attendu pour chaque fichier.

### Réinitialiser les messages "Ne plus afficher"

Utilisez **Extensions → OsmAnd bridge → Reset saved settings** pour effacer toutes les préférences mémorisées, y compris les messages masqués.

---

## 11. Compatibilité

| Environnement | Statut |
|---|---|
| QGIS 3.x — Linux | ✅ Supporté |
| QGIS 3.x — Windows | ✅ Supporté |
| QGIS 3.x — macOS | ✅ Supporté |
| QGIS 4.x — Linux | ✅ Supporté |
| QGIS 4.x — Windows | ✅ Supporté |
| QGIS 4.x — macOS | ✅ Supporté |
| OsmAnd (Android, gratuit) | ✅ Supporté |
| OsmAnd+ / OsmAnd Maps (Android) | ✅ Supporté |

**Langues de l'interface :** le plugin détecte automatiquement la langue de QGIS et charge les traductions disponibles. Les langues actuellement supportées sont : anglais (EN), espagnol (ES), italien (IT), japonais (JA), portugais (PT), finnois (FI), français (FR).

---

*Documentation générée pour OsmAnd bridge — © 2022-2026 Sylvain Théry, UMR 5281 ART-Dev (CNRS) — Licence GPL v2+*
