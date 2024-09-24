import streamlit as st


def sidebar():
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio(
        "Go to",
        [
            "About",
            "Request Key",
            "Livestream",
            "Download",
            "GUI Control",
            "Python Documentation",
        ],
    )
    return selection


if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"


def main():
    selection = sidebar()

    if st.session_state.current_page != selection:
        st.session_state.current_page = selection

        st.session_state.button_clicked = False

    if selection == "About":
        st.title("AC Microscope")
        st.write(
            "This is a request site for credentials to use remote access to Openflexure Microscopes in the AC lab. You can either control the microscopes over python or the GUI with the help of a temporary key. You can view the live camera feed on a livestream. One person can use a microscope at once. Currently only Microscope2 is functional, but they will all be functional in the future"  # noqa: E501
        )

    elif selection == "Request Key":
        import key_request

        key_request.show()
    elif selection == "Livestream":
        import livestream

        livestream.show()
    elif selection == "Download":
        import download

        download.show()
    elif selection == "GUI Control":
        import gui_control

        gui_control.show()
    elif selection == "Python Documentation":
        import documentation

        documentation.show()


if __name__ == "__main__":
    main()
