from PIL import ImageGrab, ImageFont, ImageDraw
import socket
import time
import os
import struct
import win32api

logfp = None

singleton_socket = None
def is_another_process_running():
    global singleton_socket
    singleton_socket = socket.socket()
    try:
        singleton_socket.bind(('127.0.0.1', 56231))
        singleton_socket.listen()
    except:
        return True
    return False

def send(screen, currtime, idletime, hostname, username):
    sock = socket.socket()
    sock.settimeout(60)
    sock.connect(('192.168.1.10', 56230))
    sock.sendall(struct.pack('<QQ64s64sI', int(currtime), int(idletime), hostname.encode('utf-8'), username.encode('utf-8'), len(screen)))
    sock.sendall(screen)
    sock.close()
    logfp.write('Sent {}\n'.format(time.strftime("%y:%m:%d %H:%M:%S", time.localtime())))

def work():
    img = ImageGrab.grab()
    img = img.resize((1280, 720))

    # embed metadata as text into image
    font = ImageFont.truetype("arial.ttf", 40)
    canvas = ImageDraw.Draw(img)
    canvas.multiline_text((10,10),
            '{}\n{}\n{}\n{}'.format(time.strftime("%y%m%d-%H%M", time.localtime()),
                (win32api.GetTickCount() - win32api.GetLastInputInfo()),
                socket.gethostname(), os.getlogin()),
            font=font, fill=(255,0,0))

    img.save("screentmp.jpg")
    imgfp = open("screentmp.jpg", 'rb')
    imgdata = imgfp.read()
    imgfp.close()
    os.remove("screentmp.jpg")
    send(imgdata, time.time(), win32api.GetTickCount() - win32api.GetLastInputInfo(), socket.gethostname(), os.getlogin())

def main():
    if os.path.exists('stop'):
        return
    if is_another_process_running():
        return
    global logfp
    logfp = open('screen_monitor_client.log', mode='a', buffering=1)
    logfp.write('Start {}\n'.format(time.strftime("%y:%m:%d %H:%M:%S", time.localtime())))
    while True:
        time.sleep(60)
        if os.path.exists('stop'):
            break
        try:
            work()
        except Exception as x:
            logfp.write('Send Fail {} {}\n'.format(time.strftime("%y:%m:%d %H:%M:%S", time.localtime()), str(x)))

if __name__ == '__main__':
    main()
