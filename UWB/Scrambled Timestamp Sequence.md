# Scrambled Timestamp Sequence (STS)

### The Security Flaw in Standard UWB
In standard UWB (IEEE 802.15.4a), the preamble (the sequence of pulses used to sync up) is **static** and **public**.
- Everyone knows the code.
- If the code is "Pulse-Space-Pulse-Pulse", an attacker can simply broadcast that exact pattern.
- This enables the **[[Ghost Peak Attack]]**: The attacker injects the known pattern _early_ to trick the receiver's [[Leading Edge Detection (LDE)]].

### The Solution: Cryptographic Unpredictability
To stop the attacker, we must ensure that **nobody except the car and the key knows what the signal is supposed to look like.**

We replace the static preamble with a **Scrambled Timestamp Sequence (STS)**.

### 1. The Structure (HRP-UWB PHY)
The physical packet is split into parts (defined in **IEEE 802.15.4z**):

1.  **SYNC (Standard Preamble):** Uses standard known codes.
    -   _Purpose:_ To let the receiver wake up, adjust its gain (AGC), and find the rough timing. **This part is not secure.**
2.  **STS (Secure Segment):** A sequence of thousands of pulses.
    -   _Purpose:_ **Secure Ranging.** The distance is calculated based _only_ on the arrival time of this segment.
3.  **PAYLOAD (Data):** The actual file data (if any).

### 2. How STS is Generated
The sequence of pulses is generated using a Cryptographically Secure Pseudo-Random Number Generator (CSPRNG), typically based on **AES-128**.

1.  **Shared Key:** During the initial setup (via [[Origins|BLE Handshake]]), the Car and the Phone agree on a temporary **Session Key**.
2.  **The Counter:** Both devices keep a synchronized counter.
3.  **Generation:**
    $$PulseSequence = AES_{Key}(Counter)$$
    
The result is a stream of random bits: `1, 0, 0, 1, 1, 0, 1...`
-   **If 1:** Send a Positive Polarity Pulse (+1).
-   **If 0:** Send a Negative Polarity Pulse (-1).

### 3. Why this defeats the Attack
The receiver generates the _expected_ template locally using the same Key and Counter. It then runs the **Cross-Correlation**:

$$z = \int r(t) \cdot STS_{local}(t) \, dt$$

**The Attacker's Dilemma:**
The attacker wants to inject a "Ghost" pulse to trigger the detector early.
-   But they don't know if the next pulse is supposed to be **+1** or **-1**.
-   If the attacker guesses **+1**, but the real random sequence demanded **-1**:
    -   The correlation math is: $(+1) \times (-1) = -1$.
    -   **Destructive Interference!** The attacker's signal actually _lowers_ the correlation score, making it even harder for the ghost to trigger the threshold.

### 4. BPSK Modulation (The Technical Shift)
Standard UWB uses PPM (Pulse Position Modulation). However, STS uses **BPSK (Binary Phase Shift Keying)**.
-   **PPM:** Shift the _timing_ of the pulse.
-   **BPSK:** Invert the _polarity_ of the pulse (Upside down or Right side up).

Because the "Code" is defined by the polarity (+/-), and the polarity is random, the average correlation of any random signal (noise or attacker guessing) tends toward **Zero**. Only the true owner, holding the AES Key, can produce the sequence that sums up to a high Correlation Peak.