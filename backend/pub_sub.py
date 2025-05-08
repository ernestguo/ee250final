# Member 1: Joel Sedillo
# Member 2: Ernest Guo
import paho.mqtt.client as mqtt
import time
import gps_lib

currid = "0"

# Runs on successful connection
def on_connect(client, userdata, flags, rc):

    # Connect successful messate
    print("Connected to server (i.e., broker) with result code "+str(rc))

    # Subscribe to start and timeout
    client.subscribe("hanwegjasedill/start")
    client.subscribe("hanwegjasedill/timeout")
    
    # Add the custom callbacks by indicating the topic and the name of the callback handle
    client.message_callback_add("hanwegjasedill/start", on_message_from_start)
    client.message_callback_add("hanwegjasedill/timeout", on_message_from_timeout)


# Default callback upon receiving message
def on_message(client, userdata, msg):
    print("Default callback - topic: " + msg.topic + "   msg: " + str(msg.payload, "utf-8"))

# Custom callback, runs after receiving start signal
def on_message_from_start(client, userdata, message):
    global currid

    # Get the id of the run
    currid = message.payload.decode()
    print("ID: " + currid)

    prev_lat = 0
    prev_long = 0
    dist = 0.0
    start_time = 0.0
    end_time = 0.0

    # START TIMING
    data = gps_lib.RMC_Read()
    if data is not None:
        start_time = time.time()
        prev_lat = data[0]
        prev_long = data[1]
    
    while currid != "0" and dist < 0.25:
        # read at 0.05 s intervals
        time.sleep(0.05)
        data = gps_lib.RMC_Read()
        if data is not None:
            end_time = time.time()
            cur_lat = data[0]
            cur_long = data[1]
            # CALCULATE DISTANCE
            dist += 0
        if int(end_time) - int(start_time) > 60: # Auto timeout
            currid != "0"
    
    if currid != "0":
        total = round(end_time - start_time, 3) # Round to 3 dec
        client.publish("hanwegjasedill/end", f"{currid} {total}") #Publish
        currid = "0"
        time.sleep(2)


# Custom callback, runs after receiving timeout signal
def on_message_from_timeout(client, userdata, message):
   global currid
   currid = "0" # Set global run to end


if __name__ == '__main__':
    
    client = mqtt.Client() # create a client object
    client.on_message = on_message # attach default callback
    client.on_connect = on_connect # attach function to be run on connect

    # Connect to client, if successful, on connect is called
    client.connect(host="broker.hivemq.com", port=1883, keepalive=60)

    # Use non-blocking look to check for incoming messages
    client.loop_start()