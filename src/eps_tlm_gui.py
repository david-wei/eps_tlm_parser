#!/usr/bin/env python3

from eps_tlm_parser import *

import sys, random

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class Status:
	OK = 0
	BUSY = 1

class EpsTlmGuiApp(QWidget):
	"""
	class CMD:
		DEVICE = 0
		SOURCE = 1
		TYPE = 2"""
	DEVICE, SOURCE, TYPE = range(3)

	def __init__(self):
		QWidget.__init__(self)
		
		# Logical Properties
		self.status = Status.OK

		# Plot Data
		self.eps = EpsTlmFileReader()
		self.data = list()

		# General Window Attributes
		self.setWindowTitle("EPS Telemetry Reader")
		self.setGeometry(10, 40, 900, 500)
		self.mainLayout = QHBoxLayout()
		self.setLayout(self.mainLayout)
		self.layout = QVBoxLayout()

		# Data Treeview
		self.dataSelectionTreeview = QTreeView()
		self.dataSelectionTreeview.setRootIsDecorated(False)
		self.dataSelectionTreeview.setAlternatingRowColors(True)
		self.__setupDataSelection()
		self.mainLayout.addWidget(self.dataSelectionTreeview)
		self.mainLayout.addLayout(self.layout)

		# Overall Controls
		self.controlsLayout = QHBoxLayout()
		self.openFileButton = QPushButton()
		self.openFileButton.setText("Open File")
		self.openFolderButton = QPushButton()
		self.openFolderButton.setText("Open Folder")
		self.convertFileButton = QPushButton()
		self.convertFileButton.setText("Convert File")
		self.convertFolderButton = QPushButton()
		self.convertFolderButton.setText("Convert Folder")
		self.controlsLayout.addWidget(self.openFileButton)
		self.controlsLayout.addWidget(self.openFolderButton)
		self.controlsLayout.addWidget(self.convertFileButton)
		self.controlsLayout.addWidget(self.convertFolderButton)
		self.layout.addLayout(self.controlsLayout)

		# Helper Widgets
		self.loadingBar = QProgressBar()
		self.loadingBar.setValue(50)
		self.layout.addWidget(self.loadingBar)

		# Plotting Widgets
		self.plotCanvas = PlotCanvas(self, width = 5, height = 4)
		self.layout.addWidget(self.plotCanvas)
		self.timeSliderStart = QSlider()
		self.timeSliderStart.setOrientation(Qt.Horizontal)
		self.timeSliderEnd = QSlider()
		self.timeSliderEnd.setOrientation(Qt.Horizontal)
		self.timeSliderLayout = QHBoxLayout()
		self.timeSliderLayout.addWidget(self.timeSliderStart)
		self.timeSliderLayout.addWidget(self.timeSliderEnd)
		self.layout.addLayout(self.timeSliderLayout)

		# Initial Visibility
		self.show()

		# Connections
		self.__setupConnections()


	def __setupConnections(self):
		self.openFileButton.clicked.connect(self.openFileDialog)


	def __setupDataSelection(self):
		dataSelectionModel = QStandardItemModel(0, 3, self)
		dataSelectionModel.setHeaderData(self.DEVICE, Qt.Horizontal, "Device")
		dataSelectionModel.setHeaderData(self.SOURCE, Qt.Horizontal, "Source")
		dataSelectionModel.setHeaderData(self.TYPE, Qt.Horizontal, "Type")
		self.dataSelectionTreeview.setModel(dataSelectionModel)
		for cmd in EpsTlmData.VALID_COMMANDS:
			dataSelectionModel.insertRow(0)
			dataSelectionModel.setData(dataSelectionModel.index(0, self.DEVICE), cmd[0].name)
			dataSelectionModel.setData(dataSelectionModel.index(0, self.SOURCE), cmd[1].name)
			dataSelectionModel.setData(dataSelectionModel.index(0, self.TYPE), cmd[2].name)


	def openFileDialog(self):
		fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "", "EPS Files (*.tlm)")
		if fileName:
			self.status = Status.BUSY
			self.eps.deleteData()
			self.eps.setFile(fileName)
			self.eps.readFile()
			self.status = Status.OK





class PlotCanvas(FigureCanvas):

	def __init__(self, parent = None, width = 5, height = 4, dpi = 100):
		fig = Figure()
		self.axes = fig.add_subplot(111)
		FigureCanvas.__init__(self, fig)
		self.setParent(parent)

		FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)
		self.plot()

	def plot(self):
		data = [random.random() for i in range(25)]
		ax = self.figure.add_subplot(111)
		ax.plot(data, "r-")
		ax.set_title("Matplotlib Example")
		self.draw()







if __name__ == "__main__":
	print("EPS Telemetry Reader GUI Application")
	app = QApplication(sys.argv)
	ex = EpsTlmGuiApp()
	sys.exit(app.exec_())
