"""
Micropython EMC2101 Library based on Adafruit's Arduino EMC2101 library

Software License Agreement (BSD License)

Copyright (c) 2019 Bryan Siepert for Adafruit Industries All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met: 1. Redistributions
of source code must retain the above copyright notice, this list of conditions
and the following disclaimer. 2. Redistributions in binary form must reproduce
the above copyright notice, this list of conditions and the following disclaimer
in the documentation and/or other materials provided with the distribution. 3.
Neither the name of the copyright holders nor the names of its contributors may
be used to endorse or promote products derived from this software without
specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ''AS IS'' AND ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
SHALL THE COPYRIGHT HOLDER BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY
OF SUCH DAMAGE.

From https://github.com/harrybadger/MicroPython_EMC2101/ Permalink:
https://github.com/harrybadger/MicroPython_EMC2101/blob/a6344356de50907f94f8cc0742ad54e3f745c29a/EMC2101.py # noqa: E501
"""

import time

from micropython import const

EMC2101_I2CADDR_DEFAULT = const(0x4C)  # EMC2101 default i2c address
EMC2101_CHIP_ID = const(0x16)  # EMC2101 default device id from part id
EMC2101_ALT_CHIP_ID = const(0x28)  # EMC2101 alternate device id from part id
EMC2101_CHIP_IDS = [EMC2101_CHIP_ID, EMC2101_ALT_CHIP_ID]  # List with both Chip IDs
EMC2101_WHOAMI = const(0xFD)  # Chip ID register

EMC2101_INTERNAL_TEMP = const(0x00)  # The internal temperature register
EMC2101_EXTERNAL_TEMP_MSB = const(
    0x01
)  # high byte for the external temperature reading
EMC2101_EXTERNAL_TEMP_LSB = const(0x10)  # low byte for the external temperature reading

EMC2101_STATUS = const(0x02)  # Status register
EMC2101_REG_CONFIG = const(0x03)  # configuration register
EMC2101_REG_DATA_RATE = const(0x04)  # Data rate config
EMC2101_TEMP_FORCE = const(0x0C)  # Temp force setting for LUT testing
EMC2101_TACH_LSB = const(0x46)  # Tach RPM data low byte
EMC2101_TACH_MSB = const(0x47)  # Tach RPM data high byte
EMC2101_TACH_LIMIT_LSB = const(
    0x48
)  # Tach low-speed setting low byte. INVERSE OF THE SPEED
EMC2101_TACH_LIMIT_MSB = const(
    0x49
)  # Tach low-speed setting high byte. INVERSE OF THE SPEED
EMC2101_FAN_CONFIG = const(0x4A)  # General fan config register
EMC2101_FAN_SPINUP = const(0x4B)  # Fan spinup behavior settings
EMC2101_REG_FAN_SETTING = const(
    0x4C
)  # Fan speed for non-LUT settings, as a % PWM duty cycle
EMC2101_PWM_FREQ = const(0x4D)  # PWM frequency setting
EMC2101_PWM_DIV = const(0x4E)  # PWM frequency divisor
EMC2101_LUT_HYSTERESIS = const(
    0x4F
)  # The hysteresis value for LUT lookups when temp is decreasing

EMC2101_LUT_START = const(0x50)  # The first temp threshold register

EMC2101_TEMP_FILTER = const(0xBF)  # The external temperature sensor filtering behavior
EMC2101_REG_PARTID = const(0xFD)  # 0x16
EMC2101_REG_MFGID = const(0xFE)  # 0xFF16

MAX_LUT_SPEED = const(0x3F)  # 6-bit value
MAX_LUT_TEMP = const(0x7F)  # 7-bit

EMC2101_FAN_RPM_NUMERATOR = const(5400000)  # Conversion unit to convert LSBs to fan RPM
_TEMP_LSB = 0.125  # single bit value for internal temperature readings

EMC2101_RATE_1_16_HZ = const(0x00)  # 1_16_HZ
EMC2101_RATE_1_8_HZ = const(0x01)  # 1_8_HZ
EMC2101_RATE_1_4_HZ = const(0x02)  # 1_4_HZ
EMC2101_RATE_1_2_HZ = const(0x03)  # 1_2_HZ
EMC2101_RATE_1_HZ = const(0x04)  # 1_HZ
EMC2101_RATE_2_HZ = const(0x05)  # 2_HZ
EMC2101_RATE_4_HZ = const(0x06)  # 4_HZ
EMC2101_RATE_8_HZ = const(0x07)  # 8_HZ
EMC2101_RATE_16_HZ = const(0x08)  # 16_HZ
EMC2101_RATE_32_HZ = const(0x09)  # 32_HZ


class EMC2101:
    def __init__(self, i2c_bus, address=EMC2101_I2CADDR_DEFAULT):
        self.i2c = i2c_bus
        self.address = address
        # Check that the  address exists on the bus
        if self.address not in self.i2c.scan():
            raise ValueError("i2c address was not found on i2c bus")
        # Read the Chip ID / Product ID to ensure we're talking to an EMC2101
        chip_id = self.read_byte(EMC2101_WHOAMI)
        if chip_id not in EMC2101_CHIP_IDS:
            raise ValueError("Chip ID does not match EMC2101 IDs")
        self.fan_speed_lookup = self.make_interpolator(0, 100, 0, MAX_LUT_SPEED)
        self.fan_speed_reverse_lookup = self.make_interpolator(0, MAX_LUT_SPEED, 0, 100)

        # Set default settings
        self.enable_tach_input(True)
        self.invert_fan_speed(False)
        self.set_pwm_frequency(0x1F)
        self.config_pwm_clock(False, False)
        self.set_dac_out_enabled(False)  # Use PWM output!
        self.set_lut_enabled(False)
        self.set_duty_cycle(100)
        self.set_enable_forced_temp(False)
        self.set_data_rate(EMC2101_RATE_16_HZ)

    def enable_tach_input(self, value):
        if type(value) is not bool:
            raise TypeError("Value must be a boolean")
        self.write_bit(EMC2101_REG_CONFIG, 2, value)

    def invert_fan_speed(self, value):
        if type(value) is not bool:
            raise TypeError("Value must be a boolean")
        self.write_bit(EMC2101_FAN_CONFIG, 4, value)

    def config_pwm_clock(self, clksel, clkovr):
        if type(clksel) is not bool:
            raise TypeError("clksel must be a boolean")
        if type(clkovr) is not bool:
            raise TypeError("clkovr must be a boolean")
        self.write_bit(EMC2101_FAN_CONFIG, 3, clksel)
        self.write_bit(EMC2101_FAN_CONFIG, 2, clkovr)

    def config_fan_spinup(self, value):
        if type(value) is not bool:
            raise TypeError("Value must be a boolean")
        self.write_bit(EMC2101_FAN_SPINUP, 5, value)

    def get_lut_hysteresis(self):
        return self.read_byte(EMC2101_LUT_HYSTERESIS)

    def set_lut_hysteresis(self, value):
        value = min(value, 31)
        value = max(value, 0)
        self.write_byte(EMC2101_LUT_HYSTERESIS, value)

    def set_lut(self, index, temp_thresh, fan_pwm):
        if index not in range(8):
            raise ValueError("Index must be between 0 and 7")
        if temp_thresh not in range(MAX_LUT_TEMP + 1):
            raise ValueError(f"Temp must be between 0 and {MAX_LUT_TEMP}")
        if fan_pwm not in range(101):
            raise ValueError("Fan PWM must be between 0 and 100")
        # Calculate fan speed in correct range
        scaled_speed = self.fan_speed_lookup(fan_pwm)
        # Calculate lut register addresses
        temp_reg_addr = EMC2101_LUT_START + (2 * index)
        speed_reg_addr = temp_reg_addr + 1
        # Disable the LUT so the lut values can be modified
        lut_enabled = self.get_lut_enabled()
        if lut_enabled:
            self.set_lut_enabled(False)
        # Write to the LUT
        self.write_byte(temp_reg_addr, temp_thresh)
        self.write_byte(speed_reg_addr, scaled_speed)
        # Re-set enabled back to initial setting
        if lut_enabled:
            self.set_lut_enabled(True)

    def get_lut(self, index):
        temp_reg_addr = EMC2101_LUT_START + (2 * index)
        speed_reg_addr = temp_reg_addr + 1
        temp = self.read_byte(temp_reg_addr)
        speed = self.read_byte(speed_reg_addr)
        scaled_speed = self.fan_speed_reverse_lookup(speed)
        return temp, scaled_speed

    def get_duty_cycle(self):
        duty_cycle_byte = self.read_byte(EMC2101_REG_FAN_SETTING)
        raw_duty_cycle = duty_cycle_byte & MAX_LUT_SPEED
        return self.fan_speed_reverse_lookup(raw_duty_cycle)

    def set_duty_cycle(self, value):
        if value not in range(101):
            raise ValueError("Value must be between 0 and 100")
        scaled_speed = self.fan_speed_lookup(value)
        self.write_byte(EMC2101_REG_FAN_SETTING, scaled_speed)

    def set_lut_enabled(self, value):
        if type(value) is not bool:
            raise TypeError("Value must be a boolean")
        self.write_bit(EMC2101_FAN_CONFIG, 5, not value)

    def get_lut_enabled(self):
        return not self.read_bit(EMC2101_FAN_CONFIG, 5)

    def get_fan_min_rpm(self):
        high_byte = self.read_byte(EMC2101_TACH_LIMIT_MSB)
        low_byte = self.read_byte(EMC2101_TACH_LIMIT_LSB)
        raw_limit = high_byte << 8
        raw_limit |= low_byte
        if raw_limit == 0xFFFF:
            result = 0
        else:
            result = int(EMC2101_FAN_RPM_NUMERATOR / raw_limit)
        return result

    def set_fan_min_rpm(self, min_rpm):
        raw_limit = EMC2101_FAN_RPM_NUMERATOR // min_rpm
        lsb_value = raw_limit & 0xFF
        msb_value = (raw_limit >> 8) & 0xFF
        self.write_byte(EMC2101_TACH_LIMIT_LSB, lsb_value)
        self.write_byte(EMC2101_TACH_LIMIT_MSB, msb_value)

    def get_external_temp(self):
        high_byte = self.read_byte(EMC2101_EXTERNAL_TEMP_MSB)
        low_byte = self.read_byte(EMC2101_EXTERNAL_TEMP_LSB)
        raw_ext = high_byte << 8
        raw_ext |= low_byte
        sign_bit = bool((high_byte >> 7) & 0x01)
        temp = (raw_ext >> 5) & 0x3FF
        if sign_bit:
            temp = -temp
        return temp * _TEMP_LSB

    def get_internal_temp(self):
        result_byte = self.read_byte(EMC2101_INTERNAL_TEMP)
        sign_bit = bool((result_byte >> 7) & 0x01)
        temp = result_byte & 0x7F
        if sign_bit:
            temp = -temp
        return temp

    def get_fan_rpm(self):
        low_byte = self.read_byte(EMC2101_TACH_LSB)
        high_byte = self.read_byte(EMC2101_TACH_MSB)
        raw_limit = high_byte << 8
        raw_limit |= low_byte
        if raw_limit == 0xFFFF:
            result = 0
        else:
            result = int(EMC2101_FAN_RPM_NUMERATOR / raw_limit)
        return result

    def get_data_rate(self):
        result = self.read_byte(EMC2101_REG_DATA_RATE)
        result &= 0xF
        return result

    def set_data_rate(self, value):
        if value not in range(0xF):
            raise ValueError("Value must be in range 0 to 15")
        self.write_byte(EMC2101_REG_DATA_RATE, value)

    def set_dac_out_enabled(self, value):
        if type(value) is not bool:
            raise TypeError("Value must be a boolean")
        self.write_bit(EMC2101_REG_CONFIG, 4, value)

    def get_dac_out_enabled(self):
        return self.read_bit(EMC2101_REG_CONFIG, 4)

    def get_pwm_frequency(self):
        return self.read_byte(EMC2101_PWM_FREQ)

    def set_pwm_frequency(self, value):
        if value not in range(0xFF + 1):
            raise ValueError("Value must be between 0 and 0xFF")
        self.write_byte(EMC2101_PWM_FREQ, value)

    def get_pwm_divisor(self):
        return self.read_byte(EMC2101_PWM_DIV)

    def set_pwm_divisor(self, value):
        if value not in range(0xFF + 1):
            raise ValueError("Value must be between 0 and 0xFF")
        self.write_byte(EMC2101_PWM_DIV, value)

    def set_enable_forced_temp(self, value):
        if type(value) is not bool:
            raise TypeError("Value must be a boolean")
        self.write_bit(EMC2101_FAN_CONFIG, 6, value)

    def get_enable_forced_temp(self):
        return self.read_bit(EMC2101_FAN_CONFIG, 6)

    def set_forced_temp(self, value):
        if value not in range(0xFF + 1):
            raise ValueError("Value must be between 0 and 0xFF")
        self.write_byte(EMC2101_TEMP_FORCE, value)

    def get_forced_temp(self):
        return self.read_byte(EMC2101_TEMP_FORCE)

    def make_interpolator(self, left_min, left_max, right_min, right_max):
        left_span = left_max - left_min
        right_span = right_max - right_min
        scale_factor = float(right_span) / float(left_span)

        def interp_fcn(value):
            value = min(left_max, value)
            value = max(left_min, value)
            return int(right_min + (value - left_min) * scale_factor)

        return interp_fcn

    def read_byte(self, byte_address):
        buffer = bytearray(1)
        self.i2c.readfrom_mem_into(self.address, byte_address, buffer)
        return buffer[0]

    def read_bit(self, byte_address, zero_indexed_bit_number):
        s = zero_indexed_bit_number
        byte = self.read_byte(byte_address)
        return bool((byte & (1 << s)) >> s)

    def write_byte(self, byte_address, byte_to_write):
        buffer = bytearray(1)
        buffer[0] = byte_to_write
        self.i2c.writeto_mem(self.address, byte_address, buffer)

    def write_bit(self, byte_address, zero_indexed_bit_number, value):
        s = zero_indexed_bit_number
        if type(value) is not bool:
            raise TypeError("Value must be a boolean")
        byte = self.read_byte(byte_address)
        if value:
            # If setting bit true
            mask = 1 << s
            byte |= mask
        else:
            # If setting bit false
            mask = 0b11111111 - (1 << s)
            byte &= mask
        self.write_byte(byte_address, byte)
