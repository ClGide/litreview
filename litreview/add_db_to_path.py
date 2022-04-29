from pathlib import Path

to_add = Path(r"C:\Users\gider\PycharmProjects\litreview\sqlite-tools-win32-x86-3380200\sqlite3.exe")
from sys import path

if str(to_add) not in path:
    minLen = 999999
    for index, directory in enumerate(path):
        if 'site-packages' in directory and len(directory) <= minLen:
            minLen = len(directory)
            stpi = index

    pathSitePckgs = Path(path[stpi])
    with open(str(pathSitePckgs / 'current_machine_paths.pth'),
              'w') as pth_file:
        pth_file.write(str(to_add))
