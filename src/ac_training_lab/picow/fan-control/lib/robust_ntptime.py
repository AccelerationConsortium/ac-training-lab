from time import sleep

import ntptime


def set_ntptime(host="time.google.com", retry_host="pool.ntp.org", timeout=15):
    # A valid time is required to validate certificates
    ntptime.timeout = timeout
    ntptime.host = host
    try:
        ntptime.settime()
    except Exception as e:
        print(f"{e} with {ntptime.host}. Trying again after 10 seconds")
        sleep(10)
        try:
            ntptime.settime()
        except Exception as e:
            print(f"{e} with {ntptime.host}. Trying again with {retry_host}")
            sleep(10)
            ntptime.host = retry_host
            ntptime.settime()
