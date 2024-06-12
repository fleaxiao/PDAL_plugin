# PCB Design Action Recorder

PCB Design Action Recorder (PDAR) is a plugin specifically designed for KiCad that allows use to record their actions when designing PCB layout and export a `.csv` file of each step.

**Note:** This plugin has only been tested with KiCad 7.0. It's likely incompatible with later versions.

## Setup
Launch KiCad and navigate to the folder where plugins are stored.
- Go to: `Kicad -> Tools -> External Plugins -> Open plugin Directory`

Open a terminal and change directory to the plugin folder:
```bash
cd [path-to-plugins-folder]
```

Clone the DAPE-plugin repository:
```bash
git clone https://github.com/fleaxiao/DP_plugin.git
```

Refresh your plugins in KiCad:
- Go to: `Kicad -> Tools -> External Plugins -> Refresh Plugins`

The PDAC plugin should now be visible in the menu of KiCad.

## Usage


1. Open both schematic file and PCB layout file. Make sure the PCB layout is empty
1. `Initilization:`  The components from the schematic will be imported to the PCB layout design environment. 
1. ``Start Record:`` The components of a Buck conveter will be intialized with random positions, and these components will be overlapped. The size of PCB board is fixed to `60mm x 60mm`. 
2. ``End Record:`` After manual design (select, move and rotate of footprint), a `.json` file containg a state squence of footprints, tracks, and vias will be exported.
3. ``Abandon Record:`` The current design will be delected.