import dolphin_memory_engine as dme
from CommonClient import logger

from ..addresses import BAFOMDAD_MAX_CHECK_ADDRESS


def remove_max_bafomdad_check():
    """Remove check that prevents collecting past MAX BafomDads."""
    bafomdad_branch_instruction = dme.read_word(
        BAFOMDAD_MAX_CHECK_ADDRESS
    )  # Ensure the address is valid and accessible
    if bafomdad_branch_instruction == 0x408000E4:  # Verify if it was the correct instruction before
        dme.write_word(BAFOMDAD_MAX_CHECK_ADDRESS, 0x40800004)  # Branch to next instruction
    else:
        logger.debug(
            f"Expected branch instruction not found at {hex(BAFOMDAD_MAX_CHECK_ADDRESS)}. \
            Found: {hex(bafomdad_branch_instruction)}. No changes made."
        )
