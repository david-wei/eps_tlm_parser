#!/usr/bin/python3

import json
import re
import functools
import argparse

import parser_utils
from thm.beaconconvert import *

class Measurement_Message(parser_utils.JsonMessage):
	def __init__(self, sensorId, temperature, created):
		self.sensorId = sensorId
		self.temperature = temperature
		self.createdOn = created

		self.endpoint = "/measurement"

	def to_json(self):
		log = {
			'source': "HOUSEKEEPING",
			'sensorId': self.sensorId,
			'temperature': self.temperature,
			'createdOn': self.createdOn
		}
		return json.dumps(log)

	def __eq__(self, other):
		return self.sensorId == other.sensorId \
			and self.temperature == other.temperature \
			and self.createdOn == other.createdOn

class System_Message(parser_utils.JsonMessage):
	def __init__(self, status, created):
		self.status = status
		self.createdOn = created

		self.endpoint = "/system"

	def to_json(self):
		log = {
			'source': "HOUSEKEEPING",
			'status': self.status,
			'createdOn': self.createdOn
		}
		return json.dumps(log)

	def __eq__(self, other):
		return self.status == other.status \
			and self.createdOn == other.createdOn


def parse(fname, downloaded):
	logs = []
	try:
		f = open(fname, 'r')
	except IOError:
		parser_utils.elogger.error('Error opening file')
		return []

	i = 0
	for line in f:
		data = convert(line)
		if data == 'eval_failed':
			parser_utils.elogger.error(
				'Line {} of file {} (downloaded {}) '.format(i,fname,downloaded) +\
				'could not be evaluated with eval()')
			continue

		if data == 'wrong_dim':
			parser_utils.elogger.error(
				'Line {} of file {} (downloaded {}) '.format(i,fname,downloaded) +\
				'had the wrong format. Expected 39 values, received {}'\
				.format(len(data.split())))
			continue

		if data == 'data_error':
			parser_utils.elogger.error(
				'Line {} of file {} (downloaded {}) '.format(i,fname,downloaded) +\
				'could not be interpreted. There was an unknown error')
			continue

		timestamp = parser_utils.UnixDateReader().getTimestamp(int(data.pop("Timestamp")))
		status    = data.pop('Status')[2]

		# Save system status
		logs.append(System_Message(status, timestamp))

		# Save measurements
		for sensor in data.keys():
			sensorData = data[sensor]
			temperature = sensorData[2]
			sensorId = sensorData[3]

			if temperature is None:
				parser_utils.elogger.error(
					'Invalid temperature for [{}] sensor {} ({}) with timestamp {} encountered'\
							.format(sensorData[1], sensorData[0], sensorId, timestamp, downloaded) +\
					'The interpretation of the logged data seems to have failed')
				continue

			logs.append(Measurement_Message(sensorId, temperature, timestamp))

		i += 1
	return logs


def interpret(value, subsystem):
	interpreters = {
			'ADCS_DS':  interpretDS18B20,
			'ADCS_BMX': interpretBMX055,
			'ADCS_TP':  interpretNoChange,
			'EPS':      interpretKelvinToCelsius,
			'CDH':      interpretNoChange,
			'COM_MCP':  interpretMCP9802,
			'COM_EMC':  interpretEMC1701,
			'COM_UNK':  interpretUnknownCOMSensor,
			'COM_LT':   interpretLT55599,
			'Status':   statusConverter
			}
	try:
		result = interpreters[subsystem](value)
	except:
		result = None
	return result

def convert(data):
	# Split line into array
	data = data.split()
	if len(data) != 39:
		return 'wrong_dim'
	# Convert values from str to int
	try:
		data = [eval(el) for el in data]
	except:
		return 'eval_failed'
	try:
		data = {
				'Timestamp':       data[0],
				'Battery 1':       ['EPS',   data[29], interpret(data[29], 'EPS'), 			27],
				'Battery 2':       ['EPS',   data[30], interpret(data[30], 'EPS'), 			28],
				'CDH':             ['CDH',   data[38], interpret(data[38], 'CDH'), 			36],
				'EPS 1':           ['EPS',   data[28], interpret(data[28], 'EPS'), 			26],
				'EPS 2':           ['EPS',   data[31], interpret(data[31], 'EPS'), 			29],
				'Main Panel 1':    ['ADCS',  data[24], interpret(data[24], 'ADCS_BMX'), 	22],
				'Main Panel 2':    ['ADCS',  data[25], interpret(data[25], 'ADCS_DS'), 		23],
				'Main Panel 3':    ['ADCS',  data[26], interpret(data[26], 'ADCS_DS'), 		24],
				'Main Panel 4':    ['ADCS',  data[27], interpret(data[27], 'ADCS_DS'), 		26],
				'S-Band 1':        ['COM',   data[32], interpret(data[32], 'COM_UNK'), 		30],
				'S-Band 2':        ['COM',   data[33], interpret(data[33], 'COM_MCP'), 		31],
				'S-Band 3':        ['COM',   data[34], interpret(data[34], 'COM_EMC'), 		32],
				'Side Panel 1_1':  ['ADCS',  data[8],  interpret(data[8],  'ADCS_BMX'),	 	6],
				'Side Panel 1_2':  ['ADCS',  data[9],  interpret(data[9],  'ADCS_DS'), 		7],
				'Side Panel 1_3':  ['ADCS',  data[10], interpret(data[10], 'ADCS_DS'), 		8],
				'Side Panel 1_4':  ['ADCS',  data[11], interpret(data[11], 'ADCS_DS'), 		9],
				'Side Panel 2_1':  ['ADCS',  data[12], interpret(data[12], 'ADCS_BMX'), 	10],
				'Side Panel 2_2':  ['ADCS',  data[13], interpret(data[13], 'ADCS_DS'), 		11],
				'Side Panel 2_3':  ['ADCS',  data[14], interpret(data[14], 'ADCS_DS'), 		12],
				'Side Panel 2_4':  ['ADCS',  data[15], interpret(data[15], 'ADCS_DS'), 		13],
				'Side Panel 3_1':  ['ADCS',  data[16], interpret(data[16], 'ADCS_BMX'), 	14],
				'Side Panel 3_2':  ['ADCS',  data[17], interpret(data[17], 'ADCS_DS'), 		15],
				'Side Panel 3_3':  ['ADCS',  data[18], interpret(data[18], 'ADCS_DS'), 		16],
				'Side Panel 3_4':  ['ADCS',  data[19], interpret(data[19], 'ADCS_DS'), 		17],
				'Side Panel 4_1':  ['ADCS',  data[20], interpret(data[20], 'ADCS_BMX'), 	18],
				'Side Panel 4_2':  ['ADCS',  data[21], interpret(data[21], 'ADCS_DS'), 		19],
				'Side Panel 4_3':  ['ADCS',  data[22], interpret(data[22], 'ADCS_DS'), 		20],
				'Side Panel 4_4':  ['ADCS',  data[23], interpret(data[23], 'ADCS_DS'), 		21],
				'Top Panel 1':     ['ADCS',  data[2],  interpret(data[2],  'ADCS_TP'), 		0],
				'Top Panel 2':     ['ADCS',  data[3],  interpret(data[3],  'ADCS_TP'), 		1],
				'Top Panel 3':     ['ADCS',  data[4],  interpret(data[4],  'ADCS_TP'), 		2],
				'Top Panel 4':     ['ADCS',  data[5],  interpret(data[5],  'ADCS_TP'), 		3],
				'Top Panel 5':     ['ADCS',  data[6],  interpret(data[6],  'ADCS_TP'), 		4],
				'Top Panel 6':     ['ADCS',  data[7],  interpret(data[7],  'ADCS_TP'), 		5],
				'UHF-VHF 1':       ['COM',   data[35], interpret(data[35], 'COM_MCP'), 		33],
				'UHF-VHF 2':       ['COM',   data[36], interpret(data[36], 'COM_LT'), 		34],
				'UHF-VHF 3':       ['COM',   data[37], interpret(data[37], 'COM_EMC'), 		35],
				'Status':          ['Status',data[1],  interpret(data[1],  'Status')]
			}
	except:
		return 'data_error'
	return data


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('config', type=str, help='configuration file path')
	parser.add_argument("-f", help="test file path", action="store", dest="filename")
	args = parser.parse_args()

	try:
		conf = parser_utils.Configuration(args.config)
	except:
		print('Configuration file', args.config, 'not existant or erroneous')
		exit(-1)

	parser_utils.init_logging(conf.logfile, __name__)
	poster = parser_utils.Poster(conf.url)

	if args.filename:
		messages = parse(args.filename, "2017-05-21T14:20:53")
		for message in messages:
			poster.post(message)
	else:

		rabbit_client = parser_utils.RabbitMQClient()
		rabbit_client.init(conf.hostname, conf.port, conf.exchange, conf.bindingKey, conf.user, conf.password)
		cb = functools.partial(parser_utils.callback, poster, parse)
		rabbit_client.start(cb)
