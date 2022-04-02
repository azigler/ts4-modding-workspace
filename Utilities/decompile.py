import io
import fnmatch
import os
import shutil
from settings import *
from zipfile import PyZipFile
from unpyc3 import decompile

def extract_folder(ea_folder, gameplay_folder):
    for root, dirs, files in os.walk(gameplay_folder):
        for ext_filter in ['*.zip', '*.ts4script']:
            for filename in fnmatch.filter(files, ext_filter):
                extract_subfolder(root, filename, ea_folder)

def extract_subfolder(root, filename, ea_folder):
    src = os.path.join(root, filename)
    dst = os.path.join(ea_folder, filename)
    if src != dst:
        shutil.copyfile(src, dst)
    zip = PyZipFile(dst)
    out_folder = os.path.join(ea_folder, os.path.splitext(filename)[0])
    zip.extractall(out_folder)
    decompile_dir(out_folder)
    pass

def decompile_dir(rootPath):
    pattern = '*.pyc'
    for root, dirs, files in os.walk(rootPath):
        for filename in fnmatch.filter(files, pattern):
            p = str(os.path.join(root, filename))
            try:
                py = decompile(p)
                with io.open(p.replace('.pyc', '.py'), 'w', encoding='utf-8') as output_py:
                    for statement in py.statements:
                        output_py.write(str(statement) + '\r')
                print("SUCCESS: %s" % p)
            except Exception as ex:
                print("FAIL: %s" % p)

if not os.path.exists(scripting_ea_folder):
    os.mkdir(scripting_ea_folder)

extract_folder(scripting_ea_folder, game_folder_data)
extract_folder(scripting_ea_folder, game_folder_game)
