import cv2
import numpy as np
import qrcode as qrc
import sys

from matplotlib import pyplot as plt
from PyQt5 import QtCore, QtGui, QtWidgets
from skimage.io._plugins.pil_plugin import pil_to_ndarray
from cryptography.fernet import Fernet

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(390, 130)
        MainWindow.setMinimumSize(QtCore.QSize(390, 130))
        MainWindow.setMaximumSize(QtCore.QSize(390, 130))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 50, 211, 21))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(220, 50, 51, 21))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.lineEdit.setFont(font)
        self.lineEdit.setText("")
        self.lineEdit.setObjectName("lineEdit")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(10, 10, 381, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(10, 90, 100, 35))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.button_click_1)
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(140, 90, 100, 35))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(self.button_click_2)
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(270, 90, 100, 35))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pushButton_3.setFont(font)
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.clicked.connect(self.button_click_3)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Программа"))
        self.label.setText(_translate("MainWindow", "Введите номер класса:"))
        self.label_2.setText(_translate("MainWindow", "Генерация зашифрованных QR-кодов"))
        self.pushButton.setText(_translate("MainWindow", "Сгенерировать"))
        self.pushButton_2.setText(_translate("MainWindow", "Разложить"))
        self.pushButton_3.setText(_translate("MainWindow", "Расшифровать"))
    
    def button_click_1(self):
        self.qr = QR(self.lineEdit.text())
        self.qr.show_result_1()

    def button_click_2(self):
        self.qr.show_result_2()
        
    def button_click_3(self):
        self.qr.show_result_3()
        
class Image():
    def __init__(self, i, tp):
        self.tp = tp
        self.image = cv2.imread(f'cuhk\photos\{i}.jpg')
        self.image_gray = cv2.imread(f'cuhk\photos\{i}.jpg', 0)
        
    def get_image(self):
        if self.tp == 'normal':
            return self.image[25:225, 0:200]
        
        elif self.tp == 'gray':
            return self.image_gray[25:225, 0:200]
        elif self.tp == 'index':
            return self.i
    
class QR():
    def __init__(self, i):
        self.i = i
        self.image = Image(self.i, 'normal').get_image()
        self.image_gray = Image(self.i, 'gray').get_image()
        self.r, self.g, self.b = cv2.split(self.image)
        self.key = Fernet.generate_key()
        self.data_1 = self.encrypt(self.info_1(), self.key)
        self.data_2 = self.encrypt(self.info_2(), self.key)
        self.data_3 = self.encrypt(self.info_3(), self.key)
    
    def generate(self, data):
        qr = qrc.QRCode(version=1,
                           error_correction=qrc.constants.ERROR_CORRECT_L,
                           box_size=5, border=0)
        qr.add_data(data)
        qr.make(fit=True)
        
        image = qr.make_image(fill_color="black", back_color="white")
        
        return image.resize((200, 200))
    
    def info_1(self):
        text = 'CUHK Face Sketch Database (CUFS)'     
        
        return text
    
    def info_2(self):
        text = f'Class index = {self.i}'     
        
        return text
    
    def info_3(self):
        text = 'http://mmlab.ie.cuhk.edu.hk/archive/facesketch.html'        
        
        return text
    
    def lsb(self):
        qr_1 = pil_to_ndarray(self.generate(self.data_1))
        qr_2 = pil_to_ndarray(self.generate(self.data_2))
        qr_3 = pil_to_ndarray(self.generate(self.data_3))
        
        lsb_antro = np.mod(qr_1, 2)
        lsb_pheno = np.mod(qr_2, 2)
        lsb_info = np.mod(qr_3, 2)
        
        r_qr = self.r - np.mod(self.r, 2) + lsb_antro
        g_qr = self.g - np.mod(self.g, 2) + lsb_pheno
        b_qr = self.b - np.mod(self.b, 2) + lsb_info

        return r_qr, g_qr, b_qr
    
    def cov_binary(self, num):
        binary_num = [int(i) for i in list('{0:0b}'.format(num))]
        for j in range(8 - len(binary_num)):
            binary_num.insert(0,0)        
        return binary_num
    
    def conv_decimal(self, arr):
        x = 0
        for i in range(8):
            x = x + int(arr[i])*(2**(7-i))
        return x
    
    def discriminate_bit(self, bit, image):
        z = np.zeros([200,200])
        for i in range(200):
            for j in range(200):
                x = self.cov_binary(image[i][j])
                for k in range(8):
                    if k == bit:
                        x[k] = x[k]
                    else:
                        x[k] = 0
                x1 = self.conv_decimal(x)
                z[i][j] = x1
        return z
    
    def encrypt(self, data, key):
        f = Fernet(key)
        encrypted_data = f.encrypt(str(data).encode())
        
        return encrypted_data

    def decrypt(self, encrypted_data, key):
        f = Fernet(key)
        decrypted_data = f.decrypt(encrypted_data)
        
        return decrypted_data.decode()

    def show_result_1(self):
        fig = plt.figure('Генерация', figsize=(16, 8))

        ax1 = fig.add_subplot(3, 3, 4)
        ax2 = fig.add_subplot(3, 3, 2)
        ax3 = fig.add_subplot(3, 3, 5)
        ax4 = fig.add_subplot(3, 3, 8)
        ax6 = fig.add_subplot(3, 3, 6)

        ax1.imshow(cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB))
        ax1.axis("off")
        ax1.set_title('Фотография')
        
        ax2.imshow(self.generate(self.data_1))
        ax2.axis("off")
        ax2.set_title('INFO 1 (R)')

        ax3.imshow(self.generate(self.data_2))
        ax3.axis("off")
        ax3.set_title('INFO 2 (G)')

        ax4.imshow(self.generate(self.data_3))
        ax4.axis("off")
        ax4.set_title('INFO 3 (B)')

        ax6.imshow(cv2.cvtColor(cv2.merge((self.lsb())), cv2.COLOR_BGR2RGB))
        ax6.axis("off")
        ax6.set_title('Результат')

        plt.subplots_adjust(wspace=0.5, hspace=0.3,
                            top=0.95, bottom=0.05,
                            left=0.05, right=0.95)
        plt.show()
        
    def show_result_2(self):
        fig = plt.figure('Разложение', figsize=(20, 10))
        
        r_qr, g_qr, b_qr = self.lsb()
        
        for i in range(1, 9):
            ax = fig.add_subplot(3, 8, i)
            ax.imshow(self.discriminate_bit(i - 1, r_qr), cmap='Reds_r')
            ax.axis('off')
        
        for i in range(9, 17):
            ax = fig.add_subplot(3, 8, i)
            ax.imshow(self.discriminate_bit(i - 9, g_qr), cmap='Greens_r')
            ax.axis('off')
            
        for i in range(17, 25):
            ax = fig.add_subplot(3, 8, i)
            ax.imshow(self.discriminate_bit(i - 17, b_qr), cmap='Blues_r')
            ax.axis('off')
            
        plt.subplots_adjust(wspace=0.1, hspace=0.1,
                            top=0.95, bottom=0.05,
                            left=0.05, right=0.95)
    
    def show_result_3(self):
        fig = plt.figure('Расшифрока', figsize=(16, 8))

        ax1 = fig.add_subplot(3, 3, 1)
        ax2 = fig.add_subplot(3, 3, 4)
        ax3 = fig.add_subplot(3, 3, 7)
        ax4 = fig.add_subplot(3, 3, 2)
        ax5 = fig.add_subplot(3, 3, 5)
        ax6 = fig.add_subplot(3, 3, 8)
        ax7 = fig.add_subplot(3, 3, 3)
        ax8 = fig.add_subplot(3, 3, 6)
        ax9 = fig.add_subplot(3, 3, 9)
        
        ax1.imshow(self.generate(self.data_1))
        ax1.axis("off")
        ax1.set_title('ENCRYPT INFO 1')

        ax2.imshow(self.generate(self.data_2))
        ax2.axis("off")
        ax2.set_title('ENCRYPT INFO 2')

        ax3.imshow(self.generate(self.data_3))
        ax3.axis("off")
        ax3.set_title('ENCRYPT INFO 3')
        
        ax4.imshow(self.generate(self.decrypt(self.data_1, self.key)))
        ax4.axis("off")
        ax4.set_title('DECRYPT INFO 1')

        ax5.imshow(self.generate(self.decrypt(self.data_2, self.key)))
        ax5.axis("off")
        ax5.set_title('DECRYPT INFO 2')

        ax6.imshow(self.generate(self.decrypt(self.data_3, self.key)))
        ax6.axis("off")
        ax6.set_title('DECRYPT INFO 3')

        ax7.text(-0.1, 0.35, self.decrypt(self.data_1, self.key))
        ax7.axis("off")
        
        ax8.text(-0.1, 0.35, self.decrypt(self.data_2, self.key))
        ax8.axis("off")
        
        ax9.text(-0.1, 0.35, self.decrypt(self.data_3, self.key))
        ax9.axis("off")

        plt.subplots_adjust(wspace=0.5, hspace=0.3,
                            top=0.95, bottom=0.05,
                            left=0.05, right=0.95)
        plt.show()

app = QtWidgets.QApplication(sys.argv)
MainWindow = QtWidgets.QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(MainWindow)
MainWindow.show()
sys.exit(app.exec_())