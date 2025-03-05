from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLineEdit, QStyle, QFileDialog


class MyWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Créer un layout
        layout = QVBoxLayout(self)

        # Créer un QLineEdit pour afficher le chemin sélectionné
        self.line_edit = QLineEdit(self)
        self.line_edit.setPlaceholderText("Sélectionnez un répertoire...")
        layout.addWidget(self.line_edit)

        # Créer un bouton avec une icône "Parcourir"
        self.button = QPushButton(self)
        self.button.setIcon(self.style().standardIcon(QStyle.SP_DirOpenIcon))  # Icône standard "Ouvrir un dossier"
        self.button.setToolTip("Parcourir")  # Infobulle pour expliquer l'icône
        self.button.clicked.connect(self.open_directory_dialog)  # Connecter le clic du bouton à une méthode

        # Définir la taille du bouton en fonction de la taille de l'icône
        icon_size = self.button.iconSize()  # Taille par défaut de l'icône
        self.button.setFixedSize(icon_size + QSize(10, 10))  # Ajouter un peu de marge autour de l'icône

        layout.addWidget(self.button)

    def open_directory_dialog(self):
        # Ouvrir une boîte de dialogue pour sélectionner un répertoire
        directory = QFileDialog.getExistingDirectory(
            self,  # Parent widget
            "Sélectionner un répertoire",  # Titre de la boîte de dialogue
            "",  # Répertoire initial (vide pour le répertoire par défaut)
            QFileDialog.ShowDirsOnly | QFileDialog.DontUseNativeDialog  # Options
        )

        # Si l'utilisateur a sélectionné un répertoire, mettre à jour le QLineEdit
        if directory:
            self.line_edit.setText(directory)


window = MyWindow()
window.show()