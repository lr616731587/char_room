"""
ftp文件服务器
    功能
        分为服务端和客户端，要求可以有多个客户端同时操作。
        客户端可以查看服务器文件库中有什么文件。
        客户端可以从文件库中下载文件到本地。
        客户端可以上传一个本地文件到文件库。
        使用print在客户端打印命令输入提示，引导操作
    并发模型，多线程
    数据传输 tcp传输
    结构设计
        客户端发起请求，打印请求提示界面
        文件传输
    功能
        网络搭建
        查看文件库信息
        下载文件
        上传文件
        客户端退出
"""
import signal, sys, os, time
from socket import *
from threading import Thread


class FtpServer:
    bank = set()

    def __init__(self):
        rootdir = './ftp'
        list = os.listdir(rootdir)
        for i in range(0, len(list)):
            FtpServer.bank.add(list[i])
        print(FtpServer.bank)

    def find_file(self, cli):
        if FtpServer.bank:
            li = list(FtpServer.bank)
            data = '  '.join(li)
            cli.send(data.encode())
        else:
            cli.send('空'.encode())

    def upload_file(self, cli):
        cli.send('ok'.encode())
        name = cli.recv(1024).decode()
        if name not in FtpServer.bank:
            FtpServer.bank.add(name)
            f = open('ftp/{}'.format(name), 'wb+')
            while True:
                data = cli.recv(1024)
                if data == b'##':
                    cli.send('上传结束'.encode())
                    break
                else:
                    f.write(data)
            print('{}:{} upload ok'.format(cli.getpeername(), name))
        else:
            cli.send('已存在'.encode())
            return

    def download_file(self, cli):
        self.find_file(cli)
        name = cli.recv(1024).decode()
        print(name)
        try:
            f = open(name, 'rb')
            print('ok')
        except Exception:
            print('ng')
            cli.send('文件不存在'.encode())
            return
        while True:
            a = f.read(1024)
            if not a:
                time.sleep(5)
                cli.send(b'##')
                break
            cli.send(a)
        f.close()





class Server:
    def __init__(self, ip, port):
        self.ip = (ip, port)
        self.server = socket()
        self.server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server.bind(self.ip)
        self.server.listen(3)

    def request(self):
        signal.signal(signal.SIGCHLD, signal.SIG_IGN)
        while True:
            try:
                c, addr = self.server.accept()
                print('Listen {}'.format(c.getpeername()))
            except KeyboardInterrupt:
                sys.exit('退出服务器')
            except Exception as e:
                print(e)
                continue

            t = Thread(target=self.ftpserver, args=(c,))
            t.setDaemon(True)
            t.start()

    def ftpserver(self, cli):
        while True:
            data = cli.recv(1024).decode()
            if not data:
                break
            elif data == '1':
                FtpServer().find_file(cli)
            elif data == '2':
                FtpServer().upload_file(cli)
            elif data == '3':
                FtpServer().download_file(cli)
            else:
                cli.send('错误'.encode())
        cli.close()


if __name__ == '__main__':
    s = Server('0.0.0.0', 12345)
    s.request()
    # f = FtpServer()
    # f.find_file()