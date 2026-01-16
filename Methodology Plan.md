This methodology follows a standard **Experimental Computer Science** approach: **Design $\rightarrow$ Implement $\rightarrow$ Emulate $\rightarrow$ Measure.**

---

### **Phase 1: System Design & Implementation (The "Build")**

**Goal:** Build two distinct prototypes to compare side-by-side.

- **Step 1: The Control Group (Standard PQC-QUIC)**
    - **Objective:** Set up a standard QUIC connection that uses Post-Quantum keys without any extra coding.
    - **Tools:** Use **liboqs** (Open Quantum Safe) combined with a QUIC library (e.g., `quic-go` or `MsQuic`).
    - **Configuration:** Configure the handshake to use **Kyber-1024 (ML-KEM-1024)**. This ensures the payload is large enough (~3KB+) to trigger fragmentation and amplification limits.

- **Step 2: The Experimental Group (NC-PQC Shim)**
    - **Objective:** Build the "Shim" that sits between the Application and the UDP socket.        
    - **Tools:** **Steinwurf Kodo** (C++ or Python bindings).
    - **Logic (The Shim):**
        1. Intercept the PQC Key blob.
        2. **Encode:** Split into $N$ symbols (chunks). Generate $K$ redundancy symbols (e.g., 20% overhead).
        3. **Packetize:** Wrap each symbol in a UDP packet with a small header (Symbol ID).
        4. **Send:** Blast them over the network.
        5. **Decode (Receiver):** Listen for packets. Once $N$ valid symbols arrive, reconstruct the Key.

---

### **Phase 2: Experimental Setup (The "Lab")**

**Goal:** Create a reproducible, fake "bad network" inside your computer.

- **Topology:** Two Docker containers (or VMs) connected via a virtual bridge.
    - **Container A:** Client (Sender).
    - **Container B:** Server (Receiver).
    - **The Bridge:** The Linux Kernel.

- **The Chaos Generator (Linux `tc`):**    
    - You will use Linux Traffic Control (`tc`) with `netem` (Network Emulator) to corrupt the link between the containers.
    - **The Command:**
        
```bash
# Example: Add 100ms delay and 5% packet loss
tc qdisc add dev eth0 root netem delay 100ms loss 5%
```
        
	- **Why:** This allows you to mathematically control the "garbage" level of the network.
        

---

### **Phase 3: The Scenarios (What you will test)**

**Goal:** Define the independent variables (the knobs you turn).

You need to run both **Group A (Standard)** and **Group B (NC Shim)** through these gauntlets:

1. **Baseline (Perfect Network):** 0% Loss, 20ms Latency. (Sanity check).
    
2. **The "Satellite" Scenario:** 1% - 5% Loss, 600ms RTT (High Latency).
    
3. **The "Congested WiFi" Scenario:** 5% - 20% Loss, 50ms RTT (Burst loss).
    
4. **The "Cliff Edge" Test:** Increase loss by 1% steps until the connection fails entirely (find the breaking point).
    

---

### **Phase 4: Data Collection (What you measure)**

**Goal:** Gather the metrics that prove your hypothesis.

**1. Handshake Completion Time (The "King" Metric)**

- **Definition:** Time from sending the first `ClientHello` to receiving the final `HandshakeFinished`.
    
- **Why:** This proves that even if you send _more_ data, you finish _faster_ because you don't wait for retransmissions.
    

**2. Handshake Success Rate (Reliability)**

- **Definition:** Percentage of attempts that successfully complete within a timeout (e.g., 10 seconds).
    
- **Why:** Proves the "Robustness." Standard QUIC might fail 30/100 times at 5% loss. Your Shim should fail 0/100 times.
    

**3. Bandwidth Overhead (The Cost)**

- **Definition:** Total bytes transmitted on the wire (including redundancy) vs. size of the original Key.
    
- **Why:** You must be honest about the cost. "We used 20% more bandwidth to gain 300% speed."
    

**4. CPU Usage (Optional but nice)**

- **Definition:** CPU cycles used during encoding/decoding.
    
- **Why:** To address the concern that "Math is hard." Show that it's negligible compared to the PQC math itself.
    

---

### **Phase 5: Evaluation & Analysis (The "End")**

**Goal:** Visualize the findings for the defense.

- **Plot 1: The "Cross-Over" Graph**
    
    - X-Axis: Packet Loss (0% to 20%).
        
    - Y-Axis: Handshake Time (ms).
        
    - _Expectation:_ Standard QUIC curve goes exponential (vertical) at 5%. NC-QUIC curve stays flat/linear.
        
- **Plot 2: The Reliability Bar Chart**
    
    - Comparison of "Failed Connections" at 10% loss.
        
    - _Expectation:_ Standard QUIC = 40% failure. NC-QUIC = 0% failure.
        

---

### **Summary: The "Start to End" Checklist**

1. **Start:** Get a simple Python script to send a "Hello World" UDP packet between two Docker containers.
    
2. **Step 2:** Break the link with `tc` (`loss 10%`) and see the packet die.
    
3. **Step 3:** Implement Kodo. Send "Hello World" again with redundancy. Watch it survive the 10% loss.
    
4. **Step 4:** Swap "Hello World" for a real 5KB Kyber Key.
    
5. **Step 5:** Automate the test to run 100 times and log the time.
    
6. **End:** Generate the "Cross-Over" Graph in Matplotlib.