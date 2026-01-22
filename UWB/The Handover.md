# The Handover: BLE to UWB

A car battery is large, but the specialized electronics that wake the car up must consume micro-amps to avoid draining it over weeks of parking.

**The Problem:** UWB chips are too power-hungry to stay "always on" and listening for a signal.
**The Solution:** Use Bluetooth Low Energy (BLE) as a low-power "Doorman."

The process of using one radio (BLE) to set up another (UWB) is called **Out-of-Band (OOB) Signaling**.

### The Flow of Events

#### 1. The Sleep State (Polling)
-   **Car:** UWB Radio is **OFF**. BLE Radio is in **Advertising Mode** (waking up every few 100ms to chirp "I am a Car").
-   **Phone:** UWB Radio is **OFF**. BLE Radio is **Scanning** in the background.

#### 2. Discovery & Connection
-   The user walks within ~10 meters of the car.
-   **Phone:** Hears the BLE Advert. Checks its digital wallet ("Do I have a key for this car ID?").
-   **Action:** Phone initiates a BLE Connection.
-   **Result:** A standard Bluetooth GATT connection is established.

#### 3. Authentication (The Digital Key)
Before turning on the expensive UWB sensors, the car must verify the key.
-   **Exchange:** Public Key Infrastructure (PKI) exchange occurs over BLE.
-   **Challenge:** Car sends a challenge; Phone signs it with its private key.
-   **Result:** Car trusts the Phone. **Authentication Complete.**

#### 4. The UWB Negotiation (OOB Setup)
Now they need to agree on how to talk over UWB. They exchange **Ranging Parameters** over the BLE link:
1.  **Channel ID:** (e.g., Channel 9 - 8GHz).
2.  **Preamble Code:** (Which pattern to use for SYNC).
3.  **Session ID:** A temporary ID for this transaction.
4.  **STS Key:** The most important part. They derive a fresh **AES-128 Key** for the [[Scrambled Timestamp Sequence]].
    -   *Crucial:* This key is never sent over the air in plain text. It is derived from the shared secret established during authentication.

#### 5. Time Synchronization & Activation
-   **Car:** "Turn on UWB Radio at $T_{now} + 50ms$."
-   **Phone:** "Acknowledged."
-   *Both devices power up their UWB chips simultaneously.*

#### 6. The Ranging Loop
-   The BLE connection remains active to send control data (e.g., "Ranging started").
-   The UWB radios begin the **Two-Way Ranging (TWR)** ping-pong using the secure [[HRP-UWB Frame Structure]].
-   Distance is calculated 10 times per second.

#### 7. The Unlock
-   The Car's Secure Element verifies the UWB measurements:
    1.  Is the distance < 1.5 meters?
    2.  Is the [[Scrambled Timestamp Sequence]] correct? (Authenticity).
    3.  Is the signal strictly Line-of-Sight? (Check [[Leading Edge Detection (LDE)]]).
-   **Decision:** Unlock the door.

### Summary
BLE is the **Manager**; UWB is the **Worker**.
BLE handles the "Who are you?" and "Here are the instructions."
UWB handles the "Where are you?"
