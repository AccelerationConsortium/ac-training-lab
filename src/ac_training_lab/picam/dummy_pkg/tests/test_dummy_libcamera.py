from libcamera import Transform


def test_libcamera():
    Transform(vflip=1)


if __name__ == "__main__":
    test_libcamera()
    print("All tests passed.")
