import ctypes

import dolphin_memory_engine as dme

from .structures import ObjData

START_LOADED_REGISTRY = 0x803428F8


def get_player():
    """Read and return the current player object from the loaded object registry."""
    object_address = dme.read_word(START_LOADED_REGISTRY)
    object_bytes = dme.read_bytes(object_address, ctypes.sizeof(ObjData))
    return ObjData.from_buffer_copy(object_bytes)


def get_all_loaded_objects():
    """Collect all currently loaded objects keyed by their memory addresses."""
    read_ptr = START_LOADED_REGISTRY
    obj_list = {}
    while True:
        object_address = dme.read_word(read_ptr)
        if object_address == 0:
            break
        object_bytes = dme.read_bytes(object_address, ctypes.sizeof(ObjData))
        object_data = ObjData.from_buffer_copy(object_bytes)
        obj_list[object_address] = object_data
        object_chain = follow_next_object_chain(object_data.nextObj_ptr)
        obj_list.update(object_chain)

        read_ptr += 4
        # await asyncio.sleep(0.1)
    # print(f"Total objects read: {len(obj_list)}")
    return obj_list


def search_objects(obj_list, def_no):
    """Return the first object matching the provided definition number."""
    sorted_obj_list = dict(sorted(obj_list.items(), key=lambda x: x[1].defNo))
    for obj in sorted_obj_list.values():
        if obj.defNo == def_no:
            return obj
    return None


def follow_next_object_chain(address):
    """Traverse an object's linked `nextObj_ptr` chain and return discovered objects."""
    if address == 0:
        return {}
    try:
        obj_bytes = dme.read_bytes(address, ctypes.sizeof(ObjData))
        obj_data = ObjData.from_buffer_copy(obj_bytes)
        chain = follow_next_object_chain(obj_data.nextObj_ptr)
        chain[address] = obj_data
        return chain
    except RuntimeError:
        # print(f"End of object chain reached: {address:x}")
        return {}
