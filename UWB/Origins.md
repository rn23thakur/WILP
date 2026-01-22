BLE actually uses [[Frequency Modulation]] ([[GFSK]]) to transfer data (files, music). However, for **ranging** (calculating distance), it ignores the frequency and looks solely at the **Amplitude** (Power) of the received signal.

This is called **RSSI (Received Signal Strength Indicator)**.
#### The Mathematics of RSSI

The receiver estimates distance using the **[[Log-Distance Path Loss Model]]**. Physics tells us that radio waves get weaker as they travel (inverse-square law).
$$RSSI = -10n \log_{10}(d) + A$$
Where:

- $RSSI$: The signal power received (measured in dBm).
- $d$: The distance between the devices.
- $n$: The path loss exponent (usually 2 for free space, but 2-4 in offices/hallways due to reflections).
- $A$: The RSSI value measured at exactly 1 meter (a calibration constant).
#### Why this is vulnerable (The Math of the Attack)

An attacker wants to trick the lock into thinking $d$ is small (e.g., 1 meter) when the owner is actually far away (e.g., 100 meters).

1. The lock expects an RSSI of **-50 dBm** to unlock.
2. The real owner is far away, so their signal arrives at **-90 dBm** (too weak).
3. The attacker uses a "Relay" device. They capture the weak -90 dBm signal and simply **amplify** it (add gain).
4. If they add $+40$ dB of gain, the lock receives **-50 dBm**.
5. Mathematically, the lock solves the equation for $d$ and calculates "1 meter." **The door opens.**

### How UWB Works ([[Time Modulation & Nanosecond Pulses]])

UWB does not care how "loud" the signal is. It uses **[[Time of Flight (ToF)]]**. It sends a sequence of extremely short pulses.
#### The Mathematics of ToF

The calculation relies on the universal constant, the speed of light ($c \approx 3 \times 10^8$ meters/second).

$$d = c \times t_{flight}$$

Usually, two-way ranging (TWR) is used to avoid needing synchronized clocks:

1. Device A sends a pulse at $t_1$.
2. Device B receives it, waits a specific processing time ($t_{reply}$), and sends it back.
3. Device A receives the reply at $t_2$.

$$d = \frac{c \times ((t_2 - t_1) - t_{reply})}{2}$$
#### Why this is secure

If an attacker amplifies the signal (like in BLE), the pulse still travels at the speed of light. Making the pulse "louder" does not make it arrive **sooner**. To hack this, the attacker would have to break the laws of physics and make the signal travel faster than light.

### The Tech Barrier – Why wasn't this used before?

You asked about the "tech required to modulate those nanosecond pulses" and why we waited so long. The answer lies in the **Time-Frequency Duality** (Fourier Transform).
#### The Physics: The Bandwidth Requirement

To create a very sharp, short pulse in time, you need a massive amount of frequency bandwidth. There is a fundamental mathematical relationship:

$$\Delta t \approx \frac{1}{B}$$
Where:

- $\Delta t$ is the duration of the pulse.
- $B$ is the Bandwidth (range of frequencies used).

**The Comparison:**

- **Bluetooth:** Uses narrow channels (approx 1-2 MHz bandwidth).
    - $\Delta t \approx 1 / 10^6 = 1 \mu s$ (1 microsecond).
    - In 1 microsecond, light travels **300 meters**. This pulse is too "fat" or "blurry" to measure precise distance.
        
- **UWB:** Uses massive bandwidth (500 MHz or more).
    - $\Delta t \approx 1 / (500 \times 10^6) = 2 ns$ (2 nanoseconds).
    - In 2 nanoseconds, light travels **60 centimeters**. This is sharp enough for secure locking.
#### The Hardware Challenge

Why didn't we do this in the 90s?

1. **Spectrum Licensing:** You can't just grab 500 MHz of radio spectrum. That is a huge chunk of valuable airwaves. The FCC only authorized UWB for unlicensed use in 2002 because it operates at such low power (noise floor) that it doesn't interfere with other radios.
    
2. **Sampling Rates (ADCs):** To detect a 2-nanosecond pulse, your hardware clock needs to tick incredibly fast. You need **Analog-to-Digital Converters (ADCs)** that can sample at Gigahertz speeds. In the past, these were expensive, power-hungry, and size-prohibitive (think military radar equipment).
    
3. **Power Consumption:** Generating and processing these wideband pulses used to drain batteries instantly. It is only with modern silicon processes (like 5nm/7nm chips found in modern smartphones) that we can put a UWB chip in a phone without killing the battery.