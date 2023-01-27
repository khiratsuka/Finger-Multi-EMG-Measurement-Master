import struct

import serial

ser = serial.Serial(
    port="/dev/tty.usbmodem11203",
    baudrate=470588,
)

flag1 = False


def send():
    while True:
        if ser.out_waiting == 0:
            break
    start_code = 255
    start_code = struct.pack("B", start_code)
    print(start_code)
    ser.write(start_code)
    ser.flush()


send()

while True:
    if ser.in_waiting > 0:
        recv_data = ser.read(1)
        data_num = struct.unpack_from("B", recv_data, 0)[0]
        print(recv_data)
        print(data_num)
