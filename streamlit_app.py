import streamlit as st
import imageio
import fish
import io
import os

st.set_page_config(page_title="iFish - Fish-Eye Filter", layout="centered")

st.title("iFish - Fish-Eye Filter")
doc_container = st.container(border=True)

doc_container.write("A naive implementation of Fish-Eye filter.")
doc_container.write("Slide the slider to change the effect strength. Positive values for Fish-eye effect, negative for reverse effect (Rectilinear).")
doc_container.write("Project Github page: https://github.com/Gil-Mor/iFish")

uploaded_file = st.file_uploader("", type=["png", "jpg", "jpeg"], max_upload_size=5)

if st.button("Use Mona Lisa (Default Example)", icon="🖼️"):
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
        st.stop()

    try:
        img = fish.resize_image(img)
    except Exception as e:
        status_slot.status(f"Error resizing image. {e}", expanded=True, state='error')
        st.stop()

    mode_radio_container = st.container(border=True)
    mode = mode_radio_container.radio("Distortion range mode",
        options=["Normal Mode 😌", "Wacky Mode 🤯"], horizontal=True)

    if mode == "Wacky Mode 🤯":
        distortion_range = (-15.0, 100.0)
        distortion_step = 0.5
        distortion_slider_help = "Positive values make sense even up to 100. Negative values hardly make sense below -15."
    else:
        distortion_range = (-1.0, 1.0)
        distortion_step = 0.1
        distortion_slider_help = "Positive values create a Fish Eye effect. Negative values create a Rectilinear effect."

    distortion_slider_container = st.container(border=True)
    distortion = distortion_slider_container.slider(
        label="Effect strength - Distortion amount. How much to move pixels from/to the center.",
        help=distortion_slider_help,
        min_value=distortion_range[0],
        max_value=distortion_range[1],
        value=0.0,
        step=distortion_step
    )

    img_slot = st.empty()
    img_slot.image(img, caption="Uploaded Image", use_container_width=True)

    if distortion == 0:
        status_slot.status("Set Distortion different from 0. Waiting...", state="running")
        st.stop()

    # Use a context manager so the status remains "running" until the block finishes
    with status_slot.status(f"Processing image with distortion {distortion}...", state='running') as status:
        try:
            # 1. Apply the effect
            processed_img = fish.fish(img, distortion=distortion)

            # 2. Encode the image to bytes inside the 'running' status.
            buf = io.BytesIO()
            imageio.imwrite(buf, processed_img, format='png')
            img_bytes = buf.getvalue()

            # 3. Render the pre-encoded image (much faster than passing the raw NumPy array)
            img_slot.image(img_bytes, caption="Fish Eyed Image")

            # 4. Safely transition to complete
            status.update(label=f"Processed image with distortion {distortion}.", state='complete')

        except Exception as e:
            status.update(label=f"Error applying effect. {e}", expanded=True, state='error')
            st.stop()

    # Prepare the download button
    base_name = os.path.splitext(img_name)[0]
    default_out_name = f"{base_name}_fish.png"

    # Pass the already-encoded bytes directly to the download button
    st.download_button(
        label="Save Image",
        data=img_bytes,
        file_name=default_out_name,
        mime="image/png"
    )
