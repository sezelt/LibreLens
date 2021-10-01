from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QWidget
from PyQt5.QtWidgets import QMenu, QAction, QFileDialog, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QFrame, QPushButton, QScrollArea

# import numpy as np
import sys

# import os
import pyqtgraph as pg

# from pathlib import Path
import json


class LibreLensGUI(QMainWindow):
    """
    The class is used by instantiating and then entering the main Qt loop with, e.g.:
        app = LibreLensGUI(sys.argv)
        app.exec_()
    """

    def __init__(self, argv):
        super().__init__()

        self.qtapp = QApplication.instance()
        if not self.qtapp:
            self.qtapp = QApplication(argv)

        # self.main_window = QWidget()
        self.setWindowTitle("LibreLens")

        # icon = QtGui.QIcon(str(Path(__file__).parent.absolute() / "logo.png"))
        # self.setWindowIcon(icon)
        # self.qtapp.setWindowIcon(icon)

        self.lens_file = None
        # TODO: check if there is a file in argv, open directly to that file

        self.setup_window()
        self.central_widget = QWidget()
        self.central_widget.setLayout(QVBoxLayout())
        self.setCentralWidget(self.central_widget)
        self.show()

    def setup_window(self):
        self.menu_bar = self.menuBar()

        # File menu
        self.file_menu = QMenu("&File", self)
        self.menu_bar.addMenu(self.file_menu)

        self.load_action = QAction("&Load Definition File...", self)
        self.load_action.triggered.connect(self.load_definition_file)
        self.file_menu.addAction(self.load_action)

        self.save_action = QAction("&Save Definition File...", self)
        self.save_action.triggered.connect(self.save_definition_file)
        self.file_menu.addAction(self.save_action)

        # Edit Menu
        self.edit_menu = QMenu("&Edit", self)
        self.menu_bar.addMenu(self.edit_menu)

        # Help Menu
        self.help_menu = QMenu("&Help", self)
        self.menu_bar.addMenu(self.help_menu)

        self.show_about_action = QAction("&About...", self)
        self.show_about_action.triggered.connect(self.display_about_window)
        self.help_menu.addAction(self.show_about_action)

    def setup_controls(self):
        """
        Called when a new lens file is loaded, and the UI has to be rebuilt.
        """
        if self.lens_file is None:
            print("Ruh-roh! No lens file is set!")
            return

        with open(self.lens_file, "r") as f:
            self.lenses = json.load(f)

            # print(f"Lens file contains: {self.lenses}")

        QWidget().setLayout(self.central_widget.layout())
        newlayout = QVBoxLayout(self.central_widget)
        # Make a section for each group of lenses:
        for group in self.lenses:
            newlayout.addWidget(SectionLabel(group["name"]))

            for lens in group['lenses']:
                # print(f"Adding lens {lens['name']}")
                buttonrow = QHBoxLayout()

                buttonrow.addWidget(QLabel(lens['name']))

                to_scope_button = QPushButton("<---")
                buttonrow.addWidget(to_scope_button)

                to_register_button = QPushButton("--->")
                buttonrow.addWidget(to_register_button)

                newlayout.addLayout(buttonrow)

        self.central_widget.setLayout(newlayout)
        # scroll_area = QScrollArea()
        # scroll_area.setWidget(self.central_widget)

    def load_definition_file(self):
        """
        Called by Qt when the user loads a definition file.
        """
        print("Loading definition file...")
        filename = QFileDialog.getOpenFileName(
            self,
            "Open Lens Definition File",
            "",
            "LibreLens Definition Files (*.json *.lens)",
        )
        if filename is not None:
            print(f"User chose file: {filename}")
            self.lens_file = filename[0]
            self.setup_controls()
        else:
            print("Lens file was invalid, or something?")
            self.lens_file = None

    def save_definition_file(self):
        print("Saving definition file...")

    def display_about_window(self):
        print("Displaying about window...")


class SectionLabel(QWidget):
    def __init__(self, section_title):
        QWidget.__init__(self)

        line_left = QFrame()
        line_left.setFrameShape(QFrame.HLine)
        line_left.setFrameShadow(QFrame.Sunken)
        line_left.setLineWidth(1)
        line_right = QFrame()
        line_right.setFrameShape(QFrame.HLine)
        line_right.setFrameShadow(QFrame.Sunken)
        line_right.setLineWidth(1)

        label = QLabel(section_title)
        # label.setFont(sectionFont)

        layout = QHBoxLayout()
        layout.addWidget(line_left)
        layout.addWidget(label, 0, Qt.AlignCenter)
        layout.addWidget(line_right)

        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = LibreLensGUI(sys.argv)
    win.show()
    sys.exit(app.exec_())
