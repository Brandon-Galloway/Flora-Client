#!/venv/bin/python

import os
import board
import json
import time
import configparser

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from adafruit_seesaw.seesaw import Seesaw
import adafruit_si7021
import adafruit_tsl2591

i2c_bus = board.I2C()
script_dir = os.path.dirname(os.path.abspath(__file__))
certs_dir = os.path.join(script_dir, 'certs')

config = configparser.ConfigParser()
config.read(os.path.join(script_dir,'config.ini'))

class FloraClient:
    def __init__(self, serial_number):
        self.serial_number = serial_number
        # Set Sensors
        self.soil_sensor = Seesaw(i2c_bus, addr=0x36)
        self.atmospheric_sensor = adafruit_si7021.SI7021(i2c_bus)
        self.light_sensor = adafruit_tsl2591.TSL2591(i2c_bus)
        # Set AWS IoT Client
        self.state = 0
        self.client = AWSIoTMQTTClient(config.get('aws','thing_name'))
        self.client.configureEndpoint(config.get('aws','iot_endpoint'), 8883)
        ca_file_path = os.path.join(certs_dir,"AmazonRootCA1.pem")
        private_key_path = os.path.join(certs_dir,"private.key")
        cert_path = os.path.join(certs_dir,"cert.pem")
        self.client.configureCredentials(ca_file_path, private_key_path, cert_path)
        self.client.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
        self.client.configureDrainingFrequency(2)  # Draining: 2 Hz
        self.client.configureConnectDisconnectTimeout(10)  # 10 sec
        self.client.configureMQTTOperationTimeout(5)  # 5 sec
        #self.client.onMessage = self.customOnMessage
        #self.client.subscribeAsync(co2_max_subscription, 1, None)

    # def customOnMessage(self, message):
    #     print(f"Client {self.device_id} received payload {message.payload} from topic {message.topic}.")
    
    def get_sensor_readings(self):
        return {
            "SoilTemperature": int((self.soil_sensor.get_temp()*1.8)+32),
            "AirTemperature": int((self.atmospheric_sensor.temperature*1.8)+32),
            "Humidity": int(self.atmospheric_sensor.relative_humidity),
            "Light": int(self.light_sensor.lux),
            "VisibleLight": self.light_sensor.visible,
            "InfraredLight": self.light_sensor.infrared
        }

    def submit_sensor_data(self):
        payload = {
            "DeviceId": self.serial_number,
            "Timestamp": int(time.time()),
        }
        payload.update(self.get_sensor_readings())
        payload = json.dumps(payload)
        print(f"Device {self.serial_number} sending payload: {payload}")
        self.client.publishAsync("flora/submit", payload, 0)


flora_client = FloraClient(config.get('flora','serial_number'))
flora_client.client.connect()
flora_client.submit_sensor_data()
flora_client.client.disconnect()
