# iFish

### Apply Fish Eye effect to your photos

A naive implementation that moves pixels from/to the center based on a 'distortion' value.

#### Before
<img src="Mona_Lisa.jpg" alt="Mona Lisa" width="300px"/>

#### After
<img src="Mona_Lisa_fish.png" alt="Mona Lisa after Fish-eye effect" width="300px"/>

OR

#### Before
<img src="grid.jpg" alt="grid pattern" width="300px"/>

#### After
<img src="grid_fish.png" alt="grid pattern after fish-eye effect" width="300px"/>

You can control the amount of distortion.
You can also apply "reverse-fish" (rectilinear lens) by specifying negative distortion.

### Usage:

#### Cmdline:
`python fish.py -h`

#### Local Web Interface with [streamlit](https://streamlit.io/)
`streamlit run streamlit_app.py`


### Dependencies
```bash
pip install -r requirements.txt
```
