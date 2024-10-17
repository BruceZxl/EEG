import asyncio
import socket
from typing import Callable, Union, Any

import numpy as np
from loguru import logger
import time
import threading


# Buffer size = FS * buffer_seconds = 200 * 1 = 200
BUFFER_SIZE = 125


class EegClient:
    def __init__(self, on_batch: Callable[[np.ndarray], None], on_closed: Callable, ip: str, port: str):
        '''

        :param condition:
        :return:
        '''
        self.server_socket = None
        self.buffer = []
        # self.con = condition
        self.stop_flag = False
        self.rev_flag = False
        self.got_flag = True
        self.on_batch = on_batch
        self.on_closed = on_closed
        self.ip = ip
        self.port = port
        self.stop_event = asyncio.Event()

    def handle_buffer_recv(self, received: bytes):
        rev = []
        for i in range(0, len(received), 3):
            cur = received[i:i + 3]
            temp = int.from_bytes(cur, "little")
            if temp & 0x800000 == 0x800000:
                temp = -((temp - 1) ^ 0xFFFFFF)
            rev.append(temp)
        self.buffer.append(rev)
        num_points = len(self.buffer)
        if num_points < 100:
            return
        # buffer, self.buffer = np.frombuffer(b''.join(self.buffer), dtype=np.uint8), []
        # num_channels = len(received) // 3
        # # buffer: num_points * num_channels * 3
        # buffer = buffer.reshape((num_points, num_channels, 3))
        # # outs: num_points * num_channels
        # outs = np.zeros((num_points, num_channels), dtype=np.int32)
        # outs.view(np.int8).reshape((num_points, num_channels, 4))[:, :, :3] = buffer
        # print(outs)
        outs = np.array(self.buffer)
        outs = outs.T.astype(np.float32)
        self.buffer = []
        # std=np.std(outs)
        # std=0.1/std
        # outs = outs.T.astype(np.float32)*pow(std,0.5)
        # logger.info("Sending received data of shape {} to app.", outs.shape)
        self.on_batch(outs)

    def stop(self):
        self.stop_event.set()

    async def interruptable_wait(self, waitable) -> Union[Any, bool, None]:
        """ Wait for the first between the requested event (socket receiving, etc.)
        and user-cancel event."""
        cancel_event = self.stop_event.wait()
        done, pending = await asyncio.wait([cancel_event, waitable], return_when=asyncio.FIRST_COMPLETED)
        for corpse in pending:
            corpse.cancel()
        for task in done:
            if task.get_coro() == cancel_event:
                logger.info("User cancelled receiving.")
                return False
            return task.result()
        return None

    async def run(self):
        assert self.server_socket is None, "EEGClient may only run once. Create a new instance."
        # 初始化服务器
        server = self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # host = socket.gethostname()
        host = self.ip
        port = int(self.port)
        logger.info("Starting server at {}. Waiting for device to connect.", host)
        server.bind((host, port))
        server.listen(5)
        #server.setblocking(False)
        client_socket, info = await self.interruptable_wait(asyncio.get_event_loop().sock_accept(server))
        if client_socket is False:
            return
        #client_socket, info = server.accept()  # 阻塞，等待客户端连接
        print(client_socket, info)
        thread = threading.Thread(target=self.recv_msg, args=(client_socket, info))
        thread.start()
        self.on_closed()

    def recv_msg(self, client, info):
        print('服务器已准备就绪！')
        try:
            state_flag = 0
            cnt = 0
            while True:
                received = client.recv(1)
                if (state_flag == 0) and (received == b'\xEB'):
                    state_flag = 1
                elif (state_flag == 1) and (received == b'\x03'):
                    state_flag = 2
                elif (state_flag == 2) and (received == b'\x90'):
                    state_flag = 0
                    received = client.recv(144)
                    cnt += 1
                    # print(cnt, time.strftime(', %H:%M:%S', time.localtime(time.time())))
                    # print(received)

                    if received is False:
                        return
                    self.handle_buffer_recv(received)

        except Exception as e:
            logger.info('客户端断开连接... {}', e)
            # TODO: 看看具体是啥 EXCEPTION，不能无脑全拦截
            return
