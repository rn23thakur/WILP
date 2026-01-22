### What is Signal Strength?

In strict technical terms, **Signal Strength** usually refers to **Power**.

- **Amplitude ($V$):** The "height" or voltage of the wave (e.g., 5 Volts).
- **Power ($P$):** The energy used over time. In physics, power is proportional to the square of the voltage ($P \propto V^2$).

However, in the context of Digital Signaling (1s and 0s), "strength" is often discussed as **Signal-to-Noise Ratio (SNR)**. This isn't just about how loud you shout (power); it's about how much louder you are _compared to the background noise_.

### The "Gap" = Noise Immunity

In digital communications, the "Gap" is formally called the Euclidean Distance ($d$).

Think of the "Gap" as a Safety Margin. The receiver has to decide: "Was that a 1 or a 0?"
- It usually sets a threshold right in the middle.
- Noise is like a random jitter that pushes the received signal toward the wrong side of the threshold.
- **The wider the gap, the harder the noise has to "push" to cause an error.**
### Why Antipodal is "Double" the Strength (The Math of the Gap)

Let's look at why Antipodal is a "cheat code" compared to standard Unipolar signaling (On-Off Keying).
Imagine you have a battery budget (Average Power) of **1 Watt**.
#### Scenario A: Unipolar (0 and 1)

To average 1 Watt, you send:
- **0:** 0 Volts (0 Watts)
- **1:** $\approx$ 1.41 Volts (2 Watts)
- _Average Power:_ $(0 + 2) / 2 = 1$ Watt.
- **The Gap:** The distance between 0V and 1.41V is **1.41 units**.
#### Scenario B: Antipodal (-1 and +1)

To average 1 Watt, you send:
- **0:** -1 Volt (1 Watt)
- **1:** +1 Volt (1 Watt)
- _Average Power:_ $(1 + 1) / 2 = 1$ Watt.
- **The Gap:** The distance from -1V to +1V is **2.0 units**.

The Comparison:

By simply changing how you use your voltage (swinging positive and negative instead of just positive), you increased the "Gap" from 1.41 to 2.0.
If you square that Gap to see the "Energy Distance":

- Unipolar Energy Gap $\approx 1.41^2 = 2$
- Antipodal Energy Gap $= 2.0^2 = 4$

**Result:** The Antipodal gap has **2x the energy distance** (4 vs 2) compared to the Unipolar gap, even though both use the same 1 Watt of battery power.

### Summary: Is it Immune?

**Yes.**

- **"Doubling the signal strength"** here means that for the _same_ transmit power, your signal behaves as if it is twice as powerful against noise.
- **"Free Noise Immunity":** You effectively force the noise to be **twice as strong** (in terms of power) to cause the same amount of errors as before.