from opentrons import protocol_api
metadata = {
    "apiLevel": "2.16",
    "protocolName": "demo run loop",
    "author": "Neil-YL"}


def run(protocol: protocol_api.ProtocolContext):
    plate = protocol.load_labware(
        load_name="corning_96_wellplate_360ul_flat",
        location=1)
    tiprack_1 = protocol.load_labware(
            load_name="opentrons_96_tiprack_300ul",
            location=9)
    tiprack_2 = protocol.load_labware(
            load_name="ac_color_sensor_charging_port",
            location=10)
    reservoir = protocol.load_labware(
            load_name="ac_6_tuberack_15000ul",
            location=3)
    
    p300 = protocol.load_instrument(
            instrument_name="p300_single_gen2",
            mount="right",
            tip_racks=[tiprack_1])
    positions = ["A1", "A2", "A3"]
    for i in range(3):
      
        p300.pick_up_tip(tiprack_2["A2"])
        p300.move_to(plate["A1"].top(z=3))
        protocol.delay(seconds=5)   #wait for color sensor
        p300.drop_tip(tiprack_2["A2"].top(z=-75))
        p300.well_bottom_clearance.dispense=10
        for pos in positions:
            p300.pick_up_tip(tiprack_1[pos])
            p300.aspirate(100, reservoir[pos])
            p300.dispense(100, plate["A1"])
            p300.drop_tip(tiprack_1[pos])
    
