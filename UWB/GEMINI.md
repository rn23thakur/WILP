# Gemini Context & Project Tracker

## Project Goal
Create a comprehensive technical knowledge base explaining **Secure Vehicle Access using UWB (Ultra-Wideband)** compared to legacy BLE (Bluetooth Low Energy). The final output must be a "Master Orchestrator" document detailing the end-to-end flow of unlocking a car.

## Current Knowledge Base Status

### 1. Fundamentals (Physics & Math)
- [x] **Origins**: BLE vs UWB, RSSI vs ToF concept.
- [x] **Frequency Modulation & GFSK**: How BLE transmits data.
- [x] **Log-Distance Path Loss**: Why BLE ranging (RSSI) is mathematically flawed for security.
- [x] **Time Modulation (PPM)**: How UWB pulses are generated (SRD) and modulated.

### 2. Detection & Ranging (The "How")
- [x] **Time of Flight (ToF)**: The core distance math ($d = c \times t$).
- [x] **The Sliding Correlator**: How the receiver finds the pulse in noise.
- [x] **Orthogonality & Detection**: Why antipodal signals (negative correlation) are used.
- [x] **Leading Edge Detection (LDE)**: Finding the *first* path vs the *strongest* path.

### 3. Vulnerabilities & Security
- [x] **Ghost Peak Attack**: How to fool the LDE algorithm (Cicada attack).
- [x] **Scrambled Timestamp Sequence (STS)**: The cryptographic solution to the Ghost Peak attack using AES-128 and BPSK.
- [x] **Attack Vectors & POC**: Detailed threat matrix (Cicada, Replay, Preamble Injection) and novel "Battery Drain" POC design.

### 4. System Integration (The "Missing Link")
- [x] **HRP-UWB Frame Structure**: Detailed breakdown of the PHY Frame (SYNC, STS, Payload) and the mix of modulations (BPSK vs PPM).
- [x] **The Handover**: The car doesn't just "leave" UWB on. It uses BLE for discovery and then "wakes up" the UWB. This orchestration is missing.
- [x] **Master Orchestrator**: The final requested document.

---

## TODO List

**ALL TASKS COMPLETED.**

- [x] **Fill `Scrambled Timestamp Sequence.md`**
- [x] **Create `HRP-UWB Frame Structure.md`**
- [x] **Create `The Handover.md`**
- [x] **Create `Master_Orchestrator.md`**

## Execution Log
- **2026-01-21**: Audited all files. Found `Scrambled Timestamp Sequence.md` is empty. Identified gaps in modulation details (PPM vs BPSK) and the BLE-to-UWB handover process. Created this tracker.
- **2026-01-21**: Reviewed `Bosch_BITS_WILP_Research_Colloboration_UWB_802.15.4z.pdf`.
    -   Verified "Master Orchestrator" flow.
    -   Updated `Attack_Vectors_and_POC.md` to include an **Industrial/IoT Threat Vector** (Phantom Worker/TDoA Spoofing) as requested by the "Anticipated Outcome".
    -   Refined the **Battery Drain POC** with executable Python code (using `bleak`) to better "showcase" the concept.
    -   Confirmed all "Anticipated Outcomes" are now covered in depth.
