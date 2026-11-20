import streamlit as st, numpy as np, cv2
from core import game, vision

st.set_page_config(page_title="Ambiente físico", page_icon="📷")
game.init()
game.poll("poll2")

st.header("📷 Ambiente físico")
if vision.FAKE_MODE:
    st.caption("⚠️ Modo de prueba: sin modelo de IA, el resultado es aleatorio.")

game.render_header()

if st.session_state.playing:
    f = st.file_uploader("Sube la foto de tu dibujo", type=["png", "jpg", "jpeg"],
                         key=f"up_{st.session_state.canvas_key}")
    if f:
        datos = f.getvalue()
        img = cv2.imdecode(np.frombuffer(datos, np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            st.error("No pude leer esa imagen. Prueba con otro archivo (png o jpg).")
        else:
            st.image(img, channels="BGR", width=300)
            t = vision.from_photo(img)
            if t is None:
                st.warning("No veo trazos en la foto. Usa hoja blanca, marcador "
                           "oscuro y grueso, y buena luz.")
            else:
                vista = cv2.resize((t[0, :, :, 0] * 255).astype(np.uint8), (140, 140),
                                   interpolation=cv2.INTER_NEAREST)
                st.image(vista, width=140, caption="Lo que ve la IA (28x28)")
                if st.button("Adivinar"):
                    game.evaluate(*vision.predict(t, st.session_state.target))
                    st.rerun()
