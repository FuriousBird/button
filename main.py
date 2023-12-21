""" lock = Lock()
is_open = False

def on_tray_icon_click(reason):
    if reason == QSystemTrayIcon.Trigger:
        print("Tray icon clicked!")

def open_menu():
    global is_open
    lock.acquire()
    if is_open:
        lock.release()
        return
    is_open = True
    lock.release()
    print("hello")
    window = MyWindow()
    #do some stuff
     """
    

import sys,os,time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QSystemTrayIcon, QMenu, QHBoxLayout, QAction
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QCursor



import threading

LOCK = threading.Lock()

GLOBAL_MACRO = "Macro Par Defaut"
MACRO_FILE_EXISTS = False

MACRO_SAVE_FILE = "macro.txt"
if os.path.exists(MACRO_SAVE_FILE):
    MACRO_FILE_EXISTS = True
    with open(MACRO_SAVE_FILE, "rb") as file:
        GLOBAL_MACRO=file.read().decode("UTF-8")



def thread_func(event:threading.Event):
    global GLOBAL_MACRO
    from pynput.keyboard import Key, Controller
    import time, serial

    keyboard = Controller()

    ser = serial.Serial(timeout=0.5)
    ser.braudrate = 9600
    ser.port = "/dev/ttyUSB0"
    ser.open()

    def parsemacro(string):
        
        parsed = []
        previous_escape = False
        parse_buf=""
        fact = 0
        i=0
        while i<len(string):
            char = string[i]
            hasnumparsed = False
            isCharNormalAt = True
            
            if char == "@" and previous_escape==False and i+1<len(string):
                isCharNormalAt = False
                if string[i+1]=="<":
                    fact = -1
                elif string[i+1]==">":
                    fact = 1
                numstring = ""
                i+=2
                run = True
                while i<len(string) and run:
                    numchar = string[i]
                    if numchar.isnumeric():
                        numstring+=numchar
                        i+=1
                    else:
                        i+=1
                        run=False
                num = int(numstring) if len(numstring)>0 else 0
                num *= fact
                hasnumparsed = True

            previous_escape = False
            
            if hasnumparsed:
                #end of prev parsed string
                parsed.append(parse_buf)
                parse_buf = ""
                parsed.append(num)
                continue
            
            if char == "@" and previous_escape==True:
                parse_buf=parse_buf[:-1]+char
            else:
                parse_buf+=char

            #prepare for next step
            
            if char == "\\":
                previous_escape = True
            i+=1
        parsed.append(parse_buf)
        print(string,parsed)
        return parsed

    DELAY = .5 #seconds

    prev = None
    while ser.isOpen():
        
        LOCK.acquire() ########### acquire
        if event.is_set():
            LOCK.release() ########### release 1
            print("Closed The Thread")
            break


        macro = GLOBAL_MACRO
        LOCK.release() ########### release 2
        parsed_macro = parsemacro(macro)
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
    ser.close()

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

        # Add widgets to the left layout
        left_layout.addWidget(self.input_box)
        left_layout.addWidget(self.submit_button)

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
    