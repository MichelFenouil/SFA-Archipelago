from .world import SFAWorld as SFAWorld
from worlds.LauncherComponents import Component, Type, components, launch


def run_client(*args: str) -> None:
    # Ideally, you should lazily import your component code so that it doesn't have to be loaded until necessary.
    from .SFAClient import main

    # Also, if your component has its own lifecycle, like if it is its own window that can be interacted with,
    # you should use the LauncherComponents.launch helper (which itself calls launch_subprocess).
    # This will create a subprocess for your component, launching it in a separate window from the Archipelago Launcher.
    launch(main, name="SFA Client", args=args)


# You then add this function as a component by appending a Component instance to LauncherComponents.components.
# Now, it will show up in the Launcher with its display name,
# and when the user clicks on the "Open" button, your function will be run.
components.append(
    Component(
        "SFA Client",
        func=run_client,
        game_name="Star Fox Adventure",
        component_type=Type.CLIENT,
        supports_uri=True,
    )
)