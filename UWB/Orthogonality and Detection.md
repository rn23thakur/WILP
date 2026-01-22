This page answers - Why should the signal be orthogonal or have negative correlation for successful detection?
### What is "Correlation" in Signals?

In statistics, correlation measures how strongly two variables vary together. In signals, it measures **Similarity**.

Mathematically, it is a **Dot Product** (just like vectors).
- **Vectors:** $\vec{A} \cdot \vec{B} = a_1b_1 + a_2b_2 + \dots$
- **Signals:** $\text{Corr} = \int \text{Signal}_1(t) \cdot \text{Signal}_2(t) \, dt$

Think of the integral as just a sum of infinite points. You multiply the two signals point-by-point and add up the result.

- **Positive Result:** The signals are **similar** (Positive x Positive).
- **Zero Result:** The signals are **orthogonal** (unrelated).
- **Negative Result:** The signals are **opposites** (Positive x Negative).

### The Math that follows

The receiver calculates a single number, let's call it **$z$** (the decision statistic).
Every time a pulse arrives, the hardware performs this exact integral:
$$z = \int_{0}^{T_f} r(t) \cdot v(t) \, dt$$
Where:
- $r(t)$ is the noisy signal coming from the antenna.
- $v(t)$ is the **Template** generated locally by the receiver. (_think Cicada attack_ - Solution is a [[Scrambled Timestamp Sequence]])

The result **$z$** is just a scalar (a number like 5.2 or -3.1).
How does it decide between "0" and "1"? It compares $z$ to a **Threshold** (usually 0).
- If $z > 0 \rightarrow$ Decide "Bit 0"    
- If $z < 0 \rightarrow$ Decide "Bit 1"

### Why Negative Correlation is King (The Math of Distance)

This is about **maximizing the gap** between the two possible values of $z$. We want to make it as hard as possible for Noise ($n$) to push the result across the threshold.

Let's look at the three scenarios mathematically.

Assume the signal energy is $E = \int w^2(t) dt$.
#### Scenario A: Positive Correlation (Bad)

Imagine the pulse for "1" is very close to "0" (small shift).
- **If "0" is sent:** $z = E$ (Perfect match).
- **If "1" is sent:** $z \approx 0.8E$ (Still matches the "0" template quite well).
    
- **The Gap:** $E - 0.8E = \mathbf{0.2E}$.
    - _Risk:_ If the noise is just $-0.1E$, you might mistake a "0" for a "1". The system is very fragile.

#### Scenario B: Orthogonality (Good)

We shift the pulse so "0" and "1" don't overlap at all.
- **If "0" is sent:** $z = E$.
- **If "1" is sent:** $z = 0$ (The template for "0" sees nothing).
- **The Gap:** $E - 0 = \mathbf{E}$.
    - _Benefit:_ The gap is 5x bigger than Scenario A. It takes much more noise to confuse the receiver.

#### Scenario C: Negative Correlation (Perfect)

We shift the pulse specifically so the peak of "1" aligns with the _negative_ dip of the "0" template.
- **If "0" is sent:** $z = E$.
- **If "1" is sent:** $z = -E$ (The signal is the mathematical inverse of the template).
- **The Gap:** $E - (-E) = \mathbf{2E}$.
    - _Benefit:_ The gap is **2x bigger than Orthogonality**.

**Conclusion:** By using Negative Correlation (Antipodal signaling), you effectively **double the [[Signal Strength]] without actually increasing the transmit power. You get "free" noise immunity just by being clever with the timing $\delta$.

### Does it "check" on all pulses?

You asked: _"Does it do this orthogonality check on all pulses?"_
**Yes.** But usually, we sum them up first.
In UWB, we often send **$N$ pulses** to represent a single **1 Bit** (this is called Processing Gain).

1. **Pulse 1 arrives:** Calculate $z_1$.
2. **Pulse 2 arrives:** Calculate $z_2$.
3. ...
4. **Pulse N arrives:** Calculate $z_N$.

Final Decision:
$$Z_{total} = \sum_{i=1}^{N} z_i$$

- If $Z_{total} > 0$, the bit is 0.

Why sum them?
Because noise is random. Sometimes noise adds $+0.5$, sometimes $-0.5$. Over 100 pulses, the noise averages out to zero (cancels itself out), but the signal $z$ adds up (constructive interference). This allows UWB to work even when the signal is weaker than the noise floor!