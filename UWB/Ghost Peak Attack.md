This "Backtracking" algorithm introduces a specific vulnerability.

The Attack:

An attacker injects a tiny, artificial signal (a "Ghost") just nanoseconds before the real signal arrives.

**The Exploit:**

1. The receiver finds the strong Real Peak.
    
2. It starts backtracking to find the leading edge.
    
3. Instead of stopping at the true start of the signal, the algorithm sees the attacker's "Ghost" signal.
    
4. Because the Ghost is close enough, the algorithm assumes it is part of the same pulse (just a "slow rise").
    
5. **Result:** The receiver timestamps the Ghost.
    
    - $t_{arrival}$ becomes _earlier_.
        
    - Time of Flight decreases.
        
    - **Distance is reduced.** (The car thinks the key is closer than it is).