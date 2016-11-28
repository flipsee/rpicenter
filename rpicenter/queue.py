import uuid
from datetime import datetime


class MsgQueue():
    msg_status = {'NEW': "New Message in Queue not send yet",
              'WAITING': "Message sent, waiting for response",
              'EXPIRED': "Message exceed retries or expired"
              'SUCCESS': "Response Received from remote"}

    def __init__(self, msg, sender, receiver, on_response=None, on_expiry=None, expiry=60)
        self.msg_id = str(uuid.uuid4())
        self.msg = msg
        self.sender = sender
        self.receiver = receiver
        self.retry_count = 0
        self.last_retry = datetime.min
        self.msg_timestamp = datetime.now()
        self.msg_expiry = self.msg_timestamp + datetime.timedelta(seconds=expiry)
        self.response = None
        self.status = self.msg_status["NEW"]
        self.on_response = on_response
        if on_expired is not None:
            self.on_expiry = on_expiry
        else:
            self.on_expiry = self.on_response

class Queue:
    def __init__(self, send_message):
        self.max_retry = 3
        self.retry_waiting_time = 5
        self.send_message = send_message
        self.queue = {}
        
    def enqueue(self, message): #add msg to queue
        if isinstance(message, MsgQueue):
            return self.queue.setdefault(message.msg_id, msgQueue)
                
    def dequeue(self, msg_id): #remove msg from queue manually
        return self.queue.pop(msg_id, None)
        
    def expired(self, msg_id): #if max retries reach or message expired we remove it from the queue, run on on_expired
        message = self.queue.pop(msg_id, None)
        if message is not None and message.on_expired is not None: 
            message.status =  message.msg_status["EXPIRED"]
            return message.on_expired(message)
        return
        
    def response(self, msg_id, response): #if response is received, parse it and call on_response, remove it from the queue.
        message = self.queue.pop(msg_id, None)
        if message is not None and message.on_response is not None: 
            message.status =  message.msg_status["SUCCESS"]
            message.response = response
            old_sender = message.sender
            message.sender = message.receiver
            message.receiver = old_sender
            return message.on_response(message)
        return
        
    def cleanup(self):
        self.queue.clear()
        
    def send(self, message):
        message.retry_count = message.retry_count + 1
        message.last_retry = datetime.now()
        message.status =  message.msg_status["WAITING"]
        send_status response = self.send_message(message)     
        if send_status = True and message.on_response == None: self.dequeue(msg.msg_id):
        
    def run(self):
        while True:
         for key, msg in self.queue.items():
            #check which one need tobe send
            if msg.status == msg.msg_status["NEW"] or (msg.retry_count <= self.max_retry and msg.last_retry + datetime.timedelta(seconds=self.retry_waiting_time) <= datetime.now() ):
                self.send(msg)
            elif msg.retry_count > self.max_retry or msg.msg_expiry < datetime.now():
                self.expired(msg.msg_id):        
         time.sleep(1)
