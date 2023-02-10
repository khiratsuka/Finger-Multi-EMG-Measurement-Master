# Finger-Multi-EMG-Measurement-Master

## 概要
指を動かした時の筋電位の取得プログラム(マスタ側)

STM32をスレーブ側として筋電位のデータを取得する

## コードについて
- eight_sensors_data_uart.py
  - 8つの筋電位センサのデータを記録するプログラム
- one_sensor_data_uart.py
  - 1つの筋電位センサのデータを記録するプログラム
- shell_**.sh
  - eight_sensors_data_uart.pyを繰り返し実行するシェルスクリプト