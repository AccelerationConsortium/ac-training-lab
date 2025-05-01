# LISIPAROI Camera Light

[Homepage](https://www.lisiparoi.co.uk/index.htm) and [how-to guide](https://www.lisiparoi.co.uk/how-to-use.htm)

In our case, bought from [Newark](https://canada.newark.com/cyntech/lisiparoiwht-01/lisiparoi-white-led-camera-light/dp/31AC3472)

We're choosing to use GPIO18 (pin 12) on a Pi Zero 2W for on/off control and PWM. Not every GPIO pin on the Pi Zero 2W supports PWM. Connecting to 3.3V (pin 1) will be always on.
Context: https://github.com/AccelerationConsortium/ac-training-lab/issues/158
