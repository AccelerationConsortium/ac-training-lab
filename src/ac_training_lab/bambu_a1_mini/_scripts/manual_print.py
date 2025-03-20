import os
import time
import zipfile
from io import BytesIO

import bambulabs_api as bl

from my_secrets import IP, SERIAL, ACCESS_CODE

input_dir = "/home/ac/Documents/GitHub/AccelerationConsortium/ac-training-lab/src/ac_training_lab/bambu_a1_mini/gcode/"
input_fname = "a1.gcode"
input_fpath = os.path.join(input_dir, input_fname)
upload_fname = os.path.basename(input_fpath)
# UPLOAD_FILE_NAME = "a1.gcode"

env = os.getenv("env", "debug")
plate = os.getenv("plate", "true").lower() == "true"


def create_zip_archive_in_memory(
    text_content: str, text_file_name: str = "file.txt"
) -> BytesIO:
    """
    Create a zip archive in memory

    Args:
        text_content (str): content of the text file
        text_file_name (str, optional): location of the text file.
            Defaults to 'file.txt'.

    Returns:
        io.BytesIO: zip archive in memory
    """
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr(text_file_name, text_content)
    zip_buffer.seek(0)
    return zip_buffer


if __name__ == "__main__":
    print("Starting bambulabs_api example")
    print("Connecting to BambuLab 3D printer")
    print(f"IP: {IP}")
    print(f"Serial: {SERIAL}")
    print(f"Access Code: {ACCESS_CODE}")

    # Create a new instance of the API
    printer = bl.Printer(IP, ACCESS_CODE, SERIAL)

    # Connect to the BambuLab 3D printer
    printer.connect()

    time.sleep(2)

    with open(input_fpath, "r") as file:
        gcode = file.read()

    gcode_location = "Metadata/plate_1.gcode"
    io_file = create_zip_archive_in_memory(gcode, gcode_location)
    if file:
        result = printer.upload_file(io_file, upload_fname)
        if "226" not in result:
            print("Error Uploading File to Printer")

        else:
            print("Done Uploading/Sending Start Print Command")
            printer.start_print(upload_fname, 1)
            print("Start Print Command Sent")

    time.sleep(2)

    # Get the printer status
    status = printer.get_state()
    print(f"Printer status: {status}")

    bed_temperature = printer.get_bed_temperature()
    nozzle_temperature = printer.get_nozzle_temperature()
    speed = printer.get_print_speed()
    print(
        f"Printer status: {status}, Bed temp: {bed_temperature}, "
        f"Nozzle temp: {nozzle_temperature},"
        f"Print speed: {speed}"
    )
