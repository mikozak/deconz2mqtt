# deconz2mqtt
Simple bridge between [deCONZ websocket API](https://dresden-elektronik.github.io/deconz-rest-doc/websocket/) and MQTT broker.

## Features
Reading deCONZ websocket messages of type `event` and event type `changed` and publishing them to MQTT broker.
Note that message is published to MQTT if it contains `state` or `config` property.

### Example: state changes message

deCONZ websocket message (state changes)
```
{"e":"changed","id":"3","r":"sensors","state":{"buttonevent":1002,"lastupdated":"2020-01-11T23:35:14"},"t":"event","uniqueid":"00:15:8d:00:02:7c:93:43-01-0006"}
```

is published to MQTT with topic `deconz/sensors/3/state` (`deconz` part of the topic can be configured) and following payload
```
{"buttonevent": 1002, "lastupdated": "2020-01-11T23:35:14"}
```

## Requirements
* Python: 3.7
* deCONZ REST API: 2.04.40

# Running
First you need to configure MQTT and deCONZ details in `deconz2mqtt.yaml` then run you can start `deconz2mqtt.py`
```
python3 deconz2mqtt.py --config deconz2mqtt.yaml
```

# Running as a service

1. Clone this repository to preferred location, for example `/opt` directory
   ```
   cd /opt
   git clone https://github.com/mikozak/deconz2mqtt.git
   ```

2. Create python virtual environment for running service (this is optional step, however I recommend it)
   ```
   cd deconz2mqtt/
   python3 -m venv env
   ```

3. Install dependencies
   ```
   env/bin/python3 -m pip install --update pip -r requirements.txt
   ```

4. Edit and install configuration file `deconz2mqtt.yaml`. I prefer installing it in `/etc`
   ```
   sudo cp deconz2mqtt.yaml /etc/
   ```

5. Check whether everything works as expected
   ```
   env/bin/python3 deconz2mqtt.py --config /etc/deconz2mqtt.yaml
   ```

6. Create system user which will be used to run service process (for the purpose of this instruction 
   user named *deconz* will be used)

   ```
   sudo useradd -r deconz
   ```

7. Edit `deconz2mqtt.service` and make sure paths in `WorkingDirectory` and `ExecStart` are valid (and absolute!)


8. Install service
   ```
   sudo cp deconz2mqtt.service /etc/systemd/system/
   ```

9. Run service
   ```
   sudo systemctl start deconz2mqtt
   ```

   If you want to start the service automatically after system starts just enable it
   ```
   sudo systemctl enable deconz2mqtt
   ```