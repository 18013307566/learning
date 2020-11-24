"""
基于 epoll 的 IO并发模型
重点代码！！！
"""

from socket import *
from select import *

# 创建全局变量
HOST = "0.0.0.0"
PORT = 8800
ADDR = (HOST,PORT)

# 创建套接字
sockfd = socket()
sockfd.bind(ADDR)
sockfd.listen(5)

# IO多路复用往往与非阻塞IO一起使用，防止传输过程的卡顿
sockfd.setblocking(False)

# 监控IO
ep = epoll() # 生成poll对象

# 关注监听套接字读行为
ep.register(sockfd, EPOLLIN)

# 建立找对象的关系地图 必须和关注的IO保持一直
map = {
    sockfd.fileno():sockfd,
}

# 循环监控关注的IO
while True:
    print("开始监控IO啦")
    events = ep.poll()
    print(events)  # [(4, 4), (5, 4)]
    # 对监控的套接字就绪情况分情况讨论
    for fd,event in events:
        if fd == sockfd.fileno():
            connfd, addr = map[fd].accept()
            print("Connect from",addr)
            # 连接一个客户端就多监控一个
            connfd.setblocking(False)
            ep.register(connfd, EPOLLIN | EPOLLERR)
            map[connfd.fileno()] = connfd
        elif event == EPOLLIN:
            # 某个客户端连接套接字就绪
            data = map[fd].recv(1024).decode()
            # 客户端退出
            if not data:
                ep.unregister(fd) # 删除监控
                map[fd].close()
                del map[fd]
                continue
            print(data)
            map[fd].send(b'OK') # 回复消息
