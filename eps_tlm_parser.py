import argparse
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

	def __init__(self):
		errorCount = 0
		itemCount = 0
















if __name__ == "__main__":
	parser = argparse.ArgumentParser(description = "Parses EPS telemetry data *.tlm files")
	parser.add_argument("--depp")
	print("EPS == 0:", EpsTlmData.DEVICE.EPS == 0)
	print("EPS.value == 0:", EpsTlmData.DEVICE.EPS.value == 0)
	print("EPS == DEVICE(0):", EpsTlmData.DEVICE.EPS == EpsTlmData.DEVICE(0))
	EpsTlmFileReader()
	