import cv2
import numpy as np
import streamlit as st
from core import game, vision

st.set_page_config(page_title="Cámara", page_icon="📷")
st.title("📷 Foto con la cámara")

game.init()
game.poll("camera")
game.render_header()

ss = st.session_state
if not ss.finished:
    foto = st.camera_input("Toma una foto de tu dibujo en papel",
                           key=f"cam_{ss.canvas_key}")
    if foto is not None and st.button("Adivinar", key="adivinar_cam"):
        data = np.frombuffer(foto.getvalue(), np.uint8)
        bgr = cv2.imdecode(data, cv2.IMREAD_COLOR)
        tensor = vision.from_photo(bgr)
        if tensor is None:
            game.aviso("warning", "No vi ningún dibujo. Acerca la hoja y usa trazo grueso.")
        else:
            label, prob = vision.predict(tensor, ss.target)
            game.evaluate(label, prob)
            st.rerun()
