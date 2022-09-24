from io import BytesIO
from os.path import dirname, expanduser, join
import sys
from random import randint, choice
import requests
from PIL import Image, ImageQt
from PyQt5.QtCore import QItemSelectionModel, QModelIndex, QPoint, QRect, Qt, QTimer
from PyQt5.QtGui import QCursor, QStandardItem, QStandardItemModel, QPixmap, QImage, QScreen
from PyQt5.QtWidgets import (QAbstractItemView, QApplication, QHeaderView, QDesktopWidget,
                             QLabel, QLineEdit, QTableView, QTableWidgetItem,
                             QVBoxLayout, QWidget)
from scryfall_wrapper import *

debugging = False
shiftAround = False

# Must have at least 2 cards to switch between
cards = [
    Card("Filigree Familiar"),
    Card('Sol Ring'),
]
# cards = Card_Set('aer').cards()
# small, normal, large, png, art_crop, border_crop
artType = 'border_crop'
# min: 10, max: 60
if debugging:
    timeRangeMS = (2000, 5000)
else:
    timeRangeMS = (10*60*1000, 60*60*1000)


def pil2pixmap(image):
    bytes_img = BytesIO()
    image.save(bytes_img, format='JPEG')

    qimg = QImage()
    qimg.loadFromData(bytes_img.getvalue())

    return QPixmap.fromImage(qimg)


class MainWindow(QWidget):
    def __init__(self, screen):
        super().__init__()
        # self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAutoFillBackground(True)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowFlag(Qt.WindowType.BypassGraphicsProxyWidget)
        self.setWindowFlag(Qt.WindowType.NoDropShadowWindowHint)
        # self.setWindowFlag(Qt.WindowType.WindowDoesNotAcceptFocus)
        self.setWindowFlag(Qt.WindowType.MaximizeUsingFullscreenGeometryHint)
        # self.setWindowFlag(Qt.WindowType.WindowTransparentForInput)
        self.setWindowState(Qt.WindowState.WindowFullScreen)

        # Convert all the cards into labels
        self.labels = set()
        self._useless = []
        for card in cards:
            url = card.image_uris[artType]
            stuff = requests.get(url).content
            # self._useless.append(ImageQt.ImageQt(Image.open(BytesIO(stuff)).resize((screen.size().width(), screen.size().height()))))
            # img = QImage(self._useless[-1])
            # img = QImage(self._useless[-1])
            label = QLabel(parent=self)
            label.setPixmap(pil2pixmap(Image.open(BytesIO(stuff)).resize((screen.size().width(), screen.size().height()))))
            label.hide()
            self.labels.add(label)

        # Now disperse them randomly
        # for label in self.labels:
            # label.move(randint(0, self.width()), randint(0, self.height()))

        # Start the process
        # self.currentCard.show()
        self.currentCard = choice(list(self.labels))
        self.timer = QTimer(self)
        self.timer.setInterval(randint(*timeRangeMS))
        self.timer.setSingleShot(False)
        self.timer.timeout.connect(self.nextCard)
        self.timer.start()
        self.nextCard()

    def nextCard(self):
        if debugging:
            print('switching cards')
        self.hideCard(self.currentCard)
        self.currentCard = choice(list(self.labels.difference([self.currentCard])))
        if shiftAround:
            self.currentCard.move(randint(0, self.width()-self.currentCard.width()), randint(0, self.height()-self.currentCard.height()))
        self.showCard(self.currentCard)
        self.timer.setInterval(randint(*timeRangeMS))

    def showCard(self, card):
        card.show()

    def hideCard(self, card):
        card.hide()

    def mouseMoveEvent(self, a0):
        self.close()
        return super().mouseMoveEvent(a0)

    def keyPressEvent(self, a0):
        self.close()
        return super().keyPressEvent(a0)


if __name__ == "__main__":
    app = QApplication([])
    screen = QDesktopWidget()
    widget = MainWindow(screen)
    widget.show()
    rtn = app.exec()
    sys.exit(rtn)
