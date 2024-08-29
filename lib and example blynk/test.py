import network
import machine
import time
from machine import Pin, PWM
import BlynkLib
import hcsr04
from hcsr04 import HCSR04
from machine import Pin, PWM, time_pulse_us

# Khởi tạo kết nối mạng
ssid = 'Na Na'
password = 'na161102'
staif = network.WLAN(network.STA_IF)
staif.active(True)
staif.connect(ssid, password)

while not staif.isconnected():
    pass
print("Connected", staif.ifconfig())

# Khởi tạo kết nối với Blynk
auth = "9Qap16JIs330fxPPJpV1kCZ9PoGojfM0"
blynk = BlynkLib.Blynk(auth)

# Thiết lập các chân GPIO hoặc pins để điều khiển động cơ (tùy thuộc vào loại thiết bị bạn đang sử dụng)

ENA = machine.PWM(machine.Pin(14), freq=1000)
ENB = machine.PWM(machine.Pin(4), freq=1000)
IN1 = machine.Pin(18, machine.Pin.OUT)
IN2 = machine.Pin(5, machine.Pin.OUT)
IN3 = machine.Pin(17, machine.Pin.OUT)
IN4 = machine.Pin(16, machine.Pin.OUT)
Ledtoi = machine.Pin(0, machine.Pin.OUT)
Ledtoi1 = machine.Pin(27, machine.Pin.OUT)

trigger_pin = machine.Pin(19, machine.Pin.OUT)  # GPIO13 for Trigger
echo_pin = machine.Pin(21, machine.Pin.IN)      # GPIO15 for Echo
sensor = HCSR04(trigger_pin, echo_pin)
servo = machine.PWM(machine.Pin(23), freq=50)
Duration = 0
distance = 0
limit = 50
speed = 1023
forward = 0
backward = 0
left = 0
right = 0
robotInAutoMode = 0
def smartcar():
    measure_distance()

    # Kiểm tra điều kiện khoảng cách và hành động tương ứng
    if distance < limit or distance == 0:
        print("Stopping due to obstacle or no distance measurement")
        carStop()
        if left == 1:
            carLeft()
        elif right == 1:
            carRight()
        elif backward == 1:
            for i in range(10):  # Chạy lùi trong 20 vòng lặp
                carBackward()
                time.sleep(0.1)  # Thời gian chạy lùi trong mỗi vòng lặp là 0.1 giây
                carStop()
        Ledtoi.off()
        Ledtoi1.off()  
    elif v0_state == 1:  # Kiểm tra xem chân ảo V0 có được bật không
        print("Moving forward")
        carForward()
        Ledtoi.on()  # Bật đèn LED khi xe điều khiển về phía trước
        Ledtoi1.on()
    else:
        print("No forward movement detected")
        carStop()
        Ledtoi.off()
        Ledtoi1.off()
    # Đảm bảo rằng chỉ có một hành động điều khiển xe được thực hiện trong mỗi vòng lặp
 

def measure_distance():
    global distance
    trigger_pin.off()         # Tắt Trig
    time.sleep_us(2)
    trigger_pin.on()          # Bật Trig
    time.sleep_us(10)
    trigger_pin.off()         # Tắt Trig
    pulse_duration = time_pulse_us(echo_pin, 1, 30000)  # Đo thời gian sự kiện ở chân Echo trong 30ms
    if pulse_duration > 0:    # Nếu nhận được xung từ Echo
        distance = (pulse_duration / 2) / 29.412        # Tính khoảng cách
        time.sleep(2)
        print("distance: {} cm".format(distance))
    else:
        print("No object detected")
# def Avoid():
#     print("Entering Avoid function")
#     measure_distance()
# 
#     if distance > limit or distance == 0:
#         carForward()
#         Ledtoi.on()  # Bật đèn LED khi xe điều khiển về phía trước
#         Ledtoi1.on()
#         print("Car Forward")
#     else:
#         carStop()
#         time.sleep(0.3)
#         Sensor_left()
# 
#         distance_left = distance
#         Sensor_right()
#         distance_right = distance
# 
#         if distance_right < 30 and distance_left < 30:
#             carBackward()
#             time.sleep(0.3)
#             carStop()
#             time.sleep(0.3)
#         else:
#             if distance_right >= distance_left:
#                 carRight()
#                 time.sleep(0.3)
#                 carStop()
#                 time.sleep(0.3)
#             if distance_right < distance_left:
#                 carLeft()
#                 time.sleep(0.3)
#                 carStop()
#                 time.sleep(0.3)
#         Ledtoi.off()
#         Ledtoi1.off()

    print("Exiting Avoid function")
def Sensor_left():
    servo.duty(125)  # Gửi xung điều chỉnh servo đến góc 180 độ
    time.sleep(1)   # Đợi 1 giây
    measure_distance()  # Gọi hàm đo khoảng cách
    servo.duty(75)   # Gửi xung điều chỉnh servo về góc 90 độ

def Sensor_right():
    servo.duty(25)
    time.sleep(1)
    measure_distance()
    servo.duty(75)
def Servo():
    servo.duty(75)

# Hàm điều khiển xe đi thẳng
def carForward():
    ENA.duty(speed)
    ENB.duty(speed)
    IN1.off()
    IN2.on()
    IN3.off()
    IN4.on()

# Hàm điều khiển xe lùi lại
def carBackward():
    ENA.duty(speed)
    ENB.duty(speed)
    IN1.on()
    IN2.off()
    IN3.on()
    IN4.off()

# Hàm điều khiển xe rẽ trái
def carLeft():
    ENA.duty(0)
    ENB.duty(speed)
    IN1.off()
    IN2.off()
    IN3.off()
    IN4.on()

# Hàm điều khiển xe rẽ phải
def carRight():
    print("Turning right...")
    ENA.duty(speed)
    ENB.duty(0)
    IN1.off()
    IN2.on()
    IN3.off()
    IN4.off()
    print("Right turn completed.")

# Hàm dừng xe
def carStop():
    ENA.duty(0)
    ENB.duty(0)
    IN1.off()
    IN2.off()
    IN3.off()
    IN4.off()

# Xử lý sự kiện từ chân ảo V0 trên Blynk
v0_state = 0  # Khởi tạo biến để lưu trạng thái của chân ảo V0

# Xử lý sự kiện từ chân ảo V0 trên Blynk
@blynk.on("V0")
def handle_virtual_write_0(value):
   if int(value[0]) == 1:
        carForward()  # Lùi lại nếu giá trị từ V1 là 1
    else:
        carStop()
# Xử lý sự kiện từ chân ảo V1 trên Blynk
@blynk.on("V1")
def handle_virtual_write_1(value):
    if int(value[0]) == 1:
        carBackward()  # Lùi lại nếu giá trị từ V1 là 1
    else:
        carStop()  # Dừng lại nếu giá trị từ V1 là 0

# Xử lý sự kiện từ chân ảo V2 trên Blynk
@blynk.on("V2")
def handle_virtual_write_2(value):
    if int(value[0]) == 1:
        carLeft()  # Rẽ trái nếu giá trị từ V2 là 1
    else:
        carStop()  # Dừng lại nếu giá trị từ V2 là 0

# Xử lý sự kiện từ chân ảo V3 trên Blynk
@blynk.on("V3")
def handle_virtual_write_3(value):
    print("Value from V3:", value)
    if int(value[0]) == 1:
        carRight()  # Rẽ phải nếu giá trị từ V3 là 1
    else:
        carStop()  # Dừng lại nếu giá trị từ V3 là 0

# Xử lý sự kiện từ chân ảo V5 trên Blynk
# @blynk.on("V5")
# def handle_virtual_write_5(value):
#     global robotInAutoMode
#     if isinstance(value, list):
#         robotInAutoMode = int(value[0])
#     else:
#         robotInAutoMode = int(value)

while True:
    blynk.run()
#     if robotInAutoMode == 1:
#         Avoid()  # Gọi hàm tránh vật cản nếu robot ở chế độ tự động (giá trị từ V5 là 1)
#     else:
#         pass 
#         # Thực hiện hành động khác khi giá trị là 0
    smartcar()
    measure_distance()
