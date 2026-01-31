from typing import Literal

import dolphin_memory_engine as dme
from CommonClient import logger


def extract_bitflag_list(input_bytes: int) -> list[int]:
    """
    Extract list of True flags in the input.

    :param input_bytes: Input bytes to extract flags
    :return: List of ON flag index
    """
    string_bytes = padded_string_byte(input_bytes)
    return [len(string_bytes) - 1 - i for i in range(len(string_bytes)) if string_bytes[i] == "1"]


def extract_bits_value(input_bytes: int, offset: int = 0, size: int = 8) -> int:
    """
    Extract int value inside the input bytes.

    :param input_bytes: Input bytes to read from
    :param offset: Offset to start reading value
    :param size: Number of bits to read
    :return: Integer value of extracted bits
    """
    value = input_bytes >> offset
    return value & 2**size - 1


def swap_endian(bytes: int, nb_bytes: int = 4) -> int:
    """
    Swap endian order from input bytes.

    :param bytes: Integer bytes to swap
    :param size: Number of bytes in the input
    :return: Integer bytes in the inverse endian order
    """
    return int.from_bytes(bytes.to_bytes(nb_bytes, byteorder="little"), byteorder="big")


def get_bit_address(table: int, offset: int) -> tuple[int, int]:
    """
    Return byte address and offset inside the byte for any offset.

    :param table: Start address
    :param offset: Integer bit offset
    :return: Address, offset in address byte
    """
    return table + int(offset / 8), offset % 8


def padded_string_byte(input_byte: int | bool, padding_size: int = 8) -> str:
    """
    Pad byte string with 0 to complete size.

    :param input_byte: Value to pad and return string
    :param padding_size: Length of output string
    :return: String value of input with required length
    """
    temp_str = str(bin(input_byte)).removeprefix("0b")
    while len(temp_str) % padding_size != 0:
        temp_str = "0" + temp_str
    return temp_str


def update_bits(input_byte: int, start_offset: int, value: int | bool, size: int = 1) -> int:
    """
    Update given bits inside of the input byte.

    :param input_byte: Input byte
    :param flag_position: Starting offset to update
    :param value: New value to insert in byte
    :param size: Number of bits to update
    :return: Updated byte
    """
    input_str = padded_string_byte(input_byte)
    value_str = padded_string_byte(value, size)
    if len(value_str) > size:
        raise ValueError("Value overflowing bits size")
    reverse_pos = len(input_str) - start_offset
    output_str = input_str[: reverse_pos - size] + value_str + input_str[reverse_pos:]
    return int(output_str, 2)


def set_on_or_bytes(address: int, value: int, nb_bytes: int) -> None:
    """
    Update ON bits and keep unchanged bits from memory.

    :param address: Address to update
    :param value: Value to compare with memory
    :param size: Number of bytes to update
    """
    cache_byte = dme.read_bytes(address, nb_bytes)
    updated_byte = int.from_bytes(cache_byte) | value
    dme.write_bytes(address, updated_byte.to_bytes(nb_bytes))


def read_value_bytes(
    address: int, offset: int, value_size: int = 1, nb_bytes: int = 1, endian: Literal["little", "big"] = "little"
) -> int:
    """
    Read int value from memory.

    :param address: Start address
    :param offset: Starting bit offset
    :param value_size: Number of bits to read value
    :param nb_bytes: Number of bytes to read in memory
    :param endian: Endian order to read value
    :return: Integer value from memory
    """
    byte_address, bit_position = get_bit_address(address, offset)
    if bit_position + value_size > 8 * nb_bytes:
        logger.debug("READ BYTE: Size overflowing into next byte")
        return read_value_bytes(address, offset, value_size, nb_bytes + 1, endian)
    cache_byte = dme.read_bytes(byte_address, nb_bytes)
    cache_byte = int.from_bytes(cache_byte, endian)
    return extract_bits_value(cache_byte, bit_position, value_size)


def set_value_bytes(
    address: int,
    offset: int,
    value: int,
    value_size: int = 1,
    nb_bytes: int = 1,
    endian: Literal["little", "big"] = "little",
) -> None:
    """
    Write int value into memory.

    :param address: Start address
    :param offset: Starting bit offset
    :param value: Integer value to write
    :param value_size: Number of bits to write value
    :param nb_bytes: Number of bytes to write in memory
    :param endian: Endian order to write value
    """
    byte_address, bit_position = get_bit_address(address, offset)
    if bit_position + value_size > 8 * nb_bytes:
        logger.debug("WRITE BYTE: Size overflowing into next byte")
        set_value_bytes(address, offset, value, value_size, nb_bytes + 1, endian)
        return
    cache_byte = dme.read_bytes(byte_address, nb_bytes)
    cache_byte = int.from_bytes(cache_byte, byteorder=endian)
    updated_byte = update_bits(cache_byte, bit_position, value, value_size)
    logger.debug(f"Writing byte: {updated_byte:b}")
    dme.write_bytes(byte_address, updated_byte.to_bytes(nb_bytes, endian))


def set_flag_bit(address: int, offset: int, value: bool) -> None:
    """
    Update single bit value in memory.

    :param address: Start address
    :param offset: Bit offset
    :param value: Bit value
    """
    address, bit_position = get_bit_address(address, offset)
    cache_byte = dme.read_byte(address)
    updated_byte = update_bits(cache_byte, bit_position, value)
    dme.write_byte(address, updated_byte)
