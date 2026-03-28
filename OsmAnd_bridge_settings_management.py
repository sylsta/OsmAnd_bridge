import json

from qgis.PyQt.QtWidgets import QMessageBox, QCheckBox
from qgis.PyQt.QtCore import Qt


def load_settings(PARAM_FILE):
    """
    Load settings from json file.
    :return: settings dict
    """
    try:
        with open(PARAM_FILE, "r") as file:
            settings = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        settings = {}
    return settings


def save_settings(PARAM_FILE, settings):
    """
    Save settings to json file.
    :param settings: settings dict
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
    Show a warning messagebox whose visibility can be permanently disabled by the user.
    Compatible Qt5 (PyQt5) and Qt6 (PyQt6) — Qt6 is tested first in every try/except block.

    :param self: iface or dialog instance (must expose PARAM_FILE and tr())
    :param setting_name: key used to store the "don't show again" preference
    :param title: messagebox title
    :param message: messagebox body (may contain HTML)
    :param yes_no: if True shows Yes/No buttons; otherwise shows a single Ok button
    :return: True if the user clicked Ok or Yes, False otherwise
    """

    settings = load_settings(self.PARAM_FILE)
    if not settings.get(setting_name, False):  # show only if not hidden
        message_box = QMessageBox()
        message_box.setWindowTitle(title)

        # setTextFormat — Qt6 uses namespaced enum Qt.TextFormat.RichText
        try:  # Qt6
            message_box.setTextFormat(Qt.TextFormat.RichText)
        except AttributeError:  # Qt5
            message_box.setTextFormat(Qt.RichText)

        message_box.setText(message)

        # Standard buttons — Qt6 uses QMessageBox.StandardButton.*
        if yes_no:
            try:  # Qt6
                message_box.setStandardButtons(
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            except AttributeError:  # Qt5
                message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        else:
            try:  # Qt6
                message_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            except AttributeError:  # Qt5
                message_box.setStandardButtons(QMessageBox.Ok)

        checkbox = QCheckBox(self.tr("Don't show this message again"))
        layout = message_box.layout()
        layout.addWidget(checkbox, layout.rowCount(), 0, 1, layout.columnCount())

        result = message_box.exec()

        # Compare result — Qt6 uses namespaced enum values
        answer = False
        try:  # Qt6
            if result in (QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Yes):
                answer = True
        except AttributeError:  # Qt5
            if result in (QMessageBox.Ok, QMessageBox.Yes):
                answer = True

        settings[setting_name] = checkbox.isChecked()
        save_settings(self.PARAM_FILE, settings)

        return answer
