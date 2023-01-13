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
    upper2dec = [[], [], [], [], [], [], [], []]
    lower2dec = [[], [], [], [], [], [], [], []]
    recv_pariry = []
    calc_parity = []
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
        print(LABEL_NAMES_DICT)
        id_num_str = input('ID > ')
        id_num = int(id_num_str)
        if id_num >= len(LABEL_NAMES) or id_num < 0:
            print('ERROR: input numv is out of index')
        else:
            print('select label is [{}]'.format(LABEL_NAMES[id_num]))
            break
    
    #通常時
    if not DEBUG:
        #UART通信の初期設定
        #接続時に"ls /dev/tty.usb*"でポート番号をチェックする
        ser = serial.Serial(
            port = "/dev/tty.usbmodem11403",
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
                #計算したパリティ用
                calc_parity_temp = 0

                #先頭データを受信した時間を記録
                if first_receive:
                    os.system('tput bel')
                    print('< start measurement >')
                    first_receive = False
                    start_time = time.perf_counter()
                
                #データを受信
                recv_data = ser.read(1)
                recv_data_val = struct.unpack_from("B", recv_data ,0)[0]

                #データのヘッダを検知
                if recv_data_val == 254:
                    #データの個数を取得、バイナリから変換
                    data_num = ser.read(1)
                    data_num = struct.unpack_from("B", data_num ,0)[0]

                    #データの取得とパリティの準備
                    for i in range(data_num - 1):
                        upper_temp = ser.read(1)
                        lower_temp = ser.read(1)
                        upper_temp_val = struct.unpack_from("B", upper_temp, 0)[0]
                        lower_temp_val = struct.unpack_from("B", lower_temp, 0)[0]
                        upper2dec[i].append(upper_temp_val)
                        lower2dec[i].append(lower_temp_val)
                        calc_parity_temp = calc_parity_temp + upper_temp_val + lower_temp_val
                    calc_parity.append(calc_parity_temp & pickupParity)

                    #パリティの取得
                    recv_parity_temp = ser.read(1)
                    recv_parity_temp = struct.unpack_from("B", recv_parity_temp, 0)[0]
                    recv_pariry.append(recv_parity_temp)
                    
                    #フッタの取得
                    footer_temp = ser.read(1)
                    footer_temp = struct.unpack_from("B", footer_temp, 0)[0]
                    footer.append(footer_temp)
    
    #デバッグ時
    if DEBUG:
        upper2hex, lower2hex, recv_pariry, footer= recv_test_data.test()
    
    #パリティを計算
    for i in range(len(footer)):
        #パリティが違っていればエラーデータとしてデータを全て捨てる
        if(calc_parity[i] != recv_pariry[i] or footer[i] != 255):
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
