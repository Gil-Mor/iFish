import streamlit as st
import imageio
import fish
import io
import os

st.set_page_config(page_title="iFish - Fish-Eye Filter", layout="centered")

st.title("iFish - Fish-Eye Filter")
st.write("A naive implementation of Fish-Eye filter.")
st.write("Slide the slider to change the effect strength. Positive values for Fish-eye effect, negative for reverse effect (Rectilinear).")
st.write("Project Github page: https://github.com/Gil-Mor/iFish")
st.write("Upload an image or use the default example (Mona Lisa).")

uploaded_file = st.file_uploader("Upload an image...", type=["png", "jpg", "jpeg"], max_upload_size=5)

if st.button("Use Mona Lisa (Default Example)"):
    st.session_state.img_source = "Mona_Lisa.jpg"
    st.session_state.img_name = "Mona_Lisa.jpg"
    uploaded_file = None

# Determine the active image: file_uploader takes precedence, then session_state
img_source = uploaded_file if uploaded_file else st.session_state.get('img_source')
img_name = uploaded_file.name if uploaded_file else st.session_state.get('img_name')

if img_source is not None:
    status_slot = st.empty()
    try:
        img = imageio.imread(img_source)
    except Exception as e:
        status_slot.status(f"Error reading image. {e}", expanded=True, state='error')
        raise e
    try:
        img = fish.resize_image(img)
    except Exception as e:
        status_slot.status(f"Error resizing image. {e}", expanded=True, state='error')
        raise e


    distortion = st.slider(
        label="Effect strength - Distortion amount. How much to move pixels from/to the center.",
        help="Positive values create a Fish Eye effect.\n"
        "Negative values create a Rectilinear effect.",
        min_value=-1.0,
        max_value=1.0,
        value=0.0, # default
        step=0.1
    )

    img_slot = st.empty()
    status_slot.status(f"Processing image with distortion {distortion}...", expanded=True, state='running')

    img_slot.image(img, caption="Uploaded Image", use_container_width=True)
    if distortion == 0:
        status_slot.status("Set Distortion different from 0.", expanded=True)
        status_slot.status("Set Distortion different from 0.", expanded=False, state='complete')
        st.stop()

    try:
        processed_img = fish.fish(img, distortion=distortion)
    except Exception as e:
        status_slot.status(f"Error applying effect. {e}", expanded=True, state='error')
        raise e

    img_slot.image(processed_img, caption="Fish Eyed Image")
    status_slot.status("Result", expanded=False, state='complete')
    # Prepare the download button
    base_name = os.path.splitext(img_name)[0]
    default_out_name = f"{base_name}_fish.png"

    # Convert the processed numpy array to bytes for download
    buf = io.BytesIO()
    imageio.imwrite(buf, processed_img, format='png')
    st.download_button(
        label="Save Image",
        data=buf.getvalue(),
        file_name=default_out_name,
        mime="image/png"
    )
