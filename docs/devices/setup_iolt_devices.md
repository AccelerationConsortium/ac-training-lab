# Setting Up IoLT Devices (WIP)

<!-- This document provides comprehensive instructions for setting up new IoLT devices, including documentation and demo for each device. Follow the steps below to ensure proper setup and configuration. -->

IoLT = Internet of Laboratory Things

The AC Training Lab emphasizes not just repeatability, but especially replicability. Solutions within the training lab should be chosen, designed, implemented, and documented with this in mind, within reason. in other words, if someone can take a look at something within the AC training lab and replicate it easily within their own lab with minimal frustration, the AC Training Lab is serving one of its most fundamental purposes. To achieve that, we have the following items that are typically present when taking a demo from start to finish.

1. MWE for functionality

Typically, these go into a `src/ac_training_lab/*/_scripts` folder. This also makes it easier to iteratively develop.

2. Accelerated discovery post

This is used as a sort of "travel log" of work on the project. This one is more public facing, and easier for others to look at and contribute discussion to (easier than GitHub for those who are unfamiliar with GitHub).

1. MQTT orchestrator and device code

This enables hardware/software communication over WiFi. Typically, this will follow closely to https://ac-microcourses.readthedocs.io/en/latest/courses/hello-world/1.4-hardware-software-communication.html.

2. MongoDB logging setup

Typically, anything with data and timestamp-based actions will be logged to a database. These implementations will usually follow closely to https://ac-microcourses.readthedocs.io/en/latest/courses/hello-world/1.5-data-logging.html.

3. Hugging Face Spaces

Each demo will typically have a streamlit app hosted on Hugging Face Spaces within [the Acceleration Consortium organization under a hardware control list](https://huggingface.co/collections/AccelerationConsortium/hardware-control-66a4506f9876e9781c8a0808).

Some additional context is available at https://ac-bo-hackathon.github.io/resources/ (scroll to bottom).

 I suggest starting with watching [a two-minute video about hugging face spaces](https://youtu.be/3bSVKNKb_PY?si=3qAScm2xfjNy1vrN) [[docs](https://hf.co/docs/hub/spaces)], then exploring the code (see "files" tab) in the AC's various hardware control apps: https://huggingface.co/collections/AccelerationConsortium/hardware-control-66a4506f9876e9781c8a0808. New web apps will live next to these in the same list.

5. Video demo



6. Video setup tutorial
7. Docs page and tutorial (BoM, setup, etc.)
8. Embedding into Gather Town

Periodic updates to Accelerated Discovery. 
