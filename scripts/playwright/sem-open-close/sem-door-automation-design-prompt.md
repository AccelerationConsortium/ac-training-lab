# Problem Statement: Mechanical Design for SEM Door Automation Using Tie Rod Linkage

## Context & Background
The Acceleration Consortium's Training Lab requires automated opening and closing of a Scanning Electron Microscope (SEM) door for remote operation capabilities. This is part of a larger initiative (Issue #132) to enable remote access to laboratory equipment.

## Design Challenge
Design a mechanical linkage system to connect an Actuonix L16 linear actuator to the ellipsoidal handle of a SEM door, enabling automated door operation while maintaining proper force alignment and minimizing stress on the door mechanism.

## Technical Specifications

### Actuator Specifications (Actuonix L16):
- **Mounting interface**: M4 threaded holes in clevis
- **Distance from SEM face to actuator clevis face**: (assume these are within the same plane, since the actuator can be repositioned)
- **Datasheet reference**: [ActuonixL16Datasheet.pdf](https://actuonix-com.3dcartstores.com/assets/images/datasheets/ActuonixL16Datasheet.pdf)

### Handle Dimensions:
- **Cross-sectional shape**: Ellipsoidal
- **Diameter (left-right)**: 24mm
- **Diameter (top-bottom)**: 20mm
- **Distance from right side to first handle**: 120mm
- **3D printed component width**: 150mm across
- **Optimal attachment point**: Center of handle for parallel force application

## Design Requirements

### Primary Requirements:
1. **Force Alignment**: Maintain parallel force direction with door opening motion
2. **Minimal Door Stress**: Avoid putting undue strain on door mechanism
3. **Adjustable Length**: Enable fine-tuning of linkage distance
4. **Secure Attachment**: Reliable connection to ellipsoidal handle geometry
5. **Tool Accessibility**: Consider required installation tools

### Design Constraints:
- **Space Limitation**: ~15mm clearance from SEM face to actuator
- **Handle Geometry**: Non-circular (ellipsoidal) cross-section
- **Thread Compatibility**: M4 mounting interface on actuator
- **Accessibility**: Installation must be feasible in confined SEM environment

## Proposed Solution Framework
Implement a **tie rod linkage system** consisting of:

1. **Connecting Rod ("Tie Rod")**: Adjustable-length rod with threaded ends
2. **Jam Nut**: For locking rod at desired length
3. **Clevis Rod End**: Attaches to actuator's clevis interface
4. **Rod End Bolt**: Connects to handle attachment mechanism
5. **Handle Attachment**: Secures rod end bolt to ellipsoidal handle

## Design Tasks & Deliverables

### Research & Specification Phase:
- [ ] Extract detailed clevis dimensions from Actuonix L16 datasheet
- [ ] Research and specify McMaster-Carr tie rod components:
  - Connecting rod with appropriate thread size/length
  - Compatible jam nut
  - Clevis rod end (M4 compatible)
  - Rod end bolt
- [ ] Validate component compatibility and provide direct product links

### Handle Attachment Solutions (Priority Order):
1. **Near-term**: Reusable cable/zip tie solution for rapid prototyping
2. **Long-term**: Engineered clamp solution using:
   - Square U-bolt for handle clamping
   - Matching U-bolt plate
   - Custom tab/bracket for rod end bolt attachment

### Documentation Requirements:
- Component specifications with McMaster-Carr part numbers
- Assembly instructions and required tools
- Force analysis and stress considerations
- Installation procedure for SEM environment

## Success Criteria
- **Functional**: Successful automated SEM door operation
- **Reliable**: Consistent performance without component failure
- **Maintainable**: Easy access for adjustments and maintenance
- **Safe**: No damage to SEM equipment or door mechanism
- **Scalable**: Design principles applicable to similar automation tasks

## References
- **Primary Issue**: [#460 - mechanical design attaching to handle with tie rod](https://github.com/AccelerationConsortium/ac-dev-lab/issues/460)
- **Parent Issue**: [#132 - SEM custom open/close with linear actuator](https://github.com/AccelerationConsortium/ac-dev-lab/issues/132)
- **Design Context**: [ChatGPT Design Discussion](https://chatgpt.com/share/68d44598-5d98-8007-ae93-c43bec132dc5)
- **Actuator Datasheet**: [Actuonix L16 Specifications](https://actuonix-com.3dcartstores.com/assets/images/datasheets/ActuonixL16Datasheet.pdf)

---

This design task combines mechanical engineering principles with practical laboratory automation needs, requiring careful consideration of component selection, force analysis, and installation constraints in a precision instrument environment.
