def show():
    import streamlit as st

    st.title("Download")
    st.write("You can install this program with")
    st.code(
        "pip install git+https://github.com... #PLACEHOLDER THIS METHOD OF INSTALLATION IS NOT READY YOU NEED TO DOWNLOAD IT MANUALLY FROM THE GITHUB AND ALSO PIP INSTALL ALL OF THE IMPORTS"  # noqa: E501
    )
    st.write("")
    st.write("or use the AC github")
    st.link_button(
        "AC github",
        "https://github.com/AccelerationConsortium/ac-training-lab/tree/main/src%2Fac_training_lab%2Fopenflexure",  # noqa: E501
    )
    st.write("")
    st.write(
        "You also need to install the Openflexure Stitching library if you want to stitch anything"  # noqa: E501
    )
    st.link_button(
        "Openflexure Stitching", "https://gitlab.com/openflexure/openflexure-stitching"
    )
