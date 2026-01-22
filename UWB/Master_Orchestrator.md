# Secure Vehicle Access: The Master Orchestrator

This document details the end-to-end technical flow of a Digital Key system. It serves as the index for the UWB Knowledge Base.

---

### Phase 1: The Approach (Far Field)
**Distance: > 10 Meters**

The vehicle is asleep. To save power, its UWB radar is off. It relies on **Bluetooth Low Energy (BLE)**.
1.  **Discovery:** The car broadcasts generic advertising packets.
2.  **RSSI Estimation:** The phone sees the car. It estimates rough distance using signal strength.
    -   *Reference:* [[Log-Distance Path Loss Model]] - Explains why this is used for wake-up but *ignored* for unlocking due to relay attacks.

### Phase 2: The Handshake & Handoff
**Distance: ~5 Meters**

The phone connects.
1.  **Authentication:** Cryptographic keys are exchanged over BLE.
2.  **OOB Negotiation:** The car and phone agree on UWB parameters (Channel, Preamble) and derive the session key.
    -   *Reference:* [[The Handover]] - The BLE-to-UWB transition protocol.

### Phase 3: The UWB Pulse Generation
**Distance: < 5 Meters (Ranging Active)**

The UWB radios activate. The phone generates a pulse.
1.  **Pulse Shape:** A Step Recovery Diode creates a Gaussian Monocycle.
    -   *Reference:* [[Time Modulation & Nanosecond Pulses]].
2.  **The Frame:** The pulse is packed into an **HRP-UWB Frame** containing a Sync Header (SHR), a Secure Segment (STS), and Data.
    -   *Reference:* [[HRP-UWB Frame Structure]] - The hybrid modulation (PPM + BPSK).

### Phase 4: The Flight & Reception
**Physics:** The signal travels at $c \approx 3 \times 10^8$ m/s.

1.  **Correlation:** The car's receiver continuously "slides" a local template against the incoming noise to find the signal.
    -   *Reference:* [[The Sliding Correlator]].
2.  **Interference:** The signal bounces off the ground (Multipath). The receiver must ignore the strong echoes and find the *first* weak signal.
    -   *Reference:* [[Leading Edge Detection (LDE)]].

### Phase 5: The Security Check
**The Attack Surface:** A thief tries to amplify the signal or inject a fake pulse.

1.  **Verification:** The car checks the **Scrambled Timestamp Sequence (STS)**.
    -   It ensures the received pulses match the AES-128 random sequence generated from the Session Key.
    -   *Reference:* [[Scrambled Timestamp Sequence]] - How BPSK and Cryptography defeat the Ghost Peak.
2.  **Vulnerability:** If STS was not used, the thief could perform a Cicada Attack.
    -   *Reference:* [[Ghost Peak Attack]].

### Phase 6: The Calculation (Final Decision)
**The Math:**

The system performs **Two-Way Ranging (TWR)** to cancel out clock differences.
-   *Reference:* [[Time of Flight (ToF)]].

$$Distance = \text{Speed of Light} \times \text{Time of Flight}$$

If:
1.  Distance < Unlocking Threshold (e.g., 1.5m).
2.  STS Integrity is Valid.
3.  LDE Confidence is High.

**Action:** The Body Control Module (BCM) triggers the door latches. **Access Granted.**
