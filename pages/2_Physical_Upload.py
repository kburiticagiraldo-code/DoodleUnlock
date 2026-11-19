import streamlit as st, numpy as np, cv2
from core import game, vision

st.set_page_config(page_title="Ambiente físico", page_icon="📷")
game.init()
game.poll("poll2")

st.header("📷 Ambiente físico")
if vision.FAKE_MODE:
    st.caption("⚠️ Modo de prueba: sin modelo de IA, el resultado es aleatorio.")

game.render_header()

if not st.session_state.finished:
    f = st.file_uploader("Sube la foto de tu dibujo", type=["png", "jpg", "jpeg"])
    if f:
        img = cv2.imdecode(np.frombuffer(f.read(), np.uint8), cv2.IMREAD_COLOR)
        st.image(img, channels="BGR", width=300)
        if st.button("Adivinar"):
            t = vision.from_photo(img)
            if t is None:
                game.aviso("warning", "No veo trazos en la foto.")
            else:
                game.evaluate(*vision.predict(t, st.session_state.target))
                st.rerun()
