import argparse
import struct
from enum import Enum




# ##############################
# #####   Telemetry Data   #####
# ##############################

class EpsTlmData:
	
	class DEVICE(Enum):
		EPS			= 0
		BAT			= 1
		SSE			= 2
		CE			= 3
		SOFT		= 4
		BLOCK_INIT	= 255

	class SOURCE(Enum):
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

	class TYPE(Enum):
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
		
	class DATATYPE(Enum):
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



	def __init__(self):
		self.data = dict()
		
		# BCR
		self.data[(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.BCR1, EpsTlmData.TYPE.VOLTAGE)]			= list()
		self.data[(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.BCR1, EpsTlmData.TYPE.CURRENT)]			= list()
		self.data[(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.BCR1, EpsTlmData.TYPE.CURRENTB)]		= list()
		self.data[(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.BCR2, EpsTlmData.TYPE.VOLTAGE)]			= list()
		self.data[(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.BCR2, EpsTlmData.TYPE.CURRENT)]			= list()
		self.data[(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.BCR2, EpsTlmData.TYPE.CURRENTB)]		= list()
		self.data[(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.BCR3, EpsTlmData.TYPE.VOLTAGE)]			= list()
		self.data[(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.BCR3, EpsTlmData.TYPE.CURRENT)]			= list()
		self.data[(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.BCR3, EpsTlmData.TYPE.CURRENTB)]		= list()

		# TTC
		self.data[(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.TTC, EpsTlmData.TYPE.VOLTAGE)]			= list()
		self.data[(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.TTC, EpsTlmData.TYPE.CURRENT)]			= list()
		self.data[(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.TTC, EpsTlmData.TYPE.CURRENT3V3)]		= list()
		self.data[(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.TTC, EpsTlmData.TYPE.CURRENT5V)]		= list()
		self.data[(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.TTC, EpsTlmData.TYPE.TEMPERATURE)]		= list()
		self.data[(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.TTC, EpsTlmData.TYPE.MANRESET)]			= list()
		self.data[(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.TTC, EpsTlmData.TYPE.WDRESET)]			= list()
		self.data[(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.TTC, EpsTlmData.TYPE.SOFTRESET)]		= list()
		self.data[(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.TTC, EpsTlmData.TYPE.BRWNOUTRESET)]		= list()

		# BUS
		self.data[(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.UHF, EpsTlmData.TYPE.VOLTAGE)]			= list()
		self.data[(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.UHF, EpsTlmData.TYPE.CURRENT)]			= list()
		self.data[(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.SBAND, EpsTlmData.TYPE.VOLTAGE)]		= list()
		self.data[(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.SBAND, EpsTlmData.TYPE.CURRENT)]		= list()
		self.data[(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.CDH, EpsTlmData.TYPE.VOLTAGE)]			= list()
		self.data[(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.CDH, EpsTlmData.TYPE.CURRENT)]			= list()
		self.data[(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.SMARD1, EpsTlmData.TYPE.VOLTAGE)]		= list()
		self.data[(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.SMARD1, EpsTlmData.TYPE.CURRENT)]		= list()
		self.data[(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.SMARD2, EpsTlmData.TYPE.VOLTAGE)]		= list()
		self.data[(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.SMARD2, EpsTlmData.TYPE.CURRENT)]		= list()
		self.data[(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.ADCS5V_1, EpsTlmData.TYPE.VOLTAGE)]		= list()
		self.data[(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.ADCS5V_1, EpsTlmData.TYPE.CURRENT)]		= list()
		self.data[(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.ADCS5V_2, EpsTlmData.TYPE.VOLTAGE)]		= list()
		self.data[(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.ADCS5V_2, EpsTlmData.TYPE.CURRENT)]		= list()
		self.data[(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.ADCS3V3_1, EpsTlmData.TYPE.VOLTAGE)]	= list()
		self.data[(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.ADCS3V3_1, EpsTlmData.TYPE.CURRENT)]	= list()
		self.data[(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.ADCS3V3_2, EpsTlmData.TYPE.VOLTAGE)]	= list()
		self.data[(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.ADCS3V3_2, EpsTlmData.TYPE.CURRENT)]	= list()
		self.data[(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.THM, EpsTlmData.TYPE.VOLTAGE)]			= list()
		self.data[(EpsTlmData.DEVICE.EPS, EpsTlmData.SOURCE.THM, EpsTlmData.TYPE.CURRENT)]			= list()
		
		# BAT
		self.data[(EpsTlmData.DEVICE.BAT, EpsTlmData.SOURCE.CELL, EpsTlmData.TYPE.VOLTAGE)]			= list()
		self.data[(EpsTlmData.DEVICE.BAT, EpsTlmData.SOURCE.CELL, EpsTlmData.TYPE.CURRENT)]			= list()
		self.data[(EpsTlmData.DEVICE.BAT, EpsTlmData.SOURCE.CE, EpsTlmData.TYPE.CHARGE_LVL)]		= list()
		self.data[(EpsTlmData.DEVICE.BAT, EpsTlmData.SOURCE.BTTC, EpsTlmData.TYPE.HEATER_STATE1)]	= list()
		self.data[(EpsTlmData.DEVICE.BAT, EpsTlmData.SOURCE.BTTC, EpsTlmData.TYPE.HEATER_STATE2)]	= list()
		self.data[(EpsTlmData.DEVICE.BAT, EpsTlmData.SOURCE.BTTC, EpsTlmData.TYPE.TEMPERATURE)]		= list()
		self.data[(EpsTlmData.DEVICE.BAT, EpsTlmData.SOURCE.BTTC, EpsTlmData.TYPE.TEMPERATURE2)]	= list()
		self.data[(EpsTlmData.DEVICE.BAT, EpsTlmData.SOURCE.BTTC, EpsTlmData.TYPE.TEMPERATURE3)]	= list()


	def commandIsValid(self, device, source, type):
		return (EpsTlmData.DEVICE(device),
				EpsTlmData.SOURCE(source),
				EpsTlmData.TYPE(type)) in self.data
	
	def addData(self, device, source, type, time, value):
		ret = self.commandIsValid(device, source, type)
		if ret:
			self.data[(EpsTlmData.DEVICE(device),
				EpsTlmData.SOURCE(source),
				EpsTlmData.TYPE(type))].append((time, value))
			
			# DEBUG
			print("  device: " + str(device) + " | source: " + str(source) + " | type: " + str(type) + " | time: " + str(time) + " | value: " + str(value))
			
		else:
			# DEBUG
			print("? device: " + str(device) + " | source: " + str(source) + " | type: " + str(type) + " | time: " + str(time) + " | value: " + str(value))


		return ret


# ###############################
# #####     File Reader     #####
# ###############################

class EpsTlmFileReader(EpsTlmData):
	
	INVALID_VALUE_RATE_LIMIT = 0.03		# expected (init block): 1/44 = 0.023
	MINIMUM_COUNT = 500
	

	def __init__(self, fileName = ""):
		EpsTlmData.__init__(self)
		errorCount = 0
		itemCount = 0
		
		self.fileName = fileName


	def setFile(self, fileName):
		self.fileName = fileName


	def readFile(self):
		errorCount = 0
		itemCount = 0
		
		# DEBUG
		bc = False	# print byte count
		bv = False	# print byte value

		with open(self.fileName, "rb") as file:
			while True:
				if bc: print("width: reading byte count:", EpsTlmData.DATATYPE.byteCount(EpsTlmData.DATATYPE.WIDTH))
				buffer = file.read(EpsTlmData.DATATYPE.byteCount(EpsTlmData.DATATYPE.WIDTH))
				if not buffer: break
				width = struct.unpack(EpsTlmData.DATATYPE.uint8.value, buffer)[0]
				if bv: print("width:", width)

				if bc: print("time: reading byte count:", EpsTlmData.DATATYPE.byteCount(EpsTlmData.DATATYPE.TIME))
				buffer = file.read(EpsTlmData.DATATYPE.byteCount(EpsTlmData.DATATYPE.TIME))
				if not buffer: break
				time = struct.unpack(EpsTlmData.DATATYPE.TIME.value, buffer)[0]
				if bv: print("time:", time)
				
				if bc: print("device: reading byte count:", EpsTlmData.DATATYPE.byteCount(EpsTlmData.DATATYPE.DEVICE))
				buffer = file.read(EpsTlmData.DATATYPE.byteCount(EpsTlmData.DATATYPE.DEVICE))
				if not buffer: break
				device = struct.unpack(EpsTlmData.DATATYPE.DEVICE.value, buffer)[0]
				if bv: print("device:", device)
				
				if bc: print("source: reading byte count:", EpsTlmData.DATATYPE.byteCount(EpsTlmData.DATATYPE.SOURCE))
				buffer = file.read(EpsTlmData.DATATYPE.byteCount(EpsTlmData.DATATYPE.SOURCE))
				if not buffer: break
				source = struct.unpack(EpsTlmData.DATATYPE.SOURCE.value, buffer)[0]
				if bv: print("source:", source)
				
				if bc: print("type: reading byte count:", EpsTlmData.DATATYPE.byteCount(EpsTlmData.DATATYPE.TYPE))
				buffer = file.read(EpsTlmData.DATATYPE.byteCount(EpsTlmData.DATATYPE.TYPE))
				if not buffer: break
				type = struct.unpack(EpsTlmData.DATATYPE.TYPE.value, buffer)[0]
				if bv: print("type:", type)
				
				if bc: print("value: reading byte count:", EpsTlmData.DATATYPE.byteCount(EpsTlmData.DATATYPE.VALUE(type)))
				buffer = file.read(EpsTlmData.DATATYPE.byteCount(EpsTlmData.DATATYPE.VALUE(type)))
				if not buffer: break
				value = struct.unpack(EpsTlmData.DATATYPE.VALUE(type).value, buffer)[0]
				if bv: print("value:", value)

				itemCount += 1
				if not self.addData(device, source, type, time, value):
					errorCount += 1
					if itemCount > EpsTlmFileReader.MINIMUM_COUNT and float(errorCount) / itemCount > EpsTlmFileReader.INVALID_VALUE_RATE_LIMIT:
						print("EPS telemetry file", self.fileName, "is corrupt:", errorCount, "/", itemCount)
						return False

		return True




# ###############################
# ########     Parse     ########
# ###############################

def parse(fileName):
	print("Parsing", fileName)
	fr = EpsTlmFileReader(fileName = fileName)
	fr.readFile()
	print("Parsing completed")
	return fr.data



if __name__ == "__main__":
	parser = argparse.ArgumentParser(prog = "EPS_TLM_Parser", description = "Parses EPS telemetry data *.tlm files")
	parser.add_argument("tlmFile", help = "EPS telemetry *.tlm file")
	args = parser.parse_args()
	fileName = args.tlmFile
	parse(fileName)
	