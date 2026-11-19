import math
import random
import time
import streamlit as st
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh
from core import mqtt_bridge as mb
from core.words import NOMBRES, WORDS

THRESHOLD = 0.70
MAX_ACIERTOS = 3
MAX_FALLOS = 3
TIEMPO = 20      # segundos por palabra
GRACIA = 1.5     # margen por la demora de red al enviar


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
        ss.playing = False      # True mientras la partida está en curso
        ss.deadline = None
        mb.publish(_payload("NEW"))
    ss.setdefault("playing", False)
    ss.setdefault("deadline", None)


def reset():
    ss = st.session_state
    ss.aciertos = 0
    ss.fallos = 0
    ss.deck = random.sample(WORDS, len(WORDS))  # mazo nuevo cada partida
    ss.target = _siguiente()
    ss.canvas_key += 1
    ss.finished = None
    ss.msg = None
    ss.balloons = False
    ss.playing = False
    ss.deadline = None
    mb.publish(_payload("NEW"))


def iniciar():
    """Arranca la partida: corre el cronómetro de la palabra actual."""
    ss = st.session_state
    ss.msg = None
    ss.playing = True
    ss.deadline = time.time() + TIEMPO


def jugar_de_nuevo():
    """Botón de la app al terminar: partida nueva y arranca de una vez."""
    reset()
    iniciar()


def _cerrar_ronda():
    """Si la partida sigue, la palabra nueva arranca sola su cronómetro."""
    ss = st.session_state
    if ss.finished:
        ss.playing = False
        ss.deadline = None
    else:
        ss.playing = True
        ss.deadline = time.time() + TIEMPO


def tiempo_agotado():
    """Se acabó el tiempo: cuenta como fallo."""
    ss = st.session_state
    ss.canvas_key += 1
    ss.last_try = "Se acabó el tiempo"
    ss.fallos += 1
    if ss.fallos >= MAX_FALLOS:
        ss.finished = "LOSE"
        ss.msg = ("error", "⏰ Se acabó el tiempo. ¡Game over!")
        mb.publish(_payload("LOSE"))
    else:
        ss.msg = ("error", "⏰ Se acabó el tiempo: cuenta como fallo. Nueva palabra 👇")
        ss.target = _siguiente()
        mb.publish(_payload("TIMEOUT"))
    _cerrar_ronda()


def verificar_tiempo():
    ss = st.session_state
    if ss.get("playing") and ss.get("deadline") \
            and time.time() > ss.deadline + GRACIA:
        tiempo_agotado()
        st.rerun()


def handle_hardware_events():
    for ev in mb.poll_events():
        if ev.get("action") == "RESET_REQ":
            reset()
            st.rerun()


def poll(key):
    """Escucha el botón físico y vigila el cronómetro."""
    ss = st.session_state
    if st.sidebar.toggle("Escuchar botón físico", value=True, key=f"tg_{key}"):
        st_autorefresh(interval=3000, key=key)
    if ss.get("playing"):
        st_autorefresh(interval=1000, key=f"reloj_{key}")  # el reloj avanza
    handle_hardware_events()
    verificar_tiempo()


def evaluate(label, prob):
    ss = st.session_state
    ss.canvas_key += 1       # limpia el lienzo, la cámara y la foto subida
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
        casi = (label == ss.target)  # acertó la clase pero con poca seguridad
        if casi:
            detalle = (f"Casi: la IA vio {nombre} pero solo con {prob:.0%} "
                       f"de seguridad (se necesita {THRESHOLD:.0%}).")
        else:
            detalle = f"Parece un {nombre} ({prob:.0%}), y era {objetivo}."

        if ss.fallos >= MAX_FALLOS:
            ss.finished = "LOSE"
            ss.msg = ("error", f"{detalle} ¡Game over!")
            mb.publish(_payload("LOSE", label))
        else:
            ss.msg = ("error", f"{detalle} Nueva palabra 👇")
            ss.target = _siguiente()
            mb.publish(_payload("MISMATCH", label))
    _cerrar_ronda()


def aviso(tipo, texto):
    """Guarda un mensaje para que sobreviva al refresco automático."""
    st.session_state.msg = (tipo, texto)
    st.rerun()


def fiesta():
    """Globos de Streamlit + confeti (canvas-confetti)."""
    st.balloons()
    components.html("""
    <script>
    const P = window.parent;
    function lanzar() {
      const fin = Date.now() + 4000;
      (function frame() {
        P.confetti({particleCount: 7, angle: 60,  spread: 70, origin: {x: 0}});
        P.confetti({particleCount: 7, angle: 120, spread: 70, origin: {x: 1}});
        if (Date.now() < fin) requestAnimationFrame(frame);
      })();
    }
    if (P.confetti) { lanzar(); }
    else {
      const s = P.document.createElement('script');
      s.src = 'https://cdn.jsdelivr.net/npm/canvas-confetti@1.9.3/dist/confetti.browser.min.js';
      s.onload = lanzar;
      P.document.head.appendChild(s);
    }
    </script>""", height=0)


def estilo():
    st.markdown("""
    <style>
    .reto {
        font-size: 2.3rem; text-align: center; color: white;
        padding: .7rem 1rem; margin: .5rem 0 1rem 0; border-radius: 18px;
        background: linear-gradient(90deg, #7C5CFF, #22D3EE);
        box-shadow: 0 4px 18px rgba(124, 92, 255, .35);
    }
    .reto.win  { background: linear-gradient(90deg, #16A34A, #FACC15); }
    .reto.lose { background: linear-gradient(90deg, #DC2626, #7F1D1D); }
    .reto.espera { font-size: 1.6rem; }
    .stButton > button { border-radius: 12px; font-weight: 600; }
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="baseButton-primary"] {
        font-size: 1.6rem; padding: .7rem 1rem; color: white; border: none;
        background: linear-gradient(90deg, #7C5CFF, #22D3EE);
        box-shadow: 0 4px 18px rgba(124, 92, 255, .35);
    }
    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="baseButton-primary"]:hover {
        filter: brightness(1.15); color: white;
    }
    div[data-testid="stProgress"] { padding-top: .2rem; }
    </style>
    """, unsafe_allow_html=True)


def render_header():
    ss = st.session_state
    estilo()
    playing = ss.get("playing", False)

    if ss.finished == "WIN":
        st.markdown("<div class='reto win'>🎉 ¡GANASTE! 🔓</div>", unsafe_allow_html=True)
    elif ss.finished == "LOSE":
        st.markdown("<div class='reto lose'>💀 GAME OVER</div>", unsafe_allow_html=True)
    elif playing:
        st.markdown(f"<div class='reto'>Dibuja: <b>{NOMBRES[ss.target]}</b></div>",
                    unsafe_allow_html=True)
    else:
        espera = "⏱️ ¿Listo? Tienes {} segundos por palabra".format(TIEMPO)
        st.markdown(f"<div class='reto espera'>{espera}</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    c1.progress(ss.aciertos / MAX_ACIERTOS, text=f"🟢 Aciertos {ss.aciertos}/{MAX_ACIERTOS}")
    c2.progress(ss.fallos / MAX_FALLOS, text=f"🔴 Fallos {ss.fallos}/{MAX_FALLOS}")

    if playing and ss.get("deadline"):
        resta = max(0.0, ss.deadline - time.time())
        icono = "🔥" if resta <= 5 else "⏱️"
        st.progress(min(resta / TIEMPO, 1.0),
                    text=f"{icono} Tiempo: {math.ceil(resta)} s")

    if ss.msg:
        getattr(st, ss.msg[0])(ss.msg[1])
    if ss.balloons:
        fiesta()
        ss.balloons = False

    if ss.finished:
        if st.button("🔁  ¡VOLVER A JUGAR!", type="primary", use_container_width=True,
                     key="btn_again"):
            jugar_de_nuevo()
            st.rerun()
    elif not playing:
        if st.button("▶  ¡INICIAR!", type="primary", use_container_width=True,
                     key="btn_iniciar"):
            iniciar()
            st.rerun()

    with st.expander("🔧 Diagnóstico"):
        st.write("Último mensaje MQTT:", ss.get("last_publish", "ninguno"))
        st.write("Último intento:", ss.get("last_try", "ninguno"))
