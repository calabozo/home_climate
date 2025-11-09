
import glob
import time
import os


class Temperature:
    def __init__(self, gpio_pin=4):
        """
        Initialize temperature sensor reader for DS18B20 on 1-wire protocol.
        
        Args:
            gpio_pin: GPIO pin number (default 4, which is standard for 1-wire on Raspberry Pi)
        """
        self.gpio_pin = gpio_pin
        self.sensors = {}  # Dictionary: sensor_id -> sensor_path
        self._initialize_sensors()
    
    def _initialize_sensors(self):
        """Initialize all 1-wire sensors and find their device paths."""
        try:
            # Find all DS18B20 sensors in sysfs
            base_dir = '/sys/bus/w1/devices/'
            device_folders = glob.glob(base_dir + '28*')
            
            if not device_folders:
                raise FileNotFoundError(
                    "No DS18B20 sensor found. Make sure:\n"
                    "1. 1-wire is enabled: sudo modprobe w1-gpio && sudo modprobe w1-therm\n"
                    "2. Sensor is connected to GPIO 4\n"
                    "3. Sensor is powered correctly"
                )
            
            # Store sensor ID and path for each sensor
            for device_folder in device_folders:
                sensor_id = os.path.basename(device_folder)
                sensor_path = device_folder + '/w1_slave'
                self.sensors[sensor_id] = sensor_path
            
        except Exception as e:
            print(f"Error initializing temperature sensors: {e}")
            raise
    
    def _read_temp_raw(self, sensor_path):
        """Read raw temperature data from sysfs for a specific sensor."""
        f = open(sensor_path, 'r')
        lines = f.readlines()
        f.close()
        return lines
    
    def _read_temp_sysfs(self, sensor_path):
        """Read temperature from sysfs interface for a specific sensor."""
        lines = self._read_temp_raw(sensor_path)
        
        # Check if CRC is valid
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self._read_temp_raw(sensor_path)
        
        # Extract temperature value
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos + 2:]
            temp_c = float(temp_string) / 1000.0
            return temp_c
        
        raise ValueError("Could not parse temperature from sensor data")
    
    def get_temperature(self):
        """
        Read current temperature from all DS18B20 sensors.
        
        Returns:
            dict: Dictionary mapping sensor_id to temperature in Celsius.
                  Sensors that fail to read are excluded from the dictionary.
        """
        temperatures = {}
        
        for sensor_id, sensor_path in self.sensors.items():
            try:
                temp = self._read_temp_sysfs(sensor_path)
                temperatures[sensor_id] = temp
            except Exception as e:
                print(f"Error reading temperature from sensor {sensor_id}: {e}")
                # Continue with other sensors even if one fails
        
        return temperatures
    
