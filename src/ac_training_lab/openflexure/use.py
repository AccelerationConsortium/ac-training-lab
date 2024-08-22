# DEMO USE
#
# move(x,y) required
#
# move(x,y,z,relative) optional
#
# moves to given coordinates x, y (and z if it is set to any integer value, if
# it is set to False which is the default setting, the z value wont change). If
# relative is True, then it will move relative to the current position instead
# of moving to the absolute coordinates
#
# take_image() returns an image object
#
# get_pos() returns a dictionary with x, y, and z coordinates eg.
# {'x':1,'y':2,'z':3}
#
# focus()

# focus(amount) optional
#
# focuses by different amounts: huge, fast, medium, fine, or any integer value
# (default is fast)
#
# end_connection()
#
# ends the connection
#
# scan(c1,c2) required
#
# scan(c1,c2,ov,foc) optional
#
# returns a list of image objects. Takes images to scan an entire area specified
# by two corners. you can input the corner coordinates as "x1 y1", "x2, y2" or
# [x1, y1], [x2, y2]. ov refers to the overlap between the images (useful for
# stitching) and foc refers to how much the microscope should focus between
# images (0 to disable)


# EXAMPLE CODE

from microscope_demo_client import MicroscopeDemo
from my_secrets import (
    HIVEMQ_HOST,
    HIVEMQ_PASSWORD,
    HIVEMQ_PORT,
    HIVEMQ_USERNAME,
    MICROSCOPE_NAME,
)

microscope = MicroscopeDemo(
    HIVEMQ_HOST, HIVEMQ_PORT, HIVEMQ_USERNAME, HIVEMQ_PASSWORD, MICROSCOPE_NAME
)


microscope.move(0, 0)
microscope.take_image().show()
microscope.move(3000, 3000)
microscope.move(0, 0)
print(microscope.get_pos())
microscope.focus()
microscope.take_image().show()
for i in microscope.scan([2000, 2000], [-2000, -2000]):
    i.show()
microscope.move(0, 0)
microscope.end_connection()
