"""
tcp基础示例　客户端
"""

from socket import *

tcp_socket = socket()
tcp_socket.connect(('127.0.0.1', 8800))

while True:

    data = input(">>")

    if not data:
        break

    tcp_socket.send(data.encode())

    # if data =="##":
    #     break

    data = tcp_socket.recv(1024)
    print('From server:',data.decode())

tcp_socket.close()