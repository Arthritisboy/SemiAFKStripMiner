import minescript as m
import time

while True:
    m.player_press_jump(True)
    time.sleep(0.1)
    m.player_press_jump(False)
    time.sleep(15)