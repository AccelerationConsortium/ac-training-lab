from pioreactor.whoami import get_unit_name, get_assigned_experiment_name
from pioreactor.background_jobs.stirring import Stirrer, RpmFromFrequency

"""
Running this on the Pioreactor will start the stirring motor at 300 RPM.

This is a method to directly control the stirring motor, without the need for API calls.

Author: Enrui (Edison) Lin
"""

unit = get_unit_name()
experiment = get_assigned_experiment_name(unit)

st = Stirrer(
    target_rpm=300,
    unit=unit,
    experiment=experiment,
    rpm_calculator=RpmFromFrequency()
)

st.start_stirring()

st.block_until_disconnected()


