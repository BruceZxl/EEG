'''
运行顺序：先运行软件主程序，新建空白-接收数据开关，然后运行本文件
目前通过死循环读取同一文件的方式模拟长时间接收数据
'''


import time

if __name__ == '__main__':
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = socket.gethostname()
    sock.connect((host, 8080))

    while True:
        tf = r'1mV_1Hz正弦波1+心电数据2-CH39--3.dat'
        testfile = open(tf, mode='rb+')
        testfile.seek(0, 2)
        eof = testfile.tell()
        print(eof)
        testfile.seek(0, 0)

        while True:
            time.sleep(0.001)
            bytes_arr = testfile.read(149)
            sock.send(bytes_arr)
            # print("Sending!")

            if testfile.tell() >= eof:
                print("文件结束")
                testfile.close()
                break

    sock.close()
