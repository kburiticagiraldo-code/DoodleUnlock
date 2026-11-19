import json, queue, uuid
import paho.mqtt.client as mqtt
import streamlit as st

BROKER = "broker.hivemq.com"
TEAM = "stivken1"
TOPIC_STATUS = f"doodleunlock/{TEAM}/game/status"
TOPIC_BUTTON = f"doodleunlock/{TEAM}/hardware/button"


@st.cache_resource  # se crea UNA sola vez
def get_bridge():
    q = queue.Queue()
    c = mqtt.Client(client_id=f"streamlit-{uuid.uuid4().hex[:6]}")

    def on_connect(client, userdata, flags, rc):
        client.subscribe(TOPIC_BUTTON, qos=1)

    def on_message(client, userdata, msg):
        try:
            q.put(json.loads(msg.payload))
        except Exception:
            pass

    c.on_connect = on_connect
    c.on_message = on_message
    c.connect(BROKER, 1883, 60)
    c.loop_start()  # hilo en segundo plano
    return c, q


def publish(data):
    c, _ = get_bridge()
    c.publish(TOPIC_STATUS, json.dumps(data), qos=1)


def poll_events():
    _, q = get_bridge()
    out = []
    while not q.empty():
        out.append(q.get())
    return out
