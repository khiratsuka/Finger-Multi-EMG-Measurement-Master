#ラベルのdict, id, list
LABEL_NAMES_DICT = {'thumb':0, 'index':1, 'middle':2, 'ring':3, 'pinkie':4}
LABEL_ID = []
LABEL_NAMES = []
for key, val in LABEL_NAMES_DICT.items():
    LABEL_ID.append(val)
    LABEL_NAMES.append(key)

#データセットの保存先
DATASET_FOLDER = 'dataset'

#測定に関わる定数
CH_NUM = 8
MAX_DATA_LENGTH = 4100
DATA_MEASURING_SEC = 2

#デバッグの有無
DEBUG = False