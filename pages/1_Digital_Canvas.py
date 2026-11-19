import streamlit as st
from streamlit_drawable_canvas import st_canvas
from core import game, vision

st.set_page_config(page_title="Ambiente digital", page_icon="🎨")
game.init()
game.poll("poll1")

st.header("🎨 Ambiente digital")
if vision.FAKE_MODE:
    st.caption("⚠️ Modo de prueba: sin modelo de IA, el resultado es aleatorio.")

game.render_header()

if st.session_state.playing:
    canvas = st_canvas(stroke_width=14, stroke_color="#FFFFFF",
                       background_color="#000000", height=280, width=280,
                       drawing_mode="freedraw",
                       key=f"canvas_{st.session_state.canvas_key}")

    if st.button("Adivinar") and canvas.image_data is not None:
        t = vision.from_canvas(canvas.image_data)
        if t is None:
            st.warning("Dibuja algo primero")
        else:
            game.evaluate(*vision.predict(t, st.session_state.target))
            st.rerun()
