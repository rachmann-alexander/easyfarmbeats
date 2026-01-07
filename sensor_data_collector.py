#!/usr/bin/env python3
"""
FarmBeats Sensor Data Collector
A single-file application for reading sensor data and logging to CSV and log files.
"""

import datetime
import time
import csv
import logging
import os
from typing import Optional, Tuple

# ============================================================================
# BASE SENSOR CLASS
# ============================================================================

class BaseSensor:
    """Base class for all sensors."""
    
    def __init__(self):
        self.null_value = 0
        self.sensor = None
        self.measurements = []
        self.upper_reasonable_bound = 200
        self.lower_reasonable_bound = 0
        self.init = False

    def setup(self):
        """Initialize the sensor."""
        self.sensor = None

    def read(self):
        """Read sensor data."""
        return None

    def average(self, measurements):
        """Calculate average of measurements."""
        if len(measurements) != 0:
            return sum(measurements) / len(measurements)
        else:
            return self.null_value

    def rolling_average(self, measurement, measurements, size):
        """Calculate rolling average with bounds checking."""
        if measurement is None:
            return None
        if self.lower_reasonable_bound < measurement < self.upper_reasonable_bound:
            if len(measurements) >= size:
                measurements.pop(0)
            measurements.append(measurement)
        return self.average(measurements)

    def mapNum(self, val, old_max, old_min, new_max, new_min):
        """Map a value from one range to another."""
        try:
            old_range = float(old_max - old_min)
            new_range = float(new_max - new_min)
            new_value = float(((val - old_min) * new_range) / old_range) + new_min
            return new_value
        except Exception:
            return val


# ============================================================================
# SENSOR IMPLEMENTATIONS
# ============================================================================

class AirTemperatureHumiditySensor(BaseSensor):
    """Air temperature and humidity sensor (DHT11)."""
    
    def __init__(self):
        BaseSensor.__init__(self)
        self.dht_pin = 16
        self.dht_type = '11'
        self.humidity_measurements = []
        self.temperature_measurements = []
        self.sensor = None
        self.setup()

    def setup(self):
        """Initialize the DHT sensor."""
        try:
            from seeed_dht import DHT
            self.sensor = DHT(self.dht_type, self.dht_pin)
            self.init = True
        except Exception as e:
            print(f"AirTemperatureHumiditySensor.setup: {e}")
            self.init = False

    def read(self):
        """Read air humidity and temperature."""
        air_humidity, air_temperature = self._take_readings()

        if (air_humidity == 0 or air_temperature == 0):
            time.sleep(0.1)
            reH, reT = self._take_readings()
            if (air_humidity == 0):
                air_humidity = reH
            if (air_temperature == 0):
                air_temperature = reT

        air_humidity = self.rolling_average(air_humidity, self.humidity_measurements, 10)
        air_temperature = self.rolling_average(air_temperature, self.temperature_measurements, 10)

        return air_humidity, air_temperature

    def _take_readings(self):
        """Take raw sensor readings."""
        try:
            if not self.init:
                self.setup()
            air_humidity, air_temperature = self.sensor.read()
        except Exception as e:
            print(f"AirTemperatureHumiditySensor.read: {e}")
            self.init = False
            air_humidity, air_temperature = self.null_value, self.null_value
        finally:
            return air_humidity, air_temperature


class SoilTemperatureSensor(BaseSensor):
    """Soil temperature sensor (DS18B20)."""
    
    def __init__(self):
        BaseSensor.__init__(self)
        self.sensor = None
        self.setup()

    def setup(self):
        """Initialize the DS18B20 sensor."""
        try:
            from seeed_ds18b20 import grove_ds18b20
            self.sensor = grove_ds18b20()
            self.init = True
        except Exception as e:
            print(f"SoilTemperatureSensor.setup: {e}")
            self.init = False

    def read(self):
        """Read soil temperature."""
        try:
            if not self.init:
                self.setup()
            soil_temperature, soil_tempF = self.sensor.read_temp
            soil_temperature = self.rolling_average(soil_temperature, self.measurements, 10)
        except Exception as e:
            print(f"SoilTemperatureSensor.read: {e}")
            soil_temperature = self.null_value
            self.init = False
        finally:
            return soil_temperature


class SoilMoistureSensor(BaseSensor):
    """Soil moisture sensor."""
    
    def __init__(self):
        BaseSensor.__init__(self)
        self.sensor = None
        self.soil_moisture_pin = 0
        self.setup()

    def setup(self):
        """Initialize the ADC for soil moisture."""
        try:
            from grove.adc import ADC
            self.sensor = ADC()
            self.init = True
        except Exception as e:
            print(f"SoilMoistureSensor.setup: {e}")
            self.init = False

    def read(self):
        """Read soil moisture level."""
        try:
            if not self.init:
                self.setup()
            # Grove Capacitive Soil Moisture Sensor (4096-0) - Dry ~2504 Wet ~1543
            soil_moisture = self.sensor.read_raw(self.soil_moisture_pin)
            soil_moisture = self.mapNum(soil_moisture, 2504, 1543, 0.00, 1.00)
            soil_moisture = self.rolling_average(soil_moisture, self.measurements, 20)
        except Exception as e:
            print(f"SoilMoistureSensor.read: {e}")
            soil_moisture = self.null_value
            self.init = False
        finally:
            return soil_moisture


class SunlightSensor(BaseSensor):
    """Sunlight sensor (SI115X)."""
    
    def __init__(self):
        BaseSensor.__init__(self)
        self.sensor = None
        self.setup()

    def setup(self):
        """Initialize the SI115X sensor."""
        try:
            from seeed_si115x import grove_si115x
            self.sensor = grove_si115x()
            self.init = True
        except Exception as e:
            print(f"SunlightSensor.setup: {e}")
            self.init = False

    def read(self):
        """Read sunlight measurements (visible, UV, IR)."""
        try:
            if not self.init:
                self.setup()
            sunlight_visible = self.sensor.ReadVisible
            sunlight_uv = self.sensor.ReadUV / 100
            sunlight_uv = self.rolling_average(sunlight_uv, self.measurements, 10)
            sunlight_ir = self.sensor.ReadIR
        except Exception as e:
            print(f"SunlightSensor.read: {e}")
            sunlight_visible = self.null_value
            sunlight_uv = self.null_value
            sunlight_ir = self.null_value
        finally:
            return (sunlight_visible, sunlight_uv, sunlight_ir)


class RelaySensor(BaseSensor):
    """Relay sensor for controlling devices."""
    
    def __init__(self):
        BaseSensor.__init__(self)
        self.sensor = None
        self.soil_moisture_pin = 0
        self.relay_pin = 22
        self.setup()

    def setup(self):
        """Initialize the relay."""
        try:
            from grove.grove_relay import GroveRelay
            self.sensor = GroveRelay(self.relay_pin)
            self.init = True
        except Exception as e:
            print(f"RelaySensor.setup: {e}")
            self.init = False

    def read(self):
        """Read relay state."""
        try:
            if not self.init:
                self.setup()
            relay_state = self.sensor.read()
        except Exception as e:
            print(f"RelaySensor.read: {e}")
            self.init = False
            relay_state = self.null_value
        finally:
            return relay_state

    def on(self):
        """Turn relay on."""
        if self.init:
            self.sensor.on()

    def off(self):
        """Turn relay off."""
        if self.init:
            self.sensor.off()


# ============================================================================
# SENSOR POLLER (CONTROLLER)
# ============================================================================

class SensorPoller:
    """Controller for polling all sensors and managing data collection."""
    
    def __init__(self):
        self.null_value = 0
        
        # Initialize all sensors
        self.soil_temperature_sensor = SoilTemperatureSensor()
        self.soil_moisture_sensor = SoilMoistureSensor()
        self.air_temperature_humidity_sensor = AirTemperatureHumiditySensor()
        self.sunlight_sensor = SunlightSensor()
        self.relay_sensor = RelaySensor()
        self.previous_relay_state = 0
        
        # Data storage
        self.date_time = None
        self.soil_temperature = None
        self.soil_moisture = None
        self.air_temperature = None
        self.air_humidity = None
        self.sunlight_visible = None
        self.sunlight_uv = None
        self.sunlight_ir = None
        self.relay = None
        self.relay_state_change = False

    def poll_sensors(self):
        """Poll all sensors and update data."""
        self.set_date_time()
        self.set_soil_temperature()
        self.set_soil_moisture()
        self.set_air_temperature_humidity()
        self.set_sunlight()
        self.set_relay()
        self.set_relay_state_change()

    def set_date_time(self):
        """Set current date and time."""
        self.date_time = datetime.datetime.now()

    def set_soil_temperature(self):
        """Read soil temperature sensor."""
        self.soil_temperature = self.soil_temperature_sensor.read()

    def set_soil_moisture(self):
        """Read soil moisture sensor."""
        self.soil_moisture = self.soil_moisture_sensor.read()

    def set_air_temperature_humidity(self):
        """Read air temperature and humidity sensor."""
        self.air_humidity, self.air_temperature = self.air_temperature_humidity_sensor.read()

    def set_sunlight(self):
        """Read sunlight sensor."""
        sunlight_visible, sunlight_uv, sunlight_ir = self.sunlight_sensor.read()
        self.sunlight_visible = sunlight_visible
        self.sunlight_uv = sunlight_uv
        self.sunlight_ir = sunlight_ir

    def set_relay(self):
        """Read relay state."""
        self.relay = self.relay_sensor.read()

    def set_relay_state_change(self):
        """Detect relay state changes."""
        try:
            if self.relay == self.previous_relay_state:
                self.relay_state_change = False
            else:
                self.relay_state_change = True
        except Exception:
            pass
        finally:
            self.previous_relay_state = self.relay

    def get_data_dict(self):
        """Get all sensor data as a dictionary."""
        return {
            'date_time': self.date_time.strftime("%Y-%m-%d %H:%M:%S") if self.date_time else None,
            'soil_temperature': self._format_value(self.soil_temperature),
            'soil_moisture': self._format_value(self.soil_moisture),
            'air_temperature': self._format_value(self.air_temperature),
            'air_humidity': self._format_value(self.air_humidity),
            'sunlight_visible': self._format_value(self.sunlight_visible),
            'sunlight_uv': self._format_value(self.sunlight_uv),
            'sunlight_ir': self._format_value(self.sunlight_ir),
            'relay': self._format_value(self.relay),
            'relay_state_change': self.relay_state_change
        }

    def _format_value(self, value):
        """Format a value for CSV output."""
        if value is None:
            return None
        try:
            return float("{:.2f}".format(float(value)))
        except (ValueError, TypeError):
            try:
                return int(value)
            except (ValueError, TypeError):
                return str(value)


# ============================================================================
# CSV WRITER
# ============================================================================

class CSVWriter:
    """Handles writing sensor data to CSV files."""
    
    def __init__(self, csv_file='output/sensor_data.csv'):
        self.csv_file = csv_file
        self.fieldnames = [
            'date_time',
            'soil_temperature',
            'soil_moisture',
            'air_temperature',
            'air_humidity',
            'sunlight_visible',
            'sunlight_uv',
            'sunlight_ir',
            'relay',
            'relay_state_change'
        ]
        self._ensure_output_dir()
        self._initialize_csv()

    def _ensure_output_dir(self):
        """Create output directory if it doesn't exist."""
        output_dir = os.path.dirname(self.csv_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

    def _initialize_csv(self):
        """Initialize CSV file with headers if it doesn't exist."""
        if not os.path.exists(self.csv_file):
            try:
                with open(self.csv_file, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                    writer.writeheader()
            except Exception as e:
                logging.error(f"Failed to initialize CSV file: {e}")

    def write_data(self, data_dict):
        """Write sensor data to CSV file."""
        try:
            with open(self.csv_file, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writerow(data_dict)
        except Exception as e:
            logging.error(f"Failed to write to CSV file: {e}")


# ============================================================================
# LOGGER SETUP
# ============================================================================

def setup_logging(log_file='sensor_collector.log'):
    """Configure logging to file and console."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


# ============================================================================
# MAIN APPLICATION
# ============================================================================

class SensorDataCollector:
    """Main application class for sensor data collection."""
    
    def __init__(self, csv_file='output/sensor_data.csv', log_file='sensor_collector.log', 
                 polling_interval=5.0):
        """
        Initialize the sensor data collector.
        
        Args:
            csv_file: Path to CSV output file
            log_file: Path to log file
            polling_interval: Time between sensor readings in seconds
        """
        self.logger = setup_logging(log_file)
        self.logger.info("=" * 60)
        self.logger.info("FarmBeats Sensor Data Collector Starting")
        self.logger.info("=" * 60)
        
        self.polling_interval = polling_interval
        self.sensor_poller = SensorPoller()
        self.csv_writer = CSVWriter(csv_file)
        self.running = False
        
        self.logger.info(f"CSV output file: {csv_file}")
        self.logger.info(f"Log file: {log_file}")
        self.logger.info(f"Polling interval: {polling_interval} seconds")

    def start(self):
        """Start the sensor data collection loop."""
        self.running = True
        self.logger.info("Starting sensor data collection...")
        
        try:
            while self.running:
                try:
                    # Poll all sensors
                    self.sensor_poller.poll_sensors()
                    
                    # Get data as dictionary
                    data = self.sensor_poller.get_data_dict()
                    
                    # Write to CSV
                    self.csv_writer.write_data(data)
                    
                    # Log important events
                    self._log_events(data)
                    
                    # Log successful reading
                    self.logger.debug(f"Sensor data collected: {data['date_time']}")
                    
                except KeyboardInterrupt:
                    self.logger.info("Received interrupt signal, shutting down...")
                    self.running = False
                    break
                except Exception as e:
                    self.logger.error(f"Error during sensor polling: {e}", exc_info=True)
                
                # Wait before next reading
                time.sleep(self.polling_interval)
                
        except Exception as e:
            self.logger.error(f"Fatal error in main loop: {e}", exc_info=True)
        finally:
            self.stop()

    def _log_events(self, data):
        """Log important events based on sensor data."""
        # Log relay state changes
        if data.get('relay_state_change'):
            self.logger.info(f"Relay state changed to: {data['relay']}")
        
        # Log sensor initialization issues
        if data.get('soil_temperature') is None:
            self.logger.warning("Soil temperature sensor returned None")
        if data.get('soil_moisture') is None:
            self.logger.warning("Soil moisture sensor returned None")
        if data.get('air_temperature') is None or data.get('air_humidity') is None:
            self.logger.warning("Air temperature/humidity sensor returned None")
        if data.get('sunlight_visible') is None:
            self.logger.warning("Sunlight sensor returned None")

    def stop(self):
        """Stop the sensor data collection."""
        self.running = False
        self.logger.info("Sensor data collection stopped")
        self.logger.info("=" * 60)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='FarmBeats Sensor Data Collector')
    parser.add_argument('--csv', default='output/sensor_data.csv',
                       help='Path to CSV output file (default: output/sensor_data.csv)')
    parser.add_argument('--log', default='sensor_collector.log',
                       help='Path to log file (default: sensor_collector.log)')
    parser.add_argument('--interval', type=float, default=5.0,
                       help='Polling interval in seconds (default: 5.0)')
    
    args = parser.parse_args()
    
    collector = SensorDataCollector(
        csv_file=args.csv,
        log_file=args.log,
        polling_interval=args.interval
    )
    
    try:
        collector.start()
    except KeyboardInterrupt:
        collector.logger.info("Application interrupted by user")
    except Exception as e:
        collector.logger.error(f"Application error: {e}", exc_info=True)


if __name__ == '__main__':
    main()

