def show():
    import streamlit as st

    st.title("Livestream")
    # livestreammicroscope1 = ""
    livestreammicroscope2 = "https://www.youtube.com/live/xbWFNAgEIDQ"
    # livestreamdeltastagetransmission = ""
    # livestreamdeltastagereflection = ""
    st.write("Here are the live microscope camera views of all the microscopes")

    st.write("Microscope 2:")
    st.link_button("Microscope 2 Livestream", livestreammicroscope2)
