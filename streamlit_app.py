import streamlit as st
import imageio
import fish

st.set_page_config(page_title="iFish - Fish-Eye Filter", layout="centered")

st.title("iFish - Fish-Eye Filter")
st.write("Upload an image.")

uploaded_file = st.file_uploader("Choose an image...", type=["png", "jpg", "jpeg"], )


if uploaded_file is not None:
    status_slot = st.empty()
    try:
        img = imageio.imread(uploaded_file)
    except Exception as e:
        status_slot.status(f"Error reading image. {e}", expanded=True, state='error')
        raise e
    try:
        img = fish.resize_image(img)
    except Exception as e:
        status_slot.status(f"Error resizing image. {e}", expanded=True, state='error')
        raise e


    distortion = st.slider(
        label="The distortion coefficient. How much to move pixels from/to the center.",
        help="Positive values create a Fish Eye effect.\n"
        "Negative values create a Rectilinear effect.",
        min_value=-1.0,
        max_value=1.0,
        value=0.5, # default
        step=0.1
    )

    img_slot = st.empty()
    status_slot.status(f"Processing image with distortion {distortion}...", expanded=True, state='running')

    img_slot.image(img, caption="Uploaded Image", use_container_width=True)
    try:
        processed_img = fish.fish(img, distortion_coefficient=distortion)
    except Exception as e:
        status_slot.status(f"Error applying effect. {e}", expanded=True, state='error')
        raise e
    
    status_slot.status("Result", expanded=True, state='complete')
    img_slot.image(processed_img, caption="Fish Eyed Image")
