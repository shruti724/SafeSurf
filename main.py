from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *
import sys
import urllib.parse
import time
import logging

# Set up logging
logging.basicConfig(filename="browser_debug.log", level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class MyWebBrowser(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MyWebBrowser, self).__init__(*args, **kwargs)

        logging.debug("Initializing browser")

        try:
            self.setWindowTitle("Doppler")
            self.setWindowIcon(QIcon("resources/d.png"))

            self.window = QWidget()
            self.layout = QVBoxLayout()

            # Toolbar
            self.toolbar = QToolBar()
            self.addToolBar(Qt.TopToolBarArea, self.toolbar)

            # URL bar and navigation buttons
            self.url_bar = QLineEdit()
            self.url_bar.setMaximumHeight(30)

            self.go_btn = QPushButton()
            self.go_btn.setIcon(QIcon("resources/search.png"))
            self.go_btn.setMaximumHeight(30)
            self.go_btn.clicked.connect(self.navigate)

            self.back_btn = QPushButton()
            self.back_btn.setIcon(QIcon("resources/backward.png"))
            self.back_btn.setMaximumHeight(30)
            self.back_btn.clicked.connect(lambda: self.tabs.currentWidget().back())

            self.forward_btn = QPushButton()
            self.forward_btn.setIcon(QIcon("resources/right_arrow.png"))
            self.forward_btn.setMaximumHeight(30)
            self.forward_btn.clicked.connect(lambda: self.tabs.currentWidget().forward())

            self.reload_btn = QPushButton()
            self.reload_btn.setIcon(QIcon("resources/reloading.png"))
            self.reload_btn.setMaximumHeight(30)
            self.reload_btn.clicked.connect(lambda: self.tabs.currentWidget().reload())

            self.home_btn = QPushButton()
            self.home_btn.setIcon(QIcon("resources/home_new.png"))
            self.home_btn.setMaximumHeight(30)
            self.home_btn.clicked.connect(self.navigate_home)

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

            self.view_active_time_action = QAction("Active Time", self)
            self.view_active_time_action.triggered.connect(self.show_active_time)
            self.all_menu.addAction(self.view_active_time_action)

            self.all_btn.setMenu(self.all_menu)
            self.all_btn.setMaximumHeight(30)

            self.dark_mode_btn = QPushButton()
            self.dark_mode_btn.setIcon(QIcon("resources/moon.png"))
            self.dark_mode_btn.setMaximumHeight(30)
            self.dark_mode_btn.clicked.connect(self.toggle_dark_mode)

            self.new_tab_btn = QPushButton("+")
            self.new_tab_btn.setMaximumHeight(30)
            self.new_tab_btn.clicked.connect(lambda: self.add_new_tab(QUrl(self.home_url), "New Tab"))

            self.toolbar.addWidget(self.new_tab_btn)
            self.toolbar.addWidget(self.url_bar)
            self.toolbar.addWidget(self.go_btn)
            self.toolbar.addWidget(self.back_btn)
            self.toolbar.addWidget(self.forward_btn)
            self.toolbar.addWidget(self.reload_btn)
            self.toolbar.addWidget(self.home_btn)
            self.toolbar.addWidget(self.add_extension_btn)
            self.toolbar.addWidget(self.all_btn)
            self.toolbar.addWidget(self.dark_mode_btn)

            # Tabs
            self.tabs = QTabWidget()
            self.tabs.setTabsClosable(True)
            self.tabs.tabCloseRequested.connect(self.close_tab)
            self.tabs.currentChanged.connect(self.change_tab)
            self.layout.addWidget(self.tabs)

            # Default home page
            self.home_url = "http://google.com"
            self.add_new_tab(QUrl(self.home_url), "New Tab")

            self.window.setLayout(self.layout)
            self.setCentralWidget(self.window)

            # Tracking time
            self.time_spent = {}
            self.current_tab_index = 0
            self.start_time = time.time()
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_time_spent)
            self.timer.start(1000)  # Update every second

            self.is_dark_mode = False

            # Load search history
            self.visited_urls = []
            self.load_search_history()

            logging.debug("Browser initialized successfully")
        except Exception as e:
            logging.error(f"Error during initialization: {e}")

    def add_new_tab(self, qurl=None, label="New Tab"):
        try:
            if qurl is None:
                qurl = QUrl(self.home_url)

            browser = QWebEngineView()
            browser.setUrl(qurl)
            i = self.tabs.addTab(browser, label)
            self.tabs.setCurrentIndex(i)

            browser.urlChanged.connect(lambda qurl, browser=browser: self.update_urlbar(qurl, browser))
            browser.loadFinished.connect(
                lambda _, i=i, browser=browser: self.tabs.setTabText(i, browser.page().title()))
            browser.urlChanged.connect(lambda qurl: self.add_to_search_history(qurl.toString()))

            self.url_bar.setText(qurl.toString())

            # Initialize time spent for the new tab
            self.time_spent[i] = {'time': 0, 'url': qurl.toString()}
            logging.debug(f"Added new tab: {qurl.toString()} with index {i}")
        except Exception as e:
            logging.error(f"Error adding new tab: {e}")

    def close_tab(self, i):
        try:
            if self.tabs.count() < 2:
                return

            self.tabs.removeTab(i)
            if i in self.time_spent:
                del self.time_spent[i]

            logging.debug(f"Closed tab with index {i}")
        except Exception as e:
            logging.error(f"Error closing tab: {e}")

    def change_tab(self, i):
        try:
            # Update time spent on the previous tab
            self.update_time_spent()

            # Reset start time for the new tab
            self.current_tab_index = i
            self.start_time = time.time()

            logging.debug(f"Changed to tab with index {i}")
        except Exception as e:
            logging.error(f"Error changing tab: {e}")

    def update_time_spent(self):
        try:
            if self.current_tab_index in self.time_spent:
                self.time_spent[self.current_tab_index]['time'] += time.time() - self.start_time
                self.start_time = time.time()

            logging.debug(f"Updated time spent on tab with index {self.current_tab_index}")
        except Exception as e:
            logging.error(f"Error updating time spent: {e}")

    def navigate(self):
        try:
            text = self.url_bar.text()
            if self.is_valid_url(text):
                self.tabs.currentWidget().setUrl(QUrl(text))
            else:
                self.search_google()
            logging.debug(f"Navigating to: {text}")
        except Exception as e:
            logging.error(f"Error navigating: {e}")

    def is_valid_url(self, url):
        return url.startswith("http://") or url.startswith("https://")

    def search_google(self):
        try:
            search_query = self.url_bar.text()
            if search_query:
                search_url = "https://www.google.com/search?q={}".format(urllib.parse.quote(search_query))
                self.tabs.currentWidget().setUrl(QUrl(search_url))
                logging.debug(f"Searching Google for: {search_query}")
        except Exception as e:
            logging.error(f"Error searching Google: {e}")

    def navigate_home(self):
        try:
            self.tabs.currentWidget().setUrl(QUrl(self.home_url))
            self.url_bar.setText(self.home_url)
            logging.debug("Navigating home")
        except Exception as e:
            logging.error(f"Error navigating home: {e}")

    def add_extension(self):
        try:
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getOpenFileName(self, "Select Extension File", "", "JavaScript Files (*.js)")
            if file_path:
                with open(file_path, 'r') as file:
                    extension_script = file.read()
                    self.tabs.currentWidget().page().runJavaScript(extension_script)
                logging.debug(f"Added extension from: {file_path}")
        except Exception as e:
            logging.error(f"Error adding extension: {e}")

    def show_all_history(self):
        try:
            all_history_dialog = QDialog(self)
            all_history_dialog.setWindowTitle("Search History")
            layout = QVBoxLayout()

            list_widget = QListWidget()
            list_widget.addItems(self.visited_urls)

            layout.addWidget(list_widget)
            all_history_dialog.setLayout(layout)

            all_history_dialog.exec_()
            logging.debug("Displayed search history")
        except Exception as e:
            logging.error(f"Error showing search history: {e}")

    def show_active_time(self):
        try:
            self.update_time_spent()  # Ensure the current tab's time is updated

            active_time_dialog = QDialog(self)
            active_time_dialog.setWindowTitle("Active Time")
            layout = QVBoxLayout()

            list_widget = QListWidget()
            for index, data in self.time_spent.items():
                time_spent = data['time']
                url = data['url']
                site_name = self.extract_site_name(url)
                formatted_time = self.format_time(time_spent)
                list_widget.addItem(f"{site_name}: {formatted_time}")

            layout.addWidget(list_widget)
            active_time_dialog.setLayout(layout)

            active_time_dialog.exec_()
            logging.debug("Displayed active time")
        except Exception as e:
            logging.error(f"Error showing active time: {e}")

    def extract_site_name(self, url):
        # Extract site name from URL
        if "://" in url:
            start_index = url.find("://") + 3
            end_index = url.find("/", start_index)
            return url[start_index:end_index]
        else:
            return url

    def add_to_search_history(self, url):
        try:
            if url not in self.visited_urls:
                self.visited_urls.append(url)
                self.save_search_history()
                logging.debug(f"Added to search history: {url}")
        except Exception as e:
            logging.error(f"Error adding to search history: {e}")

    def save_search_history(self):
        try:
            with open("search_history.txt", "w") as file:
                for url in self.visited_urls:
                    file.write(url + "\n")
            logging.debug("Search history saved")
        except Exception as e:
            logging.error(f"Error saving search history: {e}")

    def load_search_history(self):
        try:
            with open("search_history.txt", "r") as file:
                self.visited_urls = [line.strip() for line in file]
            logging.debug("Search history loaded")
        except FileNotFoundError:
            logging.debug("Search history file not found, starting with an empty history")
        except Exception as e:
            logging.error(f"Error loading search history: {e}")

    def update_urlbar(self, qurl, browser=None):
        try:
            if browser != self.tabs.currentWidget():
                return
            self.url_bar.setText(qurl.toString())
            self.url_bar.setCursorPosition(0)
            logging.debug(f"URL bar updated to: {qurl.toString()}")
        except Exception as e:
            logging.error(f"Error updating URL bar: {e}")

    def toggle_dark_mode(self):
        try:
            self.is_dark_mode = not self.is_dark_mode
            if self.is_dark_mode:
                self.setStyleSheet("background-color: #2E2E2E; color: #F8F8F8;")
                self.url_bar.setStyleSheet("color: #000; background-color: #FFFFFF;")
                self.tabs.setStyleSheet(
                    "QTabBar::tab { background: #444444; color: #000; } QTabBar::tab:selected { background: #777777; }")
                logging.debug("Dark mode enabled")
            else:
                self.setStyleSheet("")
                self.url_bar.setStyleSheet("")
                self.tabs.setStyleSheet("QTabBar::tab { color: #000; }")
                logging.debug("Dark mode disabled")
        except Exception as e:
            logging.error(f"Error toggling dark mode: {e}")

    def format_time(self, seconds):
        try:
            hours, remainder = divmod(seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
        except Exception as e:
            logging.error(f"Error formatting time: {e}")
            return "N/A"


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("Doppler")
    app.setOrganizationName("MyCompany")
    app.setOrganizationDomain("mycompany.com")

    window = MyWebBrowser()
    window.show()

    sys.exit(app.exec_())
