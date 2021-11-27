from __future__ import print_function

try:
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import (
        QApplication,
        QLabel,
        QMainWindow,
        QWidget,
        QMenu,
        QAction,
        QFileDialog,
        QVBoxLayout,
        QHBoxLayout,
        QFrame,
        QPushButton,
        QScrollArea,
        QCheckBox,
        QLineEdit,
        QRadioButton,
        QButtonGroup,
        QDesktopWidget,
        QMessageBox,
    )
except ImportError:
    print("PyQt5 not available... trying PyQt4")
    from PyQt4.QtCore import Qt
    from PyQt4.QtWidgets import (
        QApplication,
        QLabel,
        QMainWindow,
        QWidget,
        QMenu,
        QAction,
        QFileDialog,
        QVBoxLayout,
        QHBoxLayout,
        QFrame,
        QPushButton,
        QScrollArea,
        QCheckBox,
        QLineEdit,
        QRadioButton,
        QButtonGroup,
        QDesktopWidget,
        QMessageBox,
    )


import sys
import random  # only used in OFFLINE mode for making up values
import pprint
import json

try:
    import win32gui
    import win32con

    ONLINE = True
except Exception as exc:
    print(exc)
    print("pywinauto not found... running in offline mode")
    ONLINE = False


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

        self.setWindowTitle("LibreLens")

        # icon = QtGui.QIcon(str(Path(__file__).parent.absolute() / "logo.png"))
        # self.setWindowIcon(icon)
        # self.qtapp.setWindowIcon(icon)

        self.lens_file = None
        self.lenses = None
        # TODO: check if there is a file in argv, open directly to that file

        self.setup_window()
        layout = QVBoxLayout()
        central_widget = QLabel(
            (
                "LibreLens by SE Zeltmann\n"
                "steven.zeltmann@lbl.gov\n"
                "\n"
                "Make sure the TEMSpy Outputs pane is open.\n"
                "Then load a lens definition file to begin..."
            )
        )
        layout.addWidget(central_widget, 0, Qt.AlignCenter)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.resize(400, 250)
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
        self.edit_menu = QMenu("&Debug", self)
        self.menu_bar.addMenu(self.edit_menu)

        self.discover_HWNDs_action = QAction("&Rediscover HWNDs", self)
        self.discover_HWNDs_action.triggered.connect(self.discover_TEMSpy_handles)
        self.edit_menu.addAction(self.discover_HWNDs_action)

        self.debug_action = QAction("&Dump data to console", self)
        self.debug_action.triggered.connect(
            lambda: pprint.PrettyPrinter(indent=4).pprint(self.lenses)
        )
        self.edit_menu.addAction(self.debug_action)

        self.sync_action = QAction("&Synchronize GUI to Internal")
        self.sync_action.triggered.connect(
            lambda: self.synchronize_GUI(GUI_to_internal=True)
        )
        self.edit_menu.addAction(self.sync_action)

        self.sync_action_reverse = QAction("Synchronize Internal to &GUI")
        self.sync_action_reverse.triggered.connect(
            lambda: self.synchronize_GUI(GUI_to_internal=False)
        )
        self.edit_menu.addAction(self.sync_action_reverse)

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

        self.discover_TEMSpy_handles()

        newwidget = QWidget()
        newlayout = QVBoxLayout()

        controlarea = QVBoxLayout()

        # buttons for the overall control
        controlrow = QHBoxLayout()

        all_to_scope_button = QPushButton("⬅︎ All To Scope")
        all_to_scope_button.clicked.connect(self.all_to_scope_pressed)
        all_to_scope_button.setToolTip(
            "Copy all lens settings from the active register to the microscope."
        )
        controlrow.addWidget(all_to_scope_button)

        selected_to_scope_button = QPushButton("Selected To Scope")
        selected_to_scope_button.clicked.connect(self.selected_to_scope_pressed)
        selected_to_scope_button.setToolTip(
            "Copy lens settings from the lenses with their checkbox selected to the microscope."
        )
        controlrow.addWidget(selected_to_scope_button)

        seletcted_to_register_button = QPushButton("Selected To Register")
        seletcted_to_register_button.clicked.connect(self.selected_to_register_pressed)
        seletcted_to_register_button.setToolTip(
            "Copy lens settings from the lenses with their checkbox selected from the microscope to LibreLens."
        )
        controlrow.addWidget(seletcted_to_register_button)

        all_to_register_button = QPushButton("All To Register ➡︎")
        all_to_register_button.clicked.connect(self.all_to_register_pressed)
        all_to_register_button.setToolTip(
            "Copy all lens settings from the microscope to the active register in LibreLens."
        )
        controlrow.addWidget(all_to_register_button)

        controlarea.addLayout(controlrow)

        # buttons for (de)selecting all the checkboxes
        selectionrow = QHBoxLayout()

        select_all_button = QPushButton("Select All")
        select_all_button.clicked.connect(self.select_all_pressed)
        selectionrow.addWidget(select_all_button)

        deselect_all_button = QPushButton("Deselect All")
        deselect_all_button.clicked.connect(self.deselect_all_pressed)
        selectionrow.addWidget(deselect_all_button)

        zero_all_button = QPushButton("Zero Register")
        zero_all_button.clicked.connect(self.zero_register_pressed)
        selectionrow.addWidget(zero_all_button)

        controlarea.addLayout(selectionrow)

        # radio buttons for picking which register is active
        registerrow = QHBoxLayout()
        registerrow.addWidget(QLabel("Register:"))
        self.n_registers = len(self.lenses[0]["lenses"][0]["registers"])
        self.register_radio_group = QButtonGroup()
        self.register_radio_group.buttonClicked.connect(self.register_radio_toggled)
        for i in range(self.n_registers):
            radio = QRadioButton(f"{i+1}")
            registerrow.addWidget(radio)
            self.register_radio_group.addButton(radio, i)
            if i == 0:
                radio.setChecked(True)
        self.register_radio_toggled()

        controlarea.addLayout(registerrow)

        newlayout.addLayout(controlarea)

        # make a new layout with tight spacing
        # (we'll have to add some padding manually as a result)
        lens_layout = QVBoxLayout()
        lens_layout.setSpacing(0)
        lens_layout.setContentsMargins(11, 0, 11, 0)
        # Make a section for each group of lenses:
        for group in self.lenses:
            lens_layout.addWidget(SectionLabel(group["name"]))

            for lens in group["lenses"]:
                # an ID for the current lens that gets attached
                # to the buttons so they can be dispatched programmatically
                lenspath = f"{group['name']}/{lens['name']}"

                buttonrow = QHBoxLayout()

                namelabel = QLabel(lens["name"])
                namelabel.setMinimumWidth(30)
                buttonrow.addWidget(namelabel)

                to_scope_button = QPushButton("⬅︎")
                to_scope_button.clicked.connect(self.single_lens_to_scope_pressed)
                to_scope_button.setObjectName(lenspath + "/TOSCOPE")
                to_scope_button.setToolTip(
                    f"Copy {lens['name']} setting from active register to microscope."
                )
                buttonrow.addWidget(to_scope_button)
                buttonrow.addSpacing(11)

                to_register_button = QPushButton("➡︎")
                to_register_button.clicked.connect(self.single_lens_to_register_pressed)
                to_register_button.setObjectName(lenspath + "/TOREGISTER")
                to_register_button.setToolTip(
                    f"Copy {lens['name']} setting from microscpe to the active register. "
                )
                buttonrow.addWidget(to_register_button)
                buttonrow.addSpacing(11)

                checkbox = QCheckBox()
                checkbox.setObjectName(lenspath + "/SELECTED")
                checkbox.setChecked(lens["selected"])
                buttonrow.addWidget(checkbox)
                buttonrow.addSpacing(11)

                # add register boxes
                for i in range(self.n_registers):
                    reg = QLineEdit()
                    reg.setObjectName(lenspath + f"/REGISTER{i}")
                    reg.setText(str(lens["registers"][i]))
                    buttonrow.addWidget(reg)
                    buttonrow.addSpacing(11)

                lens_layout.addLayout(buttonrow)

        newlayout.addLayout(lens_layout)
        newwidget.setLayout(newlayout)
        scroll_area = QScrollArea()
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setWidget(newwidget)
        self.setCentralWidget(scroll_area)

        self.resize(640, QDesktopWidget().availableGeometry(self).size().height() * 0.7)

        # populate the GUI with data from the lens file
        self.synchronize_GUI(GUI_to_internal=False)

    def synchronize_GUI(self, GUI_to_internal=True):
        """
        All-purpose state synchronization.
        Rather than handle user interaction with the GUI whenever
        a value is changed, we wait until a concrete action (like
        sending a value to TEMSpy) is called and synchronize the
        GUI data with the internal datastructure en masse, before
        dispacthing whatever action.

        When GUI_to_internal is True, copies data from the GUI into
            internal dictionary
        When GUI_to_internal is False, copies data data from the
            internal dictionary to the GUI
        """
        assert type(GUI_to_internal) is bool, "GUI sync got a bad argument!"

        for group in self.lenses:
            groupname = group["name"]

            for lens in group["lenses"]:
                lensname = lens["name"]

                # get/set the select checkbox state
                selectname = f"{groupname}/{lensname}/SELECTED"
                selected = self.findChild(QCheckBox, selectname)
                if GUI_to_internal:
                    lens["selected"] = selected.isChecked()
                else:
                    selected.setChecked(lens["selected"])

                # get/set the value in each register
                for i in range(self.n_registers):
                    registername = f"{groupname}/{lensname}/REGISTER{i}"

                    register = self.findChild(QLineEdit, registername)

                    if GUI_to_internal:
                        lens["registers"][i] = float(register.text())
                    else:
                        register.setText(f"{lens['registers'][i]}")

    def get_value_from_TEMSpy(self, HWND: int) -> float:
        """
        grab the value from the TEMSpy Edit control
        referred to by the handle HWND
        """
        if ONLINE:
            print(f"Reading HWND {HWND:#x}")
            buffer_length = (
                win32gui.SendMessage(HWND, win32con.WM_GETTEXTLENGTH, 0, 0) + 1
            ) * 2  # Windows 7 seems to use UTF-16 encoding, so double the number of bytes
            buf = win32gui.PyMakeBuffer(buffer_length)
            win32gui.SendMessage(
                HWND, win32con.WM_GETTEXT, buffer_length // 2, buf
            )  # this takes number of characters as an argument
            return float(bytes(buf[:-2]).decode("utf-16"))

        else:
            print(f"Tried to read HWND {HWND:#x}")
            return float(f"{random.random():10.6f}")

    def set_value_in_TEMSpy(self, HWND: int, value: float):
        """
        set the value in the TEMSpy Edit control
        referred to by the handle HWND.
        Operates by setting the text in the control then
        simulating a press of the Return key in that Edit
        """
        if ONLINE:
            # format the number to a string:
            numstring = f"{value:2.9f}"
            buffer_length = (len(numstring) + 1) * 2
            send_buffer = win32gui.PyMakeBuffer(buffer_length)
            # python prepends 0xFF 0xFE, which identifies the byte
            # order of the string, but TEMSpy doesn't like this
            # so we have to nuke it
            send_buffer[:-2] = bytes(numstring, "utf-16")[2:]
            send_buffer[-2:] = b"\x00\x00"

            # this buffer length doesn't seem to matter
            win32gui.SendMessage(HWND, win32con.WM_SETTEXT, 0, send_buffer)
            win32gui.PostMessage(HWND, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)

            print(f"Set HWND {HWND:#x} to {numstring}")
        else:
            print(f"Tried to set HWND {HWND:#x} to {value:10.15f}")

    def zero_register_pressed(self):
        self.synchronize_GUI(GUI_to_internal=True)

        for group in self.lenses:
            for lens in group["lenses"]:
                lens["registers"][self.current_register] = 0.0

        self.synchronize_GUI(GUI_to_internal=False)

    def single_lens_to_scope_pressed(self):
        self.synchronize_GUI(GUI_to_internal=True)
        sender = self.sender().objectName()

        groupname, lensname, _ = sender.split("/")

        # get the lens that matches the sender
        group = list(filter(lambda g: g["name"] == groupname, self.lenses))[0]
        lens = list(filter(lambda l: l["name"] == lensname, group["lenses"]))[0]

        self.set_value_in_TEMSpy(lens["HWND"], lens["registers"][self.current_register])

        print(
            f"Single lens to scope pressed: {sender}, sent value {lens['registers'][self.current_register]}"
        )

    def single_lens_to_register_pressed(self):
        self.synchronize_GUI(GUI_to_internal=True)
        sender = self.sender().objectName()

        groupname, lensname, _ = sender.split("/")

        # get the lens that matches the sender
        group = list(filter(lambda g: g["name"] == groupname, self.lenses))[0]
        lens = list(filter(lambda l: l["name"] == lensname, group["lenses"]))[0]

        newvalue = self.get_value_from_TEMSpy(lens["HWND"])

        # write the value into the lens datastructure
        lens["registers"][self.current_register] = newvalue
        print(f"Single lens to register pressed: {sender}")

        self.synchronize_GUI(GUI_to_internal=False)

    def all_to_scope_pressed(self):
        self.synchronize_GUI(GUI_to_internal=True)

        for group in self.lenses:
            for lens in group["lenses"]:
                self.set_value_in_TEMSpy(
                    lens["HWND"], lens["registers"][self.current_register]
                )

    def all_to_register_pressed(self):
        self.synchronize_GUI(GUI_to_internal=True)
        for group in self.lenses:
            for lens in group["lenses"]:
                lens["registers"][self.current_register] = self.get_value_from_TEMSpy(
                    lens["HWND"]
                )
        self.synchronize_GUI(GUI_to_internal=False)

    def selected_to_scope_pressed(self):
        self.synchronize_GUI(GUI_to_internal=True)
        for group in self.lenses:
            for lens in group["lenses"]:
                if lens["selected"]:
                    self.set_value_in_TEMSpy(
                        lens["HWND"], lens["registers"][self.current_register]
                    )

    def selected_to_register_pressed(self):
        self.synchronize_GUI(GUI_to_internal=True)
        for group in self.lenses:
            for lens in group["lenses"]:
                if lens["selected"]:
                    lens["registers"][
                        self.current_register
                    ] = self.get_value_from_TEMSpy(lens["HWND"])
        self.synchronize_GUI(GUI_to_internal=False)

    def select_all_pressed(self):
        self.synchronize_GUI(GUI_to_internal=True)
        for group in self.lenses:
            for lens in group["lenses"]:
                lens["selected"] = True
        self.synchronize_GUI(GUI_to_internal=False)

    def deselect_all_pressed(self):
        self.synchronize_GUI(GUI_to_internal=True)
        for group in self.lenses:
            for lens in group["lenses"]:
                lens["selected"] = False
        self.synchronize_GUI(GUI_to_internal=False)

    def register_radio_toggled(self):
        """
        This is handled separately from the synchronize_GUI
        function because it should react immediately, so that
        we can do style updates based on it
        """
        self.current_register = self.register_radio_group.checkedId()
        print(f"selected register {self.current_register}")

    def load_definition_file(self):
        """
        Called by Qt when the user loads a definition file.
        Calls self.setup_controls() to populate the GUI
        """
        print("Loading definition file...")
        filename = QFileDialog.getOpenFileName(
            self,
            "Open Lens Definition File",
            "",
            "LibreLens Definition Files (*.json *.lens)",
        )
        if filename is not None and len(filename[0]) > 0:
            print(f"User chose file: {filename}")
            self.lens_file = filename[0]
            self.setup_controls()
        else:
            print("Lens file was invalid, or something?")
            self.lens_file = None

    def save_definition_file(self):
        self.synchronize_GUI(GUI_to_internal=True)
        print("Saving definition file...")
        filename = QFileDialog.getSaveFileName(
            self,
            "Save Lens Definition File",
            self.lens_file,
            "LibreLens Definition Files (*.lens *.json)",
        )

        if filename is not None and len(filename[0]) > 0:
            print(f"User chose file: {filename}")

            with open(filename[0], "w") as f:
                json.dump(self.lenses, f)

    def display_about_window(self):
        print("Displaying about window...")
        QMessageBox.information(
            self,
            "About LibreLens",
            (
                "Created by Steven Zeltmann, 2021\n"
                "steven.zeltmann@lbl.gov\n"
                "National Center for Electron Microscopy\n"
                "Molecular Foundry\n"
                "Lawrence Berkeley National Laboratory"
            ),
            QMessageBox.Ok,
            QMessageBox.Ok,
        )

    def discover_TEMSpy_handles(self):
        """
        Find the HWNDs of each lens by scanning the children of the
        Outputs window. The leftmost Edit box is the "speed"
        control, which we must ignore.

        We have to do this because TEMSpy does not seem to assign the HWNDs
        of its child Edit windows in any predictable way...
        """
        if ONLINE and self.lenses is not None:
            # enumerate all of the children of the Outputs window
            # to find the Edit windows, which are text boxes
            outputs = win32gui.FindWindow(0, "Outputs")
            edits = []

            def callback(hwnd, edits):
                if win32gui.GetClassName(hwnd) == "Edit":
                    edits.append((hwnd, win32gui.GetWindowRect(hwnd)[:2]))

            win32gui.EnumChildWindows(outputs, callback, edits)

            # Get the x position of each Edit box
            x = [h[1][0] for h in edits]
            x_min = min(x)

            # filter out the "speed" control, which is the leftmost one
            edits = filter(lambda h: h[1][0] > x_min, edits)

            # sort the edits by their y position
            edits = sorted(edits, key=lambda h: h[1][1])

            # update the HWND field of each lens based on its vertical position
            for group in self.lenses:
                for lens in group["lenses"]:
                    lens["HWND"] = edits[lens["position"]][0]

        else:
            print("Tried to discover HWNDs, but I am offline :(")


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
