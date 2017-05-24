#!/usr/bin/env python3

import argparse
import struct
import enum
import datetime
import os
import operator



# ##############################
# #####   Telemetry Data   #####
# ##############################

class EpsTlmData:
	
	class DEVICE(enum.Enum):
		EPS			= 0
		BAT			= 1
		SSE			= 2
		CE			= 3
		SOFT		= 4
		BLOCK_INIT	= 255

	# ++++++++++++++++++++++++++

	class SOURCE(enum.Enum):
		UHF 		= 0
		CDH 		= 1
		SBAND 		= 2
		SMARD1 		= 3
		SMARD2 		= 4
		PL 			= 5
		ADCS5V_1 	= 6	
		ADCS5V_2 	= 7
		THM 		= 8	
		ADCS3V3_1 	= 9	
		ADCS3V3_2 	= 10
		CELL 		= 11
		BCR1 		= 12
		BCR2 		= 13
		BCR3 		= 14
		SSE 		= 15
		CE 			= 16
		TTC 		= 17
		BTTC 		= 18	
		BLOCK_INIT	= 255

	# ++++++++++++++++++++++++++

	class TYPE(enum.Enum):
		VOLTAGE			= 0
		CURRENT			= 1
		CURRENTB		= 2
		TEMPERATURE		= 3
		MANRESET		= 4
		SOFTRESET		= 5
		WDRESET			= 6
		BRWNOUTRESET	= 7
		WDTIME			= 8
		CHARGE_LVL		= 9
		HEATER_STATE1	= 10
		HEATER_STATE2	= 11
		TEMPERATURE2	= 12
		TEMPERATURE3	= 13
		CURRENT3V3		= 14
		CURRENT5V		= 15
		BLOCK_INIT		= 255

		def physicalUnit(type):
			if type == EpsTlmData.TYPE.VOLTAGE:
				return "V"
			elif type == EpsTlmData.TYPE.CURRENT or type == EpsTlmData.TYPE.CURRENTB or type == EpsTlmData.TYPE.CURRENT3V3 or type == EpsTlmData.TYPE.CURRENT5V:
				return "mA"
			elif type == EpsTlmData.TYPE.TEMPERATURE or type == EpsTlmData.TYPE.TEMPERATURE2 or type == EpsTlmData.TYPE.TEMPERATURE3:
				return "K"
			elif type == EpsTlmData.TYPE.MANRESET or type == EpsTlmData.TYPE.SOFTRESET or type == EpsTlmData.TYPE.WDRESET or type == EpsTlmData.TYPE.BRWNOUTRESET:
				return "count"
			elif type == EpsTlmData.TYPE.HEATER_STATE1 or type == EpsTlmData.TYPE.HEATER_STATE2:
				return "on/off"
			else:
				return "1"
		
	# ++++++++++++++++++++++++++

	class DATATYPE(enum.Enum):
		bit = "?"
		uint8 = "B"
		uint16 = "H"
		uint32 = "I"
		uint64 = "Q"
		int8 = "b"
		int16 = "h"
		int32 = "i"
		int64 = "q"
		float32 = "f"
		float64 = "d"

		def byteCount(datatype):
			if datatype == EpsTlmData.DATATYPE.bit or datatype == EpsTlmData.DATATYPE.uint8 or datatype == EpsTlmData.DATATYPE.int8:
				return 1
			elif datatype == EpsTlmData.DATATYPE.uint16 or datatype == EpsTlmData.DATATYPE.int16:
				return 2
			elif datatype == EpsTlmData.DATATYPE.uint32 or datatype == EpsTlmData.DATATYPE.int32 or datatype == EpsTlmData.DATATYPE.float32:
				return 4
			elif datatype == EpsTlmData.DATATYPE.uint64 or datatype == EpsTlmData.DATATYPE.int64 or datatype == EpsTlmData.DATATYPE.float64:
				return 8

		WIDTH = uint8
		TIME = uint64
		DEVICE = uint8
		SOURCE = uint8
		TYPE = uint8

		def VALUE(type):
			type = EpsTlmData.TYPE(type)
			if type == EpsTlmData.TYPE.VOLTAGE:			return EpsTlmData.DATATYPE.float32
			elif type == EpsTlmData.TYPE.CURRENT:		return EpsTlmData.DATATYPE.float32
			elif type == EpsTlmData.TYPE.CURRENTB:		return EpsTlmData.DATATYPE.float32
			elif type == EpsTlmData.TYPE.TEMPERATURE:	return EpsTlmData.DATATYPE.float32
			elif type == EpsTlmData.TYPE.MANRESET:		return EpsTlmData.DATATYPE.float32
			elif type == EpsTlmData.TYPE.SOFTRESET:		return EpsTlmData.DATATYPE.float32
			elif type == EpsTlmData.TYPE.WDRESET:		return EpsTlmData.DATATYPE.float32
			elif type == EpsTlmData.TYPE.BRWNOUTRESET:	return EpsTlmData.DATATYPE.float32
			elif type == EpsTlmData.TYPE.WDTIME:		return EpsTlmData.DATATYPE.float32
			elif type == EpsTlmData.TYPE.CHARGE_LVL:	return EpsTlmData.DATATYPE.float32
			elif type == EpsTlmData.TYPE.HEATER_STATE1:	return EpsTlmData.DATATYPE.float32
			elif type == EpsTlmData.TYPE.HEATER_STATE2:	return EpsTlmData.DATATYPE.float32
			elif type == EpsTlmData.TYPE.TEMPERATURE2:	return EpsTlmData.DATATYPE.float32
			elif type == EpsTlmData.TYPE.TEMPERATURE3:	return EpsTlmData.DATATYPE.float32
			elif type == EpsTlmData.TYPE.CURRENT3V3:	return EpsTlmData.DATATYPE.float32
			elif type == EpsTlmData.TYPE.CURRENT5V:		return EpsTlmData.DATATYPE.float32
			elif type == EpsTlmData.TYPE.BLOCK_INIT:	return EpsTlmData.DATATYPE.float32

	# ++++++++++++++++++++++++++

	VALID_COMMANDS = [
		# BCR
		(DEVICE.EPS, SOURCE.BCR1, TYPE.VOLTAGE),
		(DEVICE.EPS, SOURCE.BCR1, TYPE.CURRENT),
		(DEVICE.EPS, SOURCE.BCR1, TYPE.CURRENTB),
		(DEVICE.EPS, SOURCE.BCR2, TYPE.VOLTAGE),
		(DEVICE.EPS, SOURCE.BCR2, TYPE.CURRENT),
		(DEVICE.EPS, SOURCE.BCR2, TYPE.CURRENTB),
		(DEVICE.EPS, SOURCE.BCR3, TYPE.VOLTAGE),
		(DEVICE.EPS, SOURCE.BCR3, TYPE.CURRENT),
		(DEVICE.EPS, SOURCE.BCR3, TYPE.CURRENTB),

		# TTC
		(DEVICE.EPS, SOURCE.TTC, TYPE.VOLTAGE),
		(DEVICE.EPS, SOURCE.TTC, TYPE.CURRENT),
		(DEVICE.EPS, SOURCE.TTC, TYPE.CURRENT3V3),
		(DEVICE.EPS, SOURCE.TTC, TYPE.CURRENT5V),
		(DEVICE.EPS, SOURCE.TTC, TYPE.TEMPERATURE),
		(DEVICE.EPS, SOURCE.TTC, TYPE.MANRESET),
		(DEVICE.EPS, SOURCE.TTC, TYPE.WDRESET),
		(DEVICE.EPS, SOURCE.TTC, TYPE.SOFTRESET),
		(DEVICE.EPS, SOURCE.TTC, TYPE.BRWNOUTRESET),

		# BUS
		(DEVICE.EPS, SOURCE.UHF,       TYPE.VOLTAGE),
		(DEVICE.EPS, SOURCE.UHF,       TYPE.CURRENT),
		(DEVICE.EPS, SOURCE.SBAND,     TYPE.VOLTAGE),
		(DEVICE.EPS, SOURCE.SBAND,     TYPE.CURRENT),
		(DEVICE.EPS, SOURCE.CDH,       TYPE.VOLTAGE),
		(DEVICE.EPS, SOURCE.CDH,       TYPE.CURRENT),
		(DEVICE.EPS, SOURCE.SMARD1,    TYPE.VOLTAGE),
		(DEVICE.EPS, SOURCE.SMARD1,    TYPE.CURRENT),
		(DEVICE.EPS, SOURCE.SMARD2,    TYPE.VOLTAGE),
		(DEVICE.EPS, SOURCE.SMARD2,    TYPE.CURRENT),
		(DEVICE.EPS, SOURCE.ADCS5V_1,  TYPE.VOLTAGE),
		(DEVICE.EPS, SOURCE.ADCS5V_1,  TYPE.CURRENT),
		(DEVICE.EPS, SOURCE.ADCS5V_2,  TYPE.VOLTAGE),
		(DEVICE.EPS, SOURCE.ADCS5V_2,  TYPE.CURRENT),
		(DEVICE.EPS, SOURCE.ADCS3V3_1, TYPE.VOLTAGE),
		(DEVICE.EPS, SOURCE.ADCS3V3_1, TYPE.CURRENT),
		(DEVICE.EPS, SOURCE.ADCS3V3_2, TYPE.VOLTAGE),
		(DEVICE.EPS, SOURCE.ADCS3V3_2, TYPE.CURRENT),
		(DEVICE.EPS, SOURCE.THM,       TYPE.VOLTAGE),
		(DEVICE.EPS, SOURCE.THM,       TYPE.CURRENT),
		
		# BAT
		(DEVICE.BAT, SOURCE.CELL, TYPE.VOLTAGE),
		(DEVICE.BAT, SOURCE.CELL, TYPE.CURRENT),
		(DEVICE.BAT, SOURCE.CE,   TYPE.CHARGE_LVL),
		(DEVICE.BAT, SOURCE.BTTC, TYPE.HEATER_STATE1),
		(DEVICE.BAT, SOURCE.BTTC, TYPE.HEATER_STATE2),
		(DEVICE.BAT, SOURCE.BTTC, TYPE.TEMPERATURE),
		(DEVICE.BAT, SOURCE.BTTC, TYPE.TEMPERATURE2),
		(DEVICE.BAT, SOURCE.BTTC, TYPE.TEMPERATURE3)
	]
	
	# ++++++++++++++++++++++++++

	def __init__(self, mode = ""):
		self.setMode(mode)
		self.data = dict()
		for cmd in EpsTlmData.VALID_COMMANDS:
			self.data[cmd] = list()

	# ++++++++++++++++++++++++++

	def __add__(self, other):
		for cmd in EpsTlmData.VALID_COMMANDS:
			self.data[cmd] += other.data[cmd]
		return self

	# ++++++++++++++++++++++++++

	def __str__(self):
		ret = ""
		for cmd in EpsTlmData.VALID_COMMANDS:
			ret += "\n> "
			tmp = cmd[0].name + " | " + cmd[1].name + " | " + cmd[2].name
			ret += tmp + "\n  "
			for i in range(len(tmp)): ret += "="
			ret += "\n"
			for item in self.data[cmd]:
				ret += ("  " + str(item[0]) + "   | {:10.3f}\n").format(item[1])
		return ret

	# ++++++++++++++++++++++++++

	def setMode(self, mode):
		if mode == "p" or mode == "op" or mode == "po":
			self.modePrint = True
		else:
			self.modePrint = False

		if mode == "o" or mode == "op" or mode == "po":
			self.modeWrite = True
		else:
			self.modeWrite = False

	# ++++++++++++++++++++++++++

	def commandIsValid(self, device, source, type):
		return (EpsTlmData.DEVICE(device),
				EpsTlmData.SOURCE(source),
				EpsTlmData.TYPE(type)) in self.data

	# ++++++++++++++++++++++++++
	
	def addData(self, device, source, type, time, value):
		ret = self.commandIsValid(device, source, type)
		if ret:
			self.data[(EpsTlmData.DEVICE(device),
				EpsTlmData.SOURCE(source),
				EpsTlmData.TYPE(type))].append((time, value))
			if self.modePrint:
				print(("  device: {0:3d} | source: {1:3d} | type: {2:3d} | time: " + str(time) + " | value: {3:10.3f}").format(device, source, type, value))

		else:
			if self.modePrint:
				print(("! device: {0:3d} | source: {1:3d} | type: {2:3d} | time: " + str(time) + " | value: {3:>10.3f}").format(device, source, type, value))

		return ret

	# ++++++++++++++++++++++++++

	def sortData(self, cmd):
		self.data[cmd] = sorted(self.data[cmd], key = operator.itemgetter(0), reverse = False)

	# ++++++++++++++++++++++++++

	def sortAllData(self):
		for cmd in EpsTlmData.VALID_COMMANDS:
			self.sortData(cmd)

	# ++++++++++++++++++++++++++

	def deleteData(self):
		for cmd in EpsTlmData.VALID_COMMANDS:
			self.data[cmd] = list()

	# ++++++++++++++++++++++++++

	def getDataIndexFromTime(self, cmd, time, boundary = "left"):
		if not self.commandIsValid(cmd): return -1
		if boundary != "left" and boundary != "right": return -2
		if len(self.data[cmd]) == 0: return -3

		if boundary == "left":
			it = 0
			for item in self.data[cmd]:
				if time > item[0]:
					return max(0, it - 1)
				it += 1
		elif boundary == "right":
			it = len(self.data[cmd])
			for item in reversed(self.data[cmd]):
				if time < item[0]:
					return min(len(self.data[cmd]), it + 1)
				it -= 1


# ###############################
# #######   File Reader   #######
# ###############################

class EpsTlmFileReader(EpsTlmData):
	
	INVALID_VALUE_RATE_LIMIT = 0.03		# expected (init block): 1/44 = 0.023
	MINIMUM_COUNT = 500
	
	# ++++++++++++++++++++++++++

	def __init__(self, fileName = "", mode = ""):
		EpsTlmData.__init__(self, mode)
		errorCount = 0
		itemCount = 0
		self.setFolder("")
		self.setFile(fileName)
		self.setProgressCallback(do_nothing)


	# ++++++++++++++++++++++++++

	def setFile(self, fileName):
		if type(fileName) == list:
			self.fileList = list()
			for file in fileName:
				if os.path.isfile(file): self.fileList.append(file)

		else:
			self.tlmFileName = fileName
			if fileName[-4:] == ".tlm":
				self.csvFileName = fileName[:-4] + ".csv"
			else:
				self.csvFileName = fileName + ".csv"
			if os.path.exists(self.csvFileName):
				i = 1
				while os.path.exists(self.csvFileName[:-4] + "(" + str(i) + ").csv"):
					i += 1
				self.csvFileName = self.csvFileName[:-4] + "(" + str(i) + ").csv"

	# ++++++++++++++++++++++++++

	def setFolder(self, folderName):
		self.fileList = list()
		if folderName and os.path.isdir(folderName):
			for file in os.listdir(folderName):
				if file.endswith(".tlm"):
					self.fileList.append(os.path.join(folderName, file))
			return True
		else:
			return False

	# ++++++++++++++++++++++++++

	def readFile(self):
		errorCount = 0
		itemCount = 0
		
		if not os.path.isfile(self.tlmFileName):
			print("Specified telemetry file " + self.tlmFileName + " does not exist")
			return False

		if self.modeWrite:
			of = open(self.csvFileName, "a")
			of.write("DEVICE;SOURCE;TYPE;DATE;TIME;VALUE\n")

		try:
			with open(self.tlmFileName, "rb") as file:
				while True:
					buffer = file.read(EpsTlmData.DATATYPE.byteCount(EpsTlmData.DATATYPE.WIDTH))
					if not buffer: break
					width = struct.unpack(EpsTlmData.DATATYPE.uint8.value, buffer)[0]

					buffer = file.read(EpsTlmData.DATATYPE.byteCount(EpsTlmData.DATATYPE.TIME))
					if not buffer: break
					time = datetime.datetime.fromtimestamp(int(struct.unpack(EpsTlmData.DATATYPE.TIME.value, buffer)[0] / 1e9))
				
					buffer = file.read(EpsTlmData.DATATYPE.byteCount(EpsTlmData.DATATYPE.DEVICE))
					if not buffer: break
					device = struct.unpack(EpsTlmData.DATATYPE.DEVICE.value, buffer)[0]
				
					buffer = file.read(EpsTlmData.DATATYPE.byteCount(EpsTlmData.DATATYPE.SOURCE))
					if not buffer: break
					source = struct.unpack(EpsTlmData.DATATYPE.SOURCE.value, buffer)[0]
				
					buffer = file.read(EpsTlmData.DATATYPE.byteCount(EpsTlmData.DATATYPE.TYPE))
					if not buffer: break
					type = struct.unpack(EpsTlmData.DATATYPE.TYPE.value, buffer)[0]
				
					try:
						buffer = file.read(EpsTlmData.DATATYPE.byteCount(EpsTlmData.DATATYPE.VALUE(type)))
						if not buffer: break
						value = struct.unpack(EpsTlmData.DATATYPE.VALUE(type).value, buffer)[0]

						ret = self.addData(device, source, type, time, value)

					except ValueError:
						ret = False

					itemCount += 1
					if not ret:
						errorCount += 1
						if itemCount > EpsTlmFileReader.MINIMUM_COUNT and float(errorCount) / itemCount > EpsTlmFileReader.INVALID_VALUE_RATE_LIMIT:
							print("EPS telemetry file", self.tlmFileName, "is corrupt:", errorCount, "/", itemCount)
							return False
					elif self.modeWrite:
						tmp = str(time).split(" ")
						of.write((EpsTlmData.DEVICE(device).name + ";" + 
							EpsTlmData.SOURCE(source).name + ";" +
							EpsTlmData.TYPE(type).name + ";" +
							tmp[0] + ";" + tmp[1] +
							";{:f};\n").format(value))
		except IOError:
			print("Error reading telemetry file " + self.tlmFileName + ", error rate: " + str(errorCount) + "/" + str(itemCount))
			return False

		if self.modeWrite: of.close()

		return True

	# ++++++++++++++++++++++++++

	def readFileList(self):
		ret = True
		it = 0
		self.progressCallback(float(it) / len(self.fileList))
		for file in self.fileList:
			self.setFile(file)
			ret &= self.readFile()
			it += 1
			self.progressCallback(float(it) / len(self.fileList))

		return ret

	# ++++++++++++++++++++++++++

	def writeDataToFile(self, filename, cmd):
		if not self.commandIsValid(cmd[0].value, cmd[1].value, cmd[2].value):
			print("Invalid command")
			return False

		fileExists = False
		if os.path.isfile(filename):
			fileExists = True

		of = open(filename, "a")
		if not fileExists: of.write("DEVICE;SOURCE;TYPE;DATE;TIME;VALUE\n")

		for item in self.data[cmd]:
			tmp = str(item[0]).split(" ")
			of.write((cmd[0].name + ";" + 
				cmd[1].name + ";" +
				cmd[2].name + ";" +
				tmp[0] + ";" + tmp[1] +
				";{:f};\n").format(item[1]))

		of.close()

	# ++++++++++++++++++++++++++

	def writeAllDataToFile(self, filename):
		it = 0
		self.progressCallback(float(it) / len(EpsTlmData.VALID_COMMANDS))
		for cmd in EpsTlmData.VALID_COMMANDS:
			self.writeDataToFile(filename, cmd)
			it += 1
			self.progressCallback(float(it) / len(EpsTlmData.VALID_COMMANDS))
			
	# ++++++++++++++++++++++++++

	def setProgressCallback(self, callback_function):
		self.progressCallback = callback_function
	def resetProgressCallback(self):
		self.progressCallback = do_nothing



# ###############################

def do_nothing(var = 0):
	pass


# ###############################
# ########     Main     #########
# ###############################

if __name__ == "__main__":
	parser = argparse.ArgumentParser(prog = "EPS_TLM_Parser", description = "Parses EPS telemetry data *.tlm files")
	parser.add_argument("tlmFile", help = "EPS telemetry *.tlm file or folder containing *.tlm files")
	parser.add_argument("-o", "--output", help = "outputs a human readable *.csv file", action = "store_true")
	parser.add_argument("-p", "--print", help = "prints the values read from the *.tlm file", action = "store_true")
	parser.add_argument("-s", "--sorted", help = "prints the values sorted according to the data type", action = "store_true")

	mode = ""
	isFolder = False
	args = parser.parse_args()
	fileName = args.tlmFile
	if args.output: mode += "o"
	if args.print: mode += "p"
	
	fr = EpsTlmFileReader(mode = mode)
	if os.path.isdir(fileName):
		isFolder = True
		fr.setFolder(fileName)
		print("Parsing files", fr.fileList)
		ret = fr.readFileList()
	else:
		fr.setFile(fileName)
		print("Parsing file", fileName)
		ret = fr.readFile()

	if ret:
		print("Parsing completed")
		if fr.modeWrite and isFolder: print("Output file", fr.csvFileName)
	else:
		print("Parsing failed")

	if args.sorted: print(fr)
	