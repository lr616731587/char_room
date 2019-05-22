import time, os
import socket


class FtpServer(object):
    def request(self, cli, data):
        cli.send(data.encode())
        b = cli.recv(1024).decode()
        return b

    def do_list(self, cli, data):
        r = self.request(cli, data)
        print(r)

    def upload(self, cli, data):
        r = self.request(cli, data)
        if r == 'ok':
            name = input('选择需要上传的文件')
            name1 = name.split('/')[-1]
            cli.send(name1.encode())
            f = open('{}'.format(name), 'rb')
            while True:
                a = f.read(1024)
                if not a:
                    time.sleep(0.1)
                    cli.send('##'.encode())
                    break
                cli.send(a)
            f.close()
            print(cli.recv(1024).decode())
        else:
            print('请求错误')

    def download(self, cli, data):
        r = self.request(cli, data)
        print(r)
        name = input('请输入需要下载的书籍')
        cli.send(name.encode())
        while True:
            addr = input('请选择下载位置')
            path = os.path.join(addr, name)
            if os.path.exists(path):
                print('文件已存在')
            else:
                print(path, 'ok')
                break
        f = open(path, 'wb')
        while True:
            data = cli.recv(1024)
            print(data)
            if data == b'##':
                print('下载结束'.encode())
                break
            else:
                f.write(data)


class Client():
    def __init__(self, ip, port):
        self.client = socket.socket()
        self.client.connect((ip, port))
        self.ftp = FtpServer()

    def request(self):
        while True:
            data = input()
            if not data:
                self.client.send('quit'.encode())
            elif data == '1':
                self.ftp.do_list(self.client, data)
            elif data == '2':
                self.ftp.upload(self.client, data)
            elif data == '3':
                self.ftp.download(self.client, data)


if __name__ == '__main__':
    client = Client('0.0.0.0', 12345)
    # with open('a2.jpg', 'rb') as f:
    client.request()
