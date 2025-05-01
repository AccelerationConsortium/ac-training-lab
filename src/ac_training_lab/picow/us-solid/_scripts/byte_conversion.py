def simulate_rs232_data():
    # Define the ASCII codes for the components of "11.2 g"
    data = [
        ord("+"),  # Positive sign (+)
        ord(" "),  # Space
        ord("1"),  # First digit
        ord("1"),  # Second digit
        ord("."),  # Decimal point
        ord("2"),  # Third digit
        ord(" "),  # Space
        ord("g"),  # Unit 1
        ord(" "),  # Unit 2 (can be another unit, if applicable)
        ord(" "),  # Unit 3 (optional or placeholder)
        ord("\n"),  # End/return (new line)
    ]

    # Convert ASCII codes to characters and form the message
    message = "".join(chr(byte) for byte in data)

    # Simulate the RS232 data being sent/received
    return message


# Test the function
if __name__ == "__main__":
    rs232_message = simulate_rs232_data()
    print("Simulated RS232 Data:")
    print(rs232_message)
