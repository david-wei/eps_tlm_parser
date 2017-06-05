#!/usr/bin/env python3

from eps_tlm_parser import *

import sys
import argparse

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class Status:
	OK = 0
	BUSY = 1


	
# ##############################
# PyQt5 Widget
# ##############################

class EpsTlmGuiApp(QWidget):
	DEVICE, SOURCE, TYPE = range(3)

	def __init__(self):
		QWidget.__init__(self)
		
		# Logical Properties
		self.status = Status.OK
		self.lastDirectory = ""

		# Plot Data
		self.eps = EpsTlmFileReader()
		self.eps.setProgressCallback(self.updateLoadingBar)
		self.data = list()

		# General Window Attributes
		self.setWindowTitle("EPS Telemetry Reader")
		self.setGeometry(10, 40, 1600, 900)
		self.mainLayout = QHBoxLayout()
		self.setLayout(self.mainLayout)
		self.layout = QVBoxLayout()

		# Data Treeview
		self.__setupDerivedData()
		self.dataSelectionTreeview = QTreeView()
		self.dataSelectionTreeview.setRootIsDecorated(False)
		self.dataSelectionTreeview.setAlternatingRowColors(True)
		self.__setupDataSelection()
		self.dataSelectionTreeview.setMaximumWidth(270)
		self.dataSelectionTreeview.setMinimumWidth(240)
		self.mainLayout.addWidget(self.dataSelectionTreeview)
		self.mainLayout.addLayout(self.layout)

		# Overall Controls
		self.controlsLayout = QHBoxLayout()
		self.openFilesButton = QPushButton("Open Files")
		self.openFilesButton.setToolTip("Loads EPS telemetry files, so their data content can be displayed.")
		self.saveDataButton = QPushButton("Save Data")
		self.saveDataButton .setToolTip("Saves the currently loaded data into a CSV file.")
		self.convertFilesButton = QPushButton("Convert Files")
		self.convertFilesButton.setToolTip("Opens a dialog in which TLM files can be chosen to be converted into CSV files.")
		self.resetDataButton = QPushButton("Reset Data")
		self.resetDataButton.setToolTip("Removes all currently loaded data.")
		self.controlsLayout.addWidget(self.openFilesButton)
		self.controlsLayout.addWidget(self.saveDataButton)
		self.controlsLayout.addWidget(self.convertFilesButton)
		self.controlsLayout.addWidget(self.resetDataButton)
		self.layout.addLayout(self.controlsLayout)

		# Helper Widgets
		self.loadingBar = QProgressBar()
		self.loadingBar.setValue(50)
		self.loadingBar.setTextVisible(True)
		self.layout.addWidget(self.loadingBar)

		# Plotting Widgets
		self.plotCanvas = PlotCanvas(self)
		self.layout.addWidget(self.plotCanvas)
		self.timeSliderStart = QSlider()
		self.timeSliderStart.setOrientation(Qt.Horizontal)
		self.timeSliderEnd = QSlider()
		self.timeSliderEnd.setOrientation(Qt.Horizontal)
		self.timeTextStart = QLabel()
		self.timeTextEnd = QLabel()
		self.resetTimeSliders()
		self.timeSeparation = QFrame()
		self.timeSeparation.setFrameShape(QFrame.VLine)
		self.timeLayout = QHBoxLayout()
		self.timeLayout.addWidget(self.timeSliderStart)
		self.timeLayout.addWidget(self.timeTextStart)
		self.timeLayout.addWidget(self.timeSeparation)
		self.timeLayout.addWidget(self.timeTextEnd)
		self.timeLayout.addWidget(self.timeSliderEnd)
		self.layout.addLayout(self.timeLayout)

		# Initial Visibility
		self.loadingBar.setVisible(False)
		self.show()

		# Connections
		self.__setupConnections()


	# ++++++++++++++++++++++++++++++
	# Setup
	# ++++++++++++++++++++++++++++++

	def __setupConnections(self):
		self.openFilesButton.clicked.connect(self.openFilesDialog)
		self.saveDataButton.clicked.connect(self.saveDataDialog)
		self.convertFilesButton.clicked.connect(self.convertFilesDialog)
		self.resetDataButton.clicked.connect(self.resetDataDialog)

		self.dataSelectionTreeview.selectionModel().selectionChanged.connect(self.updateDataSelection)
		self.timeSliderStart.valueChanged.connect(self.updateTimeStart)
		self.timeSliderEnd.valueChanged.connect(self.updateTimeEnd)


	def __setupDerivedData(self):
		EpsTlmData.VALID_COMMANDS.insert(2, (EpsTlmData.DEVICE.DER, EpsTlmData.SOURCE.BCR1, EpsTlmData.TYPE.POWER))
		EpsTlmData.VALID_COMMANDS.insert(5, (EpsTlmData.DEVICE.DER, EpsTlmData.SOURCE.BCR2, EpsTlmData.TYPE.POWER))
		EpsTlmData.VALID_COMMANDS.insert(8, (EpsTlmData.DEVICE.DER, EpsTlmData.SOURCE.BCR3, EpsTlmData.TYPE.POWER))
		EpsTlmData.VALID_COMMANDS.insert(10, (EpsTlmData.DEVICE.DER, EpsTlmData.SOURCE.BCR3, EpsTlmData.TYPE.POWERB))
		self.eps.data[(EpsTlmData.DEVICE.DER, EpsTlmData.SOURCE.BCR1, EpsTlmData.TYPE.POWER)] = list()
		self.eps.data[(EpsTlmData.DEVICE.DER, EpsTlmData.SOURCE.BCR2, EpsTlmData.TYPE.POWER)] = list()
		self.eps.data[(EpsTlmData.DEVICE.DER, EpsTlmData.SOURCE.BCR3, EpsTlmData.TYPE.POWER)] = list()
		self.eps.data[(EpsTlmData.DEVICE.DER, EpsTlmData.SOURCE.BCR3, EpsTlmData.TYPE.POWERB)] = list()


	def __setupDataSelection(self):
		dataSelectionModel = QStandardItemModel(0, 3, self)
		dataSelectionModel.setHeaderData(self.DEVICE, Qt.Horizontal, "Device")
		dataSelectionModel.setHeaderData(self.SOURCE, Qt.Horizontal, "Source")
		dataSelectionModel.setHeaderData(self.TYPE, Qt.Horizontal, "Type")
		
		self.dataSelectionTreeview.setModel(dataSelectionModel)
		for i in range(3):
			self.dataSelectionTreeview.header().setSectionResizeMode(i, QHeaderView.ResizeToContents)

		for cmd in EpsTlmData.VALID_COMMANDS:
			dataSelectionModel.appendRow([
				QStandardItem(cmd[0].name),
				QStandardItem(cmd[1].name),
				QStandardItem(cmd[2].name)
				])

	def updateLoadingBar(self, progress):
		self.loadingBar.setValue(progress * 100)

		
	# ++++++++++++++++++++++++++++++
	# Dialogs
	# ++++++++++++++++++++++++++++++

	@pyqtSlot()
	def openFilesDialog(self):
		fileNames, _ = QFileDialog().getOpenFileNames(self, "Load files", self.lastDirectory, "EPS Files (*.tlm)")
		if fileNames and self.status == Status.OK:
			self.status = Status.BUSY
			self.lastDirectory = os.path.dirname(fileNames[0])
			self.loadingBar.setFormat(" Loading files: %p%")
			self.loadingBar.setVisible(True)
			self.eps.setFile(fileNames)
			self.eps.readFileList()
			self.eps.sortAllData()
			self.loadingBar.setFormat(" Calculating derived data: %p%")
			self.calculateDerivedData()
			self.loadingBar.setVisible(False)
			self.status = Status.OK

	@pyqtSlot()
	def convertFilesDialog(self):
		fileNames, _ = QFileDialog().getOpenFileNames(self, "Convert files", self.lastDirectory, "EPS Files (*.tlm)")
		if fileNames and self.status == Status.OK:
			self.status = Status.BUSY
			self.lastDirectory = os.path.dirname(fileNames[0])
			self.loadingBar.setFormat(" Converting files: %p%")
			self.loadingBar.setVisible(True)
			tmpEps = EpsTlmFileReader(mode = "o")
			tmpEps.setProgressCallback(self.updateLoadingBar)
			tmpEps.setFile(fileNames)
			tmpEps.readFileList()
			self.loadingBar.setVisible(False)
			self.status = Status.OK

	@pyqtSlot()
	def saveDataDialog(self):
		fileName, _ = QFileDialog.getSaveFileName(self, "Save data", self.lastDirectory, "Comma Separated Value Files (*.csv)")
		if fileName and self.status == Status.OK:
			self.status = Status.BUSY
			self.lastDirectory = os.path.dirname(fileName)
			self.loadingBar.setFormat("Saving data: %p%")
			self.loadingBar.setVisible(True)
			self.eps.writeAllDataToFile(fileName)
			self.loadingBar.setVisible(False)
			self.status = Status.OK

	@pyqtSlot()
	def resetDataDialog(self):
		reply = QMessageBox.question(self, "Reset Data", "Are you sure you want to reset the data?", QMessageBox.Yes, QMessageBox.No)
		if reply == QMessageBox.Yes:
			self.eps.deleteAllData()
			self.resetTimeSliders()
			

	# ++++++++++++++++++++++++++++++
	# Data Calculation
	# ++++++++++++++++++++++++++++++

	def calculateDerivedData(self):
		progressSteps = 4 + 3 + 4	# 4x BCR, (2+1)x BATV, (3+1)x 5V
		progress = 0.0
		self.updateLoadingBar(progress / progressSteps)

		# BCR
		self.eps.deleteData((EpsTlmData.DEVICE.DER, EpsTlmData.SOURCE.BCR1, EpsTlmData.TYPE.POWER))
		self.eps.calculateDerivedData(operator.mul,
					(EpsTlmData.DEVICE.DER, EpsTlmData.SOURCE.BCR1, EpsTlmData.TYPE.POWER),
					(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.BCR1, EpsTlmData.TYPE.VOLTAGE),
					(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.BCR1, EpsTlmData.TYPE.CURRENT))
		progress += 1
		self.updateLoadingBar(progress / progressSteps)
		self.eps.deleteData((EpsTlmData.DEVICE.DER, EpsTlmData.SOURCE.BCR2, EpsTlmData.TYPE.POWER))
		self.eps.calculateDerivedData(operator.mul,
					(EpsTlmData.DEVICE.DER, EpsTlmData.SOURCE.BCR2, EpsTlmData.TYPE.POWER),
					(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.BCR2, EpsTlmData.TYPE.VOLTAGE),
					(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.BCR2, EpsTlmData.TYPE.CURRENT))
		progress += 1
		self.updateLoadingBar(progress / progressSteps)
		self.eps.deleteData((EpsTlmData.DEVICE.DER, EpsTlmData.SOURCE.BCR3, EpsTlmData.TYPE.POWER))
		self.eps.calculateDerivedData(operator.mul,
					(EpsTlmData.DEVICE.DER, EpsTlmData.SOURCE.BCR3, EpsTlmData.TYPE.POWER),
					(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.BCR3, EpsTlmData.TYPE.VOLTAGE),
					(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.BCR3, EpsTlmData.TYPE.CURRENT))
		progress += 1
		self.updateLoadingBar(progress / progressSteps)
		self.eps.deleteData((EpsTlmData.DEVICE.DER, EpsTlmData.SOURCE.BCR3, EpsTlmData.TYPE.POWERB))
		self.eps.calculateDerivedData(operator.mul,
					(EpsTlmData.DEVICE.DER, EpsTlmData.SOURCE.BCR3, EpsTlmData.TYPE.POWERB),
					(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.BCR3, EpsTlmData.TYPE.VOLTAGE),
					(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.BCR3, EpsTlmData.TYPE.CURRENTB))
		progress += 1
		self.updateLoadingBar(progress / progressSteps)

		# BATV
		self.eps.deleteData((EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.UHF, EpsTlmData.TYPE.VOLTAGE))
		self.eps.data[(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.UHF, EpsTlmData.TYPE.VOLTAGE)] = self.eps.data[(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.PCMBATV, EpsTlmData.TYPE.VOLTAGE)]
		progress += 1
		self.updateLoadingBar(progress / progressSteps)
		self.eps.deleteTmpData()
		self.eps.calculateDerivedData(operator.add,
					(EpsTlmData.DEVICE.TMP, EpsTlmData.SOURCE.TMP, EpsTlmData.TYPE.TMP),
					(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.SMARD1, EpsTlmData.TYPE.CURRENT),
					(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.SMARD2, EpsTlmData.TYPE.CURRENT),
					checkValidity = False)
		progress += 1
		self.updateLoadingBar(progress / progressSteps)
		self.eps.deleteData((EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.UHF, EpsTlmData.TYPE.CURRENT))
		self.eps.calculateDerivedData(operator.sub,
					(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.UHF, EpsTlmData.TYPE.CURRENT),
					(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.PCMBATV, EpsTlmData.TYPE.CURRENT),
					(EpsTlmData.DEVICE.TMP, EpsTlmData.SOURCE.TMP, EpsTlmData.TYPE.TMP),
					checkValidity = False)
		progress += 1
		self.updateLoadingBar(progress / progressSteps)

		# 5V
		self.eps.deleteData((EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.CDH, EpsTlmData.TYPE.VOLTAGE))
		self.eps.data[(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.CDH, EpsTlmData.TYPE.VOLTAGE)] = self.eps.data[(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.PCM5V, EpsTlmData.TYPE.VOLTAGE)]
		progress += 1
		self.updateLoadingBar(progress / progressSteps)
		self.eps.deleteTmpData()
		self.eps.calculateDerivedData(operator.add,
					(EpsTlmData.DEVICE.TMP, EpsTlmData.SOURCE.TMP, EpsTlmData.TYPE.TMP),
					(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.ADCS5V_1, EpsTlmData.TYPE.CURRENT),
					(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.ADCS5V_2, EpsTlmData.TYPE.CURRENT),
					checkValidity = False)
		progress += 1
		self.updateLoadingBar(progress / progressSteps)
		self.eps.calculateDerivedData(operator.add,
					(EpsTlmData.DEVICE.TMP, EpsTlmData.SOURCE.TMP, EpsTlmData.TYPE.TMP_2),
					(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.THM, EpsTlmData.TYPE.CURRENT),
					(EpsTlmData.DEVICE.TMP, EpsTlmData.SOURCE.TMP, EpsTlmData.TYPE.TMP),
					checkValidity = False)
		progress += 1
		self.updateLoadingBar(progress / progressSteps)
		self.eps.deleteData((EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.CDH, EpsTlmData.TYPE.CURRENT))
		self.eps.calculateDerivedData(operator.sub,
					(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.CDH, EpsTlmData.TYPE.CURRENT),
					(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.PCM5V, EpsTlmData.TYPE.CURRENT),
					(EpsTlmData.DEVICE.TMP, EpsTlmData.SOURCE.TMP, EpsTlmData.TYPE.TMP_2),
					checkValidity = False)
		progress += 1
		self.updateLoadingBar(progress / progressSteps)


	# ++++++++++++++++++++++++++++++
	# Data Selection
	# ++++++++++++++++++++++++++++++

	def getSelectedCmd(self):
		return self.plotCanvas.cmd


	@pyqtSlot(QItemSelection, QItemSelection)
	def updateDataSelection(self, selected, deselected):
		index = selected.indexes()[0].row()
		cmd = EpsTlmData.VALID_COMMANDS[index]
		
		if self.plotCanvas.setData(cmd, self.eps.data[cmd]):
			if len(self.eps.data[cmd]) > 0:
				self.timeSliderStart.setRange(0, len(self.eps.data[cmd]) - 1)
				self.timeSliderEnd.setRange(0, len(self.eps.data[cmd]) - 1)
				self.timeSliderStart.setValue(0)
				self.timeSliderEnd.setValue(len(self.eps.data[cmd]) - 1)
				self.timeTextStart.setText(self.eps.data[self.getSelectedCmd()][0][0].strftime("%d/%m/%y\n%H:%M:%S"))
				self.timeTextEnd.setText(self.eps.data[self.getSelectedCmd()][len(self.eps.data[cmd]) - 1][0].strftime("%d/%m/%y\n%H:%M:%S"))
				self.plotCanvas.plot()

			
	# ++++++++++++++++++++++++++++++
	# Timeline
	# ++++++++++++++++++++++++++++++

	@pyqtSlot(int)
	def updateTimeStart(self, newIndex):
		if len(self.eps.data[self.getSelectedCmd()]) == 0:
			self.timeTextStart.setText("No data\navailable")
			self.timeSliderEnd.setRange(0, 0)
		else:
			self.timeTextStart.setText(self.eps.data[self.getSelectedCmd()][newIndex][0].strftime("%d/%m/%y\n%H:%M:%S"))
			self.timeSliderEnd.setMinimum(newIndex)
			self.plotCanvas.plot(leftIndex = self.timeSliderStart.value(), rightIndex = self.timeSliderEnd.value())
		
	@pyqtSlot(int)
	def updateTimeEnd(self, newIndex):
		if len(self.eps.data[self.getSelectedCmd()]) == 0:
			self.timeTextStart.setText("No data\navailable")
			self.timeSliderStart.setRange(0, 0)
		else:
			self.timeTextEnd.setText(self.eps.data[self.getSelectedCmd()][newIndex][0].strftime("%d/%m/%y\n%H:%M:%S"))
			self.timeSliderStart.setMaximum(newIndex)
			self.plotCanvas.plot(leftIndex = self.timeSliderStart.value(), rightIndex = self.timeSliderEnd.value())

	def resetTimeSliders(self):
		self.timeSliderStart.setRange(0, 0)
		self.timeTextStart.setText("No data\navailable")
		self.timeSliderEnd.setRange(0, 0)
		self.timeTextEnd.setText("No data\navailable")


# ##############################
# Matplotlib Canvas
# ##############################

class PlotCanvas(FigureCanvas):

	def __init__(self, parent = None):
		fig = Figure(facecolor = "None", edgecolor = "None")
		FigureCanvas.__init__(self, fig)
		FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)

		self.cmd = EpsTlmData.VALID_COMMANDS[0]		# some arbitrary init cmd
		self.data = list()
		self.axes = self.figure.add_subplot(111)
		self.axes.axis("off")
		#self.axes.set_facecolor("None")

	def setData(self, cmd, data):
		if len(data) == 0:
			return False
		self.cmd = cmd
		self.data = data
		return True

	def plot(self, leftIndex = None, rightIndex = None):
		self.pltdata = list(zip(*(self.data[leftIndex:rightIndex])))
		if len(self.pltdata) == 0:
			return

		self.axes.cla()
		self.axes.plot(self.pltdata[0], self.pltdata[1], "b-", markersize = 2)
		self.axes.set_xlabel("Time")
		self.axes.set_ylabel(str(self.cmd[2].name) + " [" + EpsTlmData.TYPE.physicalUnit(self.cmd[2]) + "]")
		self.axes.legend([str(self.cmd[1].name)])
		self.draw()


# ##############################
# Main
# ##############################

if __name__ == "__main__":
	print("EPS Telemetry Reader GUI Application")
	parser = argparse.ArgumentParser()
	parser.add_argument("file", nargs = "?")
	args = parser.parse_args()
	filename = args.file
	
	app = QApplication(sys.argv)
	wnd = EpsTlmGuiApp()

	if filename:
		wnd.eps.setFile(filename)
		if not wnd.eps.readFile():
			print("File " + filename + " could not be read")

	sys.exit(app.exec_())
