from PIL import Image, ImageGrab, ImageDraw
import time
import urllib, urllib2
import json
import pytesseract as ocr

tables = [[1,2,3,5,6,7,8,9,10,11],
           [12,15,16,17,18,19,20,21,22,23],
           [26,27,28,29,30,31,32,33,555,666],
           [888,999]]
initX = 3
initY = 121
width = 100
height = 91
offset = 97
numberHeight = 53
headerHeight = 16
footerHeight = 20
footerOffset = 11

RED = (106,0,0)
GREEN = (0,114,48)

def monitorSeating():
    previousSeating = []
    while True:
        seating = []
        seatingImage = Image.open('demo2.png')
        j = 0
        for row in tables:
            i = 0
            rowRep = ''
            spacing = ''
            for table in row:
                sample1 = seatingImage.getpixel((initX+i*width, initY+j*height))
                sample2 = seatingImage.getpixel((initX+i*width+offset, initY+j*height))

                valid = (sample1==RED or sample1==GREEN) or (sample2==RED or sample2==GREEN)

                avalability1 = sample1==GREEN
                avalability2 = sample2==GREEN

                avalability = avalability1 or avalability2

                left = initX+i*width
                right = initX+i*width+width
                footerTop = initY+j*height+numberHeight
                footerBtm = initY+j*height+numberHeight+footerHeight

                footer = seatingImage.crop((left, footerTop, right, footerBtm))

                draw = ImageDraw.Draw(footer)
                draw.rectangle((0,0,footerOffset,footerHeight),fill=(192,192,192))
                del draw


                if not avalability:
                    seating.append(str(table).rjust(3, '0') + ': $' + ocr.image_to_string(footer))
                    footer.save('./x/'+str(table)+'.png')
                i+=1

            j+=1

        if valid and not previousSeating == seating:
            url = 'http://jdxhg2.applinzi.com/wechat/uploadSeating'
            value = {'access_token':'******','seating': json.dumps(seating)}
            data = urllib.urlencode(value)
            try:
                request = urllib2.Request(url, data)
                response = urllib2.urlopen(request)
                print response.read()
                print json.dumps(seating)
            except:
                pass
            previousSeating = seating
        print 'sleep'
        time.sleep(2)

monitorSeating()
