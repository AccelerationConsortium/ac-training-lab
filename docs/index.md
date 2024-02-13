# 🏢 AC Training Lab

```{warning}
This is an ongoing project. If you would like to participate or are interested in contributing, please [introduce yourself](https://github.com/AccelerationConsortium/ac-training-lab/discussions/2) or reach out to sterling.baird@utoronto.ca.
```

The [Acceleration Consortium](https://github.com/AccelerationConsortium) (AC)
Training Lab is meant to be a remotely accessible facility that will house a
diverse set of physical hardware for self-driving laboratories (SDLs) including
liquid handlers, solid dispensers, Cartesian-axis systems, mobile robotic arms,
and synthesis and characterization modules. Where possible, both educational and
research-grade hardware will be included. The AC Training Lab will be used to
develop and test SDLs, and to provide a platform for training students and
researchers in the use of SDLs. This repository also acts as an example of
setting up an autonomous laboratory.

<a class="github-button" href="https://github.com/AccelerationConsortium/ac-training-lab"
data-icon="octicon-star" data-size="large" data-show-count="true" aria-label="Star
AccelerationConsortium/ac-training-lab on GitHub">Star</a>
<a class="github-button"
href="https://github.com/AccelerationConsortium" data-size="large" data-show-count="true"
aria-label="Follow @AccelerationConsortium on GitHub">Follow</a>
<a class="github-button"
href="https://github.com/sgbaird" data-size="large" data-show-count="true"
aria-label="Follow @sgbaird on GitHub">Follow</a>
<a class="github-button" href="https://github.com/AccelerationConsortium/ac-training-lab/issues"
data-icon="octicon-issue-opened" data-size="large" data-show-count="true"
aria-label="Issue AccelerationConsortium/ac-training-lab on GitHub">Issue</a>
<a class="github-button" href="https://github.com/AccelerationConsortium/ac-training-lab/discussions" data-icon="octicon-comment-discussion" data-size="large" aria-label="Discuss AccelerationConsortium/ac-training-lab on GitHub">Discuss</a>

The equipment in the training lab can be broadly categorized in the following
categories: characterization, prototyping, synthesis, dispensing, environment,
and infrastructure. See the image below for an example of some of the equipment
intended for the AC Training Lab.

![training lab categories](training-lab-categories.png)

Here are some of the modules we have procured and are in the process of setting up (help wanted if you're in Toronto!):

<!-- TODO: Convert this to YAML and autopopulate table, preferably linked to current status somehow (planning, in progress, complete, etc.) -->

| Name | Qty | Description |
| --- | --- | --- |
| [Jubilee](https://jubilee3d.com/index.php?title=Main_Page) | 1 | A versatile, open-source toolchanger with a large community of users and developers which is used for both general 3D printing and [scientific applications](https://dx.doi.org/10.1039/D3DD00033H). |
| [Delta Stage Microscope](https://openflexure.org/projects/deltastage/) | 2 | A DIY open-source microscope with a fine-positioning, motorized stage. Reflection illumination version of Delta Stage |
| [Opentrons OT-2](https://opentrons.com/products/robots/ot-2/) | 1 | An open-source and cost-friendly commercial liquid handler |
| [Opentrons Flex](https://opentrons.com/products/flex/) | 1 | An open-source commercial liquid handler tailored towards high-throughput and advanced liquid handling operations |
| [Hiwonder ArmPi FPV](https://www.hiwonder.com/products/armpi?_pos=4&_sid=a9741a308&_ss=r) | 1 | An educational six-axis robotic arm |
| [Hiwonder JetAuto Pro](https://www.hiwonder.com/products/jetauto-pro?variant=40040875229271) | 1 | An educational six-axis mobile cobot with a 3D depth camera and lidar |
| [MyCobot 280](https://shop.elephantrobotics.com/en-ca/collections/mycobot/products/mycobot-pi-worlds-smallest-and-lightest-six-axis-collaborative-robot) and [MyAGV](https://shop.elephantrobotics.com/en-ca/collections/myagv/products/myagv-2023-pi?variant=47262714069304) | 1 | An educational six-axis mobile cobot |
| [AutoTrickler v4](https://autotrickler.com/pages/autotrickler-v4) | 1 | An automated solid dispensing station designed for ammunition loading |
| [ChargeMaster Supreme](https://www.rcbs.com/priming-and-powder-charging/powder-dispensers-and-scales/chargemaster-supreme-electronic-powder-dispenser/16-98943.html) | 1 | An automated solid dispensing station designed for ammunition loading |
| [Ingenuity Powder System](https://ingenuityprecision.com/product/ingenuity-powder-system/) | 1 | An automated solid dispensing station designed for ammunition loading |
| [Cocoa Press](https://cocoapress.com/en-ca) | 1 | A commercially sold and mostly open-source chocolate 3D printer kit |
| [FormAuto](https://formlabs.com/3d-printers/form-auto/) and [Form 3+](https://formlabs.com/3d-printers/form-3/) | 1 | 24/7 autonomous SLA 3D printer with camera inspection |
| [Form 3L](https://formlabs.com/3d-printers/form-3l/) | 1 | A large-format SLA printer |
| [Automated Turntable](https://www.tindie.com/products/fluxgarage/turntable-for-stepper-motor-kit/) | 1 | An open-source automated turntable controlled by a stepper motor and designed for photography applications |
| [Digital Pipette](https://github.com/ac-rad/digital-pipette) | 1 | A DIY linear actuator-based syringe pump designed for easy handling by robotic arms |
| [Chi.Bio](https://chi.bio/) | 1 | A commercially sold, open-source automated system with heating, stirring, liquid handling, spectrometry, and optogenetics characterization geared towards biological research |
| [Pioreactor](https://pioreactor.com/en-ca/products/pioreactor-20ml?variant=46559156469816) | 1 | A commercially sold, open-source automated bioreactor with heating, stirring, and optical density measurements |
| [Rodeostat](https://iorodeo.com/products/rodeostat) | 5 | A commercially sold, open-source potentiostat for electrochemical experiments |
| [Microfluidics](https://www.labmaker.org/collections/biotechnology/products/pressure-regulator-senyo-lab) | 1 | A commercially sold, open-source pressure regulator for controlling pneumatically-driven microfluidic chips |
| [UC2 Minibox](https://www.labmaker.org/collections/uc2-miniscope/products/uc2-minibox) | 1 | A commercially sold, open source set of introductory modular optics cubes for microscopy |
| [uMobileLab](https://unitedrobotics.group/en/robots/umobilelab) | 1 | A research-grade six-axis mobile cobot with vision capabilities optimized for laboratory environments |
| [Phenom Pure G6 SEM](https://www.thermofisher.com/ca/en/home/electron-microscopy/products/desktop-scanning-electron-microscopes/phenom-pure.html) | 1 | A desktop scanning electron microscope (SEM) with Python integrations |
| Chamber interfaces (TBD) | - | e.g., glovebox, fumehood, nitrogen environments |
| Tensile tester (TBD) | - | - |

We would love to get suggestions on the [types of workflows](https://github.com/AccelerationConsortium/ac-training-lab/discussions/3) you'd like to see in the AC Training Lab! For additional training opportunities offered by the Acceleration Consortium, please navigate to [AC Microcourses](https://ac-microcourses.readthedocs.io/en/latest/).

## Contents

```{toctree}
:maxdepth: 2

Contributions & Help <contributing>
License <license>
Authors <authors>
Module Reference <api/modules>
GitHub Source <https://github.com/AccelerationConsortium/ac-training-lab>
```

## Indices and tables

* {ref}`genindex`
* {ref}`modindex`
* {ref}`search`

[Sphinx]: http://www.sphinx-doc.org/
[Markdown]: https://daringfireball.net/projects/markdown/
[reStructuredText]: http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
[MyST]: https://myst-parser.readthedocs.io/en/latest/

<script async defer src="https://buttons.github.io/buttons.js"></script>
