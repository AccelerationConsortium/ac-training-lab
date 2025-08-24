def show():
    import random
    import time

    # import pymongo.mongo_client
    import requests
    import streamlit as st
    from my_secrets import HIVEMQ_API_TOKEN, HIVEMQ_BASE_URL, HIVEMQ_BROKER, MONGODB_URI
    from pymongo.mongo_client import MongoClient

    # SET UP ON DATABASE you need to make a variable for the time called the
    # same as the microscope prior to the running of the program running the
    # function update_variable_test() will work
    microscope = "microscope2"
    access_time = 900
    database_name = "openflexure-microscope"
    collection_name = "Cluster0"
    microscopes = [
        "microscope",
        "microscope2",
        "deltastagetransmission",
        "deltastagereflection",
    ]
    brokerport = "8883"

    client = MongoClient(MONGODB_URI)
    db = client[database_name]
    collection = db[collection_name]

    try:
        client.admin.command("ping")
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        st.write(e)

    def check_variable(variable_name):
        try:
            document = collection.find_one({"variable_name": variable_name})
            if document:
                return document.get("value", "Variable not found.")
            else:
                return "Variable not found in the collection."
        except Exception as e:
            return f"An error occurred: {e}"

    def create_user(username, password):
        api_url = HIVEMQ_BASE_URL + "/mqtt/credentials"
        headers = {
            "Authorization": f"Bearer {HIVEMQ_API_TOKEN}",
            "Content-Type": "application/json",
        }

        new_user = {"credentials": {"username": username, "password": password}}

        requests.post(api_url, json=new_user, headers=headers)

    def delete_user(username):
        headers = {
            "Authorization": f"Bearer {HIVEMQ_API_TOKEN}",
            "Content-Type": "application/json",
        }

        api_url = HIVEMQ_BASE_URL + "/mqtt/credentials/username/" + username
        requests.delete(api_url, headers=headers)

    def role_user(username, role):
        headers = {
            "Authorization": f"Bearer {HIVEMQ_API_TOKEN}",
            "Content-Type": "application/json",
        }
        api_url = HIVEMQ_BASE_URL + "/user/" + username + "/roles/" + role + "/attach"
        requests.put(api_url, headers=headers)

    def update_variable(variable_name, new_value):
        try:
            result = collection.update_one(
                {"variable_name": variable_name},
                {"$set": {"value": new_value}},
                upsert=True,
            )
            if result.matched_count > 0:
                return "Variable updated successfully."
            else:
                return "Variable created and updated successfully."
        except Exception as e:
            return f"An error occurred: {e}"

    def update_variable_test():
        update_variable(microscope, random.randint(1, 10))

    def check_variable_test():
        st.write(check_variable(microscope))

    def get_current_time():
        #    api_url = "http://worldtimeapi.org/api/timezone/Etc/UTC"
        #    try:
        #        response = requests.get(api_url)
        #        response.raise_for_status()
        #        data = response.json()
        #        return data['unixtime']
        #    except requests.RequestException as e:
        #        return f"Error: {e}"
        unix_time = int(time.time())
        return unix_time

    def button():
        st.session_state.button_clicked = True

    if "button_clicked" not in st.session_state:
        st.session_state.button_clicked = False
    if "previous_selected_value" not in st.session_state:
        st.session_state.previous_selected_value = microscopes[1]

    st.write("Keys will last 30 minutes before being overridable")
    st.write("Broker IP:")
    st.code(HIVEMQ_BROKER)
    st.write("Broker port:")
    st.code(brokerport)
    st.write("Usernames:")
    st.code(
        """
    microscope -> microscopeclientuser
    microscope2 -> microscope2clientuser
    deltastagereflection -> deltastagereflectionclientuser
    deltastagetransmission -> deltastagetransmissionclientuser
    """
    )

    microscope = st.selectbox(
        "Choose a microscope:", microscopes, index=microscopes.index("microscope2")
    )
    if microscope != st.session_state.get("previous_selected_value", microscope):
        st.session_state.button_clicked = False

        st.session_state["previous_selected_value"] = microscope

    st.button(
        "Request temporary access",
        help="If somebody is using the microscope, you will need to wait",
        on_click=button,
    )

    if st.session_state.button_clicked:
        display_text = st.empty()
        ctime = get_current_time()
        var = check_variable(microscope)
        if ctime >= var + access_time:
            access_key = "Microscope" + str(random.randint(10000000, 99999999))
            delete_user(microscope + "clientuser")
            create_user(microscope + "clientuser", access_key)
            if microscope == "microscope2":
                role_user(microscope + "clientuser", "3")
            elif microscope == "microscope":
                role_user(microscope + "clientuser", "4")
            elif microscope == "deltastagereflection":
                role_user(microscope + "clientuser", "5")
            elif microscope == "deltastagetransmission":
                role_user(microscope + "clientuser", "6")

            display_text.success(
                "Access key: " + access_key
            )  # change placeholder to access_key
            update_variable(microscope, ctime)

        else:
            while True:
                if access_time - ctime + var <= 0:
                    display_text.success("Access key ready!")
                    break
                if (access_time - ctime + var) % 60 < 10:
                    seconds = "0" + str((access_time - ctime + var) % 60)
                else:
                    seconds = str((access_time - ctime + var) % 60)
                display_text.error(
                    "Please wait "
                    + str(
                        int(
                            (
                                access_time
                                - ctime
                                + var
                                - (access_time - ctime + var) % 60
                            )
                            / 60
                        )
                    )
                    + ":"
                    + seconds
                )

                ctime = ctime + 1
                if ctime % 15 == 0:
                    ctime = get_current_time() + 1
                time.sleep(1)
            while True:
                time.sleep(5)
                cutime = get_current_time()
                var = check_variable(microscope)
                if cutime <= var + access_time:
                    display_text.error("The access key was taken!")
                    break
                time.sleep(10)
