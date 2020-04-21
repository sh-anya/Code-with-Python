import pika
import uuid
import threading

class OddEvenClient(object):
	def __init__(self):
		#create a connection
		self.connection = pika.BlockingConnection(
								pika.ConnectionParameters(host='localhost'))

		#creating a channel
		self.channel = self.connection.channel()

		#declaring the queue
		queue_c = self.channel.queue_declare(queue='', exclusive=True)
		self.callback_que = queue_c.method.queue

		#inform rabbitmq, which callback function should receive messages from  queue
		self.channel.basic_consume(
				queue = self.callback_que,
				on_message_callback = self.on_response,
				auto_ack = True
			)

	def on_response(self, ch, method, props, body):
		#reply to which request
		if self.corr_id == props.correlation_id:
			self.response = body

	def call(self, num):
		#send the request and get the response
		self.response = None
		self.corr_id = str(uuid.uuid4())

		self.channel.basic_publish(
				exchange = '', 
				routing_key = 'rpc_queue',
				properties = pika.BasicProperties(
						reply_to = self.callback_que,
						correlation_id = self.corr_id,
					),
				body = str(num)
				)

		while self.response is None:
			self.connection.process_data_events()

		return self.response

pobj = OddEvenClient()
while True:
	num = int(input('\nEnter a number : '))
	print('[x] Checking if %d'%num,' is odd/even.')
	response = pobj.call(num)

	print('[x] Response is %r'%response)
