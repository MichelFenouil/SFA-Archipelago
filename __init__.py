from worlds.LauncherComponents import Component, Type, components, launch, icon_paths

from .world import SFAWorld as SFAWorld


def run_client(*args: str) -> None:
    """Run the Star Fox Adventures client with the provided arguments."""
    from .SFAClient import main

    launch(main, name="Star Fox Adventures Client", args=args)


components.append(
    Component(
        "Star Fox Adventures Client",
        func=run_client,
        game_name="Star Fox Adventures",
        component_type=Type.CLIENT,
        supports_uri=True,
        icon="Star Fox Adventures",
    )
)

icon_paths["Star Fox Adventures"] = "ap:worlds.sfa/assets/icon.png"
