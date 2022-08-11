from pdfmodify import Ui_Form
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox
import fitz
from PyQt5.QtGui import QImage, QPixmap, QBrush, QPalette
import cv2

class PdfWindow(QtWidgets.QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.doc = None
        self.palette = QPalette()
        self.brush = QBrush(QPixmap("bg.jpg"))
        self.palette.setBrush(QPalette.Background, self.brush)
        self.setPalette(self.palette)
        self.idx = 0

        self.deletList = []
        # self.showPage(self.idx)
        self.pushButton.clicked.connect(self.markPage)
        self.pushButton_2.clicked.connect(self.pgUp)
        self.pushButton_3.clicked.connect(self.pgDn)
        self.pushButton_4.clicked.connect(self.deletPage)
        self.pushButton_5.clicked.connect(self.openPdf)

    def openPdf(self):
        pdf_file =  QFileDialog.getOpenFileName(self, 'Open file', '\\', 'PDF files (*.pdf)')
        try:
            self.doc = fitz.open(pdf_file[0])
            self.length = len(self.doc)
            self.idx = 0
            self.showPage(self.idx)

        except:
            QMessageBox.warning(self, "错误", "打开失败")

    def showPage(self, idx):
        if self.doc:
            page_one = self.doc.load_page(idx)
            # 将第一页转换为Pixmap
            page_pixmap = page_one.getPixmap()
            # 将Pixmap转换为QImage
            image_format = QImage.Format_RGBA8888 if page_pixmap.alpha else QImage.Format_RGB888
            page_image = QImage(page_pixmap.samples, page_pixmap.width,
                                page_pixmap.height, page_pixmap.stride, image_format)

            # QImage 转为QPixmap
            pix = QPixmap.fromImage(page_image)
            self.label_3.setScaledContents(True)
            self.label_3.setPixmap(pix)
            self.label.setText("第 " + str(self.idx + 1) + " 页, 共 " + str(self.length) + " 页")

    def markPage(self):
        if self.doc:
            if self.idx not in self.deletList:
                self.deletList.append(self.idx)
                self.label_2.setText("已标记")
                self.label_2.setStyleSheet("color:red;")
                self.pushButton.setText("取消标记")
            else:
                self.deletList.remove(self.idx)
                self.label_2.setText("未标记")
                self.label_2.setStyleSheet("color:black;")
                self.pushButton.setText("标记")

    def pgUp(self):
        if self.doc:
            if self.idx > 0:
                self.idx -= 1
                self.showPage(self.idx)
                if self.idx in self.deletList:
                    self.label_2.setText("已标记")
                    self.label_2.setStyleSheet("color:red;")
                    self.pushButton.setText("取消标记")
                else:
                    self.label_2.setText("未标记")
                    self.label_2.setStyleSheet("color:black;")
                    self.pushButton.setText("标记")

    def pgDn(self):
        if self.doc:
            if self.idx < self.length-1:
                self.idx += 1
                self.showPage(self.idx)
                if self.idx in self.deletList:
                    self.label_2.setText("已标记")
                    self.label_2.setStyleSheet("color:red;")
                    self.pushButton.setText("取消标记")
                else:
                    self.label_2.setText("未标记")
                    self.label_2.setStyleSheet("color:black;")
                    self.pushButton.setText("标记")

    def deletPage(self):
        if self.doc and self.deletList:
            self.deletList = sorted(self.deletList)
            conform = QMessageBox.critical(self, "确认删除", "确认删除选中页："+",".join([str(i+1) for i in self.deletList])+"?", QMessageBox.Yes|QMessageBox.No, QMessageBox.Yes)

            if conform == QMessageBox.Yes:
                save_file, _ = QFileDialog.getSaveFileName(self, 'Open file', '\\', 'PDF files (*.pdf)')
                lst = self.deletList
                try:
                    self.doc.delete_pages(self.deletList)
                    self.doc.save(save_file)
                    self.length -= len(self.deletList)
                    self.deletList = []
                    self.idx = 0
                    self.showPage(self.idx)
                    self.label_2.setText("未标记")
                    self.label_2.setStyleSheet("color:black;")
                    self.pushButton.setText("标记")
                    QMessageBox.about(self, "成功", "删除成功")

                except:
                    QMessageBox.warning(self, "失败", "删除失败")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = PdfWindow()
    window.show()
    sys.exit(app.exec_())
