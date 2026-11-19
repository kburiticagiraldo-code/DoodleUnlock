import streamlit as st
from core import game

st.set_page_config(page_title="DoodleUnlock", page_icon="🔐")
game.estilo()  # mismo estilo que las otras páginas

st.markdown("<div class='reto'>🔐 DoodleUnlock</div>", unsafe_allow_html=True)

st.write("Dibuja la palabra que te pide el juego y una IA dirá qué cree que es. "
         "La caja fuerte responde con luces, servo y pantalla.")

c1, c2, c3 = st.columns(3)
c1.metric("🟢 Para ganar", "3 aciertos")
c2.metric("🔴 Para perder", "3 fallos")
c3.metric("🎯 Seguridad mínima", "70 %")

st.subheader("Elige tu ambiente")
st.page_link("pages/1_Digital_Canvas.py", label="Ambiente digital: dibuja en el lienzo", icon="🎨")
st.page_link("pages/2_Physical_Upload.py", label="Ambiente físico: sube la foto de tu dibujo", icon="📷")
st.page_link("pages/3_Camera_Photo.py", label="Cámara: toma la foto en el momento", icon="📸")

with st.expander("📖 Cómo se juega"):
    st.markdown("""
1. La app te muestra una palabra. **Solo aparece aquí, no en la caja.**
2. Dibújala en el lienzo o en papel (con foto).
3. La IA adivina. Si acierta con **70 % o más**, cuenta como acierto.
4. Después de cada intento, sea acierto o fallo, **cambia la palabra**.
5. **3 aciertos** abren la cerradura 🔓. **3 fallos** son Game Over 💀.
6. Para jugar otra vez, pulsa **Nueva partida** o el botón físico del ESP32.
""")

with st.expander("🔌 La caja fuerte"):
    st.markdown("""
- 🟢 Los LEDs verdes marcan tus aciertos y los 🔴 rojos tus fallos.
- El servo gira poco a poco hasta abrirse con el tercer acierto.
- La pantalla OLED dice qué creyó ver la IA.
- Al ganar, los LEDs hacen una animación de premio.
""")
