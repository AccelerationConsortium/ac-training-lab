import json

import opentrons.simulate
from prefect import flow, task

# ------------------- OT-2 Setup -------------------
protocol = opentrons.simulate.get_protocol_api("2.12")
protocol.home()

# Load Labware
with open("ac_color_sensor_charging_port.json", encoding="utf-8") as f1:
    labware_def1 = json.load(f1)
    tiprack_2 = protocol.load_labware_from_definition(labware_def1, 10)

with open("ac_6_tuberack_15000ul.json", encoding="utf-8") as f2:
    labware_def2 = json.load(f2)
    reservoir = protocol.load_labware_from_definition(labware_def2, 3)

plate = protocol.load_labware("corning_96_wellplate_360ul_flat", location=1)
tiprack_1 = protocol.load_labware("opentrons_96_tiprack_300ul", location=9)

p300 = protocol.load_instrument(
    instrument_name="p300_single_gen2", mount="right", tip_racks=[tiprack_1]
)
p300.well_bottom_clearance.dispense = 8

print("Labwares loaded")


# ------------------- Prefect Tasks -------------------
@task
def mix_color(R, Y, B, mix_well):
    """Mix colors with specified RGB values into a well"""
    total = R + Y + B
    if total > 300:
        raise ValueError("The sum of the proportions must be <= 300")

    position = ["B1", "B2", "B3"]
    portion = {"B1": R, "B2": Y, "B3": B}
    color_volume = {"B1": R, "B2": Y, "B3": B}

    assert (
        p300 is not None
        and tiprack_1 is not None
        and reservoir is not None
        and plate is not None
    )

    for pos in position:
        if float(portion[pos]) != 0.0:
            p300.pick_up_tip(tiprack_1[pos])
            p300.aspirate(color_volume[pos], reservoir[pos])
            p300.dispense(color_volume[pos], plate[mix_well])
            p300.default_speed = 100
            p300.blow_out(reservoir["A1"].top(z=-5))
            p300.default_speed = 400
            p300.drop_tip(tiprack_1[pos])

    print(f"Mixed R:{R}, Y:{Y}, B:{B} in well {mix_well}")


@task
def move_sensor_to_measurement_position(mix_well):
    """Move sensor to measurement position"""
    assert p300 is not None and tiprack_2 is not None and plate is not None
    p300.pick_up_tip(tiprack_2["A2"])
    p300.move_to(plate[mix_well].top(z=-1.3))
    print("Sensor is now in position for measurement")


@task
def move_sensor_back():
    """Move sensor back to charging position"""
    assert p300 is not None and tiprack_2 is not None
    p300.drop_tip(tiprack_2["A2"].top(z=-80))
    print("Sensor moved back to charging position")


# ------------------- Prefect Flow -------------------
@flow(name="ot2-device-flow")
def main_flow(R: int = 100, Y: int = 100, B: int = 100, mix_well: str = "A1"):
    """
    Main flow for color mixing.
    Parameters will come from Prefect Cloud when orchestrator triggers it.
    """
    mix_color(R, Y, B, mix_well)
    move_sensor_to_measurement_position(mix_well)
    move_sensor_back()


if __name__ == "__main__":
    # Serve mode: register to Prefect Cloud & listen for tasks
    main_flow.serve(
        name="ot2-device-deployment",
    )

# main_flow(120, 50, 80, "A1")
