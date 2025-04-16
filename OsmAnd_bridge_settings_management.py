import json

from qgis.PyQt.QtWidgets import QMessageBox, QCheckBox
from qgis.PyQt.QtCore import Qt

def load_settings(PARAM_FILE):
    """
    load settings from json file
    :return: settingg
    """
    try:
        with open(PARAM_FILE, "r") as file:
            settings = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        settings = {}
    return settings


def save_settings(PARAM_FILE, settings):
    """
    Save settings to json file
    :param settings: settings
    :return: none
    """
    with open(PARAM_FILE, "w") as file:
        json.dump(settings, file)

def add_setting(self, name, value):
    """
    :param self:
    :param name: 
    :param value: 
    :return: 
    """
    pass

def msgbox_setting(self, setting_name: str, title: str, message: str, yes_no: bool = False) -> bool:
    """
    function used to store if warning messageboxes as to be hide or not
    :param self: iface
    :param message: str
    :param setting_name:str
    :param title: str
    :param yes_no: bool (shows yes no buttons or only ok button)
    :return: boolean
    """

    settings = load_settings(self.PARAM_FILE)
    if not settings.get(setting_name, False):  # Affiche si "hide_message" est False ou n'existe pas
        # Creates messagebox
        message_box = QMessageBox()

        message_box.setWindowTitle(title)
        try:  # Qt5
            message_box.setTextFormat(Qt.RichText)
        except: # Qt6
            message_box.setTextFormat(Qt.TextFormat.RichText)
        message_box.setText(message)
        try: # #Qt5
            if yes_no:
                message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            else:
                message_box.setStandardButtons(QMessageBox.Ok)
        except AttributeError:
            # Qt6
            if yes_no:
                message_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            else:
                message_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        checkbox = QCheckBox(self.tr("Don't show this message again"))
        layout = message_box.layout()
        layout.addWidget(checkbox, layout.rowCount(), 0, 1, layout.columnCount())

        # Affichage de la boîte de message
        result = message_box.exec()
        answer = False
        # Sauvegarder l'état de la case à cocher si l'utilisateur clique sur OK
        try: # Qt5
            if (result == QMessageBox.Ok or result == QMessageBox.Yes):
                answer = True
        except AttributeError: # Qt6
            if (result ==  QMessageBox.StandardButton.Ok or result == QMessageBox.StandardButton.Yes):
                answer = True

        settings[setting_name] = checkbox.isChecked()

        # save settings
        save_settings(self.PARAM_FILE, settings)

        return answer


