#!/usr/bin/env python

from eps.eps_tlm_parser import *
import parser_utils
import json


class EpsMessage():
	def __init__(self, dataKey, dataValue):
		parser_utils.JsonMessage.__init__(self)
		self.device = dataKey[0].name
		self.source = dataKey[1].name
		self.type = dataKey[2].name
		self.time = dataValue[0]
		self.value = dataValue[1]		

	def to_json(self):
		data = {
			"device": self.device,
			"source": self.source,
			"type": self.type,
			"time": str(self.time),
			"value": self.value
			}
		return json.dumps(data)

	def __eq__(self, other):
		return self.device == other.device and \
			self.source == other.source and \
			self.type == other.type and \
			self.time == other.time and \
			self.value == other.value


def parse(filename, downloaded):
	print(filename)
	data = list()
	epsTlmReader = EpsTlmFileReader(fileName = filename)
	if not epsTlmReader.readFile():
		print("read file error")
		parser_utils.elogger.error("[EPS] Error reading file " + str(filename))
		return []

	for cmd in EpsTlmData.VALID_COMMANDS:
		for item in epsTlmReader.data[cmd]:
			data.append(EpsMessage(cmd, item))

	return data


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('config', type=str, help='configuration file path')
	parser.add_argument("-f", help="test file path", action="store", dest="filename")
	args = parser.parse_args()

	try:
		conf = parser_utils.Configuration(args.config)
	except:
		print("Configuration file", args.config, "not existent or erroneous")
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
