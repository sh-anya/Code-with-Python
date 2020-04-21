import pika

#create connection
connection = pika.BlockingConnection(pika.ConnectionParameters(
					host = 'localhost'
				))

#create channel
channel = connection.channel()

#declare queue
channel.queue_declare(queue='rpc_queue')

def odd_even_check(num):
	'''
		Purpose : check if a number is odd/even
		Parameters : 
			- num : number
		Returns : 
			- 'even', if number is even
			- 'odd', otherwise
	'''
	if (num % 2) == 0:
		return 'EVEN'
	
	else:
		return 'ODD'

def on_request(ch, method, props, body):
	#what should be done when you get a request?

	num = int(body)
	print('[x] Request to check if %s '%num,' is odd/even...')

	#compute the response
	response = odd_even_check(num)

	#publish the response back to queue
	ch.basic_publish(
						exchange = '',
						routing_key = props.reply_to,
						properties = pika.BasicProperties(
										correlation_id = props.correlation_id),
						body = str(response)
					)
	ch.basic_ack(delivery_tag = method.delivery_tag)

channel.basic_consume(queue='rpc_queue', on_message_callback=on_request)
print("[x] Waiting for requests...")
channel.start_consuming()

