#!/usr/bin/env python3

import enum
import struct

from PyQt5.QtWidgets import *


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
		self.rawBeacon = bytes([int(byte) for byte in raw.split(" ")])
		if len(self.rawBeacon) == self.byteSize:
			return True
		else:
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



class EpsBeaconWidget(QWidget):

	def __init__(self):
		QWidget.__init__(self)