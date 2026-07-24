import dolphin_memory_engine as dme

from ..addresses import BAFOMDAD_MAX_CHECK_ADDRESS, OBJGROUP_LOAD_CODE

# from CommonClient import logger
from .loaded_objects import get_object_by_id
from .memory_struct import ObjDef


def remove_max_bafomdad_check():
    """Remove check that prevents collecting past MAX BafomDads."""
    bafomdad_branch_instruction = dme.read_word(
        BAFOMDAD_MAX_CHECK_ADDRESS
    )  # Ensure the address is valid and accessible
    if bafomdad_branch_instruction == 0x408000E4:  # Verify if it was the correct instruction before
        dme.write_word(BAFOMDAD_MAX_CHECK_ADDRESS, 0x40800004)  # Branch to next instruction
    else:
        pass
        # logger.debug(
        #     f"Expected branch instruction not found at {hex(BAFOMDAD_MAX_CHECK_ADDRESS)}. \
        #     Found: {hex(bafomdad_branch_instruction)}. No changes made."
        # )


def trigger_objgroup_load(map: int, objgroup_value: int) -> None:
    """Trigger an object group load by writing to the OBJGROUP_LOAD_CODE address."""
    objgroup_trigger_address = OBJGROUP_LOAD_CODE + 4 * map
    dme.write_bytes(objgroup_trigger_address, bytes.fromhex(f"{objgroup_value:08x}"))


def edit_platform_gamebit(objects, id, value) -> None:
    """Edit the gamebit to activate platforms."""
    platform = get_object_by_id(objects, id)
    if platform is None:
        # logger.debug(f"Platform object with ID {id:x} not found.")
        return
    trigger_gamebit = ObjDef.unk18.offset
    dme.write_bytes(platform.objDef_ptr + trigger_gamebit, bytes.fromhex(f"{value:04x}"))
