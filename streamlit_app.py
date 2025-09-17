import streamlit as st
import imageio
import fish

st.set_page_config(page_title="iFish - Fish-Eye Filter", layout="centered")

st.title("iFish - Fish-Eye Filter")
st.write("Upload an image to apply Fish Eye filter to your image.")

uploaded_file = st.file_uploader("Choose an image...", type=["png", "jpg", "jpeg"], )


if uploaded_file is not None:
    img = imageio.imread(uploaded_file)

    img = fish.resize_image(img)


    distortion = st.slider(
        "The distortion coefficient. How much the move pixels from/to the center.",
        min_value=-1.0,
        max_value=1.0,
        value=0.5, # default
        step=0.1
    )

    txt_slot = st.empty()
    img_slot = st.empty()
    txt_slot.write(f"Processing image with distortion {distortion}...")
    img_slot.image(img, caption="Uploaded Image", use_container_width=True)

    processed_img = fish.fish(img, distortion_coefficient=distortion)
    txt_slot.write("Result...")
    img_slot.image(processed_img, caption="Fish Eyed Image")
