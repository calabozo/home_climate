from wibeee import WiBeeInfluxDB


    

def parse_arguments():
    import argparse
    parser = argparse.ArgumentParser(description='WiBeee power monitoring')
    parser.add_argument('--config', type=str, default='config.ini', help='Path to the config.ini file')
    return parser.parse_args()

if __name__ == "__main__":

    args = parse_arguments()
    config_path = args.config

    wibeee = WiBeeInfluxDB(config_path)
    while True:
        try:
            wibeee.run()
        except Exception as e:
            print(f"An error occurred while starting the server: {e}")
