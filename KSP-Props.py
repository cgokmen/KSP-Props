import sys
import signal
import time
import krpc
import math
from PyMata.pymata import PyMata
# followed by another imports your application requires

# create a PyMata instance
# set the COM port string specifically for your platform
board = PyMata("/dev/cu.usbmodem1411")
SPEEDOMETER = 6
FUELGAUGE = 5
GFORCEMETER = 3

SASLAMP = 9
GEARLAMP = 8
BRAKELAMP = 10
LAMPLAMP = 11

# signal handler function called when Control-C occurs
def signal_handler(signal, frame):
    print('You pressed Ctrl+C!!!!')
    if board != None:
        board.reset()
    sys.exit(0)

# listen for SIGINT
signal.signal(signal.SIGINT, signal_handler)


board.set_pin_mode(SPEEDOMETER, board.PWM, board.DIGITAL)
board.set_pin_mode(FUELGAUGE, board.PWM, board.DIGITAL)
board.set_pin_mode(GFORCEMETER, board.PWM, board.DIGITAL)

board.set_pin_mode(SASLAMP, board.OUTPUT, board.DIGITAL)
board.set_pin_mode(GEARLAMP, board.OUTPUT, board.DIGITAL)
board.set_pin_mode(BRAKELAMP, board.OUTPUT, board.DIGITAL)
board.set_pin_mode(LAMPLAMP, board.OUTPUT, board.DIGITAL)


conn = krpc.connect(name="Device")
vessel = conn.space_center.active_vessel

throttle = conn.add_stream(getattr, vessel.control, 'throttle')

refframe = vessel.orbit.body.reference_frame

resources = vessel.resources
maxFuel = conn.add_stream(resources.max, "LiquidFuel")
fuel = conn.add_stream(resources.amount, "LiquidFuel")

flight = vessel.flight(refframe)
gforce = conn.add_stream(getattr, flight, "g_force")
speed = conn.add_stream(getattr, flight, "speed")

control = vessel.control
sas = conn.add_stream(getattr, control, "sas")
gear = conn.add_stream(getattr, control, "gear")
lights = conn.add_stream(getattr, control, "lights")
brakes = conn.add_stream(getattr, control, "brakes")

# Your Application Continues Below This Point
print "We are go!"
while 1 :
    s = speed()
    if s > 400:
        s = 400
    board.analog_write(SPEEDOMETER, int(s * 255 / 400))

    f = 0
    mf = maxFuel()
    if mf > 0 :
        f = fuel() / mf
    board.analog_write(FUELGAUGE, int(f * 255))

    g = math.fabs(gforce()) / 40
    if g > 1:
        g = 1
    board.analog_write(GFORCEMETER, int(g * 255))

    board.digital_write(SASLAMP, sas())
    board.digital_write(GEARLAMP, gear())
    board.digital_write(LAMPLAMP, lights())
    board.digital_write(BRAKELAMP, brakes())

    time.sleep(0.05)