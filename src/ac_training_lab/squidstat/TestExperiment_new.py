import sys

from PySide6.QtWidgets import QApplication
from SquidstatPyLibrary import (
    AisConstantCurrentElement,
    AisConstantPotElement,
    AisDeviceTracker,
    AisEISPotentiostaticElement,
    AisErrorCode,
    AisExperiment,
)

# AisACData,
# AisCompRange,
# AisDCData,
# AisExperimentNode,
# AisInstrumentHandler,


def startExperiment(deviceName):
    print("Device is Connected: %s" % deviceName)

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

    success = False

    subExperiment = AisExperiment()
    success &= subExperiment.appendElement(ccElement, 1)
    success &= subExperiment.appendElement(cvElement, 1)

    success &= experiment.appendElement(ccElement, 1)
    success &= experiment.appendElement(cvElement, 1)
    success &= experiment.appendSubExperiment(subExperiment, 2)
    success &= experiment.appendElement(eisElement, 1)

    error = handler.uploadExperimentToChannel(0, experiment)
    if error.value() != AisErrorCode.Success:
        print("Error uploading experiment: %s" % error.message())
        return

    error = handler.startUploadedExperiment(0)
    if error.value() != AisErrorCode.Success:
        print("Error uploading experiment: %s" % error.message())
        return


app = QApplication()

tracker = AisDeviceTracker.Instance()

tracker.connectToDeviceOnComPort("COM5")
tracker.newDeviceConnected.connect(startExperiment)

sys.exit(app.exec())
