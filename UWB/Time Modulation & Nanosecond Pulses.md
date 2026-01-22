Here is the rigorous explanation of how a UWB pulse is physically generated, mathematically modeled, and modulated.
### 1. Pulse Generation: The Step Recovery Diode (SRD)

Note - Think of SRD just like a switch that can cutoff current super fast and the inductive load attached produces a voltage spike due to dt <<.

Standard oscillators (like those in FM radios) generate continuous sine waves. To generate a specific nanosecond event, we rely on a transient switching event.
The primary component is the **Step Recovery Diode (SRD)**.

1. **Charge Storage:** When forward-biased, the SRD stores minority carriers (charge) near the junction. It acts as a low-impedance path (a closed switch).
2. **Reverse Transient:** When the bias is suddenly reversed, the diode conducts briefly as it extracts the stored charge.
3. **The "Snap":** Once the charge is depleted, the diode transitions to high impedance (an open switch) in picoseconds (e.g., $30\text{–}100 \text{ ps}$).

This rapid change in current ($di/dt$) creates a voltage impulse across the inductive load:

$$V_L = L \cdot \frac{di}{dt}$$

Because $dt$ is extremely small (picoseconds), $V_L$ becomes a massive, sharp voltage spike. This spike approximates a Dirac Delta function, which is then shaped by a filter into a **Gaussian Pulse**.
### 2. The Math of the Pulse: The Gaussian Monocycle

Note - Think of Antennas as a black box for now, I don't understand them.

In UWB, we do not use the raw Gaussian pulse for transmission because antennas cannot radiate DC energy (signals with non-zero average amplitude).

Instead, the antenna acts as a differentiator. It transmits the **first derivative** of the Gaussian pulse. This is called a **Gaussian Monocycle**.

#### A. The Base Gaussian Pulse

Let $p(t)$ be the standard Gaussian distribution:
$$p(t) = A e^{-\left(\frac{t}{\tau}\right)^2}$$
- $A$: Amplitude
- $\tau$: Decay factor (determines pulse width, typically $\approx 0.2 \text{ ns}$)

#### B. The Monocycle (Derivative)

The transmitted waveform $w(t)$ is the first time derivative of $p(t)$:
$$w(t) = \frac{d}{dt} \left[ A e^{-\left(\frac{t}{\tau}\right)^2} \right]$$
Using the Chain Rule, we derive the explicit equation for the UWB signal:
$$w(t) = A \cdot \left[ e^{-\left(\frac{t}{\tau}\right)^2} \right] \cdot \left[ -\frac{2t}{\tau^2} \right]$$
Cleaning this up, we get the canonical Gaussian Monocycle Equation:
$$w(t) = -\frac{2A}{\tau^2} t \cdot e^{-\left(\frac{t}{\tau}\right)^2}$$
**Key Mathematical Characteristics:**
1. **Zero Mean:** $\int_{-\infty}^{\infty} w(t) \, dt = 0$. This allows efficient radiation.
2. **Time Domain:** It has a single positive peak and a single negative peak (a single cycle).
3. **Frequency Domain:** The Fourier Transform of this pulse is extremely wide, spanning gigahertz of bandwidth.

![[Pasted image 20260121105138.png]]


### 3. Time Modulation: Pulse Position Modulation (PPM)

Now that we have the waveform $w(t)$, we must encode information onto it. We use **Pulse Position Modulation (PPM)**.

In standard communication, we define a "Frame Time" ($T_f$), which is the repetition period (e.g., one pulse every 100ns).

If we were sending no data, the signal would be a periodic train of pulses:
$$s(t) = \sum_{j=-\infty}^{\infty} w(t - jT_f)$$
To encode binary data, we introduce a **time delay shift** ($\delta$) to the arrival time of specific pulses.

#### The Binary PPM Equation

Let $d_j \in \{0, 1\}$ be the binary data stream.

Let $\delta$ be the modulation index (the time shift, usually $\approx 0.1 \text{ ns}$).

The modulated signal $s_{mod}(t)$ is:
$$s_{mod}(t) = \sum_{j=-\infty}^{\infty} w\left(t - jT_f - d_j \delta\right)$$
- **If $d_j = 0$:** The term becomes $w(t - jT_f)$. The pulse arrives "on time" (at the start of the frame).
- **If $d_j = 1$:** The term becomes $w(t - jT_f - \delta)$. The pulse arrives **delayed** by $\delta$ seconds.
![[Pasted image 20260121110455.png]]


#### [[Orthogonality and Detection]]

For the receiver to distinguish "0" from "1" rigorously, the standard pulse $w(t)$ and the shifted pulse $w(t-\delta)$ must be distinguishable. Ideally, they should be **orthogonal** or have negative correlation.

The receiver computes the Cross-Correlation $R(\tau)$ of the incoming signal $r(t)$ with a local template $v(t)$:

$$R(\tau) = \int_{-\infty}^{\infty} r(t) v(t - \tau) dt$$

Ideally, we choose $\delta$ such that the correlation peak for a "0" is positive and the correlation for a "1" is negative (or zero), allowing for a simple threshold decision.

### Summary of the Rigorous Chain

1. **Circuit:** SRD creates high $di/dt$ $\rightarrow$ Impulse.
2. **Antenna:** Differentiates Impulse $\rightarrow$ **Gaussian Monocycle** ($w(t)$).
3. **Math Model:** $w(t) \propto t \cdot e^{-t^2}$.
4. **Encoding:** We shift the time argument $t$ inside the function: $w(t - \delta)$.

This structure allows UWB to carry data without a carrier frequency, relying entirely on the precise **temporal location** of the electromagnetic transient.
