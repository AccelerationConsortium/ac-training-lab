# Move the print head to the front-left-upper corner of the build plate

from time import sleep
import bambulabs_api as bl

from my_secrets import IP, SERIAL, ACCESS_CODE

printer = bl.Printer(IP, ACCESS_CODE, SERIAL)

printer.connect()

sleep(2.0)

# taken from a1.gcode, with help from copilot to parse out

z_current_lowered = printer.gcode("M17 Z0.4 ; lower z motor current to reduce impact")
z_moved_high = printer.gcode("G1 Z100.2 F600   ; Move Z very high up")
z_backed_off = printer.gcode("G1 Z98.2        ; Back off slightly to release pressure")

restore_z_current = printer.mqtt_client.send_gcode(
    "M17 R ; restore z current", gcode_check=False
)

abs_positioning_set = printer.gcode("G90")
final_xy_position_set = printer.gcode("G1 X-13 Y180 F3600  ; Final XY position")

for gcode_sent in [
    z_current_lowered,
    z_moved_high,
    z_backed_off,
    restore_z_current,
    abs_positioning_set,
    final_xy_position_set,
]:
    print(f"Sent G-code: {gcode_sent}")


# gcode_sent = printer.gcode(
#     [
#         "M17 Z0.4 ; lower z motor current to reduce impact",
#         "G1 Z100.2 F600   ; Move Z very high up",
#         "G1 Z98.2        ; Back off slightly to release pressure",
#         "M17 R ; restore z current",
#         "G90",
#         "G1 X-13 Y180 F3600  ; Final XY position",
#     ]
# )


"""
Transcript with Claude 3.7 Sonnet Thinking (Preview) in GitHub Copilot Chat

Right now, my Bambu A1 Mini device is in the homed position. Will it be safe to
run this?

```
[
    "M17 Z0.4 ; lower z motor current to reduce impact",
    "G1 Z100.2 F600   ; Move Z very high up",
    "G1 Z98.2        ; Back off slightly to release pressure",
    "M17 R ; restore z current",
    "G90",
    "G1 X-13 Y180 F3600  ; Final XY position",
]
```

...

# Safety Analysis for Bambu A1 Mini G-code

The code appears to be a parking routine for your Bambu A1 Mini, and it should
be safe to run from the homed position, but there are a few things to note:

1. **Z-Axis Movement**: The code will move the Z-axis to 100.2mm and then back
   to 98.2mm. The A1 Mini has a build volume of 180x180x180mm, so this is within
   safe limits.

2. **Current Adjustment**: The command `M17 Z0.4` temporarily reduces Z motor
   current to minimize impact during movement, which is a safe practice.

3. **Final Position**: The command `G1 X-13 Y180` will move to a position where:
   - X is slightly outside the build area (negative value) - Y is at the maximum
   position

This appears to be a standard parking position for the Bambu A1 Mini, moving the
print head to the front-left corner and raising the build plate. This keeps the
nozzle away from the print surface when not in use.

If your printer is in standard configuration without modifications, this should
execute safely.
"""


# restore_z_current = printer.gcode("M17 R ; restore z current", )
# restore_z_current = printer.gcode("M17 X1.1 Y1.1 Z0.75 ; restore z current")

# HACK: bambulabs_api treating this as invalid, so circumventing check for this one
# restore_z_current = printer.mqtt_client.send_gcode("M17 R ; restore z current", gcode_check=True)
