import sys
import json
from PyQt5.QtWidgets import QApplication, QMessageBox, QCheckBox, QVBoxLayout

# Nom du fichier de paramètres
PARAM_FILE = "settings.json"

# Fonction pour charger les paramètres depuis le fichier
def load_settings():
    try:
        with open(PARAM_FILE, "r") as file:
            settings = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        settings = {}
    return settings

# Fonction pour sauvegarder les paramètres dans le fichier
def save_settings(settings):
    with open(PARAM_FILE, "w") as file:
        json.dump(settings, file)

app = QApplication(sys.argv)

# Charger les paramètres
settings = load_settings()

# Vérifier si la boîte de message doit être affichée
if not settings.get("hide_message", False):  # Affiche si "hide_message" est False ou n'existe pas
    # Création de la boîte de message
    message_box = QMessageBox()
    message_box.setWindowTitle("Message avec case à cocher")
    message_box.setText("Ceci est un message avec une case à cocher.\n\n\nCoucou")
    message_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

    # Ajout de la case à cocher
    checkbox = QCheckBox("Ne plus afficher ce message")
    layout = message_box.layout()
    layout.addWidget(checkbox, layout.rowCount(), 0, 1, layout.columnCount())

    # Affichage de la boîte de message
    result = message_box.exec_()

    # Sauvegarder l'état de la case à cocher si l'utilisateur clique sur OK
    if result == QMessageBox.Ok and checkbox.isChecked():
        settings["hide_message"] = True
    else:
        settings["hide_message"] = False

    # Enregistrer les paramètres
    save_settings(settings)
else:
    print("La boîte de message est masquée car la case a déjà été cochée.")

sys.exit(app.exec_())


# import sys
# from PyQt5.QtWidgets import QApplication, QMessageBox, QCheckBox, QVBoxLayout, QDialogButtonBox
#
# app = QApplication(sys.argv)
#
# # Création de la boîte de message
# message_box = QMessageBox()
# message_box.setWindowTitle("Message avec case à cocher")
# message_box.setText("Ceci est un message avec une case à cocher.")
# message_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
#
# # Ajout de la case à cocher
# checkbox = QCheckBox("Ne plus afficher ce message")
# layout = message_box.layout()
# layout.addWidget(checkbox, layout.rowCount(), 0, 1, layout.columnCount())
#
# # Affichage de la boîte de message
# result = message_box.exec_()
#
# # Vérification des résultats
# if result == QMessageBox.Ok:
#     print("L'utilisateur a cliqué sur OK")
# else:
#     print("L'utilisateur a cliqué sur Annuler")
#
# if checkbox.isChecked():
#     print("La case à cocher est cochée.")
# else:
#     print("La case à cocher n'est pas cochée.")