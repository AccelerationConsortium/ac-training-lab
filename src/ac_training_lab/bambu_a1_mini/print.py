import os
import time
import zipfile
from io import BytesIO

import bambulabs_api as bl

IP = "192.168.1.124"
SERIAL = "0309CA471800852"
ACCESS_CODE = "14011913"

INPUT_FILE_PATH = "test_square_3.gcode"
UPLOAD_FILE_NAME = "test_square.gcode"

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

    with open(INPUT_FILE_PATH, "r") as file:
        gcode = file.read()

    gcode_location = "Metadata/plate_1.gcode"
    io_file = create_zip_archive_in_memory(gcode, gcode_location)
    if file:
        result = printer.upload_file(io_file, UPLOAD_FILE_NAME)
        if "226" not in result:
            print("Error Uploading File to Printer")

        else:
            print("Done Uploading/Sending Start Print Command")
            printer.start_print(UPLOAD_FILE_NAME, 1)
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
