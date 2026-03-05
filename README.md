![Star Fox Adventures](https://raw.githubusercontent.com/MichelFenouil/SFA-Archipelago/refs/heads/main/StarFoxAdventuresLogo.png)

# Star Fox Adventures Client

Archipelago client for Star Fox Adventures.

## Required Software

* [Archipelago 0.6.6+](https://archipelago.gg/tutorial/Archipelago/setup/en)
* [Dolphin Gamecube Emulator](https://dolphin-emu.org/)
* Legally acquired Star Fox Adventures ISO file (US version 1.0)
* [Amethyst Mod](https://segment6.net/sfa/amethyst) for Star Fox Adventures

## Recommended Software

* [Poptracker Pack](https://github.com/OmegaZeron/Star-Fox-Adventures-AP-PopTracker-Pack), tracker with maps and items by @OmegaZeron

## First Install Setup

1. Download and install the latest release of Archipelago Multiworld from the link above.
2. Download and install the latest release of Dolphin Emulator from the link above.
3. Patch the ISO file with the Amethyst mod as explained in [these steps](https://segment6.net/sfa/amethyst#download)
4. Find your Archipelago directory, and put `sfa.apworld` in the `custom_worlds` folder

## Game Setup

1. Create a yaml settings file, and put it in the Archipelago directories `players` folder. You can generate a template yaml with the archipelago launcher.
2. Generate your game from the archipelago launcher
4. Host the game, either locally or via the [archipelago web hosting service](https://archipelago.gg/uploads)
5. Open the `Star Fox Adventures Client` and connect to the server
6. Launch the patched ISO file
7. You are now ready to play! Start a new savefile and go!


## Important information
- The game runs on live patching, there is no patch file generated and you can't see what you found in game. Check your client to see what items you find.
- To reduce crashes, turn off `Dual Core` settings in Dolphin (Config > General).
- You can enable auto-save in the Amethyst options (`L+Z+B > Game Settings > Autosave`). This is **recomended** as the randomizer is still unstable. 
- Using the Amethyst debug menu (`L+Z+B > Debug > Map > Warp`) you can warp anywhere but it is unstable. **Save or make a save state** before warping as it can crash the game. It is better to warp to recently visited areas or the planet landing zone. If the objects don't load in, walk through the closest loading zone (it can take a while but it will eventually load the new area).
- Bind `Controller3 Z button` on your gamepad to speed up the game.
- The client will give/remove items in some areas (e.g. TTH Store) to spawn location checks. Some items may also appear as colored boxes in C Menu. You can check you items receivved with `/received` command in the client.
- The `/sync` command is available in the client to resynchronize you game items with the server state.
