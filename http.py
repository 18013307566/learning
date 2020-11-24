from socket import *

socked = socket()
socked.bind(('0.0.0.0',8888))
socked.listen(5)

connfd,addr = socked.accept()
print("Connect from",addr)

data = connfd.recv(1024*10)
print(data.decode())

f = open('zhihu.html')
data1 = f.read()

response = "HTTP/1.1 200 OK\r\n"
response += "Content-Type:text/html\r\n"
response += "\r\n"
response += data1


connfd.send(response.encode())

connfd.close()
socked.close()
