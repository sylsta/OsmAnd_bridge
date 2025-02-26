import json

from qgis.PyQt.QtWidgets import QMessageBox, QCheckBox


def load_settings(PARAM_FILE):
    """

    :return:
    """
    try:
        with open(PARAM_FILE, "r") as file:
            settings = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        settings = {}
    return settings


def save_settings(PARAM_FILE, settings):
    """

    :param settings:
    :return:
    """
    with open(PARAM_FILE, "w") as file:
        json.dump(settings, file)

def msgbox_setting(self, message, setting_name, title):
    print("settings = self.load_settings() call")

    settings = load_settings(self.PARAM_FILE)
    if not settings.get(setting_name, False):  # Affiche si "hide_message" est False ou n'existe pas
        # Création de la boîte de message
        message_box = QMessageBox()

        message_box.setWindowTitle(title)

        message_box.setText(message)
        try: # #Qt5
            message_box.setStandardButtons(QMessageBox.Ok)
        except AttributeError:
            # Qt6
            message_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        checkbox = QCheckBox(self.tr("Don't show this message again"))
        layout = message_box.layout()
        layout.addWidget(checkbox, layout.rowCount(), 0, 1, layout.columnCount())

        # Affichage de la boîte de message
        result = message_box.exec()

        # Sauvegarder l'état de la case à cocher si l'utilisateur clique sur OK
        try:
            # Qt5
            if result == QMessageBox.Ok and checkbox.isChecked():
                settings[setting_name] = True
            else:
                settings[setting_name] = False
        except AttributeError:
            # Qt6
            if result ==  QMessageBox.StandardButton.Ok and checkbox.isChecked():
                settings[setting_name] = True
            else:
                settings[setting_name] = False

            # Enregistrer les paramètres
        save_settings(self.PARAM_FILE, settings)


