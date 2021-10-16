# marker.py

为图片添加随机日期时间水印

# usage

需要 PIL 库 `pip install Pillow`

```
usage: marker.py [-h] [-f FILE] [-m MARK] [-o OUT] [-c COLOR] [-s SPACE] [-a ANGLE] [-bd BEGIN_DATE] [-ed END_DATE] [-t TIME] [--font-family FONT_FAMILY] [--font-height-crop FONT_HEIGHT_CROP] [--size SIZE]
                 [--opacity OPACITY] [--quality QUALITY]

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  image file path or directory
  -m MARK, --mark MARK  watermark content
  -o OUT, --out OUT     image output directory, default is ./output
  -c COLOR, --color COLOR
                        text color like '#000000', default is #EEEEEE
  -bd BEGIN_DATE, --begin-date BEGIN_DATE
                        date string like '2021-10-01', default is 2021-10-01
  -ed END_DATE, --end-date END_DATE
                        date string like '2021-10-01', default is TODAY
  -t TIME, --time TIME  ['working-time','morning','afternoon','night'], default is working-time(9~17)
  -s SPACE, --space SPACE
                        space between watermarks, default is 75
  -a ANGLE, --angle ANGLE
                        rotate angle of watermarks, default is 0
  --font-family FONT_FAMILY
                        font family of text, default is './font/SFMono.otf'
                        using font in system just by font file name
                        for example 'PingFang.ttc', which is default installed on macOS
  --font-height-crop FONT_HEIGHT_CROP
                        change watermark font height crop
                        float will be parsed to factor; int will be parsed to value
                        default is '1.2', meaning 1.2 times font size
                        this useful with CJK font, because line height may be higher than size
  --size SIZE           font size of text, default is 50
  --opacity OPACITY     opacity of watermarks, default is 0.15
  --quality QUALITY     quality of output images, default is 90
```

# 效果

`python marker.py -f ./input/test.jpg -bd 2021-07-11 -t morning`

![](https://github.com/yonjar/watermarker/raw/master/output/test.jpg)
