#!/usr/bin/python3

import json
import re
import functools
import argparse

import parser_utils

class LogMessage(parser_utils.JsonMessage):
	def __init__(self, msg, sev, sub, comp, created, downloaded):
		super().__init__()
		if msg is None or sev is None or sub is None or comp is None or created is None or downloaded is None:
			raise Exception('Log message not complete')

		self.message = msg
		self.severity = sev
		self.subsystem = sub
		self.component = comp
		self.createdOn = created
		self.downloadedOn = downloaded

	def to_json(self):
		log = {
			'message': self.message,
			'severity': self.severity,
			'subsystem': self.subsystem,
			'component': self.component,
			'createdOn': self.createdOn,
			'downloadedOn': self.downloadedOn
		}
		return json.dumps(log)

class LogProcessorConfiguration(parser_utils.Configuration):
	def __init__(self, name):
		super().__init__(name)
		self.mappings = self.data['mappings']

def parse(subsystem_mappings, fname, downloaded):
	logs = []
	try:
		f = open(fname, 'r')
	except IOError:
		parser_utils.elogger.error('Error opening file')
		return []

	lines = f.readlines()
	msg = sev = sub = comp = created = None
	for l in lines:
		if l.startswith('PRIORITY='):
			sev = l[9:].strip('\n')
			continue
		if l.startswith('MESSAGE='):
			msg = l[8:].strip('\n')
			continue
		if l.startswith('_SYSTEMD_UNIT='):
			comp = l[14:].strip('\n')
			if comp in subsystem_mappings:
				sub = subsystem_mappings[comp]
			else:
				sub = subsystem_mappings['default']
			continue

		date = l.split(' ')
		if len(date) > 2 and re.match('^' + parser_utils.date_format + '$', date[0]) and re.match('^' + parser_utils.time_format + '$', date[1][:8]):
			try:
				if created is not None:
					logs.append(LogMessage(msg, sev, sub, comp, created, downloaded))
			except Exception as e:
				parser_utils.elogger.error('Parser failed on log at ' + created)

			created = date[0] + 'T' + date[1][:8]
			msg = sev = sub = comp = None

	f.close()
	return logs

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('config', type=str, help='configuration file path')
	args = parser.parse_args()

	try:
		conf = LogProcessorConfiguration(args.config)
	except:
		print('Configuration file', args.config, 'not existant or erroneous')
		exit(-1)

	parser_utils.init_logging(conf.logfile, __name__)
	poster = parser_utils.Poster(conf.url)
	rabbit_client = parser_utils.RabbitMQClient()
	rabbit_client.init(conf.hostname, conf.port, conf.exchange, conf.bindingKey, conf.user, conf.password)

	parsecb = functools.partial(parse, conf.mappings)
	cb = functools.partial(parser_utils.callback, poster, parsecb)
	rabbit_client.start(cb)
