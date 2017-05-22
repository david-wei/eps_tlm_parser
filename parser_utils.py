from abc import ABC, abstractmethod
import requests
import datetime
import pika
import re
import os
import json
import logging

date_format = '\d{4}-(0?[1-9]|1[012])-(0?[1-9]|[12][0-9]|3[01])'
time_format = '([0-9]+):([0-5][0-9]):([0-5][0-9])'

def init_logging(fname, logname):
	global elogger
	logging.basicConfig(filename=fname)
	elogger = logging.getLogger(logname)

class JsonMessage(ABC):
	def __init__(self):
		self.endpoint = ''

	@abstractmethod
	def to_json(self):
		pass

class UnixDateReader():
	def getTimestamp(self, seconds):
		result = datetime.datetime.utcfromtimestamp(
			int(seconds - 60 * 60 * 2)).strftime('%Y-%m-%dT%H:%M:%S')
		return result

class Poster:
	def __init__(self, url):
		self.url = url
		self.headers = {'content-type': 'application/json'}

	def post(self, msg):
		try:
			return requests.post(self.url + msg.endpoint, data=msg.to_json(), headers=self.headers).status_code
		except Exception as e:
			elogger.error(str(e))
			return -1

	def post_multiple(self, msgs):
		return [self.post(x) for x in msgs]

class RabbitMQClient:
	def init(self, hostname, port, exchange, queue, user, pas):
		self.queue = queue
		credentials = pika.PlainCredentials(user, pas)
		self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname, port=port, credentials=credentials))
		self.channel = self.connection.channel()
		self.channel.queue_declare(queue=queue, durable=True)
		self.channel.queue_bind(queue=queue, exchange=exchange, routing_key=queue)

	def start(self, callback):
		self.channel.basic_consume(callback, self.queue, no_ack=True)
		self.channel.start_consuming()

def check_rabbitmq_message(body):
	msg = body.split(' ')
	if len(msg) != 2:
		raise Exception('Incorrect number of parameters received through rabbitmq ' + msg)
	if not os.path.isfile(msg[0]):
		raise Exception(msg[0] + ' is not a valid file path')
	if not re.match('^' + date_format + 'T' + time_format + '$', msg[1]):
		raise Exception(msg[1] + ' is not a valid date format')

def callback(poster, parsecb, ch, method, prop, body):
	msg = body.decode('utf-8')
	try:
		check_rabbitmq_message(msg)
	except Exception as e:
		elogger.error(e.args[0])
		return

	try:
		msg = msg.split(' ')
		logs = parsecb(msg[0], msg[1])
	except Exception as e:
		elogger.error('Parser failed on file ' + msg[0] + ' ' + str(e))
		return
	poster.post_multiple(logs)

class Configuration():
	def __init__(self, fname):
		with open(fname) as f:
			self.data = json.load(f)

		recv = self.data['receiver']
		self.hostname = recv['hostname']
		self.port = recv['port']
		self.exchange = recv['exchange']
		self.bindingKey = recv['bindingKey']
		self.user = recv['user']
		self.password = recv['pass']

		self.url = self.data['url']
		self.logfile = self.data['logfile']
