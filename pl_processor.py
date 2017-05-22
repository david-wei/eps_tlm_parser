#!/usr/bin/python3

import json
import re
import functools
import argparse

import parser_utils

class PayloadMessage(parser_utils.JsonMessage):
	def __init__(self, cellId, beforeTemp, afterTemp, samplingPeriod, measurementsData, created):
		super().__init__()
		self.data = {}
		self.data["source"] = "HOUSEKEEPING"
		self.data["status"] = "UNKNOWN"
		self.data["cellId"] = cellId
		self.data["beforeTemp"] = beforeTemp
		self.data["afterTemp"] = afterTemp
		self.data["samplingPeriod"] = samplingPeriod
		self.data["measurementsData"] = measurementsData
		self.data["createdOn"] = created

	def addMeasurement(self, measurementData):
		self.data["measurementsData"].append(measurementData)

	def to_json(self):
		return json.dumps(self.data)

	def __eq__(self, other):
		return False

def parse(fname, downloaded):
	try:
		f = open(fname, 'r')
	except IOError:
		parser_utils.elogger.error('[PL] Error opening file: ' + str(fname))
		return []

	valid_message = False
	lines = f.readlines()

	filename = fname.split('/')[-1]
	created = parser_utils.UnixDateReader().getTimestamp(int(filename.split('_')[0]))	# Received timestamp: overhead_3ms
	cellId = int(lines[0].split(' ')[1])			# Cell: 3
	samplingPeriod = int(lines[1].split(' ')[2])	# Sampling period: 3 ms
	beforeTemp = float(lines[3].split(' ')[2])		# T = 36.75 deg
	afterTemp = float(lines[-1].split(' ')[2])		# T = 38.437 deg

	message = PayloadMessage(cellId, beforeTemp, afterTemp, samplingPeriod, [], created)

	for l in lines[4:-1]:
		values = l.split(' ')

		data = {}
		data["gateDac"] = float(values[1])
		data["voltage"] = float(values[2])
		data["current"] = float(values[3])

		message.addMeasurement(data)

	f.close()

	return [message]

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

	# If filename given, then parse and send without rabbitmq
	if args.filename:
		messages = parse(args.filename, "2017-05-21T14:20:53")
		for message in messages:
			poster.post(message)
	else:
		rabbit_client = parser_utils.RabbitMQClient()
		rabbit_client.init(conf.hostname, conf.port, conf.exchange, conf.bindingKey, conf.user, conf.password)
		cb = functools.partial(parser_utils.callback, poster, parse)
		rabbit_client.start(cb)
