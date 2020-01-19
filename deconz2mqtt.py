import asyncio
import websockets
import logging
from hbmqtt.client import MQTTClient
from hbmqtt.client import ConnectException
import json
import yaml
import io
import argparse

def _config_value(config: dict, name: str, default = None):
    names = name.split('.')
    result = None
    if len(names) > 0:
        while config is not None:
            n = names.pop(0)
            result = config.get(n, None)
            config = result if len(names) > 0 else None
    return result if result is not None else default

async def mqtt_publisher(config: dict, message_queue: asyncio.Queue) -> None:
    log = logging.getLogger('deconz2mqtt.mqtt_publisher')
    mqtt = MQTTClient(config=_config_value(config, 'client'))
    log.info('Connecting to MQTT...')
    try:
        await mqtt.connect(uri=_config_value(config, 'client.uri'), cleansession=_config_value(config, 'client.cleansession'))
    except ConnectException as ce:
        log.error('Can\'t connect to MQTT: {}'.format(ce))
    log.info('Connected to MQTT')
    while True:
        message = await message_queue.get()
        message_json = json.loads(message)
        t = message_json.get('t', None)
        if t is None:
            log.warn('Message with empty type. Message={}'.format(message))
            continue
        if t != 'event':
            log.warn('Message with unsupported type={}. Message={}'.format(t, message))
            continue
        e = message_json.get('e', None)
        if e != 'changed':
            log.debug('Message with event type={} will be skipped. Only "changed" event type is supported. Message={}'.format(e, message))
            continue
        r = message_json.get('r', None)
        if r is None:
            log.warn('Message with empty resource type. Message={}'.format(message))
            continue
        id = message_json.get('id', None)
        if id is None:
            log.warn('Message without id. Message={}'.format(message))
            continue
        event_state = message_json.get('state', None)
        event_config = message_json.get('config', None)
        if event_state is None and event_config is None:
            log.debug('Message without state or config. Message={}'.format(message))
            continue
        # prepare mqtt topic
        mqtt_topic = _config_value(config, 'topic_prefix', 'deconz')
        mqtt_topic += '/{}/{}/{}'.format(r, id, 'state' if event_state is not None else 'config')
        # prepare mqtt payload
        mqtt_payload = event_state if event_state is not None else event_config
        mqtt_payload = json.dumps(mqtt_payload).encode('utf-8')
        log.debug('Publishing: topic={} payload={}'.format(mqtt_topic, mqtt_payload))
        await mqtt.publish(mqtt_topic, mqtt_payload)

async def deconz_message_reader(config: dict, message_queue: asyncio.Queue) -> None:
    log = logging.getLogger('deconz2mqtt.deconz_message_reader')
    while True:
        try:
            async with websockets.connect(config['uri']) as websocket:
                log.info('Connected')
                async for message in websocket:
                    log.debug('Got message: {}'.format(message))
                    message_queue.put_nowait(message)
        except (OSError, websockets.exceptions.ConnectionClosedError) as error:
            log.error("Can't read message from wbesockets. {}: {}".format(error.__class__.__name__, error))
            log.info('Connection retry in 20 seconds')
            await asyncio.sleep(20)

async def main(config: dict):
    message_queue = asyncio.Queue(10)
    mqtt = asyncio.create_task(mqtt_publisher(_config_value(config, 'mqtt'), message_queue))
    deconz = asyncio.create_task(deconz_message_reader(_config_value(config, 'deconz'), message_queue))

    done, pending = await asyncio.wait([mqtt, deconz], return_when=asyncio.FIRST_EXCEPTION)
    for task in done:
        task.result()
    for task in pending:
        task.cancel()

if __name__ == "__main__":

    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    args = parser.parse_args()

    # read config file
    with io.open(args.config, 'r') as stream:
        config = yaml.safe_load(stream)

    # configure logging
    logging.basicConfig(
        format='%(asctime)s %(levelname)s:%(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    for logger_name, logger_level in _config_value(config, 'logging', {}).items():
        logging.getLogger(None if logger_name == 'root' else logger_name).setLevel(logger_level)

    asyncio.run(main(config))
