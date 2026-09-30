import sys
import cv2 as cv
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
from PySide6.QtCore import Qt

camera = cv.VideoCapture(0)
app = QApplication(sys.argv)

def slider_func(value):
    print("Volume: ", value)

window = QMainWindow()
window.setWindowTitle("My App")

central = QWidget()
layout = QVBoxLayout()
label = QLabel("Tung Tung Sahur")
button = QPushButton("Click Me")
dropdown = QComboBox()
dropdown.addItem("1")
dropdown.addItem("2")
dropdown.addItem("3")
dropdown.addItem("4")
slider = QSlider(Qt.Horizontal)
slider.setRange(0, 100)
slider.setValue(50)
slider.valueChanged.connect(slider_func)

button.clicked.connect(lambda: label.setText("Tung Tung Gone Bhaya"))

layout.setContentsMargins(50, 50, 50, 50)
layout.addWidget(label)
layout.addWidget(button)
layout.addWidget(slider)
layout.addWidget(dropdown)

central.setLayout(layout)
window.setCentralWidget(central)

window.resize(800, 500)
window.show()

app.exec()