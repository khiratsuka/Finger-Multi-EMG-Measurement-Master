# sensors_data_uart.py

import serial
import struct
import time
import os
import matplotlib.pyplot as plt

import utils
import recv_test_data
from settings import *


#マイコンとの通信をスタートさせるコードを送信
def sendStartCode(ser, start_code):
    while True:
        if ser.out_waiting == 0:
            break
    start_code = struct.pack( "B", start_code )
    ser.write(start_code)
    ser.flush()


def main():
    #受信データ格納用
    upper2hex = [[], [], [], [], [], [], [], []]
    lower2hex = [[], [], [], [], [], [], [], []]
    upper2dec = [[], [], [], [], [], [], [], []]
    lower2dec = [[], [], [], [], [], [], [], []]
    recv_pariry = []
    footer = []

    #パリティ計算用
    pickupParity = 0x00FF

    #データ保存用
    data = [[], [], [], [], [], [], [], []]
    csv_data = [[], [], [], [], [], [], [], []]
    id_num = -1

    #フラグ
    first_receive = True
    
    #データ保存フォルダの設定
    utils.datasetFolderCheck()

    #どの指のデータにするか選択する
    while True:
        print('< thumb:0, index:1, middle:2, ring:3, pinkie:4 >')
        id_num_str = input('ID > ')
        id_num = int(id_num_str)
        if id_num > 4 or id_num < 0:
            print('ERROR: input numv is out of index')
        else:
            print('select label is [{}]'.format(LABEL_NAMES[id_num]))
            break
    
    #通常時
    if not DEBUG:
        #UART通信の初期設定
        #接続時に"ls /dev/tty.usb*"でポート番号をチェックする
        ser = serial.Serial(
            port = "/dev/tty.usbmodem11203",
            baudrate = 470588,
        )

        #通信開始合図を送信
        sendStartCode(ser, 255)

        #時間計測用
        start_time = time.perf_counter()
        while True:
            #2sec測定したら終了
            if time.perf_counter() - start_time > DATA_MEASURING_SEC:
                break

            if ser.in_waiting > 0:
                #先頭データを受信した時間を記録
                if first_receive:
                    print('< start measurement >')
                    first_receive = False
                    start_time = time.perf_counter()
                
                #データを受信
                recv_data = ser.read(1)
                recv_data_val = struct.unpack_from("B",recv_data ,0)[0]
                
                #データのヘッダを検知
                if recv_data_val == 254:
                    #データの個数を取得、バイナリから変換
                    data_num = ser.read(1)
                    data_num = struct.unpack_from("B",data_num ,0)[0]

                    #データの取得
                    for i in range(data_num - 1):
                        upper2hex[i].append(ser.read(1))
                        lower2hex[i].append(ser.read(1))
                    
                    #パリティの取得
                    recv_pariry.append(ser.read(1))
                    
                    #フッタの取得
                    footer.append(ser.read(1))
    
    #デバッグ時
    if DEBUG:
        upper2hex, lower2hex, recv_pariry, footer= recv_test_data.test()

    #受信データをバイナリから数値へ変換
    for i in range(len(upper2hex)):
        for upper_hex_data in upper2hex[i]:
            upper2dec[i].append(struct.unpack_from("B",upper_hex_data ,0)[0])
        for lower_hex_data in lower2hex[i]:
            lower2dec[i].append(struct.unpack_from("B",lower_hex_data ,0)[0])
    for i in range(len(footer)):
        recv_pariry[i] = struct.unpack_from("B",recv_pariry[i] ,0)[0]
        footer[i]      = struct.unpack_from("B",footer[i] ,0)[0]
    
    #パリティを計算
    for i in range(len(footer)):
        parity = 0
        for j in range(len(upper2dec)):
            parity = parity + upper2dec[j][i] + lower2dec[j][i]
        parity = parity & pickupParity
        
        #パリティが違っていればエラーデータとしてデータを全て捨てる
        if(parity != recv_pariry[i] or footer[i] != 255):
            print('ERROR: broken data\n')
            return -1
    
    #データを復元してリストへ追加
    for i in range(len(upper2dec)):
        for j in range(len(upper2dec[i])):
            #データの最大長より超えるデータは捨てる
            if j >= MAX_DATA_LENGTH:
                break

            sensor_data = upper2dec[i][j] * 100 + lower2dec[i][j]
            sensor_data = 3.3 * sensor_data / 4096
            csv_data[i].append(str(sensor_data) + '\n')
            data[i].append(sensor_data)
        
        #データの長さが足りない or データが長すぎる場合は捨てる
        if not len(data[i]) == MAX_DATA_LENGTH:
            print('ERROR: save data length({}) is not equal MAX_DATA_LENGTH({})'.format(len(data[i]), MAX_DATA_LENGTH))
            return -1
    
    #データの書き込み
    for ch in range(len(csv_data)):
        class_name = LABEL_NAMES[id_num]
        ch_name = 'ch' + str(ch)
        folder_path = os.path.join(DATASET_FOLDER, class_name, ch_name)
        file_name = utils.setFilePath(folder_path)
        utils.outputCsvFile(file_name, csv_data[ch])
    

if __name__ == '__main__':
    main()
