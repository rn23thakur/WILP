In the real world, the "infinite" correlation integral is replaced by a continuous, moving window operation that only looks at the recent past.

This process is usually called **matched filtering**, and physically, it behaves like a convolution. Here is a breakdown of how the math translates to real-world systems and how that "sliding" actually happens.
### The Math: From Correlation to Convolution
In theoretical textbooks, you see the cross-correlation formula looking for the arrival time $\tau$:
$$R_{rv}(\tau) = \int_{-\infty}^{\infty} r(t) v(t - \tau) \, dt$$
Where:
- $r(t)$ is the received signal (which is "always on").
- $v(t)$ is the template (the pulse shape you expect).
The cross-correlation $R_{rv}(\tau)$ is essentially a function that asks: **"How well do they match if I assume the delay is $\tau$ by shifting v to be at $(\tau)$ instead of zero?**

In a real-time system, we cannot integrate into the future ($+\infty$) because it hasn't happened yet. Instead, we construct a linear filter—called a **Matched Filter**—whose impulse response $h(t)$ is a time-reversed and delayed version of the template $v(t)$.

If your template $v(t)$ has a duration $T$, the filter is:
$$h(t) = v(T - t)$$
When you pass the continuous received signal $r(t)$ through this filter, the output $y(t)$ is the convolution:
$$y(t) = r(t) * h(t) = \int_{0}^{T} r(t - \lambda) h(\lambda) \, d\lambda$$
This output $y(t)$ is mathematically equivalent to the correlation sliding across time. When $y(t)$ hits a peak, it means the template "matched" perfectly with the signal that just entered the filter.

### Analog vs. Digital Implementation

How this integral is performed depends on whether the system is analog or digital.

#### A. Analog (Old School / High Speed RF)
In analog circuitry, you don't calculate sums; physics does it for you.

- **The Filter:** You build a physical circuit (using capacitors, inductors, or SAW devices) that has an impulse response exactly opposite to your pulse.
- **The Result:** You simply feed the continuous voltage $r(t)$ into the input. The output voltage _automatically_ swells to a peak whenever the correct pulse passes through the circuit. There is no CPU calculating "past minus length"; the circuit's energy storage acts as the memory.

#### B. Digital (Modern DSP)
Most modern receivers (WiFi, GPS, 4G/5G) are digital.

1. **Sampling:** The ADC (Analog-to-Digital Converter) turns the voltage into a stream of numbers: $r[n]$.
2. **FIFO Buffer:** The system keeps a First-In-First-Out buffer of the last $N$ samples (where $N$ is the length of the template).
3. Dot Product: At every clock cycle, the processor calculates the dot product of the Buffer and the Template.
$$y[n] = \sum_{k=0}^{N-1} r[n-k] \cdot v[k]$$
4. **Threshold:** If $y[n]$ exceeds a certain threshold, the system declares "Signal Detected!"