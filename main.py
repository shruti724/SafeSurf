from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *
import sys
import urllib.parse

class MyWebBrowser(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MyWebBrowser, self).__init__(*args, **kwargs)

        self.setWindowTitle("Doppler")
        self.setWindowIcon(QIcon("resources/d.png"))

        self.window = QWidget()
        self.layout = QVBoxLayout()
        self.horizontal = QHBoxLayout()

        self.url_bar = QLineEdit()
        self.url_bar.setMaximumHeight(30)

        self.go_btn = QPushButton()
        self.go_btn.setIcon(QIcon("resources/search.png"))
        self.go_btn.setMaximumHeight(30)
        self.go_btn.clicked.connect(self.navigate)

        self.back_btn = QPushButton()
        self.back_btn.setIcon(QIcon("resources/backward.png"))
        self.back_btn.setMaximumHeight(30)

        self.forward_btn = QPushButton()
        self.forward_btn.setIcon(QIcon("resources/right_arrow.png"))
        self.forward_btn.setMaximumHeight(30)

        self.reload_btn = QPushButton()
        self.reload_btn.setIcon(QIcon("resources/reloading.png"))
        self.reload_btn.setMaximumHeight(30)

        self.home_btn = QPushButton()
        self.home_btn.setIcon(QIcon("resources/home_new.png"))
        self.home_btn.setMaximumHeight(30)

        self.add_extension_btn = QPushButton("Add Extension")
        self.add_extension_btn.setMaximumHeight(30)
        self.add_extension_btn.clicked.connect(self.add_extension)

        self.all_btn = QToolButton()
        self.all_btn.setText("All")
        self.all_btn.setPopupMode(QToolButton.InstantPopup)
        self.all_menu = QMenu(self)
        self.view_history_action = QAction("View History", self)
        self.view_history_action.triggered.connect(self.show_all_history)
        self.all_menu.addAction(self.view_history_action)
        self.all_btn.setMenu(self.all_menu)
        self.all_btn.setMaximumHeight(30)

        self.dark_mode_btn = QPushButton()
        self.dark_mode_btn.setIcon(QIcon("resources/moon.png"))
        self.dark_mode_btn.setMaximumHeight(30)
        self.dark_mode_btn.clicked.connect(self.toggle_dark_mode)

        self.horizontal.addWidget(self.url_bar)
        self.horizontal.addWidget(self.go_btn)
        self.horizontal.addWidget(self.back_btn)
        self.horizontal.addWidget(self.forward_btn)
        self.horizontal.addWidget(self.reload_btn)
        self.horizontal.addWidget(self.home_btn)
        self.horizontal.addWidget(self.add_extension_btn)
        self.horizontal.addWidget(self.all_btn)
        self.horizontal.addWidget(self.dark_mode_btn)

        self.browser = QWebEngineView()

        self.go_btn.clicked.connect(self.navigate)
        self.back_btn.clicked.connect(self.browser.back)
        self.forward_btn.clicked.connect(self.browser.forward)
        self.reload_btn.clicked.connect(self.browser.reload)
        self.home_btn.clicked.connect(self.navigate_home)

        self.layout.addLayout(self.horizontal)
        self.layout.addWidget(self.browser)

        self.home_url = "http://google.com"
        self.browser.setUrl(QUrl(self.home_url))

        self.window.setLayout(self.layout)
        self.setCentralWidget(self.window)

        self.cache = {}
        self.visited_urls = []
        self.load_search_history()

        self.browser.urlChanged.connect(self.on_url_changed)

        self.is_dark_mode = False  # Keep track of the mode

    def navigate(self):
        text = self.url_bar.text()
        if self.is_valid_url(text):
            self.browser.setUrl(QUrl(text))
            self.add_to_search_history(text)
        else:
            self.search_google()

    def is_valid_url(self, url):
        return url.startswith("http://") or url.startswith("https://")

    def search_google(self):
        search_query = self.url_bar.text()
        if search_query:
            search_url = "https://www.google.com/search?q={}".format(urllib.parse.quote(search_query))
            self.browser.setUrl(QUrl(search_url))
            self.add_to_search_history(search_query)

    def navigate_home(self):
        self.browser.setUrl(QUrl(self.home_url))
        self.url_bar.setText(self.home_url)

    def add_extension(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Extension File", "", "JavaScript Files (*.js)")
        if file_path:
            with open(file_path, 'r') as file:
                extension_script = file.read()
                self.browser.page().runJavaScript(extension_script)

    def show_all_history(self):
        all_history_dialog = QDialog(self)
        all_history_dialog.setWindowTitle("Search History")
        layout = QVBoxLayout()

        list_widget = QListWidget()
        list_widget.addItems(self.visited_urls)

        layout.addWidget(list_widget)
        all_history_dialog.setLayout(layout)

        all_history_dialog.exec_()

    def save_search_history(self):
        with open("search_history.txt", "w") as file:
            file.write("\n".join(self.visited_urls))

    def load_search_history(self):
        try:
            with open("search_history.txt", "r") as file:
                self.visited_urls = file.read().splitlines()
        except FileNotFoundError:
            pass

    def add_to_search_history(self, url):
        if url not in self.visited_urls:
            self.visited_urls.append(url)
            self.save_search_history()

    def on_url_changed(self, url):
        if not url.isEmpty():
            self.add_to_search_history(url.toString())

    def toggle_dark_mode(self):
        if not self.is_dark_mode:
            self.setStyleSheet("background-color: #333; color: #fff;")
            self.browser.setStyleSheet("background-color: #000; color: #fff;")
            self.dark_mode_btn.setIcon(QIcon("resources/sun.png"))
        else:
            self.setStyleSheet("")
            self.browser.setStyleSheet("")
            self.dark_mode_btn.setIcon(QIcon("resources/moon.png"))
        self.is_dark_mode = not self.is_dark_mode


app = QApplication(sys.argv)
window = MyWebBrowser()
window.show()
window.showMaximized()
app.exec_()
