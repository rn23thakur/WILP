Radio waves follow the **Inverse-Square Law**. Imagine a lightbulb; as you move away, the light spreads out over the surface of a sphere.

In a perfect vacuum (Free Space), the received power ($P_r$) is inversely proportional to the square of the distance ($d$):
$$P_r \propto \frac{1}{d^2}$$
However, in the real world (inside a building or a city), signals don't just spread out; they reflect, diffract, and pass through walls. To account for this, we generalize the exponent from $2$ to a variable path loss exponent, $n$.$$P_r \propto \frac{1}{d^n}$$
We cannot measure absolute "power" easily without a reference point. Therefore, we compare the power at a specific distance ($d$) to the power at a known reference distance ($d_0$). Usually, we choose **$d_0 = 1$ meter**.

The ratio of power at distance $d$ versus distance $d_0$ is:

$$\frac{P_r(d)}{P_r(d_0)} = \left( \frac{d_0}{d} \right)^n$$

- $P_r(d)$: Received Power at distance $d$ (in Watts)
- $P_r(d_0)$: Received Power at reference distance $d_0$ (in Watts)

In engineering, RSSI is measured in **dBm** (decibel-milliwatts), which is a logarithmic unit. To convert the linear equation above into the logarithmic formula you want, we take the standard definition of decibels: $10 \log_{10}$.

We take the base-10 logarithm of both sides and multiply by 10:

$$10 \log_{10}\left( \frac{P_r(d)}{P_r(d_0)} \right) = 10 \log_{10}\left( \left( \frac{d_0}{d} \right)^n \right)$$

### 4. Simplifying Using Logarithm Rules

Now we use three rules of logarithms to simplify the equation:

1. **Division Rule:** $\log(a/b) = \log(a) - \log(b)$
2. **Exponent Rule:** $\log(x^y) = y \log(x)$
3. **Inversion Rule:** $\log(1/d) = -\log(d)$

Left Side:

Using the division rule, we split the ratio:
$$10 \log_{10}(P_r(d)) - 10 \log_{10}(P_r(d_0))$$

Note: $10 \log_{10}(\text{Power in Watts})$ is literally the definition of RSSI in dBm.
So, let's rename them:

$$\text{RSSI}(d) - \text{RSSI}(d_0)$$

Right Side:

Using the exponent rule, bring the $n$ to the front:

$$10n \log_{10}\left( \frac{d_0}{d} \right)$$

Now, assume our reference distance $d_0 = 1$ meter. The fraction becomes $1/d$.

$$10n \log_{10}\left( \frac{1}{d} \right)$$

Using the inversion rule ($\log(1/x) = -\log(x)$):

$$-10n \log_{10}(d)$$
Now we equate the Left Side and the Right Side:

$$\text{RSSI}(d) - \text{RSSI}(d_0) = -10n \log_{10}(d)$$

We want to solve for $\text{RSSI}(d)$ (the current signal strength). We move $\text{RSSI}(d_0)$ to the other side:

$$\text{RSSI}(d) = -10n \log_{10}(d) + \text{RSSI}(d_0)$$

If we replace $\text{RSSI}(d_0)$ (the signal strength at 1 meter) with the constant **$A$**, we arrive at your exact formula:

$$\text{RSSI} = -10n \log_{10}(d) + A$$

### Why is this model useful?

Because the relationship is logarithmic, signal strength drops **drastically** in the first few meters and then slows down.

- Doubling distance from 1m to 2m drops the signal by roughly **6 dB**.
- Doubling distance from 10m to 20m also drops it by **6 dB**, even though the physical distance is much larger.

Power is proportional to the square of the Amplitude:
$$P \propto V^2$$
Since we know from the path loss model that Power drops as $\frac{1}{d^n}$, the Amplitude drops as the square root of that:
$$V \propto \sqrt{\frac{1}{d^n}} = \frac{1}{d^{n/2}}$$Bluetooth (which uses GFSK, a type of Frequency Modulation) is a "Constant Envelope" signal. This means that at the **transmitter**, the amplitude (height) of the sine wave does not change over time; it only changes its frequency to send 0s and 1s.

However, once that wave leaves the antenna, the **Inverse-Square Law** takes over.