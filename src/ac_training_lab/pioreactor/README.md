# Pioreactor

Pioreactor is an open-source bioreactor platform that can be used for a variety of applications, including fermentation, cell culture, and more.

Related issue(s):
- https://github.com/AccelerationConsortium/ac-training-lab/issues/174
- https://github.com/AccelerationConsortium/ac-training-lab/issues/76
- https://github.com/AccelerationConsortium/ac-training-lab/issues/117
- https://github.com/AccelerationConsortium/ac-training-lab/issues/145
- https://github.com/AccelerationConsortium/ac-training-lab/issues/97
- https://github.com/AccelerationConsortium/ac-training-lab/issues/51


## Pinch Valve

The PS-1615NC pinch valve appears to operate regardless of polarity.

For the Pioreactor after installing the [relay plugin](https://github.com/camdavidsonpilon/pioreactor-relay-plugin) set the `start_on` for the relay in the configurations to 0. May require restart.

```bash
nano ~/.pioreactor/config.ini
```

```ini
[relay.config]
post_delay_duration = 1
pre_delay_duration = 1
enable_dodging_od = 1
start_on = 0
```

Also ensure the PWM mapping in `config.ini` corresponds to the PWM port that the relay is plugged into (e.g., `3=relay`).


```ini
[PWM]
# map the PWM channels to externals.
# hardware PWM are available on channels 2 & 4.
1=stirring
2=media
3=relay
4=waste
5=heating
```