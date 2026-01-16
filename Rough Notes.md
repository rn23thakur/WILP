Let’s break down exactly why your thesis is still safe and how to differentiate it.

### 1. The "HUNCC" Paper vs. Your Thesis

**What they did:** HUNCC (Hybrid Universal Network-Coding Cryptosystems) is a theoretical framework. It combines "Information Theoretic Security" (perfect math secrecy) with PQC.

- **Their Goal:** "Can we use Network Coding to make the _encryption itself_ stronger?"
    
- **Your Goal:** "Can we use Network Coding just to **stop the packet loss** so the handshake doesn't crash?"
    

**The Difference:**

- **They are mixing the chemicals:** They are trying to merge Crypto and Coding into one mathematical soup. This is PhD-level math.
    
- **You are building the truck:** You are taking standard, unmodified NIST PQC (Kyber) and building a "Network Coding Truck" (Kodo shim) to transport it safely.
    
- **The Gap:** No one needs to "verify" your security because you aren't touching the math. You are solving the **usability** problem, which engineers care about more.
    

### 2. The "PQC over 5G" Research

**What they did:** These papers (like the 5G Core studies) often run simulations inside a "Core Network" (perfect fiber optics between cell towers) or focus on the radio layer (Layer 1/2).

- **Their Context:** "How does the 5G base station talk to the 5G Core?" (Telco infrastructure).
    
- **Your Context:** "How does a Raspberry Pi (IoT) talk to a Cloud Server over the messy public Internet?" (End-to-End UDP).
    

**The Difference:**

- 5G papers assume the "network" handles the reliability (HARQ layers in 5G).
    
- Your thesis assumes the "network" is garbage (Public UDP), requiring the **Application Layer** to fix it.
    

### 3. McEliece vs. Network Coding

**What you found:** "McEliece is mathematically similar to Network Coding."

- **The Reality:** Yes, both use matrices. But McEliece is an _algorithm_ for keys. Network Coding is a _technique_ for transport.
    
- **Your Angle:** You don't care about the math similarity. You care that McEliece keys are **massive** (1MB+). They represent the _extreme case_ of the fragmentation problem you are solving.