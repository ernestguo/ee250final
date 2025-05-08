import time, threading, serial, pynmea2
from geopy.distance import geodesic
import paho.mqtt.client as mqtt

# Config
GPS_PORT    = '/dev/ttyAMA0'
GPS_BAUD    = 9600
MQTT_HOST   = 'localhost'
MQTT_PORT   = 1883
TOPIC_START = 'hanwegjasedill/start'
TOPIC_END   = 'hanwegjasedill/end'
# (backend does not need to subscribe to timeout)

# State
latest = None
start_coords = None
start_id     = None
start_ts     = None
tracking     = False

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    print(f"MQTT connected rc={rc}")
    client.subscribe(TOPIC_START)

def on_message(client, userdata, msg):
    global start_coords, start_id, start_ts, tracking
    if msg.topic==TOPIC_START:
        try:
            sid = int(msg.payload.decode())
        except:
            return
        if latest is None:
            print("No GPS fix; cannot start.")
            return
        start_id     = sid
        start_coords = latest
        start_ts     = time.time()
        tracking     = True
        print(f"Started id={start_id} at {start_coords}")

# Setup MQTT
mc = mqtt.Client()
mc.on_connect = on_connect
mc.on_message = on_message
mc.connect(MQTT_HOST, MQTT_PORT)
threading.Thread(target=mc.loop_forever, daemon=True).start()

# GPS reader thread
def gps_reader():
    global latest, start_coords, start_id, start_ts, tracking
    ser = serial.Serial(GPS_PORT, GPS_BAUD, timeout=1)
    while True:
        line = ser.readline().decode('ascii',errors='ignore')
        if line.startswith(('$GPRMC','$GPGGA')):
            try:
                msg = pynmea2.parse(line)
                if msg.latitude and msg.longitude:
                    latest = (msg.latitude, msg.longitude)
                    if tracking and start_coords:
                        dist = geodesic(start_coords, latest).miles
                        if dist>=0.25:
                            elapsed = time.time()-start_ts
                            payload = f"{start_id} {elapsed:.3f}"
                            mc.publish(TOPIC_END, payload)
                            print(f"Published end: {payload}")
                            tracking=False
            except Exception as e:
                print("GPS error:", e)
        time.sleep(0.1)

if __name__=='__main__':
    threading.Thread(target=gps_reader, daemon=True).start()
    print("Backend running, waiting for start.")
    while True:
        time.sleep(1)