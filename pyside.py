import sys
import cv2 as cv
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QWidget,
    QVBoxLayout,
    QLabel,
    QSlider,
    QComboBox
)

class CameraWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("WebCam Viewer")
        self.resize(800, 600)

        self.camera = cv.VideoCapture(0)

        self.cameraLabel = QLabel()
        self.cameraLabel.setAlignment(Qt.AlignCenter)

        central = QWidget()
        layout = QVBoxLayout(central)

        layout.setContentsMargins(20, 20, 20, 20)
        layout.addWidget(self.cameraLabel)

        self.setCentralWidget(central)

app = QApplication(sys.argv)
window = CameraWindow()
window.show()
app.exec()