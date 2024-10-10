from pymycobot.mycobot import MyCobot

cobot = MyCobot("/dev/ttyAMA0", 1000000)

def rise():
	cobot.send_angles([0, 0, 0, 0, 0, 0], 100)

def kill():
	cobot.release_all_servos()
