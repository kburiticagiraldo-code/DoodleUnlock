import streamlit as st, numpy as np, cv2
from core import game, vision

st.set_page_config(page_title="Cámara", page_icon="📸")
game.init()
game.poll("poll3")

st.header("📸 Foto con la cámara")
if vision.FAKE_MODE:
    st.caption("⚠️ Modo de prueba: sin modelo de IA, el resultado es aleatorio.")

game.render_header()

if st.session_state.playing:
    foto = st.camera_input("Toma una foto de tu dibujo en papel",
                           key=f"cam_{st.session_state.canvas_key}")
    if foto is not None:
        img = cv2.imdecode(np.frombuffer(foto.getvalue(), np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            st.error("No pude leer la foto. Intenta tomarla otra vez.")
        else:
            t = vision.from_photo(img)
            if t is None:
                st.warning("No veo trazos. Acerca la hoja, usa marcador oscuro "
                           "grueso y buena luz.")
            else:
                vista = cv2.resize((t[0, :, :, 0] * 255).astype(np.uint8), (140, 140),
                                   interpolation=cv2.INTER_NEAREST)
                st.image(vista, width=140, caption="Lo que ve la IA (28x28)")
                if st.button("Adivinar"):
                    game.evaluate(*vision.predict(t, st.session_state.target))
                    st.rerun()
