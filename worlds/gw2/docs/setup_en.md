# Guild Wars 2 for Archipelago Setup Guide

## Required Software
* [BlishHUD](https://blishhud.com/).
* A free or paid version of [Guild Wars 2](https://www.guildwars2.com/en/)
* This [Gw2 Archipelago](https://github.com/Feldar99/Archipelago/releases) release
* The [Archipelago Launcher](https://archipelago.gg/tutorial/Archipelago/setup/en)

## Installing the Archipelago Mod using BlishHUD
1. Move BlishHUD to a convenient location. You will need to open it manually.
2. Move Gw2Archipelago.bhm to the BlishHUD module directory. This will probably be
`Documents/Guild Wars 2/addons/blishud/modules`
3. Launch Gw2
4. Open BlishHUD
5. Click the BlishHUD icon in the upper left hand corner of the Guild Wars 2 screen
6. Follow the instructions in "Manage API Keys" to register an API key with BlishHUD
7. Under Manage Modules, make sure that Archipelago is enabled

## Configuring your YAML File
### What is a YAML and why do I need one?
A YAML file is the way that you provide your player options to Archipelago.
See the [basic multiworld setup guide](/tutorial/Archipelago/setup/en) here on the Archipelago website to learn more.

### Where do I get a YAML?
Until this world is released you will have to edit your YAML manually. You can modify the provided template, but
it is recommended that you generate one using the provided gw2YamlGenerator.exe to create one with triggers for 
using your existing characters. These triggers will set the profession and race to match the character and 
update the max_quests value to be the number of quests that character has remaining in the storyline.  You may
modify the generated yaml how you like as well.

### Generating a multi-world
1. Double click the .apworld file to install it into your `Archipelago/custom_worlds/` directory.
   * If you have an old version installed in `Archipelago/lib/worlds/` you will need to delete that.
2. Follow the [standard instructions](https://archipelago.gg/tutorial/Archipelago/setup/en) for generating a 
game locally 

### Joining an Archipelago Game in Guild Wars 2
1. Start the game and open the BlishHUD window.
2. Under "Manage Modules", click "Archipelago"
3. Enable all requested API Permissions
4. Enter the Archipelago Server URL including the port number
5. Enter your slot name
6. If the "Enable Module" button is not disabled, click it.
7. Click on the archipelago icon at the top of the screen to open the Archipelago window.
8. Click "Connect"
9. If you don't know what character you will be playing it should populate on the modules screen now.
    * The profession and race will also be shown. If you are making a new character, make sure they match these
10. Log into your chosen character
    * If you created a new character for this, change the character name in the manage modules at this time 
11. Click "Generate Locations." This can take several minutes, and when it's done you will see a selection of achievement 
locations at the bottom of the archipelago window
12. In your Hero panel, clear an equipment template and a build template and activate the empty templates
13. Equip gear, skills, and traits that the Archipelago module says you are allowed to use.
    * If you created a new character, feel free to continue using the starting weapon until you finish the tutorial zone

   
## Hints and other commands
While playing in a multiworld, you can interact with the server using various commands listed in the 
[commands guide](/tutorial/Archipelago/commands/en). You can use the Archipelago Text Client to do this,
which is included in the latest release of the [Archipelago software](https://github.com/ArchipelagoMW/Archipelago/releases/latest).

### Notes about Gw2 implementation
* Your objective is to collect a number of "Mist Fragments" which are placed behind checks. They are all local in the 
current implementation
* This module uses the Gw2 public API to track locations, but this API can take up to 15 minutes to update, so you will
not see your locations checked immediately
* In order to not tie up your account entirely when doing an Archipelago run, this mod does not check that you are
limiting yourself to the unlocked skills and traits
* If any achievements are included as locations that you feel shouldn't be, please let me know in the Discord. This is
unfortunately a much more manual process than I had hoped. In the meantime, once you've gotten everything that you can
feel free to hit the generate locations button again to get new achievements
* It is recommended to play with the text client open on a second monitor, because there are currently no in-game 
notifications when you receive an item