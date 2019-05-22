"""
聊天室思路分析

1. 技术点的确认
    * 转发模型， 客户端--》服务端--》转发给其他客户端
    * 网络模型， UDP通信
    * 保存用户信息  [(name,addr),()]  {name:addr}
    * 收发关系处理： 采用多进程分别进行收发操作

2. 结构设计
    * 采用什么样的封装结构 : 函数
    * 编写一个功能，测试一个功能
    * 注意注释和结构的设计

3. 分析功能模块，指定具体编写流程

* 搭建网络连接
* 进入聊天室
    客户端:
        * 输入姓名
        * 将姓名发送给服务器
        * 接收返回的结果
        * 如果不允许则重复输入姓名


服务端：
    * 接收姓名
    * 判断姓名是否存在
    * 将结果给客户端
    * 如果允许进入聊天室增加用户信息
    * 通知其他用户

* 聊天
     客户端：
        * 创建新的进程
        * 一个进程循环发送消息
        * 一个进程循环接收消息

     服务端：
        * 接收请求，判断请求类型
        * 将消息转发个其他用户


* 退出聊天室
    客户端 ：
    * 输入quit或者ctrl-c退出
    * 将请求发送给服务端
    * 结束进程
    * 接收端收到EXIT退出进程

    服务端 ：
    * 接收消息
    * 将退出消息告知其他人
    * 给该用户发送“EXIT”
    * 删除用户

* 管理员消息


4. 协议

* 如果允许进入聊天室 服务端发送 'OK' 给客户端
* 如果不允许进入聊天室，服务端发送 不允许的原因
* 请求类别：

         L --> 进入聊天室
         C --> 聊天信息
         Q --> 退出聊天室

* 用户存储结构： {name:addr ...}
* 客户端如果输入quit或者ctrl-c，点击esc表示退出

"""

from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_REUSEADDR

import os


class Server:
    def __init__(self, ip, port):
        self.ip = (ip, port)
        self.server_socket = socket(AF_INET, SOCK_DGRAM)
        self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server_socket.bind(self.ip)
        self.name = {}

    def do_request(self):
        """
        处理客户端请求
        :return:
        """
        while True:
            data, addr = self.server_socket.recvfrom(1024)
            msg = data.decode().split(' ')
            if msg[0] == 'L':
                self.do_login(msg[1], addr)
            elif msg[0] == 'Q':
                if msg[1] not in self.name:
                    self.server_socket.sendto('EXIT'.encode(), addr)
                    continue
                self.do_quit(msg[1])
            elif msg[0] == 'C':
                self.recv_data(msg[1], ' '.join(msg[2:]))

    def recv_data(self, name, data):
        """
        接收消息
        :return:
        """
        for i in self.name:
            if i != name:
                self.server_socket.sendto('\n{}:{}'.format(name, data).encode(), self.name[i])

    def do_login(self, name, addr):
        """
        判断用户名是否存在
        :param name:
        :param addr:
        :return:
        """
        if name in self.name or '管理员' in name:
            self.server_socket.sendto('\n用户名已存在，请重新输入'.encode(), addr)
            return
        self.server_socket.sendto('OK'.encode(), addr)
        self.name[name] = addr
        msg = '\n欢迎{}进入聊天室'.format(name)
        for i in self.name:
            self.server_socket.sendto(msg.encode(), self.name[i])

    def do_quit(self, msg):
        """
        退出聊天室
        :param msg:
        :return:
        """
        for i in self.name:
            if i != msg:
                self.server_socket.sendto('{}断开连接'.format(msg).encode(), self.name[i])
            else:
                self.server_socket.sendto('EXIT'.encode(), self.name[i])
        del self.name[msg]

    def run(self):
        pid = os.fork()
        if pid < 0:
            return
        elif pid == 0:
            while True:
                msg = input('管理员消息')
                msg = 'C 管理员消息 {}'.format(msg)
                self.server_socket.sendto(msg.encode(), self.ip)
        else:
            self.do_request()

if __name__ == '__main__':
    s = Server('192.168.232.128', 12345)
    s.run()
