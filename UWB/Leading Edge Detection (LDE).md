**Leading Edge Detection (LDE)** doesn't care if the bit is a `0` or a `1`. It only cares: **"When did the energy arrive?"**

A strong negative peak is just as much of a "signal" as a strong positive peak. They both mean the pulse has arrived.

So, before we run the LDE algorithm, we perform a transformation. We usually calculate the **Envelope** or simply the **Absolute Value**:

$$Signal_{LDE}[t] = | Correlation[t] |$$

- If the raw correlation is $+0.9$, the LDE sees **$0.9$**.
- If the raw correlation is $-0.9$, the LDE sees **$0.9$**.

Now, everything is positive (0 to Max), and the "Threshold" logic I described earlier works perfectly. We are looking for the _presence_ of energy, regardless of its polarity.

### 1. The Concept: Why Leading Edge?

In Time-of-Flight (ToF) systems (like Lidar, Radar, or Ultra-Wideband), the signal often bounces off multiple objects before returning. This creates "Multipath" interference.

- **The Peak:** Often represents the strongest reflection (e.g., a retro-reflector or a large wall), but not necessarily the _shortest_ path.
- **The Leading Edge:** Represents the **First Path**—the very first photons or radio waves to hit the target and return. This is the "True Distance."

### 2. The Math: Thresholding & Z-Scores

The core of this algorithm relies on distinguishing "Signal" from "Noise" using statistics.

A. The Noise Floor

We assume the "quiet air" (buffer before the pulse) follows a Normal (Gaussian) distribution:

$$Noise \sim \mathcal{N}(\mu, \sigma^2)$$

- $\mu$ (Mu): The average background noise level.
- $\sigma$ (Sigma): The standard deviation (how much the noise jitters).

B. The Threshold

To find where the signal effectively disappears into the noise, we calculate a dynamic threshold ($T$). We use a "Sigma factor" (usually denoted as $k$):

$$T_{edge} = \mu + k \cdot \sigma$$

- If $k=3$, we are setting the threshold at $3\sigma$. Statistically, 99.7% of pure noise falls below this line. Therefore, if we cross this line while backtracking, we are almost certainly looking at the signal, not noise.

C. The Edge Logic

Given a signal array $S[t]$ and the peak index $t_{peak}$:

$$t_{LE} = \max \{ t \mid t < t_{peak} \land S[t] \le T_{edge} \}$$
- **The Set:** $\{ t \mid t < t_{peak} \land S[t] \le T_{edge} \}$
    - Find all time points ($t$) that are _before_ the peak ($t < t_{peak}$)...
    - ...AND where the signal ($S[t]$) is _below or equal_ to the noise floor ($S[t] \le T_{edge}$).
- **The Operation:** $\max \{ ... \}$
    - From that collection of time points, pick the **largest** one (the latest time).

In plain English: The Leading Edge ($t_{LE}$) is the latest time point _before_ the peak where the signal amplitude drops down to the threshold.

Notes - 
**The Correlation Score ($S[t]$):** This is your **Signal**. It is the "Y-axis" value in your graph. If you ran a matched filter (correlation), $S[t]$ is the result of that correlation at every time step.
**$T_{edge}$ (Threshold):** This is a **Ruler**. It is a constant, horizontal line that we calculate based on the noise.