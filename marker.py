#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import datetime
import os
import random
import sys
import math
import textwrap
import time
from os import system

from PIL import Image, ImageFont, ImageDraw, ImageEnhance, ImageChops

import datetime


def create_assist_date(datestart=None, dateend=None):
    # 创建日期辅助表

    if datestart is None:
        datestart = '2021-10-01'
    if dateend is None:
        dateend = datetime.datetime.now().strftime('%Y-%m-%d')

    # 转为日期格式
    datestart = datetime.datetime.strptime(datestart, '%Y-%m-%d')
    dateend = datetime.datetime.strptime(dateend, '%Y-%m-%d')
    date_list = []
    date_list.append(datestart.strftime('%Y-%m-%d'))
    while datestart < dateend:
        # 日期叠加一天
        datestart += datetime.timedelta(days=1)
        # 日期转字符串存入列表
        date_list.append(datestart.strftime('%Y-%m-%d'))
    return date_list


def lead_zero(num):
    if num < 10:
        return f'0{num}'
    return f'{num}'


def create_random_time(args):
    date_list = create_assist_date(args.begin_date, args.end_date)
    minute = random.randint(0, 59)

    # if args.time == 'working-time':
    #
    if args.time == 'morning':
        hour = random.randint(9, 11)
    elif args.time == 'afternoon':
        hour = random.randint(14, 17)
    elif args.time == 'night':
        hour = random.randint(18, 20)
    else:
        hour = random.randint(9, 17)

    return f'{random.choice(date_list)} {lead_zero(hour)}:{lead_zero(minute)}'


def create_random_date(args):
    date_list = create_assist_date(args.begin_date, args.end_date)
    return random.choice(date_list)


def get_marked_image(imagePath, mark):
    '''
    添加水印，然后返回图片二进制数据
    '''
    im = Image.open(imagePath)
    image = mark(im)
    image = image.convert('RGB')
    return image


def add_mark(imagePath, mark, args):
    '''
    添加水印，然后保存图片
    '''
    im = Image.open(imagePath)

    image = mark(im)
    name = os.path.basename(imagePath)
    if image:
        if not os.path.exists(args.out):
            os.mkdir(args.out)

        new_name = os.path.join(args.out, name)
        # if os.path.splitext(new_name)[1] != '.png':
        #     image = image.convert('RGB')

        # 全转jpg
        image = image.convert('RGB')
        image.save(
            # f"{args.lead}_{os.path.splitext(new_name)[0]}_{args.mark}.jpg"
            os.path.join(args.out, f"{args.lead}_{name}"), quality=args.quality)
        # print(os.path.splitext(new_name)[0], os.path.splitext(new_name)[1])
        print(f"{name} <- '{args.mark}' Success.")
    else:
        print(f"{name} <- '{args.mark}' Failed.")


def set_opacity(im, opacity):
    '''
    设置水印透明度
    '''
    assert opacity >= 0 and opacity <= 1

    alpha = im.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    im.putalpha(alpha)
    return im


def crop_image(im):
    '''裁剪图片边缘空白'''
    bg = Image.new(mode='RGBA', size=im.size)
    diff = ImageChops.difference(im, bg)
    del bg
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)
    return im


def gen_mark(args):
    '''
    生成mark图片，返回添加水印的函数
    '''
    # 字体宽度、高度
    is_height_crop_float = '.' in args.font_height_crop  # not good but work
    width = len(args.mark) * args.size
    if is_height_crop_float:
        height = round(args.size * float(args.font_height_crop))
    else:
        height = int(args.font_height_crop)

    # 创建水印图片(宽度、高度)
    mark = Image.new(mode='RGBA', size=(width, height))

    # 生成文字
    draw_table = ImageDraw.Draw(im=mark)
    # 叠加阴影
    draw_table.text(xy=(2, 2),
                    text=args.mark,
                    fill="#000000",
                    font=ImageFont.truetype(args.font_family,
                                            size=args.size))
    draw_table.text(xy=(0, 0),
                    text=args.mark,
                    fill=args.color,
                    font=ImageFont.truetype(args.font_family,
                                            size=args.size))

    del draw_table

    # 裁剪空白
    mark = crop_image(mark)

    # 透明度
    set_opacity(mark, args.opacity)

    def mark_im(im):
        w, h = im.size

        if im.mode != 'RGBA':
            im = im.convert('RGBA')

        mark_resize = w * 0.35 / mark.size[0]
        mark2 = mark.resize(
            (int(mark_resize * mark.size[0]), int(mark_resize * mark.size[1])))
        im.paste(mark2,  # 大图
                 (int(w * 0.04), int(w * 0.97 - (w - h) - mark2.size[1])), mask=mark2.split()[3])
        return im

    def mark_im1(im):
        '''在im图片上添加水印 im为打开的原图'''

        # 计算斜边长度
        c = int(math.sqrt(im.size[0] * im.size[0] + im.size[1] * im.size[1]))

        # 以斜边长度为宽高创建大图（旋转后大图才足以覆盖原图）
        mark2 = Image.new(mode='RGBA', size=(c, c))

        # 在大图上生成水印文字，此处mark为上面生成的水印图片
        y, idx = 0, 0
        while y < c:
            # 制造x坐标错位
            x = -int((mark.size[0] + args.space) * 0.5 * idx)
            idx = (idx + 1) % 2

            while x < c:
                # 在该位置粘贴mark水印图片
                mark2.paste(mark, (x, y))
                x = x + mark.size[0] + args.space
            y = y + mark.size[1] + args.space

        # 将大图旋转一定角度
        mark2 = mark2.rotate(args.angle)

        # 在原图上添加大图水印
        if im.mode != 'RGBA':
            im = im.convert('RGBA')
        im.paste(mark2,  # 大图
                 (int((im.size[0] - c) / 2), int((im.size[1] - c) / 2)),  # 坐标
                 mask=mark2.split()[3])
        del mark2
        return im

    return mark_im


def main():
    now = int(time.time() - 86400)
    time_local = time.localtime(now)
    before3 = int(time.time() - 86400 * 1)  # 2天前
    time_before3 = time.localtime(before3)

    parse = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    parse.add_argument("-f", "--file", type=str, default="./input/",
                       help="image file path or directory")
    parse.add_argument("-m", "--mark", type=str, help="watermark content")
    parse.add_argument("-o", "--out", default="./output",
                       help="image output directory, default is ./output")
    parse.add_argument("-c", "--color", default="#EEEEEE", type=str,
                       help="text color like '#000000', default is #EEEEEE")
    parse.add_argument("-l", "--lead", default="xx", type=str,
                       help="filename lead text', default is xx")
    parse.add_argument("-bd", "--begin-date", default=time.strftime('%Y-%m-%d', time_before3), type=str,
                       help="date string like '2021-10-01', default is 2021-10-01")
    parse.add_argument("-ed", "--end-date", default=time.strftime('%Y-%m-%d', time_local), type=str,
                       help="date string like '2021-10-01', default is TODAY")
    parse.add_argument("-hr", "--hour", default="09", type=str,
                       help="24h, default is 09")
    parse.add_argument("-t", "--time", default="working-time", type=str,
                       help="['working-time','morning','afternoon','night'], default is working-time")
    parse.add_argument("-s", "--space", default=80, type=int,
                       help="space between watermarks, default is 80")
    parse.add_argument("-a", "--angle", default=0, type=int,
                       help="rotate angle of watermarks, default is 0")
    parse.add_argument("--font-family", default="../font/SFMono.otf", type=str,
                       help=textwrap.dedent('''\
                       font family of text, default is './font/SFMono.otf'
                       using font in system just by font file name
                       for example 'PingFang.ttc', which is default installed on macOS
                       '''))
    parse.add_argument("--font-height-crop", default="1.2", type=str,
                       help=textwrap.dedent('''\
                       change watermark font height crop
                       float will be parsed to factor; int will be parsed to value
                       default is '1.2', meaning 1.2 times font size
                       this useful with CJK font, because line height may be higher than size
                       '''))
    parse.add_argument("--size", default=50, type=int,
                       help="font size of text, default is 50")
    parse.add_argument("--opacity", default=1, type=float,
                       help="opacity of watermarks, default is 1")
    parse.add_argument("--quality", default=80, type=int,
                       help="quality of output images, default is 90")

    args = parse.parse_args()

    time_start = time.mktime(time.strptime(
        f"{create_random_date(args)} {random.randint(10, 11)}:01", "%Y-%m-%d %H:%M"))
    # time_start = time.mktime(time.strptime(
    #     "%Y-%m-%d %H:%M", f"{args.begin_date} {args.hour}:01"))
    args.mark = time.strftime('%Y-%m-%d %H:%M', time.localtime(time_start))
    # args.mark = create_random_time(args)

    if isinstance(args.mark, str) and sys.version_info[0] < 3:
        args.mark = args.mark.decode("utf-8")

    print(args.time)
    mark = gen_mark(args)

    if os.path.isdir(args.file):
        names = os.listdir(args.file)
        for name in names:
            # args.mark = create_random_time(args)
            time_start += random.randint(60, 180)

            args.mark = time.strftime(
                '%Y-%m-%d %H:%M',  time.localtime(time_start))

            if isinstance(args.mark, str) and sys.version_info[0] < 3:
                args.mark = args.mark.decode("utf-8")

            mark = gen_mark(args)
            image_file = os.path.join(args.file, name)
            add_mark(image_file, mark, args)
    else:
        add_mark(args.file, mark, args)


if __name__ == '__main__':
    main()
    # system('rm input/*')
    # system('explorer.exe output')
