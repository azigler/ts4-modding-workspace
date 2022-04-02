# HOW TO USE: https://modthesims.info/showpost.php?p=5423701&postcount=2

import os

def get_dir():
    pathname = os.path.dirname(os.path.realpath(__file__))
    if pathname.lower().endswith('.ts4script'):
        pathname = os.path.dirname(pathname)
    return pathname
