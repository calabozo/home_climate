from wibeee_influxdb import WiBeeeInfluxDB
from temperature_influxdb import TemperatureInfluxDB
import time
    

def parse_arguments():
    import argparse
    parser = argparse.ArgumentParser(description='WiBeee power monitoring')
    parser.add_argument('--config', type=str, default='config.ini', help='Path to the config.ini file')
    return parser.parse_args()

if __name__ == "__main__":

    args = parse_arguments()
    config_path = args.config

    wibeee = WiBeeeInfluxDB(config_path)
    temperature = TemperatureInfluxDB(config_path)
    while True:
        try:
            wibeee.save_power()            
        except Exception as e:
            print(f"An error occurred while saving power: {e}")
        
        try:
            temperature.save_temperature()
        except Exception as e:
            print(f"An error occurred while saving temperature: {e}")

        time.sleep(30)