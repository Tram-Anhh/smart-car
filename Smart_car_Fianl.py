import network
import machine
import time
from machine import Pin, PWM
import hcsr04
from hcsr04 import HCSR04
from umqtt.simple import MQTTClient
import ubinascii

ssid = 'Redmi'
password = '12345678'
staif = network.WLAN(network.STA_IF)
staif.active(True)
staif.connect(ssid, password)

while not staif.isconnected():
    pass
print("Connected", staif.ifconfig())


ENA = machine.PWM(machine.Pin(5), freq=15)
ENB = machine.PWM(machine.Pin(2), freq=15)
IN1 = machine.Pin(17, machine.Pin.OUT)
IN2 = machine.Pin(16, machine.Pin.OUT)
IN3 = machine.Pin(4, machine.Pin.OUT)
IN4 = machine.Pin(0, machine.Pin.OUT)
Ledtoi = machine.Pin(15, machine.Pin.OUT)
Ledtoi1 = machine.Pin(27, machine.Pin.OUT)
ultrasonic = HCSR04(trigger_pin=19, echo_pin=21, echo_timeout_us=1000000)
servo = machine.PWM(machine.Pin(23), freq=50)

distance = 0
limit = 70
speed = 255
forward = 0
backward = 0
left = 0
right = 0
robotInAutoMode = 0

def smartcar():
    global distance, backward, left, right, forward
    
    measure_distance()

    if distance < limit or distance == 0:
        carStop()
        Ledtoi.on()
        Ledtoi1.on()
   
        if (forward == 1 or left == 1 or right == 1) and distance < limit:
            carStop()
            Ledtoi.on()  # Bật đèn cảnh báo khi gặp vật cản
            Ledtoi1.on()

    elif backward == 1:  # Lệnh điều khiển lùi riêng
        carBackward()
        Ledtoi.off()
        Ledtoi1.off()

    elif left == 1 and distance < limit:  # Kiểm tra rẽ trái và gặp vật cản
        carStop()
        Ledtoi.on()
        Ledtoi1.on()

    elif right == 1 and distance < limit:  # Kiểm tra rẽ phải và gặp vật cản
        carStop()
        Ledtoi.on()
        Ledtoi1.on()

    elif forward == 1 and distance >= limit:  # Điều khiển tiến khi không gặp vật cản
        carForward()
        Ledtoi.off()
        Ledtoi1.off()
    else:
        Ledtoi.off()
        Ledtoi1.off()

  

def Avoid():
    print("Entering Avoid function")
    measure_distance()

    if distance > limit or distance == 0:
        carForward()
        print("Car Forward")
        Ledtoi.off()
        Ledtoi1.off()
    else:
        Ledtoi.on()
        Ledtoi1.on()
        carStop()
        time.sleep(0.3)
        Sensor_left()

        distance_left = distance
        Sensor_right()
        distance_right = distance

        if distance_right < 30 and distance_left < 30:
            carBackward()
            time.sleep(2)
            carStop()
            time.sleep(0.3)
        else:
            if distance_right >= distance_left:
                carRight()
                time.sleep(1)  # Chờ 1 giây để rẽ phải
            else:
                carLeft()
                time.sleep(1)  # Chờ 1 giây để rẽ trái

            # Kiểm tra vật cản sau khi rẽ phải hoặc trái
            measure_distance()
            if distance < limit:  # Nếu gặp vật cản, dừng xe
                carStop()

    print("Exiting Avoid function")



    
def Sensor_left():
    servo.duty(125)
    time.sleep(1)
    measure_distance()
    servo.duty(75)

def Sensor_right():
    servo.duty(25)
    time.sleep(1)
    measure_distance()
    servo.duty(75)

def Servo():
    servo.duty(75)

def carForward():
    ENA.duty(speed)
    ENB.duty(speed)
    IN1.off()
    IN2.on()
    IN3.off()
    IN4.on()

def carBackward():
    ENA.duty(speed)
    ENB.duty(speed)
    IN1.on()
    IN2.off()
    IN3.on()
    IN4.off()

def carLeft():
    ENA.duty(speed)
    ENB.duty(speed)
    IN1.off()
    IN2.off()
    IN3.off()
    IN4.on()

def carRight():
    ENA.duty(speed)
    ENB.duty(speed)
    IN1.off()
    IN2.on()
    IN3.off()
    IN4.off()

def carStop():
    ENA.duty(0)
    ENB.duty(0)
    IN1.off()
    IN2.off()
    IN3.off()
    IN4.off()

SERVER = "broker.hivemq.com"
USERNAME = "anhnguyen161102@gmail.com" 
PASSWORD = "6rNcc8xLf#!xKH_"  
CLIENT_ID = ubinascii.hexlify(machine.unique_id())
MQTT_TELEMETRY_TOPIC    = "Distance"
MQTT_CONTROL_TOPIC      = "Control"
def on_message(topic, msg):
    global robotInAutoMode, left, right, backward, forward
    command = msg.decode()
    print("Received message:", command)
    
    if command == "backward":
        backward = 1
        left = 0
        right = 0
        forward = 0
    elif command == "left":
        left = 1
        right = 0
        backward = 0
        forward = 0
    elif command == "right":
        right = 1
        left = 0
        backward = 0
        forward = 0
    elif command == "stop":
        left = 0
        right = 0
        backward = 0
        forward = 0
    elif command == "forward":
        forward = 1
        left = 0
        right = 0
        backward = 0
    elif command == "auto":
        robotInAutoMode = 1
    elif command == "manual":
        robotInAutoMode = 0
    else:
        print("Unknown command")
    if command != "left":
        left = 0
    if command != "right":
        right = 0
    if command != "backward":
        backward = 0
    if command != "forward":
        forward = 0

def mqtt_main():
    global mqtt_client

    mqtt_client = MQTTClient(CLIENT_ID, SERVER)
    try:
        mqtt_client.username_pw_set(USERNAME, PASSWORD)
        mqtt_client.connect()
        print(f"Connected to MQTT Broker :: {SERVER}")
        mqtt_client.set_callback(on_message)
        mqtt_client.subscribe(MQTT_CONTROL_TOPIC)

        while True:
            try:
                mqtt_client.check_msg()
                measure_distance()
                
            except Exception as e:
                print(f"Error in main loop: {e}")
    except Exception as e:
        print(f"MQTT Connection Error: {e}")
        
def measure_distance():
    global distance
    distance = ultrasonic.distance_cm()
    print('Distance:', distance, 'cm')
    
    try:
        if mqtt_client:
            mqtt_client.publish(MQTT_TELEMETRY_TOPIC, str(distance).encode(), qos=1)
    except Exception as e:
        print("Error publishing telemetry data:")
def main():
    global  mqtt_client,robotInAutoMode, smartcar
    mqtt_client = MQTTClient(CLIENT_ID, SERVER)
    mqtt_client.connect()
    print(f"Connected to MQTT Broker :: {SERVER}")
    mqtt_client.set_callback(on_message)
    print(f"Subscribed to topic: {MQTT_CONTROL_TOPIC}")
    mqtt_client.subscribe(MQTT_CONTROL_TOPIC)
    while True:
        mqtt_client.check_msg()
        if robotInAutoMode == 1:
            Avoid()
        else:
            carStop()
            if left == 1:
                carLeft()
            elif right == 1:
                carRight()
            elif backward == 1:
                carBackward()
            elif forward == 1:
                if distance > limit:  # Kiểm tra điều kiện trước khi tiến lên
                    carForward()
                else:
                    carStop()  # Dừng xe khi gặp vật cản
                    forward == 0

        smartcar()
        measure_distance()
        

if __name__ == "__main__":
    main()



