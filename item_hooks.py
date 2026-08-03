from .game_memory.code_edit import edit_platform_gamebit
from .game_memory.loaded_objects import get_all_loaded_objects

lfv_triangle_platforms = [(0x4942F, 0x0BDF), (0x49430, 0x0BE1), (0x49431, 0x0BE3)]
lfv_square_platforms = [(0x45CE9, 0x0612), (0x45CEA, 0x090B), (0x45CEB, 0x0087)]
lfv_circle_platforms = [(0x49322, 0x02C6), (0x49323, 0x02CE), (0x49324, 0x0BDC)]


def lfv_disable_triangle_platform():
    """Disable the LFV triangle block platform by using OFF gamebit."""
    # Get all loaded objects
    object_list = get_all_loaded_objects()

    for platform_id, _ in lfv_triangle_platforms:
        edit_platform_gamebit(object_list, platform_id, 0x0096)


def lfv_enable_triangle_platform(_item) -> None:
    """Enable the LFV triangle block platform by putting the real gamebit."""
    # Get all loaded objects
    object_list = get_all_loaded_objects()

    # Toggle the LFV triangle block platform
    for platform_id, platform_gamebit in lfv_triangle_platforms:
        edit_platform_gamebit(object_list, platform_id, platform_gamebit)


def lfv_disable_square_platform():
    """Disable the LFV square block platform by usign OFF gamebit."""
    # Get all loaded objects
    object_list = get_all_loaded_objects()

    for platform_id, _ in lfv_square_platforms:
        edit_platform_gamebit(object_list, platform_id, 0x0096)


def lfv_enable_square_platform(_item) -> None:
    """Enable the LFV square block platform by putting the real gamebit."""
    # Get all loaded objects
    object_list = get_all_loaded_objects()

    # Toggle the LFV square block platform
    for platform_id, platform_gamebit in lfv_square_platforms:
        edit_platform_gamebit(object_list, platform_id, platform_gamebit)


def lfv_disable_circle_platform():
    """Disable the LFV circle block platform by using OFF gamebit."""
    # Get all loaded objects
    object_list = get_all_loaded_objects()

    for platform_id, _ in lfv_circle_platforms:
        edit_platform_gamebit(object_list, platform_id, 0x0096)


def lfv_enable_circle_platform(_item) -> None:
    """Enable the LFV circle block platform by putting the real gamebit."""
    # Get all loaded objects
    object_list = get_all_loaded_objects()

    # Toggle the LFV circle block platform
    for platform_id, platform_gamebit in lfv_circle_platforms:
        edit_platform_gamebit(object_list, platform_id, platform_gamebit)
