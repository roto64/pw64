#!/usr/bin/env python3
import binascii
import sys

# ADAT encoder

def main():
#    print(encode_adat("TEST"))
    encode_adat()

def encode_adat():
    # 'FE': Newline
    # 'FD': Tab?
    # 'FF': EOF/EOS
    char_map_combined = { # // Normal Font //
						'00': '0', '01': '1', '02': '2', '03': '3', '04': '4',
						'05': '5', '06': '6', '07': '7', '08': '8', '09': '9',
						'0A': 'A', '0B': 'B', '0C': 'C', '0D': 'D', '0E': 'E',
						'0F': 'F', '10': 'G', '11': 'H', '12': 'I', '13': 'J',
						'14': 'K', '15': 'L', '16': 'M', '17': 'N', '18': 'O',
						'19': 'P', '1A': 'Q', '1B': 'R', '1C': 'S', '1D': 'T',
						'1E': 'U', '1F': 'V', '20': 'W', '21': 'X', '22': 'Y',
						'23': 'Z', '24': 'a', '25': 'b', '26': 'c', '27': 'd',
						'28': 'e', '29': 'f', '2A': 'g', '2B': 'h', '2C': 'i',
						'2D': 'j', '2E': 'k', '2F': 'l', '30': 'm', '31': 'n',
						'32': 'o', '33': 'p', '34': 'q', '35': 'r', '36': 's',
						'37': 't', '38': 'u', '39': 'v', '3A': 'w', '3B': 'x',
						'3C': 'y', '3D': 'z', '3E': '-', '3F': '#', '40': '<',
						'41': '>', '42': ' ', '43': '\"', '44': '(', '45': ')',
						'46': '*', '47': '&', '48': ',', '49': '.', '4A': '/',
						'4B': '!', '4C': '?', '4D': '\'', '4E': '#', '4F': ':',
						'50': '0', '51': '1', '52': '2', '53': '3', '54': '4',
						'55': '5', '56': '6', '57': '7', '58': '8', '59': '9',
						'5A': '\\', '5B': '\\', '5C': '\\', '5D': '\\',
						'5E': '\\', '5F': '\\',
						# // Bold Font //
						# This obviously doesn't show up in this code.
						# But it is bold in the game. Trust me.
						'60': '0', '61': '1', '62': '2', '63': '3', '64': '4',
						'65': '5', '66': '6', '67': '7', '68': '8', '69': '9',
						'6A': 'A', '6B': 'B', '6C': 'C', '6D': 'D', '6E': 'E',
						'6F': 'F', '70': 'G', '71': 'H', '72': 'I', '73': 'J',
						'74': 'K', '75': 'L', '76': 'M', '77': 'N', '78': 'O',
						'79': 'P', '7A': 'Q', '7B': 'R', '7C': 'S', '7D': 'T',
						'7E': 'U', '7F': 'V', '80': 'W', '81': 'X', '82': 'Y',
						'83': 'Z', '84': 'a', '85': 'b', '86': 'c', '87': 'd',
						'88': 'e', '89': 'f', '8A': 'g', '8B': 'h', '8C': 'i',
						'8D': 'j', '8E': 'k', '8F': 'l', '90': 'm', '91': 'n',
						'92': 'o', '93': 'p', '94': 'q', '95': 'r', '96': 's',
						'97': 't', '98': 'u', '99': 'v', '9A': 'w', '9B': 'x',
						'9C': 'y', '9D': 'z', '9E': '-', '9F': '#', 'A0': '<',
						'A1': '>', 'A2': ' ', 'A3': '\"', 'A4': '(', 'A5': ')',
						'A6': '*', 'A7': '&', 'A8': ',', 'A9': '.', 'AA': '/',
						'AB': '!', 'AC': '?', 'AD': '\'', 'AE': '}', 'AF': ':',
						'B0': '0', 'B1': '1', 'B2': '2', 'B3': '3', 'B4': '4',
						'B5': '5', 'B6': '6', 'B7': '7', 'B8': '8', 'B9': '9',
						'BA': '\\', 'BB': '\\', 'BC': '\\', 'BD': '\\',
						'BE': '\\', 'BF': '\\' }

    expected_string_length = 0x70 # hardcoded for now

    string_to_encode = '''Fly through 3 rings and...\nooh look a balloon!'''

    encoded_string_hex = []

    for c in string_to_encode:
        encoded_string_hex.append("00")
        if c == '\n':
            encoded_string_hex.append("FE") 
        for k, v in char_map_combined.items():
            if v == c:
                encoded_string_hex.append(k)
                break
        

    # Newline, EOF/EOS and padding, to be automated later
    end1 = ["00", "FE","00","FF","00", "00", "00", "00"]
    for bla in end1:
        encoded_string_hex.append(bla)

    if len(encoded_string_hex) < expected_string_length:
        pad = expected_string_length - len(encoded_string_hex)
        for i in range(0, pad):
            encoded_string_hex.append("00")
    elif len(encoded_string_hex) > expected_string_length:
        print("String too long! %s" % hex(len(encoded_string_hex)))
        sys.exit(1)

    print(hex(len(encoded_string_hex)))
    print(encoded_string_hex)
    print(' '.join(encoded_string_hex))

    print(binascii.unhexlify(''.join(encoded_string_hex)))

if __name__== "__main__":
  main()
