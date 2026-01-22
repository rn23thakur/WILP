**Subject:** Feasibility of Network Coding for Post-Quantum Handshakes **Status:** In Progress / Hypothesis Validation **Author:** Aryan Thakur

Initial Thought: Looking for alternatives to Bolina (proprietary) to perform Post-Quantum Cryptography (PQC) operations.

Discovery: Bolina is closed source. We need an open-source alternative for a thesis.

The Pivot: Instead of finding a "Bolina Clone," the goal shifted to building a Shim Layer using open-source libraries to inject reliability into standard PQC.

- **Selected Tool:** **Kodo** (by Steinwurf). (might have to find alternatives)
    - _Why:_ C++ based, gold standard for RLNC (Random Linear Network Coding), academic license available.
        
- **Selected Architecture:**
    - Sender: `PQC Key` $\rightarrow$ `Kodo Encoder` $\rightarrow$ `UDP Packets`
    - Receiver: `UDP Packets` $\rightarrow$ `Kodo Decoder` $\rightarrow$ `PQC Key`

- **Thesis Statement:** "Enhancing Post-Quantum Handshake Reliability in Lossy Networks using Application-Layer Random Linear Network Coding."

Hypothesis: Standard QUIC breaks when sending large PQC keys over lossy networks.

Evidence Gathered:
1. **Software QUIC Fragility:** Software implementations (MsQuic) show catastrophic throughput collapse at **1-2% packet loss** (Design Gateway, 2025).
2. **The Amplification Deadlock:** RFC 9000 limits servers to sending 3x the data received. A Kyber-1024 key ($>3$KB) often hits this limit. If a packet is lost while paused by this limit, the handshake deadlocks (AWS / S. Kampanakis).
3. **Middlebox Drops:** Firewalls (Cisco Firepower) are seen dropping fragmented UDP packets that look "anomalous" (Google Chrome Kyber experiments).

**Conclusion:** The problem is real. It is not just about speed; it is about **connection failure**.

> "We will be sending _more_ packets to solve the problem of _already large_ packets. This won't fit well with existing infra either."

The Resolution (The Logic for the Thesis):

This is a trade-off optimization problem: Bandwidth vs. Latency.

1. The "Goodput" Argument

In a lossy channel (e.g., $p=5\%$), standard ARQ (Automatic Repeat Request) throughput collapses because the sender stops to wait for ACKs.

- _Equation:_ Throughput $\approx \frac{MSS}{RTT \sqrt{p}}$ (Mathis Equation). As $p$ goes up, throughput crashes.
- _RLNC Approach:_ We add redundancy factor $k$. We consume bandwidth, but we maintain the flow. We prevent the $RTT$ penalty.

**2. The "Infra" Defense**

- **Source Coding:** We are performing coding at the _End Hosts_ (Application Layer).
- **Transparency:** To the "Existing Infra" (Routers/Switches), our coded packets look exactly like standard UDP traffic. We do not require router upgrades (unlike Multicast or Network-layer NC).
- **MTU Compliance:** By chopping the PQC key into Kodo symbols ourselves, we can ensure every UDP packet is strictly smaller than the MTU (1500 bytes), actually _helping_ packets pass through rigid firewalls that hate IP fragmentation.

Final Thesis Stance:

We accept a Bandwidth Penalty (sending 120% data) to achieve Handshake Reliability (preventing the 1000ms+ delay of retransmission loops). *Not empirical numbers, only for emphasis sake*