# Member 1: Joel Sedillo
# Member 2: Ernest Guo
import paho.mqtt.client as mqtt
import time
from threading import Thread
from threading import Event

e = None

# Runs on successful connection
def on_connect(client, userdata, flags, rc):

    # Connect successful message
    print("Connected to server (i.e., broker) with result code "+str(rc))

    # Subscribe to start and timeout
    client.subscribe("hanwengjasedill/start")
    client.subscribe("hanwengjasedill/timeout")
    
    # Add the custom callbacks by indicating the topic and the name of the callback handle
    client.message_callback_add("hanwengjasedill/start", on_message_from_start)
    client.message_callback_add("hanwengjasedill/timeout", on_message_from_timeout)


# Default callback upon receiving message
def on_message(client, userdata, msg):
    print("Default callback - topic: " + msg.topic + "   msg: " + str(msg.payload, "utf-8"))


# Custom callback, runs after receiving start signal
def on_message_from_start(client, userdata, message):
    global e

    print("Received start")

    # Get the id of the run
    currid = int(message.payload.decode())

    # RUN THE TIMING
    e = Event()
    t = TimingThread(event=e, target=run_timing, args=(currid,))
    t.start()

class TimingThread(Thread):
    def __init__(self, event=None, target=None, args=()):
        super(TimingThread, self).__init__(target=target, args=args)
        self.event = event
        self._target = target
        self._args = args

    def run(self):
        self._target(*self._args)


def run_timing(id):
    global e

    print("Starting run")
    print(f"ID: {id}")

    dist = 0.0
    start_time = 0.0
    last_time = 0.0

    # START TIMING
    start_time = time.time()

    while (not e.is_set()) and (dist < 0.25):
        e.wait(0.02)
        last_time = time.time()
        dist += 0.0005 # Simulate distance traveled
        if last_time - start_time > 60: # Auto timeout
            print("Server timeout, ending run")
            return
        
    if e.is_set():
        print("Event set, ending run")
        return

    total = round(last_time - start_time, 3) # Round to 3 dec
    client.publish("hanwengjasedill/end", f"{id} {total}") #Publish
    print(f"Published time {id} {total}")


# Custom callback, runs after receiving timeout signal
def on_message_from_timeout(client, userdata, message):
   print("Received client timeout")
   e.set()


if __name__ == '__main__':
    client = mqtt.Client() # create a client object
    client.on_message = on_message # attach default callback
    client.on_connect = on_connect # attach function to be run on connect

    # Connect to client, if successful, on connect is called
    client.connect(host="broker.hivemq.com", port=1883, keepalive=60)

    # Use non-blocking look to check for incoming messages
    client.loop_start()

    print("Starting test file")

    while True:
        pass
