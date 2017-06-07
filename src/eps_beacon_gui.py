#!/usr/bin/env python3

import enum
import struct
import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


# ##############################
# Beacon Parser
# ##############################

class EpsBeaconData:

	class CUR(enum.Enum):
		UHF =		0
		CDH =		1
		SBAND =		2
		SMARD1 =	3
		SMARD2 =	4
		PL =		5
		ADCS5V_1 =	6
		ADCS5V_2 =	7
		THM =		8
		ADCS3V3_1 =	9
		ADCS3V3_2 =	10
		BAT =		11
		BCR1 =		12
		BCR2 =		13
		BCR3A =		14
		BCR3B =		15
		def datatype():
			return "h"	# int16
		def bytecount():
			return 2
		def unit():
			return "mA"

	class RES(enum.Enum):
		MAN	=	0
		SW =	1
		BRW =	2
		def datatype():
			return "b"	# uint8
		def bytecount():
			return 1
		def unit():
			return "1"

	class VOL(enum.Enum):
		BAT =	0
		BCR1 =	1
		BCR2 =	2
		BCR3 =	3
		def datatype():
			return "h"	# int16
		def bytecount():
			return 2
		def unit():
			return "mV"

	def __init__(self):
		self.rawBeacon = list()
		self.beaconSize = len(EpsBeaconData.CUR) + len(EpsBeaconData.RES) + len(EpsBeaconData.VOL)
		self.byteSize = len(EpsBeaconData.CUR) * EpsBeaconData.CUR.bytecount() + \
						len(EpsBeaconData.RES) * EpsBeaconData.RES.bytecount() + \
						len(EpsBeaconData.VOL) * EpsBeaconData.VOL.bytecount()
		self.data = [0] * self.beaconSize

	def __str__(self):
		tmp = "Currents"
		ret = "\n" + tmp + "\n"
		for i in range(len(tmp)): ret += "="
		for cur in EpsBeaconData.CUR:
			ret += ("\n {:9s} | {:6d} | {:2s}").format(cur.name,
						self.data[cur.value],
						EpsBeaconData.CUR.unit())
		tmp = "Resets"
		ret += "\n\n" + tmp + "\n"
		for i in range(len(tmp)): ret += "="
		for res in EpsBeaconData.RES:
			ret += ("\n {:9s} | {:6d} | {:2s}").format(res.name,
						self.data[res.value + len(EpsBeaconData.CUR)],
						EpsBeaconData.RES.unit())
		tmp = "Voltages"
		ret += "\n\n" + tmp + "\n"
		for i in range(len(tmp)): ret += "="
		for vol in EpsBeaconData.VOL:
			ret += ("\n {:9s} | {:6d} | {:2s}").format(vol.name,
						self.data[vol.value + len(EpsBeaconData.CUR) + len(EpsBeaconData.RES)],
						EpsBeaconData.VOL.unit())
		return ret

	def setRawBeacon(self, raw):
		try:
			self.rawBeacon = bytes([int(byte) for byte in raw.split(" ")])
			if len(self.rawBeacon) == self.byteSize:
				return True
			else:
				return False
		except ValueError:
			return False

	def parseBeacon(self):
		byteOffset = 0
		dataOffset = 0
		for it in range(len(EpsBeaconData.CUR)):
			self.data[dataOffset] = struct.unpack(EpsBeaconData.CUR.datatype(), self.rawBeacon[byteOffset:byteOffset + EpsBeaconData.CUR.bytecount()])[0]
			dataOffset += 1
			byteOffset += EpsBeaconData.CUR.bytecount()
		for it in range(len(EpsBeaconData.RES)):
			self.data[dataOffset] = struct.unpack(EpsBeaconData.RES.datatype(), self.rawBeacon[byteOffset:byteOffset + EpsBeaconData.RES.bytecount()])[0]
			dataOffset += 1
			byteOffset += EpsBeaconData.RES.bytecount()
		for it in range(len(EpsBeaconData.VOL)):
			self.data[dataOffset] = struct.unpack(EpsBeaconData.VOL.datatype(), self.rawBeacon[byteOffset:byteOffset + EpsBeaconData.VOL.bytecount()])[0]
			dataOffset += 1
			byteOffset += EpsBeaconData.VOL.bytecount()

			
# ##############################
# Beacon Widget
# ##############################

class EpsBeaconWidget(QWidget, EpsBeaconData):

	def __init__(self):
		QWidget.__init__(self)
		self.setGeometry(10, 40, 300, 700)
		self.setWindowTitle("EPS Beacon Reader")
		self.inputField = QPlainTextEdit()
		self.inputField.setPlaceholderText("Copy beacon bytes here")
		self.inputField.setMaximumHeight(100)
		self.outputTable = QTableWidget(len(self.CUR) + len(self.RES) + len(self.VOL), 3)
		
		self.layout = QVBoxLayout()
		self.layout.addWidget(self.inputField)
		self.layout.addWidget(self.outputTable)

		self.__setupOutputTable()
		self.__setupConnections()
		
		self.setLayout(self.layout)
		self.setVisible(True)


	def __setupOutputTable(self):
		it = 0
		for cur in self.CUR:
			self.outputTable.setItem(it, 0, QTableWidgetItem(cur.name))
			self.outputTable.setItem(it, 1, QTableWidgetItem("{:6d}".format(self.data[it])))
			self.outputTable.setItem(it, 2, QTableWidgetItem(self.CUR.unit()))
			it += 1
		for res in self.RES:
			self.outputTable.setItem(it, 0, QTableWidgetItem(res.name))
			self.outputTable.setItem(it, 1, QTableWidgetItem("{:6d}".format(self.data[it])))
			self.outputTable.setItem(it, 2, QTableWidgetItem(self.RES.unit()))
			it += 1
		for vol in self.VOL:
			self.outputTable.setItem(it, 0, QTableWidgetItem(vol.name))
			self.outputTable.setItem(it, 1, QTableWidgetItem("{:6d}".format(self.data[it])))
			self.outputTable.setItem(it, 2, QTableWidgetItem(self.VOL.unit()))
			it += 1
		for i in range(it):
			self.outputTable.setVerticalHeaderItem(i, QTableWidgetItem(""))
			self.outputTable.verticalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)
		self.outputTable.setHorizontalHeaderItem(0, QTableWidgetItem("ID"))
		self.outputTable.setHorizontalHeaderItem(1, QTableWidgetItem("Value"))
		self.outputTable.setHorizontalHeaderItem(2, QTableWidgetItem("Unit"))
		for i in range(3):
			self.outputTable.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)


	def __setupConnections(self):
		self.inputField.textChanged.connect(self.parse)


	def updateOutputTable(self):
		it = 0
		for cur in self.CUR:
			self.outputTable.item(it, 1).setText("{:6d}".format(self.data[it]))
			it += 1
		for res in self.RES:
			self.outputTable.item(it, 1).setText("{:6d}".format(self.data[it]))
			it += 1
		for vol in self.VOL:
			self.outputTable.item(it, 1).setText("{:6d}".format(self.data[it]))
			it += 1

	@pyqtSlot()
	def parse(self):
		if not self.setRawBeacon(self.inputField.toPlainText()):
			self.inputField.setStyleSheet("border: 1px solid red")
			return False
		else:
			self.inputField.setStyleSheet("")
			self.parseBeacon()
			self.updateOutputTable()
			return True


		
# ##############################
# Main
# ##############################

if __name__ == "__main__":
	print("EPS Beacon Parser GUI Application")
	
	app = QApplication(sys.argv)
	wnd = EpsBeaconWidget()

	sys.exit(app.exec_())