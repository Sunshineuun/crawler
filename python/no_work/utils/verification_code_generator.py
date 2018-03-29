#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie

from PIL import Image, ImageFont, ImageDraw, ImageFilter
import random


# 返回随机字母
def charRandom():
    return chr((random.randint(65, 90)))


# 返回随机数字
def numRandom():
    return random.randint(0, 9)


# 随机颜色
def colorRandom1():
    return random.randint(64, 255), random.randint(64, 255), random.randint(64, 255)


# 随机生成颜色2
def colorRandom2():
    return random.randint(32, 127), random.randint(32, 127), random.randint(32, 127)

# 随机生成颜色2
def colorRandom3():
    return random.randint(0, 0), random.randint(0, 0), random.randint(0, 0)


if __name__ == '__main__':
    width = 60 * 4
    height = 60
    image = Image.new('RGB', (width, height), (255, 255, 255))
    # 创建font对象
    font = ImageFont.truetype('C:\Windows\Fonts\Arial.ttf', 36)

    # 创建draw对象
    draw = ImageDraw.Draw(image)
    # 填充每一个颜色
    # for x in range(width):
    #     for y in range(height):
    #         draw.point((x, y), fill=colorRandom1())

    text = '大小'
    # 输出文字
    for t in range(4):
        temp = charRandom()
        text += temp
        draw.text((60 * t + 10, 10), text, font=font, fill=colorRandom3())

    # 模糊
    image = image.filter(ImageFilter.BLUR)
    image.save('D:\\Temp\\Image\\{code}.jpg'.format(code=text), 'jpeg')
