from worlds.LauncherComponents import Component, Type, components, launch

from .world import SFAWorld as SFAWorld


def run_client(*args: str) -> None:
    """Run the Star Fox Adventures client with the provided arguments."""
    from .SFAClient import main

    launch(main, name="SFA Client", args=args)


components.append(
    Component(
        "SFA Client",
        func=run_client,
        game_name="Star Fox Adventure",
        component_type=Type.CLIENT,
        supports_uri=True,
    )
)
