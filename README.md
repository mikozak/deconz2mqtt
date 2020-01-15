# deconz2mqtt
Simple bridge between [Conbee](https://phoscon.de/en/conbee2) (its [deCONZ websocket API](https://dresden-elektronik.github.io/deconz-rest-doc/websocket/)) and MQTT broker.


*deconz2mqtt.py* reads deCONZ messages, parses them and converts to MQTT message.
Let's see this on example. Following deCONZ message:
```
{"e":"changed","id":"3","r":"sensors","state":{"buttonevent":1002,"lastupdated":"2020-01-11T23:35:14"},"t":"event","uniqueid":"00:15:8d:00:02:7c:93:43-01-0006"}
```

is published to MQTT with topic `deconz/sensors/3/state` (`deconz` part of the topic can be configured) and following payload
```
{"buttonevent": 1002, "lastupdated": "2020-01-11T23:35:14"}
```

# Installation

### You will need
* *deconz2mqtt.py* - script which does the job
* *deconz2mqtt.yaml* - configuration file
* Python (at least 3.7)
* Running deCONZ REST API (at least 2.04.40)
* Running MQTT broker

### Installation steps

1. Create directory (for example */opt/deconz2mqtt*) and put inside *deconz2mqtt.py*
    ```
    cd /opt
    mkdir deconz2mqtt
    cd deconz2mqtt
    curl -o deconz2mqtt.py 'https://raw.githubusercontent.com/mikozak/deconz2mqtt/master/deconz2mqtt.py'
    ```

2. Create python virtual environment 
    ```
    python3 -m venv env
    ```

3. Install dependencies
    ```
    curl -o requirements.txt 'https://raw.githubusercontent.com/mikozak/deconz2mqtt/master/requirements.txt'
    env/bin/python -m pip install --upgrade pip -r requirements.txt
    ```

3. Install configuration file (for example in */etc*)
    ```
    sudo curl -o /etc/deconz2mqtt.yaml 'https://raw.githubusercontent.com/mikozak/deconz2mqtt/master/deconz2mqtt.yaml'
    ```

4. Edit configuration file installed in previous step. You need to verify/update at least two parameters
   * MQTT connection details
        ```
        mqtt:
            client:
            uri: "mqtt://localhost"
        ```

   * deCONZ websocket connection details
        ```
        deconz:
            uri: "ws://localhost:8080/ws"
        ```

5. Run it
    ```
    env/bin/python deconz2mqtt.py --config /etc/deconz2mqtt.yaml
    ```

### Installation as a service

1. Create system user which will be used to run service process (for the purpose of this instruction user named *deconz* will be used)
    ```
    sudo useradd -r deconz
    ```

2. Install service
    ```
    sudo curl -o /etc/systemd/system/deconz2mqtt.service 'https://raw.githubusercontent.com/mikozak/deconz2mqtt/master/deconz2mqtt.service'
    ```

3. Verify and edit if needed in `/etc/systemd/system/deconz2mqtt.service`:
    * `WorkingDirectory` and `ExecStart` paths are valid (and absolute!)
    * `User` is correct (equals username created in step 1)

4. Start service
    ```
    sudo systemctl start deconz2mqtt
    ```

    If you want to start the service automatically after system restart you need to enable it
    ```
    sudo systemctl enable deconz2mqtt
    ```
