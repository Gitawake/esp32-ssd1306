import machine
import time
import ssd1306
import uasyncio as asyncio
import network
import socket


station = network.WLAN(network.STA_IF)
station.active(True)

i2c = machine.I2C(scl=machine.Pin(22), sda=machine.Pin(21))

oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

async def connect_wifi():
    if not station.isconnected():
        station.connect("SuHome2022", "SuJunWei2022")
        while not station.isconnected():
            await asyncio.sleep(1)
    # 打印获取到的 IP 地址
    ip_address = station.ifconfig()[0]
    print("Connected to Wi-Fi. IP Address:", ip_address)

async def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 1212))
    server_socket.listen(1)
    print("Server started, waiting for connection...")

    # 设置 server_socket 为非阻塞模式
    server_socket.setblocking(False)

    while True:
        try:
            conn, addr = server_socket.accept()
            print("Connected to:", addr)

            while True:
                data = conn.recv(1024)
                if not data:
                    print("Connection closed by client.")
                    conn.close()  # 关闭连接
                    break
                print("Received:", data.decode())
                
                print("sendOK")
                response = "Message received: {}".format(data.decode())
                conn.send(response.encode())

                # 在 OLED 显示屏上显示接收到的数据
                oled.fill(0)
                oled.text("Received:", 0, 0, 1)
                oled.text(data.decode(), 0, 16, 1)
                oled.show()

        except OSError as e:
            pass  # 没有连接或接收数据时，继续等待

        await asyncio.sleep(0.1)  # 添加一个短暂的等待，避免无限循环阻塞

    server_socket.close()

async def update_display():
    while True:
        cpu_freq = machine.freq() // 1000000  # 将频率转换为 MHz
        oled.fill(0)
        oled.text("CPU Freq:{}MHz".format(cpu_freq), 0, 0, 1)
        oled.text("IP:{}".format(station.ifconfig()[0]), 0, 16, 1)  # 在第二行显示 Wi-Fi 的 IP 地址
        oled.show()
        await asyncio.sleep(1)  # 每秒刷新一次，可以根据需要调整刷新频率

# 创建一个事件循环，并在其中运行 update_display() 协程
loop = asyncio.get_event_loop()
loop.create_task(connect_wifi())
loop.create_task(start_server())
loop.create_task(update_display())
loop.run_forever()