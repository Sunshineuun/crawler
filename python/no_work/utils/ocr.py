#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie

from PIL import Image
import pytesseract
import os

# 文件夹目录
path = "D:\\Temp\\Image\\"
# 得到文件夹下的所有文件名称
files = os.listdir(path)

# for file in files:
#     image = Image.open(path + file)
#     image.save(path + file.replace('jpg', 'png'), 'png')

# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe' 验证码生成器材
# for file in files:
tessdata_dir_config = '--tessdata-dir "D:\\Program Files (x86)\\Tesseract-OCR\\tessdata\\"'
pytesseract.pytesseract.tesseract_cmd = r'D:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
image = Image.open('D:\\Temp\\Image\\10.png')
print(pytesseract.image_to_string(image, lang='chi_tra', config=tessdata_dir_config))

"""

Error opening data file \Program Files (x86)\Tesseract-OCR\chi_tra.traineddata
Please make sure the TESSDATA_PREFIX environment variable is set to your "tessdata" directory.
Failed loading language 'chi_tra'
Tesseract couldn't load any languages!
Could not initialize tesseract.
"""