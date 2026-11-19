import streamlit as st, numpy as np, cv2
from core import game, vision

st.set_page_config(page_title="Cámara", page_icon="📸")
game.init()
game.poll("poll3")

st.header("📸 Foto con la cámara")
if vision.FAKE_MODE:
    st.caption("⚠️ Modo de prueba: sin modelo de IA, el resultado es aleatorio.")

game.render_header()

if not st.session_state.finished:
    foto = st.camera_input("Toma una foto de tu dibujo en papel",
                           key=f"cam_{st.session_state.canvas_key}")
    if foto is not None:
        img = cv2.imdecode(np.frombuffer(foto.getvalue(), np.uint8), cv2.IMREAD_COLOR)
        if st.button("Adivinar"):
            t = vision.from_photo(img)
            if t is None:
                game.aviso("warning", "No veo trazos. Acerca la hoja y usa un marcador grueso.")
            else:
                game.evaluate(*vision.predict(t, st.session_state.target))
                st.rerun()
