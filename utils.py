import os

from settings import *


#ファイル名決定
def setFilePath(folder):
    file_num = 0
    while True:
        filename = "./" + folder + "/{}.csv".format(str(file_num).zfill(4))
        if not os.path.exists(filename):
            break
        file_num += 1
    return filename


#CSVファイルへの書き込み
def outputCsvFile(filename, data):
    with open(filename, 'x') as f:
        f.writelines(data)
    print('save > ' + filename)


#データ保存先フォルダの確認と作成
def datasetFolderCheck():
    #データセット保存先フォルダの確認と作成
    if not os.path.exists(DATASET_FOLDER):
        os.makedirs(DATASET_FOLDER)
    
    #データセット内クラスフォルダの確認と作成
    for l_id in LABEL_NAMES:
        class_folder = os.path.join(DATASET_FOLDER, l_id)
        if not os.path.exists(class_folder):
            os.makedirs(class_folder)
    
    #クラスフォルダ内chフォルダの確認と作成
    for l_id in LABEL_NAMES:
        for i in range(CH_NUM):
            ch_name = 'ch' + str(i)
            ch_folder = os.path.join(DATASET_FOLDER, l_id, ch_name)
            if not os.path.exists(ch_folder):
                os.makedirs(ch_folder)