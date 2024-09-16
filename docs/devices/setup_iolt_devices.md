# Setting Up IoLT Demos (WIP)

<!-- This document provides comprehensive instructions for setting up new IoLT devices, including documentation and demo for each device. Follow the steps below to ensure proper setup and configuration. -->

The AC Training Lab emphasizes not just repeatability, but also _replicability_. Solutions within the training lab should be chosen, designed, implemented, and documented with this in mind. In other words, if someone can take a look at something within the AC training lab and replicate it easily within their own lab with minimal frustration, the AC Training Lab is serving one of its most fundamental purposes. To achieve that, the following steps are typically present when taking an Internet of Laboratory Things (IoLT) device and corresponding demo from start to finish.

## MWE for functionality

Typically, these go into a `src/ac_training_lab/*/_scripts` folder. This also makes it easier to iteratively develop (start with basic functionality of the device, gradually work towards the full implementation with MQTT).

## Accelerated discovery post

This is used as a sort of "travel log" of work on the project. This one is more public facing, and easier for others to look at and contribute discussion to (easier than GitHub for those who are unfamiliar with GitHub). Periodic updates should be provided.

## MQTT orchestrator and device code

This enables hardware/software communication over WiFi. Typically, this will follow closely to https://ac-microcourses.readthedocs.io/en/latest/courses/hello-world/1.4-hardware-software-communication.html and the [companion notebook tutorial](https://ac-microcourses.readthedocs.io/en/latest/courses/hello-world/1.4.1-onboard-led-temp.html). See below for some examples (both orchestration and device code).

Orchestration
- [Light-mixing](https://huggingface.co/spaces/AccelerationConsortium/light-mixing/blob/main/app.py), [Digital Pipette](https://huggingface.co/spaces/AccelerationConsortium/digital-pipette/blob/main/app.py), [Fan control](https://huggingface.co/spaces/AccelerationConsortium/fan-control/blob/main/app.py)
- https://github.com/sparks-baird/self-driving-lab-demo/blob/main/src/self_driving_lab_demo/utils/observe.py
- https://github.com/AccelerationConsortium/ac-training-lab/blob/main/src/ac_training_lab/openflexure/microscope_demo_client.py

Device
- https://github.com/AccelerationConsortium/ac-training-lab/blob/main/src/ac_training_lab/picow/fan-control/main.py
- https://github.com/AccelerationConsortium/ac-training-lab/blob/main/src/ac_training_lab/picow/digital-pipette/main.py
- https://github.com/AccelerationConsortium/ac-training-lab/blob/main/src/ac_training_lab/picow/magnetometer/main.py

## MongoDB logging setup

Typically, anything with data and timestamp-based actions will be logged to a database. These implementations will usually follow closely to https://ac-microcourses.readthedocs.io/en/latest/courses/hello-world/1.5-data-logging.html and the companion notebook.

## Hugging Face Spaces

Each demo will typically have a streamlit app hosted on Hugging Face Spaces within [the Acceleration Consortium organization under a hardware control list](https://huggingface.co/collections/AccelerationConsortium/hardware-control-66a4506f9876e9781c8a0808).

Some additional context is available at https://ac-bo-hackathon.github.io/resources/ (scroll to bottom).

I suggest starting with watching [a two-minute video about hugging face spaces](https://youtu.be/3bSVKNKb_PY?si=3qAScm2xfjNy1vrN) [[docs](https://hf.co/docs/hub/spaces)], then exploring the code (see "files" tab) in the AC's various hardware control apps: https://huggingface.co/collections/AccelerationConsortium/hardware-control-66a4506f9876e9781c8a0808. New web apps will live next to these in the same list.

## Video demo

Some examples:
- https://youtube.com/shorts/jQLtg0luPNc?feature=share
- https://youtube.com/shorts/rVnvR2fWg2Y?feature=share
- https://accelerated-discovery.org/t/building-the-high-resolution-motorized-openflexure-microscope-v7-using-the-rodeostat-kit/231/16?u=sgbaird

## Video setup tutorial

Examples:
- https://youtu.be/U_jJQKIOzTg
- https://youtu.be/meaXhH14zzY
- https://youtube.com/shorts/_3stUKidY7Y?feature=share

## Docs page and tutorial (BoM, setup, etc.)

To be added as [a device page](https://github.com/AccelerationConsortium/ac-training-lab/tree/main/docs/devices). More examples to follow.

Examples:
- https://ac-microcourses.readthedocs.io/en/latest/courses/robotics/3.1-pumps-and-pipettes.html
- https://ac-microcourses.readthedocs.io/en/latest/courses/robotics/3.2-serial-communication.html

## Embedding into Gather Town

![image](https://github.com/user-attachments/assets/0fade265-76f1-471d-a202-ad8c7ae847c1)
