from typing import Literal
import dolphin_memory_engine as dme
from CommonClient import logger


def extract_bitflag_list(input_bytes: int) -> list[int]:
    """
    Extract list of True bitflags
    
    :param input_byte: Input bytes to read
    :return: List of ON bits indexes
    """
    bit_list = []
    string_bytes = padded_string_byte(input_bytes)

    for i in range(len(string_bytes), 0, -1):
        if string_bytes[i-1] == "1":
            bit_list.append(len(string_bytes)-i)

    return bit_list

def extract_bits_value(input_bytes: int, offset: int = 0, size: int = 8) -> int:
    """
    Extract int value from subset of bits
    
    :param input_byte: Input byte to read from
    :param offset: Offset to start reading value
    :param size: Number of bits to read
    :return: Integer value of extracted bits
    """
    value = input_bytes >> offset
    return value & 2**size-1

def swap_endian(byte: int, size=4) -> int:
    return int.from_bytes(byte.to_bytes(size, byteorder='little'), byteorder='big')

def get_bit_address(table: int, offset: int) -> tuple[int, int]:
    return table + int(offset/8), offset%8

def padded_string_byte(input_byte: int | bool, padding_size: int = 8) -> str:
    temp = str(bin(input_byte)).removeprefix('0b')
    while len(temp)%padding_size != 0:
        temp = "0" + temp
    return temp

def bit_flagger(input_byte: int, flag_position: int, value: int | bool, size: int = 1) -> int:
    input_str = padded_string_byte(input_byte)
    value_str = padded_string_byte(value, size)
    if len(value_str) > size:
        raise ValueError("Value overflowing bits size")
    reverse_pos = len(input_str) - flag_position
    output_str = input_str[:reverse_pos - size] + value_str + input_str[reverse_pos:]
    return int(output_str, 2)

def set_on_or_bytes(address: int, value: int, size: int) -> None:
    """
    Or operation on bytes, set on all 1 and keep the rest
    
    :param address: Description
    :param value: Description
    :param size: Description
    """
    cache_byte = dme.read_bytes(address, size)
    updated_byte = int.from_bytes(cache_byte) | value
    dme.write_bytes(address, updated_byte.to_bytes(size))

def read_value_bytes(address: int, offset: int, value_size: int = 1, nb_bytes: int = 1, endian: Literal['little', 'big'] = 'little') -> int:
    byte_address, bit_position = get_bit_address(address, offset)
    if bit_position + value_size > 8 * nb_bytes:
        logger.debug("READ BYTE: Size overflowing into next byte")
        return read_value_bytes(address, offset, value_size, nb_bytes + 1, endian)
    cache_byte = dme.read_bytes(byte_address, nb_bytes)
    cache_byte = int.from_bytes(cache_byte, endian)
    return extract_bits_value(cache_byte, bit_position, value_size)

def set_value_bytes(address: int, offset: int, value: int, value_size: int = 1, nb_bytes: int = 1, endian: Literal['little', 'big'] = 'little') -> None:
    byte_address, bit_position = get_bit_address(address, offset)
    if bit_position + value_size > 8 * nb_bytes:
        logger.debug("WRITE BYTE: Size overflowing into next byte")
        set_value_bytes(address, offset, value, value_size, nb_bytes + 1, endian)
        return 
    cache_byte = dme.read_bytes(byte_address, nb_bytes)
    cache_byte = int.from_bytes(cache_byte, byteorder=endian)
    updated_byte = bit_flagger(cache_byte, bit_position, value, value_size)
    logger.debug(f"Writing byte: {updated_byte:b}")
    dme.write_bytes(byte_address, updated_byte.to_bytes(nb_bytes, endian))


def set_flag_bit(address: int, offset: int, value: bool) -> None:
    address, bit_position = get_bit_address(address, offset)
    cache_byte = dme.read_byte(address)
    updated_byte = bit_flagger(cache_byte, bit_position, value)
    dme.write_byte(address, updated_byte)