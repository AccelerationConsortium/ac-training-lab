import sys

from PySide6.QtWidgets import QApplication
from SquidstatPyLibrary import (
    AisConstantCurrentElement,
    AisConstantPotElement,
    AisDeviceTracker,
    AisErrorCode,
    AisExperiment,
)

# AisExperimentNode,; AisInstrumentHandler,; AisACData,; AisCompRange,;
# AisDCData,; AisEISPotentiostaticElement,


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
    cvElement = AisConstantPotElement(0.5, 0.1, 10)
    ccElement = AisConstantCurrentElement(0.1, 0.1, 10)

    success = False

    subExperiment = AisExperiment()
    success &= subExperiment.appendElement(ccElement, 1)
    success &= subExperiment.appendElement(cvElement, 1)

    success &= experiment.appendElement(ccElement, 1)
    success &= experiment.appendElement(cvElement, 1)
    success &= experiment.appendSubExperiment(subExperiment, 2)

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
