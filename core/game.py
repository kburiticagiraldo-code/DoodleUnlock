import random
import streamlit as st
from core import mqtt_bridge as mb

WORDS = ["cat", "dog", "house", "sun", "tree", "car"]
THRESHOLD = 0.70
MAX_ACIERTOS = 3
MAX_FALLOS = 3


def _payload(result, guess=""):
    ss = st.session_state
    return {"result": result, "aciertos": ss.aciertos,
            "fallos": ss.fallos, "guess": guess}


def init():
    ss = st.session_state
    if "aciertos" not in ss:
        ss.aciertos = 0
        ss.fallos = 0
        ss.target = random.choice(WORDS)
        ss.canvas_key = 0
        ss.finished = None      # None, "WIN" o "LOSE"
        ss.msg = None
        ss.balloons = False
        mb.publish(_payload("NEW"))


def reset():
    ss = st.session_state
    ss.aciertos = 0
    ss.fallos = 0
    ss.target = random.choice(WORDS)
    ss.canvas_key += 1
    ss.finished = None
    ss.msg = None
    mb.publish(_payload("NEW"))


def handle_hardware_events():
    for ev in mb.poll_events():
        if ev.get("action") == "RESET_REQ":
            reset()
            st.rerun()


def evaluate(label, prob):
    ss = st.session_state
    ss.canvas_key += 1  # limpia el lienzo

    if label == ss.target and prob >= THRESHOLD:
        ss.aciertos += 1
        if ss.aciertos >= MAX_ACIERTOS:
            ss.finished = "WIN"
            ss.balloons = True
            ss.msg = ("success", f"¡Es un {label}! 🔓 Cerradura desbloqueada")
            mb.publish(_payload("WIN", label))
        else:
            ss.msg = ("success", f"¡Es un {label}! ({prob:.0%})")
            ss.target = random.choice(WORDS)
            mb.publish(_payload("MATCH", label))
    else:
        ss.fallos += 1
        if ss.fallos >= MAX_FALLOS:
            ss.finished = "LOSE"
            ss.msg = ("error", f"Parece un {label}. ¡Game over!")
            mb.publish(_payload("LOSE", label))
        else:
            ss.msg = ("error", f"Parece un {label} ({prob:.0%}). ¡Intenta otra vez!")
            mb.publish(_payload("MISMATCH", label))


def render_header():
    """Palabra, marcadores y mensajes. Se llama después de procesar eventos."""
    ss = st.session_state
    if ss.finished == "WIN":
        st.subheader("🎉 ¡GANASTE!")
    elif ss.finished == "LOSE":
        st.subheader("💀 GAME OVER")
    else:
        st.subheader(f"Dibuja: **{ss.target}**")

    c1, c2 = st.columns(2)
    c1.progress(ss.aciertos / MAX_ACIERTOS, text=f"🟢 Aciertos {ss.aciertos}/{MAX_ACIERTOS}")
    c2.progress(ss.fallos / MAX_FALLOS, text=f"🔴 Fallos {ss.fallos}/{MAX_FALLOS}")

    if ss.msg:
        getattr(st, ss.msg[0])(ss.msg[1])
    if ss.balloons:
        st.balloons()
        ss.balloons = False

    if ss.finished:
        if st.button("Nueva partida"):
            reset()
            st.rerun()
