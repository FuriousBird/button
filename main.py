import sys,os,time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QSystemTrayIcon, QMenu, QHBoxLayout, QTabWidget, QCheckBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QCursor
from tmp import macro_parser

import serial.tools.list_ports

GLOBAL_COMPORTS = []
GLOBAL_COMPORT_NAMES = []

def filter_COMS(COMLIST):
    VID=6790
    RETURNPORTS = []
    for device in COMLIST:
        if (device.vid != None):
            print(device.vid)
            if (device.vid == VID):
                port = device.device
                print("Detected Possible COMPORT:",port)
                RETURNPORTS.append(device)
                continue
            port = None
    return RETURNPORTS

def update_COM():
    global GLOBAL_COMPORTS, GLOBAL_COMPORT_NAMES
    RETURN_COMS = list(serial.tools.list_ports.comports())
    GLOBAL_COMPORTS = filter_COMS(RETURN_COMS)
    GLOBAL_COMPORT_NAMES = [getattr(dev, "device", None) for dev in GLOBAL_COMPORTS]
    
update_COM()

GLOBAL_DEFAULTCOM = None
DEFAULTCOM_FILE = "defaultcom.txt"
if os.path.exists(DEFAULTCOM_FILE):
    with open(DEFAULTCOM_FILE, "r") as file:
        GLOBAL_DEFAULTCOM = file.read().strip()
        print("Found Default COM PORT")
else:
    print("Default COM PORT not set")
if GLOBAL_DEFAULTCOM not in GLOBAL_COMPORT_NAMES:
    print("Warning: Default COM not present, ignoring defaults")
    GLOBAL_DEFAULTCOM=None #don't try default port if it is not present

import threading

LOCK = threading.Lock()

GLOBAL_MACRO = "Macro Par Defaut"
MACRO_FILE_EXISTS = False

MACRO_SAVE_FILE = "macro.txt"
if os.path.exists(MACRO_SAVE_FILE):
    print("Using saved Macro")
    MACRO_FILE_EXISTS = True
    with open(MACRO_SAVE_FILE, "rb") as file:
        GLOBAL_MACRO=file.read().decode("UTF-8")
else:
    print("Using software default Macro")

def thread_func(event:threading.Event):
    print("Serial Thread started")
    global GLOBAL_MACRO
    from pynput.keyboard import Key, Controller
    import time, serial

    keyboard = Controller()

    ser = serial.Serial(timeout=0.5)
    ser.braudrate = 9600
    ser.port = "/dev/ttyUSB0"
    ser.open()

    DELAY = .5 #seconds

    prev = None
    while ser.isOpen():
        
         
        if event.is_set():
            print("Closing Thread...")
            break

        LOCK.acquire() ###########
        macro = GLOBAL_MACRO     
        LOCK.release() ###########
        parsed_macro = macro_parser(macro)
        dat = None
        try:
            if ser.closed:
                raise ValueError
            dat = ser.readline().strip().decode("ASCII")
        except:
            print("couldn't find serial, retrying in 5sec")
            time.sleep(5)
            ser.close()
            try:
                ser.open()
            except:
                ser.close()
            continue
        
        #THERE IS AN ISSUE WITH THE 
        if not dat:
            continue
        now = time.perf_counter()
        if prev is not None:
            dt = now-prev
            if dt<DELAY:
                continue
        prev = now
        if dat == "bruh":
            for item in parsed_macro:
                if isinstance(item, int):
                    if item<0:
                        for i in range(-item):
                            keyboard.tap(Key.left)
                    if item>0:
                        for i in range(item):
                            keyboard.tap(Key.right)
                    continue
                keyboard.type(item)
    print("Closing Serial...")
    ser.close()
    print("Thread Exited!")
#main thread
stop_event = threading.Event()
proc = threading.Thread(target=thread_func, args=(stop_event,))
proc.start()

class MyWindow(QWidget):
    def __init__(self, app):
        super().__init__()
        self.qapp = app
        self.init_ui()
    def closeEvent(self, event):
        # Reimplementing the close event to hide the window instead of closing the app
        event.ignore()
        self.hide()

    def init_ui(self):
        global MACRO_FILE_EXISTS, GLOBAL_MACRO
        # Set up the main layout
        main_layout = QHBoxLayout()

        # Create a vertical layout for the left side (input box and submit button)
        left_layout = QVBoxLayout()
        tabs = QTabWidget()
        tabs.setDisabled(True)

        macro_tab = self.macroTabUI()

        tabs.addTab(macro_tab, "Macro Mode")
        # Create input box
        
        self.input_box = QTextEdit(self)
        self.input_box.setPlaceholderText("Ex: \sum_0^n{}@<1")
        if MACRO_FILE_EXISTS:
            self.input_box.setText(GLOBAL_MACRO)
        self.input_box.setAlignment(Qt.AlignTop | Qt.AlignLeft)  # Align text to top left
        self.input_box.setFixedHeight(100)  # Set the height of the input box
        self.input_box.setAcceptRichText(True)  # Enable multiline

        # Create submit button
        self.submit_button = QPushButton("💾 save", self)
        self.submit_button.clicked.connect(self.on_submit_clicked)

        # Add widgets to the macro tab
        macro_tab.layout().addWidget(self.input_box)
        macro_tab.layout().addWidget(self.submit_button)

        tabs.addTab(self.scriptTabUI(), "Script Mode")

        left_layout.addWidget(tabs)

        # Create a vertical spacer to push widgets to the top
        left_layout.addStretch(1)

        # Create a horizontal layout for the entire window
        main_layout.addLayout(left_layout)

        # Create text label on the right
        self.text_label = QLabel("pour effectuer un deplacement du curseur, utilisez @>X ou @<x pour effectuer un deplacement gauche/droite de x, pour utiliser un symbole @ utiliser \@", self)
        self.text_label.setFixedWidth(200)
        #self.text_label.setTextFormat(Qt.RichText)  # Enable rich text
        self.text_label.setWordWrap(True) 
        self.text_label.setAlignment(Qt.AlignTop)  # Align text to the top

        # Add text label to the main layout
        main_layout.addWidget(self.text_label)

        # Set the main layout for the window
        self.setLayout(main_layout)

        # Set up the window
        self.setGeometry(100, 100, 500, 200)
        self.setWindowTitle("Configuration")
        self.show()
    
    def scriptTabUI(self):

        """Create the General page UI."""

        generalTab = QWidget()

        layout = QVBoxLayout()

        layout.addWidget(QCheckBox("Not Ready"))

        layout.addWidget(QCheckBox("WIP"))

        generalTab.setLayout(layout)

        return generalTab


    def macroTabUI(self):

        """Create the Network page UI."""

        networkTab = QWidget()

        layout = QVBoxLayout()

        layout.addWidget(QCheckBox("BracketAutoCloseFix"))

        layout.addWidget(QCheckBox("Enabled"))

        networkTab.setLayout(layout)

        return networkTab

    def on_submit_clicked(self):
        global GLOBAL_MACRO
# do lengthy process
        # Get text from input box and display it in the label
        
        input_text = self.input_box.toPlainText()
        LOCK.acquire()
        GLOBAL_MACRO = input_text
        LOCK.release()
        with open(MACRO_SAVE_FILE, "wb") as file:
            file.write(input_text.encode("UTF-8"))

class SystemTrayApp(QApplication):
    def __init__(self, *args, **kwargs):
        super(SystemTrayApp, self).__init__(*args, **kwargs)

        # Initialize the system tray
        # Create a system tray icon
        self.tray_icon = QSystemTrayIcon(QIcon("icon.png"), parent=self)
        self.tray_icon.setToolTip("Bouton")

        # Create a context menu
        context_menu = QMenu()
        open_action = context_menu.addAction("Configuration")
        open_action.triggered.connect(self.show_window)
        context_menu.addSeparator()
        exit_action = context_menu.addAction("Exit")
        exit_action.triggered.connect(self.quit)

        # Set the context menu
        self.tray_icon.setContextMenu(context_menu)
        #self.tray_icon.activated.connect(self.on_tray_icon_activated)

        self.tray_icon.show()

        self.my_window = MyWindow(self)
        self.my_window.hide()

    def show_window(self):
        self.my_window.show()
        

    """ def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.show_window() """

if __name__ == "__main__":
    app = SystemTrayApp(sys.argv)
    code = app.exec_()
    LOCK.acquire()
    stop_event.set()
    LOCK.release()
    sys.exit(code)
    