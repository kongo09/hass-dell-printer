[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)


## Support DELL printers in Home Assistant

### Supported models:
* Dell C1765nfw MFP Laser Printer 
    
  
## Setup

### Installation:
* Go to HACS -> Integrations
* Click the three dots on the top right and select `Custom Repositories`
* Enter `https://github.com/kongo09/hass-dell-printer` as repository, select the category `Integration` and click Add
* A new custom integration shows up for installation (Dell Printer) - install it
* Restart Home Assistant
  
  
### Configuration:
* The printer will be discovered automatically by Home Assistant. If not:
* Go to Configuration -> Integrations
* Click `Add Integration`
* Search for `Dell Printer` and select it
  
  
## Usage:

### Devices:

The integration provides a printer device with several entities to Home Assistant
  
  
### Entities:

| Entity ID                                      | Type               |  Description                                                               |
|------------------------------------------------|--------------------|----------------------------------------------------------------------------|
| binary_sensor.dell_printer                     | Binary Sensor      |  The general state of the printer, with informational attributes           |
| binary_sensor.adf_cover                        | Binary Sensor      |  State of the automatic document feeder cover                              |
| binary_sensor.rear_cover                       | Binary Sensor      |  State of the rear cover                                                   |
| binary_sensor.multi_purpose_feeder             | Binary Sensor      |  State of the multi purpose feeder                                         |
| binary_sensor.output_tray                      | Binary Sensor      |  State of the output tray                                                  |
| sensor.print_volume                            | Sensor             |  Number of printed pages, with attributes about paper formats              |
| sensor.cyan                                    | Sensor             |  Remaining level of cyan toner                                             |
| sensor.magenta                                 | Sensor             |  Remaining level of magenta toner                                          |
| sensor.yellow                                  | Sensor             |  Remaining level of yellow toner                                           |
| sensor.black                                   | Sensor             |  Remaining level of black toner                                            |