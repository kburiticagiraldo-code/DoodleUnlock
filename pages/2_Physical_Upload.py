import streamlit as st, numpy as np, cv2
from streamlit_autorefresh import st_autorefresh
from core import game, vision

st.set_page_config(page_title="Ambiente físico", page_icon="📷")
game.init()
st_autorefresh(interval=2000, key="poll2")
game.handle_hardware_events()

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
                st.warning("No veo trazos")
            else:
                game.evaluate(*vision.predict(t, st.session_state.target))
                st.rerun()
