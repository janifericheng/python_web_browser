import sys
import os
import json

from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QLineEdit, QTabBar,
                             QFrame, QStackedLayout, QTabWidget, QShortcut,
                             QKeySequenceEdit, QSplitter)

from PyQt5.QtGui import QIcon, QWindow, QImage, QKeySequence
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *

class AddressBar(QLineEdit):
    def __init__(self):
        super().__init__()

    def mousePressEvent(self, e):
        self.selectAll()

class App(QFrame):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Web Browser")

        self.setBaseSize(1366, 768)
        self.setMinimumSize(1366, 768)
        self.CreateApp()
        self.setWindowIcon(QIcon("logo.png"))

    def CreateApp(self):
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Create Tabs
        self.TabBar = QTabBar(movable=True, tabsClosable=True)
        self.TabBar.tabCloseRequested.connect(self.CloseTab)
        self.TabBar.tabBarClicked.connect(self.SwitchTab)
        self.TabBar.setCurrentIndex(0)
        self.TabBar.setDrawBase(False)
        self.TabBar.setLayoutDirection(Qt.LeftToRight)
        self.TabBar.setElideMode(Qt.ElideLeft)

        self.shortcutNewTab = QShortcut(QKeySequence("Ctrl+T"), self)
        self.shortcutNewTab.activated.connect(self.AddTab)

        self.shortcutReload = QShortcut(QKeySequence("Ctrl+R"), self)
        self.shortcutReload.activated.connect(self.ReloadPage)

        # Keep track of tabs
        self.TabCount = 0
        self.Tabs = []

        # Create AddressBar
        self.Toolbar = QWidget()
        self.Toolbar.setObjectName("Toolbar")
        self.ToolBarLayout = QHBoxLayout()
        self.AddressBar = AddressBar()
        self.AddTabButton = QPushButton("+")

        #Connect AddressBar + button Signals
        self.AddressBar.returnPressed.connect(self.BrowseTo)
        self.AddTabButton.clicked.connect(self.AddTab)

        #Set Toolbar Buttons
        self.BackButton = QPushButton("<")
        self.BackButton.clicked.connect(self.GoBack)

        self.ForwardButton = QPushButton(">")
        self.ForwardButton.clicked.connect(self.GoForward)

        self.ReloadButton = QPushButton("R")
        self.ReloadButton.clicked.connect(self.ReloadPage)

        #Build Toolbar
        self.Toolbar.setLayout(self.ToolBarLayout)
        self.ToolBarLayout.addWidget(self.BackButton)
        self.ToolBarLayout.addWidget(self.ForwardButton)
        self.ToolBarLayout.addWidget(self.ReloadButton)
        self.ToolBarLayout.addWidget(self.AddressBar)
        self.ToolBarLayout.addWidget(self.AddTabButton)

        # set main view
        self.Container = QWidget()
        self.Container.layout = QStackedLayout()
        self.Container.setLayout(self.Container.layout)

        self.layout.addWidget(self.TabBar)
        self.layout.addWidget(self.Toolbar)
        self.layout.addWidget(self.Container)

        self.setLayout(self.layout)

        self.AddTab()

        self.show()

    def CloseTab(self, i):
        self.TabBar.removeTab(i)

    def AddTab(self):
        i = self.TabCount

        #set self.tabs<#> = QWidget
        self.Tabs.append(QWidget())
        self.Tabs[i].layout = QVBoxLayout()
        self.Tabs[i].layout.setContentsMargins(0,0,0,0)


        #For tab switching
        self.Tabs[i].setObjectName("Tab " + str(i))

        #Create webview within the tabs top level widget
        self.Tabs[i].content = QWebEngineView()
        self.Tabs[i].content.load(QUrl.fromUserInput("http://google.com"))

        self.Tabs[i].content1 = QWebEngineView()
        self.Tabs[i].content1.load(QUrl.fromUserInput("http://google.com"))

        self.Tabs[i].content.titleChanged.connect(lambda: self.SetTabContent(i, "title"))
        self.Tabs[i].content.iconChanged.connect(lambda: self.SetTabContent(i, "icon"))
        self.Tabs[i].content.urlChanged.connect(lambda: self.SetTabContent(i, "url"))

        # Add widget to tabs layout
        self.Tabs[i].splitview = QSplitter()
        self.Tabs[i].splitview.setOrientation(Qt.Vertical)
        self.Tabs[i].layout.addWidget(self.Tabs[i].splitview)

        self.Tabs[i].splitview.addWidget(self.Tabs[i].content)
        self.Tabs[i].splitview.addWidget(self.Tabs[i].content1)

        # set tab layout to .layout
        self.Tabs[i].setLayout(self.Tabs[i].layout)

        # Add and set new tabs content to the stack widget
        self.Container.layout.addWidget(self.Tabs[i])
        self.Container.layout.setCurrentWidget(self.Tabs[i])

        # Create tab on tabbar, representing this tab,
        #Set tabData to tab<#> So it knows what self.tabs[#] it needs to control
        self.TabBar.addTab("New Tab - " + str(i))
        self.TabBar.setTabData(i, {"object": "Tab" + str(i), "initial": i})


        self.TabBar.setCurrentIndex(i)

        self.TabCount += 1

    def SwitchTab(self, i):
        #Switch to tab.  get current tabs tabData ("tab0") and find object with that name.
        if self.TabBar.tabData(i):
            Tab_Data = self.TabBar.tabData(i)["object"]
            Tab_Content = self.findChild(QWidget, Tab_Data)
            self.Container.layout.setCurrentWidget(Tab_Content)
            new_url = Tab_Content.content.url().toString()
            self.addressbar.setText(new_url)

    def BrowseTo(self):
        text = self.AddressBar.text()
        print(text)

        i = self.TabBar.currentIndex()
        Tab = self.TabBar.tabData(i)["object"]
        wv = self.findChild(QWidget, Tab).content

        if "http" not in text:
            if "." not in text:
                url = "http://www.google.com/#q=" + text
            else:
                url = "http://" + text
        else:
            url = text

        wv.load(QUrl.fromUserInput(url))

    def SetTabContent(self, i, type):
        # self.Tabs[i].objectName = tab1
        # self.TabBar.tabData(i)["object"] = tab1
        tab_name = self.Tabs[i].objectName()
#       tab1

        count = 0
        running = True

        current_tab = self.TabBar.tabData(self.TabBar.currentIndex())["object"]

        if current_tab == tab_name and type == "url":
            new_url = self.findChild(QWidget, tab_name).content.url().toString()
            self.AddressBar.setText(new_url)
            return False

        while running:
            tab_data_name = self.TabBar.tabData(count)

            if count >= 99:
                running = False

            if tab_name == tab_data_name["object"]:
                if type == "title":
                    newTitle = self.findChild(QWidget, tab_name).content.title()
                    self.TabBar.setTabContent(count, newTitle)
                elif type == "icon":
                    newIcon = self.findChild(QWidget, tab_name).content.icon()
                    self.TabBar.setTabIcon(count, newIcon)

                running = False
            else:
                count += 1

    def GoBack(self):
        activeIndex = self.TabBar.currentIndex()
        tab_name = self.TabBar.tabData(activeIndex)["object"]
        tab_content = self.findChild(QWidget, tab_name).content

        tab_content.back()

    def GoForward(self):
        activeIndex = self.TabBar.currentIndex()
        tab_name = self.TabBar.tabData(activeIndex)["object"]
        tab_content = self.findChild(QWidget, tab_name).content

        tab_content.forward()

    def ReloadPage(self):
        activeIndex = self.TabBar.currentIndex()
        tab_name = self.TabBar.tabData(activeIndex)["object"]
        tab_content = self.findChild((QWidget, tab_name)).content

        tab_content.reload()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # os.environ['QTWEBENGINE_REMOTE_DEBUGGING'] = "667"

    window = App()

    with open("style.css", "r") as style:
        app.setStyleSheet(style.read())
    sys.exit(app.exec_())
