import struct
import numpy as np

def test():
    pickupParity = 0x00FF
    wave_length = 8500
    upper2hex = [[], [], [], [], [], [], [], []]
    lower2hex = [[], [], [], [], [], [], [], []]
    upper2dec = [[], [], [], [], [], [], [], []]
    lower2dec = [[], [], [], [], [], [], [], []]
    parity = []
    footer = []

    for i in range(len(upper2hex)):
        for j in range(wave_length):
            #up2 = j + (i+1)*10
            #low2 = j + (i+2)*10
            up2 = 55
            low2 = 88
            upper2dec[i].append(up2)
            lower2dec[i].append(low2)
            upper2hex[i].append(struct.pack("B", up2))
            lower2hex[i].append(struct.pack("B", low2))

    upper2dec = np.array(upper2dec).T.tolist()
    lower2dec = np.array(lower2dec).T.tolist()

    for i in range(wave_length):
        p = sum(upper2dec[i]) + sum(lower2dec[i])
        p = p & pickupParity
        parity.append(struct.pack("B", p))
        footer.append(struct.pack("B", 255))
    
    #parity[3] = struct.pack("B", (sum(upper2dec[3]) + sum(lower2dec[3]))&0x000F)
    #footer[4] = struct.pack("B", 255)
    
    return upper2hex, lower2hex, parity, footer

if __name__ == '__main__':
    test()
        
