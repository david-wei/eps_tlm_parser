#!/usr/bin/python3

import unittest
import log_processor
import parser_utils

from datetime import datetime, timedelta
import string
import random
import json
import os

class TestLogProcessor(unittest.TestCase):
	url = 'http://localhost:8080/logbook/logs'

	def test_logmessage(self):
		[msg, sev, sub, comp, cr, do] = self.__get_random_log()
		log = log_processor.LogMessage(msg, sev, sub, comp, cr, do)
		logjs = json.dumps({
			'message': msg,
			'severity': sev,
			'subsystem': sub,
			'component': comp,
			'createdOn': cr,
			'downloadedOn': do			
		})
		self.assertEqual(log.to_json(), logjs)


	# def test_logger(self):
	# 	log = self.__to_log(self.__get_random_log())
	# 	logger = log_processor.Logger(self.url)
	# 	rcode = logger.post(log)
	# 	self.assertEqual(201, rcode)

	# def test_logger_multiple(self):
	# 	nlogs = 10
	# 	logs = [self.__to_log(self.__get_random_log()) for _ in range(nlogs)]
	# 	logger = log_processor.Logger(self.url)
	# 	ret = logger.post_multiple(logs)
	# 	for i in ret:
	# 		self.assertEqual(201, i)

	def test_parser_ok(self):
		fname = 'temp.txt'
		logs, dt = self.__create_logfile(fname)
		plogs = log_processor.parse(fname, self.__current_time(dt))

		self.assertEqual(len(logs), len(plogs))
		for a, b in zip(logs, plogs):
			self.assertEqual(a, b)
		os.remove(fname)

	def test_parser_bad_log(self):
		fname = 'temp.txt'
		logs, dt = self.__create_logfile(fname, badidx=3, badlog='MESSAGE=asd:qwe:zxc')
		plogs = log_processor.parse(fname, self.__current_time(dt))
		self.assertEqual(0, len(plogs))
		os.remove(fname)

	def test_parser_bad_date(self):
		parser_utils.init_logging('test.log', __name__)
		fname = 'temp.txt'
		logs, dt = self.__create_logfile(fname, badidx=3, baddate='201-33-28 00:00:00')
		plogs = log_processor.parse(fname, self.__current_time(dt))
		self.assertEqual(0, len(plogs))
		os.remove(fname)

	def test_check_message(self):
		self.assertRaises(Exception, parser_utils.check_rabbitmq_message, 'asd qwe zxc')
		self.assertRaises(Exception, parser_utils.check_rabbitmq_message, 'asd qwe')
		self.assertRaises(Exception, parser_utils.check_rabbitmq_message, 'test-log_processor.py qwe')
		parser_utils.check_rabbitmq_message('test-log_processor.py 2017-03-27T15:08:00')

	def __create_logfile(self, fname, badidx = -1, badlog = '', baddate = ''):
		nlogs = 10
		logs = []
		with open(fname, 'w') as f:
			dt = datetime.now()
			for i in range(nlogs):
				ndt = dt - timedelta(seconds=i)
				logs.append(self.__to_log(self.__get_random_log(ndt, dt)))
				f.write(self.__to_logfile_string(logs[-1], ndt, badlog if badidx == i else '', baddate if badidx == i else ''))
		return logs, dt

	def __to_logfile_string(self, log, ct, badlog, baddate):
		s = 'PRIORITY=6\n'
		s += ('MESSAGE=' + log.subsystem + ':' + log.component + ':' + log.message + ':' + log.severity if not badlog else badlog) + '\n'
		s += (self.__current_time_logfile(ct) if not baddate else baddate) + '\n'
		return s

	def __to_log(self, log):
		return log_processor.LogMessage(log[0], log[1], log[2], log[3], log[4], log[5])

	def __get_random_log(self, ct=datetime.now(), dt=datetime.now()):
		return [self.__str_generator(10), 'DEBUG', self.__str_generator(3), self.__str_generator(3), self.__current_time(ct), self.__current_time(dt)]

	def __str_generator(self, size=6, chars=string.ascii_uppercase):
		return ''.join(random.choice(chars) for _ in range(size))


	def __current_time(self, dt):
		return dt.strftime('%Y-%m-%dT%H:%M:%S')

	def __current_time_logfile(self, dt):
		return dt.strftime('%Y-%m-%d %H:%M:%S.%f CET')

if __name__ == '__main__':
	unittest.main()
