import random
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from core import mqtt_bridge as mb
from core.words import NOMBRES, WORDS

THRESHOLD = 0.70
MAX_ACIERTOS = 3
MAX_FALLOS = 3


def _siguiente():
    """Palabra nueva: sale de un mazo barajado y nunca es igual a la actual."""
    ss = st.session_state
    actual = ss.get("target")
    if not ss.get("deck"):
        ss.deck = random.sample(WORDS, len(WORDS))
    w = ss.deck.pop()
    if w == actual:
        w = random.choice([x for x in WORDS if x != actual])
    return w


def _payload(result, guess=""):
    ss = st.session_state
    return {"result": result, "aciertos": ss.aciertos, "fallos": ss.fallos,
            "guess": NOMBRES.get(guess, guess)}


def init():
    ss = st.session_state
    if "aciertos" not in ss:
        ss.aciertos = 0
        ss.fallos = 0
        ss.target = _siguiente()
        ss.canvas_key = 0
        ss.finished = None      # None, "WIN" o "LOSE"
        ss.msg = None
        ss.balloons = False
        mb.publish(_payload("NEW"))


def reset():
    ss = st.session_state
    ss.aciertos = 0
    ss.fallos = 0
    ss.deck = random.sample(WORDS, len(WORDS))  # mazo nuevo cada partida
    ss.target = _siguiente()
    ss.canvas_key += 1
    ss.finished = None
    ss.msg = None
    mb.publish(_payload("NEW"))


def handle_hardware_events():
    for ev in mb.poll_events():
        if ev.get("action") == "RESET_REQ":
            reset()
            st.rerun()


def poll(key):
    """Escucha el botón físico. Se puede apagar desde la barra lateral."""
    if st.sidebar.toggle("Escuchar botón físico", value=True, key=f"tg_{key}"):
        st_autorefresh(interval=3000, key=key)
    handle_hardware_events()


def evaluate(label, prob):
    ss = st.session_state
    ss.canvas_key += 1  # limpia el lienzo
    nombre = NOMBRES.get(label, label)
    objetivo = NOMBRES[ss.target]
    ss.last_try = f"IA vio '{label}' ({prob:.0%}); objetivo era '{ss.target}'"

    if label == ss.target and prob >= THRESHOLD:
        ss.aciertos += 1
        if ss.aciertos >= MAX_ACIERTOS:
            ss.finished = "WIN"
            ss.balloons = True
            ss.msg = ("success", f"¡Es un {nombre}! 🔓 Cerradura desbloqueada")
            mb.publish(_payload("WIN", label))
        else:
            ss.msg = ("success", f"¡Es un {nombre}! ({prob:.0%}) Nueva palabra 👇")
            ss.target = _siguiente()
            mb.publish(_payload("MATCH", label))
    else:
        ss.fallos += 1
        if ss.fallos >= MAX_FALLOS:
            ss.finished = "LOSE"
            ss.msg = ("error", f"Parece un {nombre}, y era {objetivo}. ¡Game over!")
            mb.publish(_payload("LOSE", label))
        else:
            ss.msg = ("error",
                      f"Parece un {nombre} ({prob:.0%}), y era {objetivo}. Nueva palabra 👇")
            ss.target = _siguiente()
            mb.publish(_payload("MISMATCH", label))


def aviso(tipo, texto):
    """Guarda un mensaje para que sobreviva al refresco automático."""
    st.session_state.msg = (tipo, texto)
    st.rerun()


def render_header():
    ss = st.session_state
    if ss.finished == "WIN":
        st.subheader("🎉 ¡GANASTE!")
    elif ss.finished == "LOSE":
        st.subheader("💀 GAME OVER")
    else:
        st.subheader(f"Dibuja: **{NOMBRES[ss.target]}**")

    c1, c2 = st.columns(2)
    c1.progress(ss.aciertos / MAX_ACIERTOS, text=f"🟢 Aciertos {ss.aciertos}/{MAX_ACIERTOS}")
    c2.progress(ss.fallos / MAX_FALLOS, text=f"🔴 Fallos {ss.fallos}/{MAX_FALLOS}")

    if ss.msg:
        getattr(st, ss.msg[0])(ss.msg[1])
    if ss.balloons:
        st.balloons()
        ss.balloons = False

    if ss.finished and st.button("Nueva partida"):
        reset()
        st.rerun()

    with st.expander("🔧 Diagnóstico"):
        st.write("Último mensaje MQTT:", ss.get("last_publish", "ninguno"))
        st.write("Último intento:", ss.get("last_try", "ninguno"))
