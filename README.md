# FarmBeats Sensor Data Collector

A standalone Python application for collecting sensor data from FarmBeats for Students Grove Smart Agriculture Kit sensors. This single-file application reads data from multiple environmental sensors and logs it to CSV files with comprehensive event logging.

## Features

- **Single-file application**: All sensor classes and controller logic in one Python file
- **Multiple sensor support**: Reads data from 5 different sensor types
- **CSV data logging**: Automatically writes sensor readings to CSV files
- **Event logging**: Comprehensive logging of important events and errors
- **Configurable polling**: Adjustable sensor reading intervals
- **Error handling**: Graceful handling of sensor failures and initialization issues
- **Rolling averages**: Data smoothing for noisy sensors

## Supported Sensors

1. **Air Temperature & Humidity Sensor (DHT11)**
   - Air temperature (°C)
   - Air humidity (%)

2. **Soil Temperature Sensor (DS18B20)**
   - Soil temperature (°C)

3. **Soil Moisture Sensor (Grove Capacitive)**
   - Soil moisture level (0.0 - 1.0)

4. **Sunlight Sensor (SI115X)**
   - Visible light intensity
   - UV index
   - IR light intensity

5. **Relay Sensor (Grove Relay)**
   - Relay state (on/off)
   - Relay state change detection

## Hardware Requirements

- Raspberry Pi (tested on Raspberry Pi 4)
- FarmBeats for Students Grove Smart Agriculture Kit sensors:
  - DHT11 Temperature & Humidity Sensor (connected to pin D16)
  - DS18B20 One-Wire Temperature Sensor
  - Grove Capacitive Soil Moisture Sensor (connected to ADC pin 0)
  - Grove Sunlight Sensor (SI115X)
  - Grove Relay (connected to pin D22)
- Grove Base Hat for Raspberry Pi

## Software Requirements

- Python 3.6 or higher
- Raspberry Pi OS (or compatible Linux distribution)
- Required Python packages (see Installation)

## Installation

### 1. Clone or download this repository

```bash
cd /path/to/your/project
```

### 2. Create a virtual environment (recommended)

```bash
python3 -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install grove.py seeed-python-dht seeed-python-Ds18b20 seeed-python-si114x
```

### 4. Ensure hardware interfaces are enabled

On Raspberry Pi, make sure the following interfaces are enabled:
- I2C
- SPI
- 1-Wire (for DS18B20)

You can enable them using `raspi-config`:

```bash
sudo raspi-config
```

Navigate to **Interfacing Options** and enable:
- I2C
- SPI
- 1-Wire

## Usage

### Basic Usage

Run the application with default settings:

```bash
python sensor_data_collector.py
```

### Command-Line Options

```bash
python sensor_data_collector.py [OPTIONS]
```

**Options:**
- `--csv PATH`: Specify CSV output file path (default: `output/sensor_data.csv`)
- `--log PATH`: Specify log file path (default: `sensor_collector.log`)
- `--interval SECONDS`: Set polling interval in seconds (default: 5.0)

### Examples

**Custom CSV and log file locations:**

```bash
python sensor_data_collector.py --csv data/my_sensors.csv --log logs/app.log
```

**Poll sensors every 10 seconds:**

```bash
python sensor_data_collector.py --interval 10.0
```

**Full custom configuration:**

```bash
python sensor_data_collector.py --csv output/farm_data.csv --log logs/farmbeats.log --interval 30.0
```

### Stopping the Application

Press `Ctrl+C` to gracefully stop the application. The application will finish writing current data and close log files properly.

## Output Files

### CSV Data File

The application creates a CSV file (default: `output/sensor_data.csv`) with the following columns:

- `date_time`: Timestamp of the reading (YYYY-MM-DD HH:MM:SS)
- `soil_temperature`: Soil temperature in °C
- `soil_moisture`: Soil moisture level (0.0 - 1.0)
- `air_temperature`: Air temperature in °C
- `air_humidity`: Air humidity percentage
- `sunlight_visible`: Visible light intensity
- `sunlight_uv`: UV index
- `sunlight_ir`: IR light intensity
- `relay`: Relay state (0 = off, 1 = on)
- `relay_state_change`: Boolean indicating if relay state changed

The CSV file is created automatically if it doesn't exist, and new readings are appended to it.

### Log File

The application creates a log file (default: `sensor_collector.log`) that records:

- Application startup and shutdown
- Sensor initialization status
- Sensor reading errors
- Relay state changes
- Important events and warnings

Log entries include timestamps and log levels (INFO, WARNING, ERROR, DEBUG).

## Project Structure

```
easyfarmbeats/
├── sensor_data_collector.py  # Main application file
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── .gitignore                # Git ignore rules
├── output/                   # CSV output directory (created automatically)
│   └── sensor_data.csv      # Sensor data CSV file
└── sensor_collector.log      # Application log file
```

## Sensor Configuration

The sensor pin configurations are defined in the sensor classes and can be modified if needed:

- **DHT11**: Pin D16 (default)
- **Soil Moisture**: ADC pin 0 (default)
- **Relay**: Pin D22 (default)
- **DS18B20**: 1-Wire interface (no pin configuration needed)
- **SI115X**: I2C interface (no pin configuration needed)

To change pin assignments, edit the corresponding sensor class in `sensor_data_collector.py`.

## Troubleshooting

### Sensors Not Reading

1. **Check hardware connections**: Ensure all sensors are properly connected to the Grove Base Hat
2. **Verify interfaces are enabled**: Make sure I2C, SPI, and 1-Wire are enabled in `raspi-config`
3. **Check permissions**: You may need to run with `sudo` or add your user to the `i2c` and `gpio` groups:
   ```bash
   sudo usermod -a -G i2c,gpio $USER
   ```
4. **Review log file**: Check `sensor_collector.log` for specific error messages

### Permission Errors

If you encounter permission errors when accessing sensors:

```bash
sudo python sensor_data_collector.py
```

Or add your user to the appropriate groups (see above).

### CSV File Not Created

- Ensure the application has write permissions in the output directory
- Check that the directory path exists or can be created
- Review the log file for specific error messages

### Import Errors

If you get import errors for sensor libraries:

```bash
pip install --upgrade grove.py seeed-python-dht seeed-python-Ds18b20 seeed-python-si114x
```

## Data Analysis

The CSV file can be opened in:
- Microsoft Excel
- Google Sheets
- Python pandas
- Any CSV-compatible data analysis tool

Example Python analysis:

```python
import pandas as pd

# Load the CSV data
df = pd.read_csv('output/sensor_data.csv', parse_dates=['date_time'])

# View basic statistics
print(df.describe())

# Plot temperature over time
df.plot(x='date_time', y='air_temperature')
```

## License

This project is based on the FarmBeats for Students project. Please refer to the original project's license for details.

## Acknowledgments

- Based on [FarmBeats for Students](https://github.com/microsoft/farmbeatsforstudents) by Microsoft
- Uses Grove sensor libraries from Seeed Studio
- Designed for educational and agricultural monitoring applications

## Support

For issues related to:
- **Hardware**: Refer to the FarmBeats for Students documentation
- **Sensor libraries**: Check Seeed Studio documentation
- **Application bugs**: Review the log file for detailed error messages

## Contributing

This is a standalone, simplified version of the FarmBeats data collection system. Feel free to modify and adapt it for your specific needs.

