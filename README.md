![Star Fox Adventures](https://raw.githubusercontent.com/MichelFenouil/SFA-Archipelago/refs/heads/main/StarFoxAdventuresLogo.png)

# Star Fox Adventures Client

Archipelago client for Star Fox Adventures.

## Required Software

* [Archipelago 0.6.6+](https://archipelago.gg/tutorial/Archipelago/setup/en)
* [Dolphin Gamecube Emulator](https://dolphin-emu.org/)
* Legally acquired Star Fox Adventures ISO file (US version 1.0)
* [Amethyst Mod](https://segment6.net/sfa/amethyst) for Star Fox Adventures

## Recommended Software

* [Poptracker Pack](https://github.com/OmegaZeron/Star-Fox-Adventures-AP-PopTracker-Pack), tracker with maps and items by OmegaZeron

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
- You can enable auto-save in the Amethyst options (`L+Z+B > Game Settings > Autosave`). It is **recomended** to turn it on or save regularly as the randomizer can crash.
- Using the Amethyst debug menu (`L+Z+B > Debug > Map > Warp`) you can warp anywhere but it is unstable. **Save or make a save state** before warping as it can crash the game. It is better to warp to recently visited areas or the planet landing zone. If the objects don't load in, walk through the closest loading zone (it can take a while but it will eventually load the new area).
- The client will give/remove items in some areas (e.g. TTH Store items, Upgrades in Magic Cave) to spawn location checks. This updates when you leave the go through a loading zone.
- You can check you items received with `/received` command in the client.
- The `/sync` command is available in the client to resynchronize you game items with the server state.

### Amethyst Features
**Open options using `L+Z+B` or `PDA On/Off` in the C menu**
- Toggle camera controls on C joystick in `Control Settings > Camera Control`. When this is on, you can navigate C menu with D-pad.
- Switch between Fox and Krystal in `Player Settings`. Some fight combos don't work correctly with Krystal.
- Toggle autosave in `Game Settings > Autosave`.
- Speed up button by binding `Controller 3 Z Button` in dolphin. Cutscene audio still plays at normal speed, reset audio by opening and closing START menu.

## What is randomized?

- Staff powerups and magic meter upgrades (currently Fire Blaster and Staff Booster). The client will give/remove the staff ability inside the cave but it updates when leaving.
- Tricky commands. Tricky is always following the player but C menu commands are locked until receiving `Tricky (Progressive)` item.
- Quest items and some keys
- Dig spots with Tricky
- Fuel Cells
- Store items

The 2 `SHW Alpine Root` and 2 `DIM Alpine Root` both appear as "Alpine Root" in the C menu. Check the tracker to know which one you have.
The 3 `SharpClaw Fort Bride Cogs` items don't show in the C menu, they will be already placed in the mechanism.

### Current areas
- ThornTail Hollow
- ThornTail Hollow Ancient Well
- Ice Mountain
- SnowHorn Wastes
- DarkIce Mines

`LightFoot Village` and `Moon Mountain Pass` are accessible but *NOT* randomized. Only `2 Fuel Cells` and `1 Digspot` are shuffled just behind the closed gate to LFV.
`SnowHorn Wastes` is fully open to prevent softlocks but logic requires `Tricky` to access it.

Randomizer starts with the flying ship sequence like normal. The client connected correctly if the *magic meter* shows up during gameplay.

## Credits
DacoderWolf - Item and location logic</br>
OmegaZeron - Poptracker Pack</br>
RenaKunisaki - [Amethyst mod](https://github.com/RenaKunisaki/StarFoxAdventures) and reverse engineering of SFA