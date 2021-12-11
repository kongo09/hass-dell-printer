[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)

Note: this is work in progress. Currently, it doesn't work at all.

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
* Go to Configuration -> Integrations
* Click `Add Integration`
* Search for `Dell Printer` and select it
* The integration will try to automatically discover your printer hostname or IP address
  
  
## Usage:

### Devices:

The integration provides a printer device with several entities to Home Assistant
  
  
### Entities:

| Entity ID                                      | Type        |  Description                                                               |
|------------------------------------------------|-------------|----------------------------------------------------------------------------|
| sensor.dell_printer_pages_printed              | Sensor      |  The total number of printed pages of this printer                         |
