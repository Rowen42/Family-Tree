# Function to identify the problematic byte
def identify_problematic_byte(filename):

    with open(filename, 'rb') as file:
        content = file.read()

        for i, byte in enumerate(content):
            try:
                bytes([byte]).decode('utf-8')

            except UnicodeDecodeError:
                print(f"Invalid byte found at position {i}: {byte}")
                return i

    return None


# Function to find the exact cell with the invalid character
def find_position_in_csv(filename, byte_position):

    with open(filename, 'rb') as file:
        content = file.read(byte_position + 1)
        row = content[:byte_position].count(b'\n') + 1
        row_start = content.rfind(b'\n', 0, byte_position) + 1
        column = content[row_start:byte_position].count(b',') + 1

    return row, column


# Function to find the exact cell with the invalid character
def find_invalid_character_cell(filename, error_position):

    row, column = find_position_in_csv(filename, error_position)
    print(f"Invalid character found in row {row}, column {column}")
    return row, column
