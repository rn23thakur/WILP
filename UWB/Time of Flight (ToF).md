We have established how the receiver decides _if_ a bit is a 1 or a 0 (by checking if $z > 0$). Now, to calculate distance, we need to know exactly **when** that bit arrived. Read [[Orthogonality and Detection]]

#### [[The Sliding Correlator]]
The receiver doesn't know the arrival time in advance. It effectively "slides" the template $v(t)$ across time, performing the correlation integral continuously.

This produces a graph over time called the **Channel Impulse Response (CIR)**.
- **X-axis:** Time (Delay).
- **Y-axis:** Correlation Strength ($z$).

We are looking for the exact instant where the Correlation $z$ is Maximized.
$$t_{arrival} = \arg \max_t \left( \int r(\tau) \cdot v(\tau - t) \, d\tau \right)$$

Once we identify the arrival times, we use **Two-Way Ranging (TWR)** to remove the need for synchronized clocks.
#### Two-Way Ranging (TWR)
- **Device A (The Initiator):** Has a stopwatch. Starts the conversation.
- **Device B (The Responder):** Has its own stopwatch. Responds to A.
They want to know the distance between them, but their watches aren't synchronized (Device A might say it's 12:00:00 while Device B says it's 12:05:00). To solve this, they measure the **Round Trip Time**.
##### **1: The Poll (A $\to$ B)**
1. **A Sends:** Device A sends a signal (a "ping") to Device B.
    - A records exactly when it left: **$t_1$**.
2. **B Receives:** Device B hears the signal.
    - _Here is where the Correlation Math comes in!_ Device B runs the correlation formula on its received data to find the exact peak.
    - It records this arrival instant as: **$t_{RX}$**.

#### **2: The Reply (B $\to$ A)**
3. **B Processes:** Device B takes a moment to prepare a reply. It waits a short duration.
4. **B Sends:** Device B sends a response signal back to A.
    - It records exactly when it leaves: **$t_{TX}$**.
    - _(Note: The time B spent holding the signal is $t_{reply} = t_{TX} - t_{RX}$)_.
5. **A Receives:** Device A hears the response.
    - _Math time again!_ Device A runs the correlation formula to find the exact peak of the returning signal.
    - A records this arrival instant as: **$t_2$**.

Using the timestamps from the exchange:
$$d = c \times \left( \frac{(t_2 - t_1) - t_{reply}}{2} \right)$$
- **$t_1$:** Device A sends the poll (Local Clock A).
- **$t_2$:** Device A receives the response (Local Clock A).
- **$t_{reply}$:** The processing time taken by Device B (Calculated as $t_{TX} - t_{RX}$ on Device B).
- **$c$:** Speed of Light.
### The Real World Problem: Multipath and Reflections

In a perfect vacuum, the CIR graph has one single sharp peak. In the real world, the signal bounces off walls, the ground, and metal objects. The receiver sees **multiple peaks**.

**Crucial Physics:**
1. **Reflections travel longer:** They always arrive _later_ than the direct line-of-sight (LoS).
2. **Reflections can be stronger:** If the direct line-of-sight is blocked (e.g., by a body), a reflection off a metal wall might be much "louder" (higher peak) than the true signal.

**The Trap:** If we simply timestamp the **Maximum Peak** (the loudest signal), we might be measuring the distance to the wall, not the car. This adds meters of error.

### The Solution: [[Leading Edge Detection (LDE)]]

To find the true distance, we must find the **First Path**, even if it is weak.

**The Algorithm:**

1. **Find the Main Peak:** Scan the buffer for the absolute highest correlation value ($Index_{max}$).
2. **Calculate Noise Floor:** Measure the average noise level ($\sigma$) in the "quiet" air before the signal.
3. **Backtrack:** Start at $Index_{max}$ and walk **backwards** in time.
4. **Stop at the Edge:** The moment the signal drops close to the Noise Floor (e.g., $3\sigma$), stop.

That specific point is the **Leading Edge**. We timestamp _this_ moment, not the peak.

### Security Vulnerability: The [[Ghost Peak Attack]]

