
```python
import os
import streamlit as st
import base64
from openai import OpenAI
import openai
from PIL import Image
import numpy as np
from streamlit_drawable_canvas import st_canvas

Expert = " "
profile_imgenh = " "

# Inicializar session_state
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'full_response' not in st.session_state:
    st.session_state.full_response = ""
if 'base64_image' not in st.session_state:
    st.session_state.base64_image = ""

def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return "Error: La imagen no se encontró en la ruta especificada."

# Configuración de la página
st.set_page_config(page_title='Tablero Inteligente')
st.title('🖌️ Tablero Inteligente: Historias y Chistes con tus Dibujos')

with st.sidebar:
    st.subheader("Acerca de:")
    st.write("En esta aplicación puedes **dibujar un boceto** y la IA lo analizará para luego crear una historia infantil o un chiste relacionado con lo que dibujaste.")

st.subheader("✏️ Dibuja el boceto en el panel y presiona el botón para analizarlo")

# Opciones del canvas
drawing_mode = "freedraw"
stroke_width = st.sidebar.slider('Selecciona el ancho de línea', 1, 30, 5)
stroke_color = "#000000"
bg_color = '#FFFFFF'

# Canvas para dibujar
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=300,
    width=400,
    drawing_mode=drawing_mode,
    key="canvas",
)

# Ingreso de API Key
ke = st.text_input('🔑 Ingresa tu API Key de OpenAI', type="password")
os.environ['OPENAI_API_KEY'] = ke
api_key = os.environ['OPENAI_API_KEY']

# Inicializar cliente de OpenAI
client = OpenAI(api_key=api_key)

# Botón de análisis
analyze_button = st.button("🔍 Analizar dibujo", type="secondary")

if canvas_result.image_data is not None and api_key and analyze_button:
    with st.spinner("Analizando ..."):
        # Guardar imagen dibujada
        input_numpy_array = np.array(canvas_result.image_data)
        input_image = Image.fromarray(input_numpy_array.astype('uint8')).convert('RGBA')
        input_image.save('img.png')

        # Codificar en base64
        base64_image = encode_image_to_base64("img.png")
        st.session_state.base64_image = base64_image

        prompt_text = "Describe en español brevemente la imagen."

        try:
            full_response = ""
            message_placeholder = st.empty()
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_text},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}},
                        ],
                    }
                ],
                max_tokens=300,
            )

            if response.choices[0].message.content is not None:
                full_response += response.choices[0].message.content
                message_placeholder.markdown(full_response + "▌")

            # Actualización final
            message_placeholder.markdown(full_response)

            # Guardar estado
            st.session_state.full_response = full_response
            st.session_state.analysis_done = True

            if Expert == profile_imgenh:
                st.session_state.mi_respuesta = response.choices[0].message.content

        except Exception as e:
            st.error(f"Ocurrió un error: {e}")

# Opciones después del análisis
if st.session_state.analysis_done:
    st.divider()
    st.subheader("✨ Opciones creativas")

    # Historia infantil
    if st.button("📚 Crear historia infantil"):
        with st.spinner("Creando historia..."):
            story_prompt = f"Basándote en esta descripción: '{st.session_state.full_response}', crea una historia infantil breve y entretenida. La historia debe ser creativa y apropiada para niños."
            
            story_response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": story_prompt}],
                max_tokens=500,
            )
            
            st.markdown("**📖 Tu historia:**")
            st.write(story_response.choices[0].message.content)

    # Generador de chistes
    st.subheader("😂 Generador de chistes")
    estilo = st.selectbox(
        "Elige un estilo de chiste",
        ["Chiste clásico", "Chiste de niños", "Chiste tipo papá", "Chiste sarcástico", "Chiste absurdo"]
    )

    if st.button("🎭 Crear chiste"):
        with st.spinner("Pensando un chiste..."):
            joke_prompt = f"A partir de esta descripción: '{st.session_state.full_response}', crea un {estilo.lower()} en español, corto y divertido, relacionado con el dibujo."

            joke_response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": joke_prompt}],
                max_tokens=150,
            )

            st.markdown("**🤣 Tu chiste:**")
            st.write(joke_response.choices[0].message.content)

# Advertencia si falta API key
if not api_key:
    st.warning("⚠️ Por favor ingresa tu API Key para continuar.")

