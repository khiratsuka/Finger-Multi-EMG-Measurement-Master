# onesensor_data_uart.py

import serial
import struct

#マイコンとの通信をスタートさせるコードを送信
def sendStartCode(ser, start_code):
    while True:
        if ser.out_waiting == 0:
            break
    start_code = struct.pack( "B", start_code )
    print(start_code)
    ser.write(start_code)
    ser.flush()


def main():
    pickupParity = 0x00FF

    ser = serial.Serial(
        port = "/dev/tty.usbmodem11203",
        baudrate = 470588,
    )

    sendStartCode(ser, 255)

    while True:
        if ser.in_waiting > 0:
            recv_data = ser.read(1)
            recv_data_val = struct.unpack_from("B",recv_data ,0)[0]
            
            #データのヘッダを検知
            if recv_data_val == 254:
                #データの個数を取得
                data_num = ser.read(1)
                data_num_val = struct.unpack_from("B",data_num ,0)[0]

                #データの取得
                upper2dec = ser.read(1)
                upper2dec = struct.unpack_from("B",upper2dec ,0)[0]
                lower2dec = ser.read(1)
                lower2dec = struct.unpack_from("B",lower2dec ,0)[0]
                recv_pariry = ser.read(1)
                recv_pariry = struct.unpack_from("B",recv_pariry ,0)[0]
                footer = ser.read(1)
                footer = struct.unpack_from("B",footer ,0)[0]

                #パリティを比較
                parity = upper2dec + lower2dec
                parity = parity & pickupParity
                if(parity != recv_pariry or footer != 255):
                    print('error data.\n')
                    continue
                sensor_data = upper2dec * 100 + lower2dec
                print('data > '+ str(sensor_data))

if __name__ == '__main__':
    main()
