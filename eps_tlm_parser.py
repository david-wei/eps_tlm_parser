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
		bit = 0
		uint8 = 1
		uint16 = 2
		uint32 = 3
		uint64 = 4
		int16 = 5
		int32 = 6
		int64 = 7
		float32 = 8
		float64 = 9

		def byteCount(datatype):
			if datatype == EpsTlmData.DATATYPE.bit or datatype == EpsTlmData.DATATYPE.uint8:
				return 1
			elif datatype == EpsTlmData.DATATYPE.uint16 or datatype == EpsTlmData.DATATYPE.int16:
				return 2
			elif datatype == EpsTlmData.DATATYPE.uint32 or datatype == EpsTlmData.DATATYPE.int32 or datatype == EpsTlmData.DATATYPE.float32:
				return 4
			elif datatype == EpsTlmData.DATATYPE.uint64 or datatype == EpsTlmData.DATATYPE.int64 or datatype == EpsTlmData.DATATYPE.float64:
				return 8

		TIME = EpsTlmData.DATATYPE.uint64
		DEVICE = EpsTlmData.DATATYPE.uint8
		SOURCE = EpsTlmData.DATATYPE.uint8
		TYPE = EpsTlmData.DATATYPE.uint8

		def VALUE(type):
			type = EpsTlmData.TYPE(type)
			if type == EpsTlmData.TYPE.VOLTAGE:			return EpsTlmData.DATATYPE.float32
			elif type == EpsTlmData.TYPE.CURRENT:		return EpsTlmData.DATATYPE.float32
			elif type == EpsTlmData.TYPE.CURRENTB:		return EpsTlmData.DATATYPE.float32
			elif type == EpsTlmData.TYPE.TEMPERATURE:	return EpsTlmData.DATATYPE.float32
			elif type == EpsTlmData.TYPE.MANRESET:		return EpsTlmData.DATATYPE.uint8
			elif type == EpsTlmData.TYPE.SOFTRESET:		return EpsTlmData.DATATYPE.uint8
			elif type == EpsTlmData.TYPE.WDRESET:		return EpsTlmData.DATATYPE.uint8
			elif type == EpsTlmData.TYPE.BRWNOUTRESET:	return EpsTlmData.DATATYPE.uint8
			elif type == EpsTlmData.TYPE.WDTIME:		return EpsTlmData.DATATYPE.float32
			elif type == EpsTlmData.TYPE.CHARGE_LVL:	return EpsTlmData.DATATYPE.float32
			elif type == EpsTlmData.TYPE.HEATER_STATE1:	return EpsTlmData.DATATYPE.bit
			elif type == EpsTlmData.TYPE.HEATER_STATE2:	return EpsTlmData.DATATYPE.bit
			elif type == EpsTlmData.TYPE.TEMPERATURE2:	return EpsTlmData.DATATYPE.float32
			elif type == EpsTlmData.TYPE.TEMPERATURE3:	return EpsTlmData.DATATYPE.float32
			elif type == EpsTlmData.TYPE.CURRENT3V3:	return EpsTlmData.DATATYPE.float32
			elif type == EpsTlmData.TYPE.CURRENT5V:		return EpsTlmData.DATATYPE.float32
			elif type == EpsTlmData.TYPE.BLOCK_INIT:	return EpsTlmData.DATATYPE.uint8



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
		return ret


# ###############################
# #####     File Reader     #####
# ###############################

class EpsTlmFileReader(EpsTlmData):
	
	ERROR_RATE_LIMIT = 0.2
	MINIMUM_COUNT = 500



	def __init__(self, fileName = ""):
		errorCount = 0
		itemCount = 0
			
		self.newData = EpsTlmData()
		self.fileName = fileName


	def readFile(self):
		self.file = open(self.fileName, "rb")
		









if __name__ == "__main__":
	parser = argparse.ArgumentParser(description = "Parses EPS telemetry data *.tlm files")
	parser.add_argument("-f", "--file", nargs = 1, action = "store", help = "*.tlm file")
	#parser.add_argument("--depp")
	args = parser.parse_args()
	print(args)
	EpsTlmFileReader()
	