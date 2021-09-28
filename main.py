from PyQt5 import QtWidgets, QtCore
from mydesign import Ui_MainWindow
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from imageai.Detection import ObjectDetection
import os
import sys

exec_path = os.getcwd()
output_images_folder_path = os.path.join(exec_path, "result_images")
proceeded_file_path = os.path.join(exec_path, "started_image.png")

start_image_name = "started_image.png"
output_file_name = start_image_name

detections = None
detector = ObjectDetection()
detector.setModelTypeAsRetinaNet()
detector.setModelPath(os.path.join(exec_path, "resnet50_coco_best_v2.0.1.h5"))
detector.loadModel()

def toFixed(numObj, digits=0):
    return f"{numObj:.{digits}f}"

class mywindow(QtWidgets.QMainWindow):

    __twColumnCount = 2

    def __init__(self):
        super(mywindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        #Персонализируем нашу модель
        self.setWindowFlags(QtCore.Qt.MSWindowsFixedSizeDialogHint)
        self.open_img(start_image_name)
        # Здесь прописываем событие нажатия на кнопку загрузки изображения
        self.ui.pbtnOpenIm.clicked.connect(self.pbtnOpenIm)
        # Здесь прописываем событие нажатия на кнопку распознавания объектов на изображении
        self.ui.pbtnDetectOb.clicked.connect(self.pbtnDetectOb)
        # Инициализация таблицы "название класса" - "вероятность"
        self.ui.twDetectedClasses.setRowCount(0)
        self.ui.twDetectedClasses.setColumnCount(self.__twColumnCount)
        self.ui.twDetectedClasses.setHorizontalHeaderLabels(["Name", "Probability"])
        self.ui.twDetectedClasses.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # Окна справки
        self.ui.actionDetectionable_classes.triggered.connect(self.msbxClassesInfo)
        self.ui.actionDetectionable_classes.setShortcut("Ctrl+D")
        self.ui.actionAbout_program.triggered.connect(self.msbxAboutProgram)
        self.ui.actionAbout_program.setShortcut("Ctrl+A")
        self.ui.actionClose_program.triggered.connect(self.close)
        self.ui.actionClose_program.setShortcut("Ctrl+C")

    def msbxClassesInfo(self):
        QMessageBox.about(self, "Program message", "There are 80 possible objects "
        "that you can detect with the help of this program, and they are as seen below.\n\n"
        "Person, bicycle, car, motorcycle, airplane, bus, train, truck, boat, traffic light,"
        " fire hydrant, stop_sign, parking meter, bench, bird, cat, dog, horse, sheep,"
        " cow, elephant, bear, zebra, giraffe, backpack, umbrella, handbag, tie, suitcase, frisbee,"
        "skis, snowboard, sports ball, kite, baseball bat, baseball glove, skateboard, surfboard, tennis racket, "
        "bottle, wine glass, cup, fork, knife, spoon, bowl, banana, apple, sandwich, orange,"
        " broccoli, carrot, hot dog, pizza, donot, cake, chair, couch, potted plant, bed,"
        " dining table, toilet, tv, laptop, mouse, remote, keyboard, cell phone, microwave,"
        " oven, toaster, sink, refrigerator, book, clock, vase, scissors, teddy bear, hair dryer, toothbrush.")

    def msbxAboutProgram(self):
        QMessageBox.about(self, "Program message", "This program used for Image Object Detection.\n"
        "Here we have the picture at the left side of the window and the table at the right side.\n"
        "When you click on the \"Open image\" button program create a special dialog window for you "
        "where you can choose an image to work with.\nWhen you finally choose your image you can "
        "click on the \"Detect objects\" button to determine what objects are in this picture.\n"
        "Moreover, all information about the detected objects will be loaded into the program table, "
        "so if you don't see the class name of the object or it's probability you can immediately check all necessary information.")

    def open_img(self, file_path):
        self.ui.lblPicture.setPixmap(QPixmap(file_path))

    def getFilePath(self):
        file_path, filetype = QFileDialog.getOpenFileName(self,
                                                "Select your file",
                                                ".",
                                                "JPEG Files(*.jpg);;PNG Files(*.png);;GIF File(*.gif)"
                                                )
        if file_path == filetype:
            return None
        global proceeded_file_path, output_file_name
        proceeded_file_path = file_path
        output_file_name = os.path.basename(file_path)
        return file_path

    def pbtnOpenIm(self):
        file_path = self.getFilePath()
        if file_path != None:
            self.open_img(file_path)
            self.cleanGrid()

    def pbtnDetectOb(self):
        self.cleanGrid()
        global detections
        output_path = os.path.join(output_images_folder_path, output_file_name)
        detections = detector.detectObjectsFromImage(
            input_image=proceeded_file_path,
            output_image_path=output_path,
            input_type="file",
            output_type="file",
            display_percentage_probability=True,
            display_object_name=True,
            minimum_percentage_probability=50
        )
        self.open_img(output_path)
        if not bool(detections):
            rowPosition = self.ui.twDetectedClasses.rowCount()
            self.ui.twDetectedClasses.insertRow(rowPosition)
            self.ui.twDetectedClasses.setItem(0, 0, QTableWidgetItem("None"))
            self.ui.twDetectedClasses.setItem(0, 1, QTableWidgetItem("None"))
        else:
            self.fillGrid(detections)

    def fillGrid(self, detections):
        for eachObject in detections:
            rowPosition = self.ui.twDetectedClasses.rowCount()
            self.ui.twDetectedClasses.insertRow(rowPosition)
            self.ui.twDetectedClasses.setItem(rowPosition, 0, QTableWidgetItem(eachObject["name"]))
            self.ui.twDetectedClasses.setItem(rowPosition, 1, QTableWidgetItem(str(toFixed(eachObject["percentage_probability"],3))))

    def cleanGrid(self):
        self.ui.twDetectedClasses.clear()
        self.ui.twDetectedClasses.setHorizontalHeaderLabels(["Name", "Probability"])
        self.ui.twDetectedClasses.setRowCount(0)

if __name__ == "__main__":
    app = QtWidgets.QApplication([]) #run app
    application = mywindow()
    application.show()
    sys.exit(app.exec())