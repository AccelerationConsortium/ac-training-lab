def show():
    # note to self you can check for empty with if statement st.image(image,
    # caption='PIL Image', use_column_width=True)
    import streamlit as st
    from microscope_demo_client import MicroscopeDemo

    host = "marooncarder-nvscfy.a02.usw2.aws.hivemq.cloud"
    port = 8883
    microscopes = [
        "microscope",
        "microscope2",
        "deltastagetransmission",
        "deltastagereflection",
    ]

    def get_pos_button():
        microscope = MicroscopeDemo(
            host,
            port,
            microscopeselection + "clientuser",
            access_key,
            microscopeselection,
        )
        # "acmicroscopedemo" is a placeholder until access keys are implemented
        pos = microscope.get_pos()
        st.write("x: " + str(pos["x"]))
        st.write("y: " + str(pos["y"]))
        st.write("z: " + str(pos["z"]))
        microscope.end_connection()

    def take_image_button():
        microscope = MicroscopeDemo(
            host,
            port,
            microscopeselection + "clientuser",
            access_key,
            microscopeselection,
        )
        # "acmicroscopedemo" is a placeholder until access keys are implemented
        st.image(
            microscope.take_image(),
            caption="Taken from the microscope camera",
            use_column_width=True,
        )
        microscope.end_connection()

    def focus_button():
        microscope = MicroscopeDemo(
            host,
            port,
            microscopeselection + "clientuser",
            access_key,
            microscopeselection,
        )
        # "acmicroscopedemo" is a placeholder until access keys are implemented
        microscope.focus(focusamount)
        st.write("Autofocus complete")
        microscope.end_connection()

    def move_button():
        microscope = MicroscopeDemo(
            host,
            port,
            microscopeselection + "clientuser",
            access_key,
            microscopeselection,
        )
        # "acmicroscopedemo" is a placeholder until access keys are implemented
        microscope.move(xmove, ymove)
        st.write("Move complete")
        microscope.end_connection()

    st.title("GUI control")

    microscopeselection = st.selectbox(
        "Choose a microscope:", microscopes, index=microscopes.index("microscope2")
    )

    access_key = st.text_input(label="Enter your access key here:", max_chars=1000)

    st.button("Get position", on_click=get_pos_button)
    st.write("")
    st.button("Take image", on_click=take_image_button)
    st.write("")
    focusamount = st.number_input(
        "Autofocus amount 1-5000", min_value=1, max_value=5000, step=100, value=1000
    )
    st.button("Focus", on_click=focus_button)
    st.write("")
    xmove = st.number_input("X", min_value=-20000, max_value=20000, step=250, value=0)
    ymove = st.number_input("Y", min_value=-20000, max_value=20000, step=250, value=0)
    st.button("Move", on_click=move_button)
