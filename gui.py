from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QWidget
from PyQt5.QtWidgets import QMenu, QAction, QFileDialog, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QFrame, QPushButton, QScrollArea, QCheckBox
from PyQt5.QtWidgets import QLineEdit, QGroupBox, QRadioButton, QButtonGroup

# import numpy as np
import sys

# import os
# import pyqtgraph as pg

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
        self.central_widget = QLabel("Please load a lens definition file...")
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

        newwidget = QWidget()
        newlayout = QVBoxLayout()
        # newlayout.setSpacing(0)
        # newlayout.setContentsMargins(11, 0, 11, 0)

        controlarea = QVBoxLayout()

        # buttons for the overall control
        controlrow = QHBoxLayout()

        all_to_scope_button = QPushButton("⬅︎ All To Scope")
        all_to_scope_button.clicked.connect(self.all_to_scope_pressed)
        controlrow.addWidget(all_to_scope_button)

        selected_to_scope_button = QPushButton("Selected To Scope")
        selected_to_scope_button.clicked.connect(self.selected_to_scope_pressed)
        controlrow.addWidget(selected_to_scope_button)

        seletcted_to_register_button = QPushButton(" Selected To Register")
        seletcted_to_register_button.clicked.connect(self.selected_to_register_pressed)
        controlrow.addWidget(seletcted_to_register_button)

        all_to_register_button = QPushButton("All To Register ➡︎")
        all_to_register_button.clicked.connect(self.all_to_register_pressed)
        controlrow.addWidget(all_to_register_button)

        controlarea.addLayout(controlrow)

        registerrow = QHBoxLayout()
        registerrow.addWidget(QLabel("Register:"))
        n_registers = len(self.lenses[0]['lenses'][0]['registers'])
        self.register_radio_group = QButtonGroup()
        self.register_radio_group.buttonClicked.connect(self.register_radio_toggled)
        for i in range(n_registers):
            radio = QRadioButton(f"{i+1}")
            registerrow.addWidget(radio)
            self.register_radio_group.addButton(radio, i)
            if i == 0:
                radio.setChecked(True)

        controlarea.addLayout(registerrow)


        newlayout.addLayout(controlarea)

        # Make a section for each group of lenses:
        for group in self.lenses:
            newlayout.addWidget(SectionLabel(group["name"]))

            for lens in group['lenses']:
                # print(f"Adding lens {lens['name']}")

                # an ID for the current lens that gets attached
                # to the buttons so they can be dispatched later
                lenspath = f"{group['name']}/{lens['name']}"

                buttonrow = QHBoxLayout()

                buttonrow.addWidget(QLabel(lens['name']))

                to_scope_button = QPushButton("⬅︎")
                to_scope_button.clicked.connect(self.single_lens_to_scope_pressed)
                to_scope_button.setObjectName(lenspath+"/TOSCOPE")
                buttonrow.addWidget(to_scope_button)

                to_register_button = QPushButton("➡︎")
                to_register_button.clicked.connect(self.single_lens_to_register_pressed)
                to_register_button.setObjectName(lenspath+"/TOREGISTER")
                buttonrow.addWidget(to_register_button)

                checkbox = QCheckBox()
                checkbox.setObjectName(lenspath+"/SELECTED")
                checkbox.setChecked(lens['selected'])
                buttonrow.addWidget(checkbox)

                # add register boxes
                for i in range(len(lens['registers'])):
                    reg = QLineEdit()
                    reg.setObjectName(lenspath+f"/REGISTER{i}")
                    reg.setText(str(lens['registers'][i]))
                    buttonrow.addWidget(reg)

                newlayout.addLayout(buttonrow)

        newwidget.setLayout(newlayout)
        scroll_area = QScrollArea()
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setWidget(newwidget)
        self.setCentralWidget(scroll_area)

    def single_lens_to_scope_pressed(self):
        sender = self.sender().objectName()
        print(f"Single lens to scope pressed: {sender}")

    def single_lens_to_register_pressed(self):
        sender = self.sender().objectName()
        print(f"Single lens to register pressed: {sender}")

    def all_to_scope_pressed(self):
        return

    def all_to_register_pressed(self):
        return

    def selected_to_scope_pressed(self):
        return

    def selected_to_register_pressed(self):
        return

    def register_radio_toggled(self):
        print(self.register_radio_group.checkedId())

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
