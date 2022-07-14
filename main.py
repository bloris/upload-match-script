import os
import time

from tqdm import tqdm

from upload_data import AutoScript
from secret import getPath

if __name__ == "__main__":
    autoScript = AutoScript()
    path = getPath()
    matchList = sorted(os.listdir(path))
    idx = 0
    for match in tqdm(matchList):
        #print(match)
        response = autoScript.getData(path=os.path.join(path,match))
        if response:
            autoScript.updateElo()
            autoScript.putData()
            idx += 1
        
        if idx % 10 == 0:
            print("Sleep 2m, API Limits over")
            time.sleep(120)