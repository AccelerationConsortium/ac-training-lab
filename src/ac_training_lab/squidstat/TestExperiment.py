import sys

from PySide6.QtWidgets import QApplication
from SquidstatPyLibrary import (
    AisConstantCurrentElement,
    AisConstantPotElement,
    AisDeviceTracker,
    AisEISPotentiostaticElement,
    AisExperiment,
)

# AisExperimentNode,; AisInstrumentHandler,; AisACData,; AisCompRange,;
# AisDCData,; AisErrorCode,

app = QApplication()

tracker = AisDeviceTracker.Instance()

tracker.newDeviceConnected.connect(
    lambda deviceName: print("Device is Connected: %s" % deviceName)
)
tracker.connectToDeviceOnComPort("COM3")

handler = tracker.getInstrumentHandler("Prime2645")

handler.activeDCDataReady.connect(
    lambda channel, data: print(
        "timestamp:",
        "{:.9f}".format(data.timestamp),
        "workingElectrodeVoltage: ",
        "{:.9f}".format(data.workingElectrodeVoltage),
    )
)
handler.activeACDataReady.connect(
    lambda channel, data: print(
        "frequency:",
        "{:.9f}".format(data.frequency),
        "absoluteImpedance: ",
        "{:.9f}".format(data.absoluteImpedance),
        "phaseAngle: ",
        "{:.9f}".format(data.phaseAngle),
    )
)
handler.experimentNewElementStarting.connect(
    lambda channel, data: print(
        "New Node beginning:",
        data.stepName,
        "step number: ",
        data.stepNumber,
        " step sub : ",
        data.substepNumber,
    )
)
handler.experimentStopped.connect(
    lambda channel: print("Experiment Completed: %d" % channel)
)

experiment = AisExperiment()
cvElement = AisConstantPotElement(5, 1, 10)
eisElement = AisEISPotentiostaticElement(10000, 1, 10, 0.15, 0.1)
ccElement = AisConstantCurrentElement(1, 1, 10)


subExperiment = AisExperiment()
subExperiment.appendElement(ccElement, 1)
subExperiment.appendElement(cvElement, 1)


experiment.appendElement(ccElement, 1)
experiment.appendElement(cvElement, 1)
experiment.appendSubExperiment(subExperiment, 2)
experiment.appendElement(eisElement, 1)


handler.uploadExperimentToChannel(0, experiment)
handler.startUploadedExperiment(0)


sys.exit(app.exec())
