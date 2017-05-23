#!/usr/bin/env python3

from eps_tlm_parser import *

import sys

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
		self.lastDirectory = ""

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
		self.dataSelectionTreeview.setMaximumWidth(350)
		self.mainLayout.addWidget(self.dataSelectionTreeview)
		self.mainLayout.addLayout(self.layout)

		# Overall Controls
		self.controlsLayout = QHBoxLayout()
		self.openFilesButton = QPushButton("Open Files")
		self.saveDataButton = QPushButton("Save Data")
		self.convertFilesButton = QPushButton("Convert Files")
		self.resetDataButton = QPushButton("Reset Data")
		self.controlsLayout.addWidget(self.openFilesButton)
		self.controlsLayout.addWidget(self.saveDataButton)
		self.controlsLayout.addWidget(self.convertFilesButton)
		self.controlsLayout.addWidget(self.resetDataButton)
		self.layout.addLayout(self.controlsLayout)

		# Helper Widgets
		self.loadingBar = QProgressBar()
		self.loadingBar.setValue(50)
		self.layout.addWidget(self.loadingBar)

		# Plotting Widgets
		self.plotCanvas = PlotCanvas(self)
		self.layout.addWidget(self.plotCanvas)
		self.timeSliderStart = QSlider()
		self.timeSliderStart.setOrientation(Qt.Horizontal)
		self.timeSliderEnd = QSlider()
		self.timeSliderEnd.setOrientation(Qt.Horizontal)
		self.timeSliderEnd.setValue(100)
		self.timeSliderLayout = QHBoxLayout()
		self.timeSliderLayout.addWidget(self.timeSliderStart)
		self.timeSliderLayout.addWidget(self.timeSliderEnd)
		self.layout.addLayout(self.timeSliderLayout)

		# Initial Visibility
		self.show()

		# Connections
		self.__setupConnections()


	def __setupConnections(self):
		self.openFilesButton.clicked.connect(self.openFilesDialog)
		self.saveDataButton.clicked.connect(self.saveDataDialog)
		self.convertFilesButton.clicked.connect(self.convertFilesDialog)
		self.resetDataButton.clicked.connect(self.resetDataDialog)

		self.dataSelectionTreeview.selectionModel().selectionChanged.connect(self.updateDataSelection)


	def __setupDataSelection(self):
		dataSelectionModel = QStandardItemModel(0, 3, self)
		dataSelectionModel.setHeaderData(self.DEVICE, Qt.Horizontal, "Device")
		dataSelectionModel.setHeaderData(self.SOURCE, Qt.Horizontal, "Source")
		dataSelectionModel.setHeaderData(self.TYPE, Qt.Horizontal, "Type")
		self.dataSelectionTreeview.setModel(dataSelectionModel)
		for cmd in EpsTlmData.VALID_COMMANDS:
			"""dataSelectionModel.insertRow(0)
			dataSelectionModel.setData(dataSelectionModel.index(0, self.DEVICE), cmd[0].name)
			dataSelectionModel.setData(dataSelectionModel.index(0, self.SOURCE), cmd[1].name)
			dataSelectionModel.setData(dataSelectionModel.index(0, self.TYPE), cmd[2].name)"""
			dataSelectionModel.appendRow([
				QStandardItem(cmd[0].name),
				QStandardItem(cmd[1].name),
				QStandardItem(cmd[2].name)
				])

	@pyqtSlot()
	def openFilesDialog(self):
		fileNames, _ = QFileDialog().getOpenFileNames(self, "Load files", self.lastDirectory, "EPS Files (*.tlm)")
		if fileNames and self.status == Status.OK:
			self.status = Status.BUSY
			self.lastDirectory = os.path.dirname(fileNames[0])
			self.eps.setFile(fileNames)
			self.eps.readFileList()
			self.eps.sortAllData()
			self.status = Status.OK

	@pyqtSlot()
	def convertFilesDialog(self):
		fileNames, _ = QFileDialog().getOpenFileNames(self, "Convert files", self.lastDirectory, "EPS Files (*.tlm)")
		if fileNames and self.status == Status.OK:
			self.status = Status.BUSY
			self.lastDirectory = os.path.dirname(fileNames[0])
			tmpEps = EpsTlmFileReader(mode = "o")
			tmpEps.setFile(fileNames)
			tmpEps.readFileList()
			self.status = Status.OK

	@pyqtSlot()
	def saveDataDialog(self):
		fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", self.lastDirectory, "Comma Separated Value Files (*.csv)")
		if fileName and self.status == Status.OK:
			self.status = Status.BUSY
			self.lastDirectory = os.path.dirname(fileName)
			self.eps.writeAllDataToFile(fileName)
			self.status = Status.OK

	@pyqtSlot()
	def resetDataDialog(self):
		reply = QMessageBox.question(self, "Reset Data", "Are you sure you want to reset the data?", QMessageBox.Yes, QMessageBox.No)
		if reply == QMessageBox.Yes:
			self.eps.deleteData()

	def getSelectedCmd(self):
		return self.plotCanvas.cmd


	@pyqtSlot(QItemSelection, QItemSelection)
	def updateDataSelection(self, selected, deselected):
		index = selected.indexes()[0].row()
		cmd = EpsTlmData.VALID_COMMANDS[index]
		if self.plotCanvas.setData(cmd, self.eps.data[cmd]):
			self.plotCanvas.plot()


class PlotCanvas(FigureCanvas):

	def __init__(self, parent = None):
		fig = Figure(facecolor = "None", edgecolor = "None")
		FigureCanvas.__init__(self, fig)
		FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)

		self.axes = self.figure.add_subplot(111)
		self.axes.axis("off")
		#self.axes.set_facecolor("None")

	def setData(self, cmd, data):
		if len(data) == 0:
			return False
		self.cmd = cmd
		self.pltdata = list(zip(*data))
		return True

	def plot(self):
		self.axes.cla()
		self.axes.plot(self.pltdata[0], self.pltdata[1], "b-", markersize = 2)
		self.axes.set_xlabel("Time")
		self.axes.set_ylabel(str(self.cmd[2].name) + " [" + EpsTlmData.TYPE.physicalUnit(self.cmd[2]) + "]")
		self.axes.legend([str(self.cmd[1].name)])
		self.draw()







if __name__ == "__main__":
	print("EPS Telemetry Reader GUI Application")
	app = QApplication(sys.argv)
	ex = EpsTlmGuiApp()
	sys.exit(app.exec_())
