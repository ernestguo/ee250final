# Member 1: Joel Sedillo
# Member 2: Ernest Guo
import paho.mqtt.client as mqtt
import time

currid = 0

# Runs on successful connection
def on_connect(client, userdata, flags, rc):

    # Connect successful message
    print("Connected to server (i.e., broker) with result code "+str(rc))

    # Subscribe to start and timeout
    client.subscribe("hanwengjasedill/end")
    
    # Add the custom callbacks by indicating the topic and the name of the callback handle
    client.message_callback_add("hanwengjasedill/end", on_message_from_end)


# Default callback upon receiving message
def on_message(client, userdata, msg):
    print("Default callback - topic: " + msg.topic + "   msg: " + str(msg.payload, "utf-8"))

# Custom callback, runs after receiving end signal
def on_message_from_end(client, userdata, message):
    global currid

    msg = message.payload.decode().split()
    run_id = int(msg[0])
    run_time = msg[1]
    
    print(f"Received data: {run_id} {run_time}")
    print(f"{currid} {run_id}")
    if run_id == currid:
        print("Ids match")
        currid = 0


if __name__ == '__main__':
    
    client = mqtt.Client() # create a client object
    client.on_message = on_message # attach default callback
    client.on_connect = on_connect # attach function to be run on connect

    # Connect to client, if successful, on connect is called
    client.connect(host="broker.hivemq.com", port=1883, keepalive=60)

    print("Starting test file")
    time.sleep(2)

    print("Simulating test run")
    curr_t = int(time.time())
    currid = curr_t
    client.publish("hanwengjasedill/start", f"{currid}")
    print("Published start time")
    # Use non-blocking loop to check for incoming messages
    client.loop_start()

    while (int(time.time()) - curr_t < 20):
        pass

    if currid != 0:
        client.publish("hanwengjasedill/timeout", f"{currid}")
        print("Published timeout")
        currid = 0
        time.sleep(2)
