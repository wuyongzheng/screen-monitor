import socket
import time
import struct

logfp = None

def recvall(sock, msgsize):
    result = bytearray()
    while msgsize > 0:
        buff = sock.recv(msgsize)
        if not buff:
            break
        result.extend(buff)
        msgsize -= len(buff)
    return result

def work(sock, addr):
    ts = int(time.time() * 1000)
    sock.settimeout(60)
    buf = sock.recv(struct.calcsize("<QQ64s64sI"))
    if len(buf) != struct.calcsize("<QQ64s64sI"):
        logfp.write('len(buf) != struct.calcsize()\n')
        return
    currtime, idletime, hostname, username, imglen = struct.unpack("<QQ64s64sI", buf)
    hostname = hostname.decode("utf-8").split('\0', 1)[0]
    username = username.decode("utf-8").split('\0', 1)[0].replace(" ", "")
    buf = recvall(sock, imglen)
    if len(buf) != imglen:
        logfp.write('{} {}'.format(len(buf), imglen))
        logfp.write('len(buf) != imglen\n')
        return
    with open(time.strftime('img-' + addr[0].split('.')[3] + '-%w%H%M.jpeg', time.localtime()), 'wb') as imgfp:
        imgfp.write(buf)
    logfp.write('{}\t{}\t{}\t{}\t{}\n'.format(ts, currtime, idletime, hostname, username))

def main():
    global logfp
    logfp = open('screen_monitor_server.log', mode='a', buffering=1)
    logfp.write('Start {}\n'.format(time.strftime("%y:%m:%d %H:%M:%S", time.localtime())))
    sock = socket.socket()
    sock.bind(('', 56230))
    sock.listen()
    while True:
        connection, client_address = sock.accept()
        logfp.write('Connected from {}\n'.format(str(client_address)))
        work(connection, client_address)
        connection.close()

if __name__ == '__main__':
    main()
