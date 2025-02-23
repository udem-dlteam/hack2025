# File: FG_test.py

from FG import *
import time

host = '127.0.0.1'  # alternative: blgXX.iro.umontreal.ca

sim_host_set(host)

sim_connect()


t = 0

while t < 120:

    print('******** t =', t)

    recv_instruments()  # get instrument readings and location
    print(instruments)

    if t == 0:  # start the engine!
        autostart_c172p()

    elif t == 1:  # parking brake!
        controls.parking = 1
        controls.throttle = 0.1
        send_controls()

    elif t == 20:  # when engine is warm, give full throttle!
        controls.throttle = 1
        send_controls()

    elif t == 25:  # go!
        controls.parking = 0
        send_controls()

    elif t == 60:  # when we have some speed, up elevator!
        controls.elevator = -0.2
        send_controls()

    elif t == 100:
        reset_aircraft('LOWI', '08')

    time.sleep(0.5)
    t += 1


print('done!')
