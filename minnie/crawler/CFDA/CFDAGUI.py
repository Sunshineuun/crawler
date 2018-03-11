#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.init_window()

    def init_window(self):
        self.setGeometry(300, 300, 500, 300)
        self.setWindowTitle('Minnie')
        self.setWindowIcon(QIcon('/zhutou.png'))

        self.show()


if __name__ == '__main__':
    print(sys.argv)
    
    app = QApplication(sys.argv)
    w = Window()
    sys.exit(app.exec_())
