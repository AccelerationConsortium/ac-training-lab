from opentrons import protocol_api

metadata = {
    "apiLevel": "2.16",
    "protocolName": "OCT28 demo run loop",
    "author": "Neil-YL",
}


def run(protocol: protocol_api.ProtocolContext):
    plate = protocol.load_labware(
        load_name="corning_96_wellplate_360ul_flat", location=1
    )
    tiprack_1 = protocol.load_labware(
        load_name="opentrons_96_tiprack_300ul", location=9
    )
    tiprack_2 = protocol.load_labware(
        load_name="ac_color_sensor_charging_port", location=10
    )
    reservoir = protocol.load_labware(load_name="ac_6_tuberack_15000ul", location=3)

    p300 = protocol.load_instrument(
        instrument_name="p300_single_gen2", mount="right", tip_racks=[tiprack_1]
    )
    positions = ["B1", "B2", "B3"]

    # Define rows and columns for the 96-well plate
    rows = ["A", "B", "C", "D", "E", "F", "G", "H"]
    columns = [str(i) for i in range(1, 13)]

    for i in range(60):
        # Calculate the current well in the plate based on i
        row = rows[i // 12]  # Determine row (A-H)
        col = columns[i % 12]  # Determine column (1-12)
        current_well = f"{row}{col}"  # Combine to get well name
        p300.well_bottom_clearance.dispense = 10
        # three color dispensing
        for pos in positions:
            p300.pick_up_tip(tiprack_1[pos])
            p300.aspirate(40, reservoir[pos])
            p300.dispense(40, plate[current_well])
            p300.default_speed = 100  # reduce pipette speed
            p300.blow_out(reservoir["A1"].top(z=-5))
            p300.default_speed = 400  # reduce pipette speed
            p300.drop_tip(tiprack_1[pos])

        # color sensor measuring
        p300.pick_up_tip(tiprack_2["A2"])
        p300.move_to(plate[current_well].top(z=3))
        protocol.delay(seconds=5)  # wait for color sensor
        p300.drop_tip(tiprack_2["A2"].top(z=-75))
