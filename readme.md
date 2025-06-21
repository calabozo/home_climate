# Home assistant


This is the home assistant configuration for the home climate project.

It is expected to be run in an Raspberry Pi. 


## Configure APP

1. Create a virtual environment and activate it

```
python3 -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
```


2. Create config.ini file

```
[influxdb]
url = http://localhost:8086
token = <YOUR_TOKEN_ID>
org = home_climate
bucket = home_climate
```



## How to configure influxDB

1. Install influx server following the instructions from here: https://docs.influxdata.com/influxdb/v2/install/#download-and-install-influxdb-v2

If the config file is not in the default location, you can create it with:
```
influxd print-config > /etc/influxdb/influxdb.conf
service influxd restart
service influxd status
```

2. Log in into the influxDB web interface and create the database [http://localhost:8086/](http://localhost:8086/) Create an user and follow the instructions. I created a bucket and an orgamization called `home_climate`. Once you finished it will provide you with token ID. Save that token ID for the config file.


3. Install influx client following the instructions from here: https://docs.influxdata.com/influxdb/v2/tools/influx-cli/?t=Linux

```
influx config create --config-name home_climate --host-url http://localhost:8086 --org home_climate --token <YOUR_TOKEN_ID> --active
```

## Run as a systemd service

A sample `home_climate.service` file is included to run the backend and web server automatically.
Update the `WorkingDirectory` and `ExecStart` paths so they point to the location of this project.

1. Copy the service file to your systemd directory:

```bash
sudo cp home_climate.service /etc/systemd/system/
```

2. Reload systemd and enable the service so it starts on boot:

```bash
sudo systemctl daemon-reload
sudo systemctl enable home_climate.service
sudo systemctl start home_climate.service
```
