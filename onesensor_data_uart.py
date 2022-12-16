# onesensor_data_uart.py

import serial
import struct
import time
import matplotlib.pyplot as plt

import utils

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
    data_num = []
    upper2dec = []
    lower2dec = []
    recv_pariry = []
    footer = []
    csvdata = []
    data = []
    first_receive = True
    
    ser = serial.Serial(
        port = "/dev/tty.usbmodem1403",
        baudrate = 470588,
    )
    
    #Enterキーが押されたら開始する
    while True:
        _ = input('Press enter key to start.')
        break

    #通信開始合図を送る
    sendStartCode(ser, 255)

    #時間計測用
    start_time = time.perf_counter()

    while True:
        #2秒間測定したら終える
        if time.perf_counter() - start_time > 2:
            break
        
        #データが来た時
        if ser.in_waiting > 0:
            if first_receive:
                first_receive = False
                start_time = time.perf_counter()
            
            recv_data = ser.read(1)
            recv_data_val = struct.unpack_from("B",recv_data ,0)[0]
            
            #データのヘッダを検知
            if recv_data_val == 254:
                #データ取得
                data_num.append(ser.read(1))
                upper2dec.append(ser.read(1))
                lower2dec.append(ser.read(1))
                recv_pariry.append(ser.read(1))
                footer.append(ser.read(1))

    #受け取ったデータをバイナリから数値へ変換
    for i in range(len(data_num)):
        data_num[i]    = struct.unpack_from("B",data_num[i] ,0)[0]
        upper2dec[i]   = struct.unpack_from("B",upper2dec[i] ,0)[0]
        lower2dec[i]   = struct.unpack_from("B",lower2dec[i] ,0)[0]
        recv_pariry[i] = struct.unpack_from("B",recv_pariry[i] ,0)[0]
        footer[i]      = struct.unpack_from("B",footer[i] ,0)[0]

    for i in range(len(recv_pariry)):
        #データ長をを揃える、長いデータは後ろをカット
        if i >= 8500:
            break

        #パリティを計算
        parity = upper2dec[i] + lower2dec[i]
        parity = parity & pickupParity

        #パリティが違っていればエラーデータとしてデータを全て捨てる
        if(parity != recv_pariry[i] or footer[i] != 255):
            print('error data.\n')
            return -1
        
        #データを復元してリストへ追加
        sensor_data = upper2dec[i] * 100 + lower2dec[i]
        sensor_data = 3.3 * sensor_data / 4096
        csvdata.append(str(sensor_data)+'\n')
        data.append(sensor_data)
    
    filename = utils.setFilePath('single_data')
    utils.outputCsvFile(filename, csvdata)

    print('length > ' + str(len(data)))
    plt.plot(data)
    plt.show()

if __name__ == '__main__':
    main()
