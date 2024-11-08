import sys
from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QWidget


def generate_annotations(ui_file: str):
    # Charger dynamiquement le fichier .ui dans un objet QWidget
    app = QtWidgets.QApplication(sys.argv)

    # Charger dynamiquement la classe et la base de l'interface utilisateur depuis le fichier .ui
    UiClass, BaseClass = uic.loadUiType(ui_file)

    # Créer une instance temporaire pour inspecter les widgets
    class UiLoader(BaseClass, UiClass):
        def __init__(self):
            super(UiLoader, self).__init__()
            self.setupUi(self)
    # Créer une instance pour inspecter les widgets
    widget = UiLoader()

    annotations = []

    # Parcourir les attributs de l'instance pour détecter les widgets
    for name, obj in widget.__dict__.items():
        if isinstance(obj, QWidget):
            # Récupère le nom de la classe du widget (QLabel, QPushButton, etc.)
            widget_type = type(obj).__name__
            # Crée une annotation au format : `name: widget_type`
            annotation = f"{name}: {widget_type}"
            annotations.append(annotation)

    # Génère le code avec les annotations
    for annotation in annotations:
        print(f"    {annotation}")



# Utiliser le script en passant le nom du fichier .ui en argument
if __name__ == "__main__":
    generate_annotations('OsmAnd_bridge_import_dialog.ui')
