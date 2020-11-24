"""
web server 程序

完成一个类，提供给使用者
使用者可以通过这个类 快速方便的搭建一个web服务展示自己的网页
"""
from socket import *
from select import select
import re


class WebServer:
    def __init__(self, *, host="0.0.0.0", port=80, html=None):
        self.host = host
        self.port = port
        self.html = html
        # 将关注的IO存入列表
        self.rlist = []
        self.wlist = []
        self.xlist = []
        # 准备工作
        self.create_socket()
        self.bind()

    # 创建套接字
    def create_socket(self):
        self.sock = socket()
        self.sock.setblocking(False)

    def bind(self):
        self.address = (self.host, self.port)
        self.sock.bind(self.address)

    # 连接客户端(浏览器连接上)
    def connect(self, sockfd):
        connfd, addr = sockfd.accept()
        print("Connect from", addr)
        # 连接一个客户端就多监控一个
        connfd.setblocking(False)
        self.rlist.append(connfd)

    # 启动网络服务 --> IO 并发模型
    def start(self):
        self.sock.listen(5)
        self.rlist.append(self.sock)  # 初始
        # 循环监控关注的IO
        while True:
            rs, ws, xs = select(self.rlist, self.wlist, self.xlist)
            # 对监控的套接字就绪情况分情况讨论
            for r in rs:
                if r is self.sock:
                    self.connect(r)
                else:
                    # 某个浏览器发送http请求
                    try:
                        self.handle(r)
                    except:
                        pass
                    finally:
                        r.close()
                        self.rlist.remove(r)

    # 具体处理http请求
    def handle(self, connfd):
        # 接收HTTP请求
        request = connfd.recv(1024 * 10).decode()

        # 提取请求内容 GET     /xxx.html   HTTP/1.1
        pattern = r"[A-Z]+\s+(?P<info>/\S*)"
        result = re.match(pattern, request)  # match/None
        if result:
            # info ： 请求内容
            info = result.group("info")
            self.send_html(connfd, info)
        else:
            # 匹配失败则结束函数，表示请求响应失败
            return

    # 最终发送网页数据给浏览器
    def send_html(self, connfd, info):
        # 分情况讨论
        if info == '/':
            filename = self.html + "/index.html"
        else:
            filename = self.html + info

        try:
            file = open(filename, "rb")
        except:
            # 请求的网页不存在
            with open(self.html + "/404.html", 'rb') as f:
                data = f.read()
            response = "HTTP/1.1 404 Not Found\r\n"
            response += "Content-Type:text/html\r\n"
            response += "\r\n"
            response = response.encode() + data
        else:
            # 请求的网页存在
            data = file.read()  # data--> bytes
            response = "HTTP/1.1 200 OK\r\n"
            response += "Content-Type:text/html\r\n"
            response += "\r\n"
            response = response.encode() + data
            file.close()
        finally:
            connfd.send(response)  # 发送给浏览器响应


if __name__ == '__main__':
    # 使用者怎么用？

    # 用户自己决定    地址 ip  port  网页
    httpd = WebServer(host="0.0.0.0", port=8000, html="./static")

    # 启动服务
    httpd.start()
