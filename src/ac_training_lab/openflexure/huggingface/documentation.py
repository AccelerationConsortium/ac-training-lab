def show():
    import streamlit as st

    st.title("AC Microscope Client Documentation")

    st.subheader("Move")
    st.write("Required parameters:")
    st.code("move(x,y)")
    st.write("Optional parameters:")
    st.code("move(x,y,z,relative)")
    st.write("Default values:")
    st.code("z=False, relative=False")
    st.write(
        "The move() function moves to given coordinates x, y (and z if it is set to any integer value, if it is set to False which is the default setting, the z value wont change). If relative is True, then it will move relative to the current position instead of moving to the absolute coordinates. Coordinates arent based on screen percentage. The size of the screen is around 3600x2700."  # noqa: E501
    )
    st.write("")
    st.subheader("Take image")
    st.code("take_image()")
    st.write(
        "The take_image() function takes an image on the microscope camera and returns an image object"  # noqa: E501
    )
    st.write("")
    st.subheader("Get position")
    st.code("get_pos()")
    st.write(
        "The get_pos() returns a dictionary with x, y, and z coordinates eg. {'x':1,'y':2,'z':3}"  # noqa: E501
    )
    st.write("")
    st.subheader("Focus")
    st.write("Required parameters:")
    st.code("focus()")
    st.write("Optional parameters:")
    st.code("focus(amount)")
    st.write("Default value:")
    st.code('amount="fast"')
    st.write(
        'The focus() function auto focuses by different amounts: "huge", "fast", "medium", "fine", or any integer value'  # noqa: E501
    )
    st.write("")
    st.subheader("End connection")
    st.code("end_connection()")
    st.write(
        "The end_connection() function ends the connection to the microscope at the end of your script. This is not required, but is reccomended to place at the end of your script."  # noqa: E501
    )
    st.write("")
    st.subheader("Scan")
    st.write("Required parameters:")
    st.code("scan(c1,c2)")
    st.write("Optional parameters:")
    st.code("scan(c1,c2,ov,foc)")
    st.write("Default values:")
    st.code("ov=1200,foc=0")
    st.write(
        'The scan() function returns a list of image objects. Takes images to scan an entire area specified by two corners. you can input the corner coordinates as "x1 y1", "x2 y2" or [x1, y1], [x2, y2]. ov refers to the overlap between the images and foc refers to how much the microscope should focus between images (0 to disable)'  # noqa: E501
    )
    st.subheader("Scan and stitch")
    st.write("Required parameters:")
    st.code("scan_and_stitch(c1,c2,temp)")
    st.write("Optional parameters:")
    st.code("scan_and_stitch(c1,c2,temp,ov,foc,output)")
    st.write("Default values:")
    st.code('ov = 1200,foc = 0,output="Downloads/stitched.jpeg"')
    st.write(
        "The scan_and_stitch() function takes a scan with the same inputs + 2 more and outputs a stitched image. Output is the directory the stitched image will go to and temp is the temporary directory to stitch the image (make sure this is an empty directory (it will also be created automatically if it doesn't exist) the program will clear this directory) otherwise it works just like scan(). You need Openflexure Stitching installed and you need to define path_to_openflexure_stitching when instantiating your class for this to work"  # noqa: E501
    )
    st.write("")
    st.subheader("Instantiating the class")
    st.code(
        'Microscope = MicroscopeDemo(host, port, key, microscope, path_to_openflexure_stitching) #path_to_openflexure_stitching is optional, an example for the microscope field would be "microscope2"'  # noqa: E501
    )
    st.write("")
    st.subheader("Example code")
    st.code(
        """
    print(microscope.get_pos())
    microscope.take_image().show()
    microscope.scan([2000, 2000], "-2000 -2000")
    for i in microscope.scan("2000 2000", "-2000 -2000", ov=1500, foc=1000):
        i.show()
    microscope.scan_and_stitch([2000, 2000], [-2000, -2000], temp="c:/Users/-/Downloads/scanimages", output="c:/Users/-/Downloads/scanstitch.jpg") # noqa: E501
    microscope.move(0,0)
    microscope.focus(700)
    microscope.move(0,1000,relative=True)
    microscope.focus("fast")
    microscope.move(1000,0,z=3000)
    microscope.focus()
    microscope.end_connection()
    """
    )
