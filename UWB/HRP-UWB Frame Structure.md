# HRP-UWB Frame Structure (IEEE 802.15.4z)

Modern secure vehicle access relies on **HRP-UWB** (High Repetition Pulse Ultra-Wideband). Unlike the older UWB standards used for simple file transfers, this "z-standard" is specifically designed for security.

The magic lies in its **Hybrid Modulation Scheme**: It changes the language it speaks halfway through the sentence.

### The Anatomy of a Packet

A single UWB transmission is called a **Frame**. It has three distinct parts, each with a different job and modulation.

```text
|-------------------|-------------------|-------------------|
|      1. SYNC      |      2. STS       |      3. DATA      |
|  (The "Hello")    |   (The "Ruler")   |   (The "Files")   |
|-------------------|-------------------|-------------------|
```

---

### 1. The SYNC (Synchronization Header)
**Goal:** Be as loud and easy to find as possible.

-   **Component:** Called the **SHR (Synchronization Header)**.
-   **Modulation:** **Ternary Preamble codes.**
-   **Logic:** It repeats a known, static code (like `+1, 0, -1, +1...`) hundreds of times.
-   **Why?** The receiver is "asleep" (listening to noise). It needs a strong, predictable pattern to wake up, latch on, and synchronize its clock.
-   **Security:** **Zero.** Since the code is public, anyone can fake it. This is why we *cannot* trust the arrival time of the SYNC for unlocking a car.

### 2. The STS (Scrambled Timestamp Sequence)
**Goal:** Be cryptographically impossible to fake.

-   **Component:** The **Secure Segment**.
-   **Modulation:** **BPSK (Binary Phase Shift Keying).**
    -   It uses the AES-128 generated sequence explained in [[Scrambled Timestamp Sequence]].
-   **Logic:**
    -   No "Time Slots" (PPM).
    -   Just a relentless stream of pulses with random polarity ($+1$ or $-1$).
-   **Why?** This segment is used *exclusively* for the **Time of Flight** calculation. The receiver ignores the SYNC timestamp and only trusts the timestamp derived from correlating this secure BPSK stream.

### 3. The DATA (Payload)
**Goal:** Carry information (like "Door Open" command or Handshake ID).

-   **Component:** The **PHR (PHY Header)** and **PSDU (Data Unit)**.
-   **Modulation:** **BPM-BPSK (Burst Position Modulation + BPSK).**
-   **Logic:** This is the most complex part. It combines two ideas:
    1.  **Burst Position (BPM):** "Did I send the burst in the first half or the second half of the time slot?" (Encodes 1 bit).
	2.  **Phase (BPSK):** "Was the burst positive or negative?" (Encodes another bit).
-   **Efficiency:** This allows it to send 2 bits per symbol, making it faster for data transfer than the raw STS.

### Summary: The Modulation Handoff

| Field | Function | Modulation | Security |
| :--- | :--- | :--- | :--- |
| **SHR** | Wake up & Sync | Static Codes | Low |
| **STS** | **Measure Distance** | **BPSK (Random)** | **High** |
| **DATA** | Send Info | BPM-BPSK | Med |

**The Critical takeaway:**
When a car unlocks, it effectively ignores Part 1 and Part 3 for the distance check. It relies entirely on the arrival time of the **STS (Part 2)**.
