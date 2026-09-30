import sys
import cv2 as cv
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QComboBox
)

class CameraWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("WebCam Viewer")
        self.resize(800, 600)

        self.cameraLabel = QLabel()
        self.cameraLabel.setAlignment(Qt.AlignCenter)
        self.dropdown = QComboBox()
        self.find_cameras()

        self.dropdown.currentIndexChanged.connect(self.change_camera)

        central = QWidget()
        layout = QVBoxLayout(central)

        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        layout.addWidget(self.cameraLabel)
        layout.addWidget(self.dropdown)

        self.setCentralWidget(central)

        self.camera = None

        if self.dropdown.count() > 0:
            self.change_camera(0)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_camera)
        self.timer.start(30)

    def find_cameras(self):
        for index in range(10):
            camera = cv.VideoCapture(index)

            if camera.isOpened():
                self.dropdown.addItem(f"Camera {index}", index)
                camera.release()
            else:
                camera.release()

    def change_camera(self, dropdownIndex):
        if self.camera is not None:
            self.camera.release()
            self.camera = None   

        cameraIndex = self.dropdown.itemData(dropdownIndex)

        if cameraIndex is None:
            return
        self.camera = cv.VideoCapture(cameraIndex)         

    def update_camera(self):
        success, frame = self.camera.read()

        if not success:
            return
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

        height, width, channels = frame.shape
        bytesPerLine = channels * width

        image = QImage(
            frame.data,
            width,
            height,
            bytesPerLine,
            QImage.Format_RGB888
        )

        pixmap = QPixmap.fromImage(image)

        pixmap = pixmap.scaled(
            self.cameraLabel.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.cameraLabel.setPixmap(pixmap)

    def closeEvent(self, event):
        self.camera.release()
        event.accept()

app = QApplication(sys.argv)
window = CameraWindow()
window.show()
app.exec()