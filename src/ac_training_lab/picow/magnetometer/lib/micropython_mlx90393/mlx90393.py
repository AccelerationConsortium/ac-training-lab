# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT
"""
`mlx90393`
================================================================================

MicroPython Driver for the MLX90393 magnetometer sensor


* Author(s): Jose D. Montoya

Implementation Notes
--------------------

**Software and Dependencies:**

This library depends on Micropython

"""

# pylint: disable=too-many-arguments, line-too-long

import struct
import time

from micropython import const

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/jposada202020/MicroPython_MLX90393.git"


class CBits:
    """
    Changes bits from a byte register
    """

    def __init__(
        self,
        num_bits: int,
        register_address: int,
        start_bit: int,
        register_width=2,
        lsb_first=True,
        cmd_read=None,
        cmd_write=None,
    ) -> None:
        self.bit_mask = ((1 << num_bits) - 1) << start_bit
        self.register = register_address
        self.star_bit = start_bit
        self.lenght = register_width + 1
        self.lsb_first = lsb_first
        self.cmd_read = cmd_read
        self.cmd_write = cmd_write

    def __get__(
        self,
        obj,
        objtype=None,
    ) -> int:
        payload = bytes([self.cmd_read, self.register << 2])
        obj._i2c.writeto(obj._address, payload)

        data = bytearray(self.lenght)
        data = obj._i2c.readfrom(obj._address, self.lenght)

        mem_value = memoryview(data[1:])

        reg = 0
        order = range(len(mem_value) - 1, -1, -1)
        if not self.lsb_first:
            order = reversed(order)
        for i in order:
            reg = (reg << 8) | mem_value[i]

        reg = (reg & self.bit_mask) >> self.star_bit

        return reg

    def __set__(self, obj, value: int) -> None:
        payload = bytes([self.cmd_read, self.register << 2])
        obj._i2c.writeto(obj._address, payload)

        data = bytearray(self.lenght)
        data = obj._i2c.readfrom(obj._address, self.lenght)

        memory_value = memoryview(data[1:])

        reg = 0
        order = range(len(memory_value) - 1, -1, -1)
        if not self.lsb_first:
            order = range(0, len(memory_value))
        for i in order:
            reg = (reg << 8) | memory_value[i]
        reg &= ~self.bit_mask

        value <<= self.star_bit
        reg |= value
        reg = reg.to_bytes(self.lenght - 1, "big")

        payload = bytearray(self.lenght + 1)
        payload[0] = self.cmd_write
        payload[3] = self.register << 2
        payload[1] = reg[0]
        payload[2] = reg[1]

        obj._i2c.writeto(obj._address, payload)

        data = obj._i2c.readfrom(obj._address, self.lenght)

        obj._status_last = data[0]


class RegisterStructCMD:
    """
    Register Struct
    """

    def __init__(
        self,
        register_address: int,
        form: str,
        cmd_read: int = None,
        cmd_write: int = None,
    ) -> None:
        self.format = form
        self.register = register_address
        self.lenght = (
            struct.calcsize(form) + 1
        )  # Read the response (+1 to account for the mandatory status byte!)
        self.cmd_read = cmd_read
        self.cmd_write = cmd_write

    def __get__(
        self,
        obj,
        objtype=None,
    ):
        payload = bytes([self.cmd_read, self.register << 2])
        obj._i2c.writeto(obj._address, payload)

        data = bytearray(self.lenght)
        data = obj._i2c.readfrom(obj._address, self.lenght)

        obj._status_last, val = struct.unpack(">BH", data)

        return val

    def __set__(self, obj, value):
        data = bytearray(self.lenght)
        payload = bytes(
            [
                self.cmd_write,
                value >> 8,
                value & 0xFF,
                self.register << 2,
            ]
        )
        obj._i2c.writeto(obj._address, payload)

        data = obj._i2c.readfrom(obj._address, self.lenght)

        obj._status_last = data[0]


_CMD_RR = const(0b01010000)
_CMD_WR = const(0b01100000)
_CMD_SM = const(0b00110000)
_CMD_RM = const(0b01000000)
_CMD_AXIS_ALL = const(0xE)
_REG_WHOAMI = const(0x0C)

# Gain settings
GAIN_5X = const(0x00)
GAIN_4X = const(0x01)
GAIN_3X = const(0x02)
GAIN_2_5X = const(0x03)
GAIN_2X = const(0x04)
GAIN_1_67X = const(0x05)
GAIN_1_33X = const(0x06)
GAIN_1X = const(0x07)

# Resolution settings
RESOLUTION_0 = 0x0
RESOLUTION_1 = 0x1
RESOLUTION_2 = 0x2
RESOLUTION_3 = 0x3

# Filter settings
FILTER_0 = 0x0
FILTER_1 = 0x1
FILTER_2 = 0x2
FILTER_3 = 0x3
FILTER_4 = 0x4
FILTER_5 = const(0x5)
FILTER_6 = const(0x6)
FILTER_7 = const(0x7)

# Oversampling settings
OSR_0 = const(0x0)
OSR_1 = const(0x1)
OSR_2 = const(0x2)
OSR_3 = const(0x3)


class MLX90393:
    """Main class for the Sensor

    :param ~machine.I2C i2c: The I2C bus the MLX90393 is connected to.
    :param int address: The I2C device address. Defaults to :const:`0x0C`

    :raises RuntimeError: if the sensor is not found


    **Quickstart: Importing and using the device**

    Here is an example of using the :class:`MLX90393` class.
    First you will need to import the libraries to use the sensor

    .. code-block:: python

        from machine import Pin, I2C
        import micropython_mlx90393.mlx90393 as mlx90393

    Once this is done you can define your `machine.I2C` object and define your sensor object

    .. code-block:: python

        i2c = I2C(sda=Pin(8), scl=Pin(9))
        mlx = mlx90393.MLX90393(i2c)

    Now you have access to the :attr:`magnetic` attribute

    .. code-block:: python

        magx, magy, magz = mlx.magnetic

    """

    _res0_xy = {
        0: (0.751, 0.601, 0.451, 0.376, 0.300, 0.250, 0.200, 0.150),
        1: (0.787, 0.629, 0.472, 0.393, 0.315, 0.262, 0.21, 0.157),
    }
    _res1_xy = {
        0: (1.502, 1.202, 0.901, 0.751, 0.601, 0.501, 0.401, 0.300),
        1: (1.573, 1.258, 0.944, 0.787, 0.629, 0.524, 0.419, 0.315),
    }
    _res2_xy = {
        0: (3.004, 2.403, 1.803, 1.502, 1.202, 1.001, 0.801, 0.601),
        1: (3.146, 2.517, 1.888, 1.573, 1.258, 1.049, 0.839, 0.629),
    }
    _res3_xy = {
        0: (6.009, 4.840, 3.605, 3.004, 2.403, 2.003, 1.602, 1.202),
        1: (6.292, 5.034, 3.775, 3.146, 2.517, 2.097, 1.678, 1.258),
    }
    _res0_z = {
        0: (1.210, 0.968, 0.726, 0.605, 0.484, 0.403, 0.323, 0.242),
        1: (1.267, 1.014, 0.760, 0.634, 0.507, 0.422, 0.338, 0.253),
    }
    _res1_z = {
        0: (2.420, 1.936, 1.452, 1.210, 0.968, 0.807, 0.645, 0.484),
        1: (2.534, 2.027, 1.521, 1.267, 1.014, 0.845, 0.676, 0.507),
    }
    _res2_z = {
        0: (4.840, 3.872, 2.904, 2.420, 1.936, 1.613, 1.291, 0.968),
        1: (5.068, 4.055, 3.041, 2.534, 2.027, 1.689, 1.352, 1.014),
    }
    _res3_z = {
        0: (9.680, 7.744, 5.808, 4.840, 3.872, 3.227, 2.581, 1.936),
        1: (10.137, 8.109, 6.082, 5.068, 4.055, 3.379, 2.703, 2.027),
    }

    _TCONV = (
        (1.27, 1.84, 3.00, 5.30),
        (1.46, 2.23, 3.76, 6.84),
        (1.84, 3.00, 5.30, 9.91),
        (2.61, 4.53, 8.37, 16.05),
        (4.15, 7.60, 14.52, 28.34),
        (7.22, 13.75, 26.80, 52.92),
        (13.36, 26.04, 51.38, 102.07),
        (25.65, 50.61, 100.53, 200.37),
    )

    _resolutionsxy = {0: _res0_xy, 1: _res1_xy, 2: _res2_xy, 3: _res3_xy}
    _resolutionsz = {0: _res0_z, 1: _res1_z, 2: _res2_z, 3: _res3_z}

    _reg_0 = RegisterStructCMD(0x00, "H", _CMD_RR, _CMD_WR)
    _reg_2 = RegisterStructCMD(0x02, "H", _CMD_RR, _CMD_WR)

    _bits = CBits(3, 0x02, 3, 2, False, _CMD_RR, _CMD_WR)

    # Register 0x00
    #  Z-Series(3) | Gain(3) |  Gain(1) | Gain(0) | HallConf(3) | HallConf(2) | HallConf(1) | HallConf(0) |
    # ----------------------------------------------------------------------------------------------------
    #  CONV0(1)    | AVG1(1) | AVG0(1)  | T/nA(1) |    POL(1)   | DR/Alert(1) | Soft_Reset  |   —         |
    _hall = CBits(4, 0x00, 0, 2, False, _CMD_RR, _CMD_WR)
    _gain = CBits(3, 0x00, 4, 2, False, _CMD_RR, _CMD_WR)

    # Register 0x02
    #  ResY(0)     | ResX(1) |  ResX(0) | DIGFILT(2) | DIGFILT(1)  | DIGFILT(0) | |   OSR(1)  |   OSR(0)    |
    # -------------------------------------------------------------------------------------------------------
    #  ---------   | ------- | -------- | T/nA(1)    |    POL(1)   |  ResZ(1)   |   ResZ(0)   |  ResY(1)    |
    _oversampling = CBits(2, 0x02, 0, 2, False, _CMD_RR, _CMD_WR)
    _digfilt = CBits(3, 0x02, 2, 2, False, _CMD_RR, _CMD_WR)
    _res_x = CBits(2, 0x02, 5, 2, False, _CMD_RR, _CMD_WR)
    _res_y = CBits(2, 0x02, 7, 2, False, _CMD_RR, _CMD_WR)
    _res_z = CBits(2, 0x02, 9, 2, False, _CMD_RR, _CMD_WR)

    def __init__(self, i2c, address=0x0C):
        self._i2c = i2c
        self._address = address
        self._status_last = None
        self._res_x = self._res_y = self._res_z = RESOLUTION_3
        self._digfilt = FILTER_7
        self._oversampling = OSR_3
        self._gain = GAIN_1X

    @property
    def gain(self):
        """
        The gain setting for the device. Sets the analog gain to the desired value.
        The sensitivity is dependent on the axis (the X- and Y-axis have higher
        sensitivity, compared with the Z-axis, expressed in LSB/µT) as well as
        the setting of the `resolution_x`, `resolution_y`, `resolution_z` parameter.
        """
        gain_values = (
            "GAIN_5X",
            "GAIN_4X",
            "GAIN_3X",
            "GAIN_2_5X",
            "GAIN_2X",
            "GAIN_1_67X",
            "GAIN_1_33X",
            "GAIN_1X",
        )

        return gain_values[self._gain]

    @gain.setter
    def gain(self, value):
        if value not in range(1, 8):
            raise ValueError("Invalid GAIN setting")
        self._gain = value

    @property
    def resolution_x(self):
        """
        X Axis Resolution

        +------------------------------------+-----------------+
        | Mode                               | Value           |
        +====================================+=================+
        | :py:const:`mlx90393.RESOLUTION_3`  | :py:const:`0x3` |
        +------------------------------------+-----------------+
        | :py:const:`mlx90393.RESOLUTION_2`  | :py:const:`0x2` |
        +------------------------------------+-----------------+
        | :py:const:`mlx90393.RESOLUTION_1`  | :py:const:`0x1` |
        +------------------------------------+-----------------+
        | :py:const:`mlx90393.RESOLUTION_0`  | :py:const:`0x0` |
        +------------------------------------+-----------------+

        """
        res_values = ("RESOLUTION_0", "RESOLUTION_1", "RESOLUTION_2", "RESOLUTION_3")

        return res_values[self._res_x]

    @resolution_x.setter
    def resolution_x(self, value):
        if value not in range(0, 4):
            raise ValueError("Invalid resolution setting")
        self._res_x = value

    @property
    def resolution_y(self):
        """
        Y Axis Resolution

        +------------------------------------+-----------------+
        | Mode                               | Value           |
        +====================================+=================+
        | :py:const:`mlx90393.RESOLUTION_3`  | :py:const:`0x3` |
        +------------------------------------+-----------------+
        | :py:const:`mlx90393.RESOLUTION_2`  | :py:const:`0x2` |
        +------------------------------------+-----------------+
        | :py:const:`mlx90393.RESOLUTION_1`  | :py:const:`0x1` |
        +------------------------------------+-----------------+
        | :py:const:`mlx90393.RESOLUTION_0`  | :py:const:`0x0` |
        +------------------------------------+-----------------+

        """
        res_values = ("RESOLUTION_0", "RESOLUTION_1", "RESOLUTION_2", "RESOLUTION_3")

        return res_values[self._res_y]

    @resolution_y.setter
    def resolution_y(self, value):
        if value not in range(0, 4):
            raise ValueError("Invalid resolution setting")
        self._res_y = value

    @property
    def resolution_z(self):
        """
        Z Axis Resolution

        +------------------------------------+-----------------+
        | Mode                               | Value           |
        +====================================+=================+
        | :py:const:`mlx90393.RESOLUTION_3`  | :py:const:`0x3` |
        +------------------------------------+-----------------+
        | :py:const:`mlx90393.RESOLUTION_2`  | :py:const:`0x2` |
        +------------------------------------+-----------------+
        | :py:const:`mlx90393.RESOLUTION_1`  | :py:const:`0x1` |
        +------------------------------------+-----------------+
        | :py:const:`mlx90393.RESOLUTION_0`  | :py:const:`0x0` |
        +------------------------------------+-----------------+

        """
        res_values = ("RESOLUTION_0", "RESOLUTION_1", "RESOLUTION_2", "RESOLUTION_3")

        return res_values[self._res_z]

    @resolution_z.setter
    def resolution_z(self, value):
        if value not in range(0, 4):
            raise ValueError("Invalid resolution setting")
        self._res_z = value

    @property
    def digital_filter(self):
        """
        Digital filter applicable to ADC

        +-------------------------------+-----------------+
        | Mode                          | Value           |
        +===============================+=================+
        | :py:const:`mlx90393.FILTER_0` | :py:const:`0x0` |
        +-------------------------------+-----------------+
        | :py:const:`mlx90393.FILTER_1` | :py:const:`0x1` |
        +-------------------------------+-----------------+
        | :py:const:`mlx90393.FILTER_2` | :py:const:`0x2` |
        +-------------------------------+-----------------+
        | :py:const:`mlx90393.FILTER_3` | :py:const:`0x3` |
        +-------------------------------+-----------------+
        | :py:const:`mlx90393.FILTER_4` | :py:const:`0x4` |
        +-------------------------------+-----------------+
        | :py:const:`mlx90393.FILTER_5` | :py:const:`0x5` |
        +-------------------------------+-----------------+
        | :py:const:`mlx90393.FILTER_6` | :py:const:`0x6` |
        +-------------------------------+-----------------+
        | :py:const:`mlx90393.FILTER_7` | :py:const:`0x7` |
        +-------------------------------+-----------------+

        """
        digfilt_values = (
            "FILTER_0",
            "FILTER_1",
            "FILTER_2",
            "FILTER_3",
            "FILTER_4",
            "FILTER_5",
            "FILTER_6",
            "FILTER_7",
        )

        return digfilt_values[self._digfilt]

    @digital_filter.setter
    def digital_filter(self, value):
        if value not in range(0, 8):
            raise ValueError("Invalid Digital Filter setting")
        self._digfilt = value

    @property
    def oversampling(self):
        """
        Temperature sensor ADC oversampling ratio

        .. note::
            The MLX90393 provides configurable filters to adjust the tradeoff
            between current consumption, noise, and conversion time. See section
            15.1.5 for details on selecting the conversion time by adjusting
            `oversampling` and `digital_filter`

        +----------------------------+-----------------+
        | Mode                       | Value           |
        +============================+=================+
        | :py:const:`mlx90393.OSR_0` | :py:const:`0x0` |
        +----------------------------+-----------------+
        | :py:const:`mlx90393.OSR_1` | :py:const:`0x1` |
        +----------------------------+-----------------+
        | :py:const:`mlx90393.OSR_2` | :py:const:`0x2` |
        +----------------------------+-----------------+
        | :py:const:`mlx90393.OSR_3` | :py:const:`0x3` |
        +----------------------------+-----------------+

        """
        oversampling_values = ("OSR_0", "OSR_0_1", "OSR_0_2", "OSR_0_3")

        return oversampling_values[self._oversampling]

    @oversampling.setter
    def oversampling(self, value):
        if value not in range(0, 8):
            raise ValueError("Invalid oversampling setting")
        self._oversampling = value

    @property
    def magnetic(self):
        """
        The processed magnetometer sensor values.
        A 3-tuple of X, Y, Z axis values in microteslas that are signed floats.
        """
        delay = self._TCONV[self._digfilt][self._oversampling] / 1000
        delay = delay * 1.1

        payload = bytes([_CMD_SM | _CMD_AXIS_ALL])
        data = bytearray(1)
        self._i2c.writeto(self._address, payload)
        data = self._i2c.readfrom(self._address, len(data))
        self._status_last = data[0]

        time.sleep(delay)

        data2 = bytearray(7)
        payload = bytes([_CMD_RM | _CMD_AXIS_ALL])
        self._i2c.writeto(self._address, payload)
        data2 = self._i2c.readfrom(self._address, len(data2))

        self._status_last = data2[0]
        x = self._unpack_axis_data(self._res_x, data2[1:3])
        y = self._unpack_axis_data(self._res_y, data2[3:5])
        z = self._unpack_axis_data(self._res_z, data2[5:7])

        if self._hall == 12:
            hallconf_index = 0
        else:
            hallconf_index = 1

        x = x * self._resolutionsxy[self._res_x][hallconf_index][self._gain]
        y = y * self._resolutionsxy[self._res_y][hallconf_index][self._gain]
        z = z * self._resolutionsz[self._res_z][hallconf_index][self._gain]

        return x, y, z

    @staticmethod
    def _unpack_axis_data(resolution, data):
        # see datasheet
        if resolution == RESOLUTION_3:
            (value,) = struct.unpack(">H", data)
            value -= 0x4000
        elif resolution == RESOLUTION_2:
            (value,) = struct.unpack(">H", data)
            value -= 0x8000
        else:
            value = struct.unpack(">h", data)[0]
        return value
