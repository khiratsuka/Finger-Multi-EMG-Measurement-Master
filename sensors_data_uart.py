# sensors_data_uart.py

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
    upper2dec = []
    lower2dec = []
    paritydec = 0
    raw_data = [[], [], [], [], [], [], [], []]
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
                for i in range(data_num_val - 1):
                    upper2hex = ser.read(1)
                    upper2dec.append(struct.unpack_from("B",upper2hex ,0)[0])
                    lower2hex = ser.read(1)
                    lower2dec.append(struct.unpack_from("B",lower2hex ,0)[0])
                    paritydec = upper2dec[i] + lower2dec[i]
                
                #パリティの取得
                recv_pariryhex = ser.read(1)
                recv_parirydec = struct.unpack_from("B",recv_pariryhex ,0)[0]
                paritydec = paritydec & pickupParity
                
                #フッタの確認
                footer = ser.read(1)
                footer = struct.unpack_from("B",footer ,0)[0]

                #パリティを比較
                if(paritydec != recv_parirydec or footer != 255):
                    print('error data.\n')
                    continue

                #実際のデータに変換して代入
                for i in range(data_num_val - 1):
                    raw_data[i].append(upper2dec[i] * 100 + lower2dec)
                

if __name__ == '__main__':
    main()
