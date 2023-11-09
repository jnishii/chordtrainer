import pygame.midi as m
import time

m.init()
i_num = m.get_count()
for i in range(i_num):
    print(i)
    print(m.get_device_info(i))

channel=4

print("channel: ", channel)
player = m.Output(channel)

print("1")
player.note_on(64,127)
player.note_off(64)
time.sleep(1)

print("2")
player.note_on(50,100)
time.sleep(1)
player.note_off(50)
time.sleep(1)

print("end")
del player
m.quit()
