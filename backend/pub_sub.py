# Member 1: Joel Sedillo
# Member 2: Ernest Guo
import paho.mqtt.client as mqtt
import time
from threading import Thread
from threading import Event
import gps_lib

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

# Custom callback, runs after receiving timeout signal
def on_message_from_timeout(client, userdata, message):
   print("Received client timeout")
   e.set()


# DEFINE TIMING FUNCTIONS
# Custom thread class to run the timing
class TimingThread(Thread):
    def __init__(self, event=None, target=None, args=()):
        super(TimingThread, self).__init__(target=target, args=args)
        self.event = event
        self._target = target
        self._args = args

    def run(self):
        self._target(*self._args)

# Function to run the timing
def run_timing(id):
    global e

    print("Starting run")
    print(f"ID: {id}")

    start_time = 0.0
    last_time = 0.0
    dist = 0.0
    last_lat = 0.0
    last_long = 0.0

    # START TIMING
    start_time = time.time()
    x = gps_lib.RMC_Read()
    if x is not None:
        data = list(x)
        last_lat = float(data[0])
        last_long = float(data[1])

    while (not e.is_set()) and (dist < 0.25):
        e.wait(0.02)
        last_time = time.time()
        x = gps_lib.RMC_Read()
        if x is not None:
            data = list(x)
            dist += calc_dist(float(data[0]), float(data[1]), last_lat, last_long)
            last_lat = float(data[0])
            last_long = float(data[1])
            print(f"Distance: {dist} miles")
            print(f"Lat: {last_lat} Long: {last_long}")
        if last_time - start_time > 60: # Auto timeout
            print("Server timeout, ending run")
            return
        
    if e.is_set():
        print("Event set, ending run")
        return

    total = round(last_time - start_time, 3) # Round to 3 dec
    client.publish("hanwengjasedill/end", f"{id} {total}") #Publish
    print(f"Published time {id} {total}")


# Function to calculate distance between two lat/long points
def calc_dist(lat, long, last_lat, last_long):
    # Haversine formula to calculate distance between two lat/long points
    # Radius of the Earth in miles
    R = 3958.8
    dlat = (lat - last_lat) * (3.141592653589793 / 180.0)
    dlong = (long - last_long) * (3.141592653589793 / 180.0)
    a = (pow((pow(dlat, 2) + pow((dlong), 2)), 0.5))
    c = 2 * (3.141592653589793 / 180.0) * a
    # distance in miles
    return R * c


# Main function to run the MQTT client
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
