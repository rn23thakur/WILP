Have a look at the OSI Model here [[Networking Basics]].

## Layer 0 (Pre-network, but unavoidable): URL Interpretation & Intent

This is not an OSI layer, but nothing works without it.
### What the browser does immediately
1. Parses the URL:
    - **Scheme**: `https`
    - **Host**: `example.com`
    - **Port**: default `443` (because HTTPS)
    - **Path/query**: `/` (if none specified)
2. Critical decision:
    - `https` ⇒ **TLS is mandatory**
    - Browser knows it must establish a **secure transport** before any HTTP data is sent
3. Browser checks internal caches:
    - DNS cache?
    - Existing TLS session?
    - HTTP/2 or HTTP/3 capability
No packets are sent yet.
### Key takeaway at this stage
- HTTPS is **not HTTP + encryption**
- HTTPS is **HTTP over TLS over TCP (or QUIC)**
- The browser already knows encryption is non-negotiable

Nothing security-sensitive has happened yet — this is pure setup.

## Layer 1: DNS Resolution (Name → IP)

This is the **first point where packets leave your machine**.
### The problem DNS solves
- Humans use names: `example.com`
- Networks route packets using **IP addresses**
- TLS **cannot begin** until we know the server’s IP

So the browser must answer:

> “What IP address corresponds to `example.com`?”
---
### What the browser actually does (ordered, precise)

1. **Browser cache**
    - Have I resolved `example.com` recently?
    - If yes and TTL not expired → use it
2. **OS resolver cache**
    - Shared across applications
3. **Configured DNS resolver**
    - Usually your ISP, router, or a public resolver (8.8.8.8, 1.1.1.1)

If none of the above have it:
- A **DNS query packet** is sent
---
### How DNS queries travel (simplified)

- Traditionally: **UDP port 53**
- Increasingly:
    - **DoH** (DNS over HTTPS)
    - **DoT** (DNS over TLS)

Important distinction:
- **Classic DNS** → plaintext
- **DoH/DoT** → encrypted

But note:

> DNS security is _separate_ from TLS to the website.
---
### What comes back

The resolver responds with:
- One or more **IP addresses** (A / AAAA records)
- A **TTL** (how long this answer is valid)

Example:
`example.com → 93.184.216.34`

The browser now knows **where** to connect.

---
### Subtle but important security reality

Even with HTTPS:
- DNS can leak:
    - Which domain you are visiting
- Unless:
    - You use DoH/DoT
    - Or the browser has DNS encryption enabled

TLS **does not protect DNS** by default.

---
### Key takeaway at this layer

- DNS is about **location**, not security
- TLS has not started yet
- DNS can be a privacy weak point
- Without DNS, nothing else can proceed

**Incognito / private browsing does _not_ prevent DNS leakage.**  
~95% confidence for typical configurations.

Your ISP, network operator, or whoever controls your DNS resolver can still infer **which domains you are visiting**, even though they cannot see _what_ you are doing on those sites.

---
## Why incognito does not help here

### What incognito actually does

Incognito / private mode:
- Does **not** save:
    - History
    - Cookies
    - Cached files (after session ends)
- Does **not**:
    - Change DNS behavior
    - Encrypt traffic beyond normal HTTPS
    - Hide you from ISPs, routers, employers, or governments

Incognito is about **local privacy**, not **network privacy**.

---
## What exactly leaks via DNS

With classic DNS:
- The resolver sees:
    - `example.com`
    - Timestamp        
    - Your IP address
- It does **not** see:
    - URL paths (`/login`)
    - Query params
    - Page content

So:

> “User at IP X looked up reddit.com at 14:32”

This is already quite revealing.

---
## What about HTTPS — doesn’t TLS hide this?

TLS protects:
- HTTP headers
- Request bodies
- Cookies
- Responses

TLS does **not** protect:
- DNS (unless DoH/DoT is used)
- Destination IP
- Often the **SNI** (Server Name Indication)

Even worse:
- Traditional TLS sends SNI **in plaintext**

So observers may learn the domain _twice_:
1. Via DNS
2. Via SNI during TLS handshake

---
## Modern mitigations (partial, not perfect)

### 1. DNS over HTTPS (DoH)

- DNS queries are sent inside HTTPS    
- Your ISP cannot see the domain
- But the DoH provider **can**

This shifts trust, it does not eliminate it.

### 2. Encrypted Client Hello (ECH)

- Encrypts SNI
- Still rolling out
- Requires:
    - Browser support
    - Server support
    - Correct DNS records

Adoption is growing but incomplete.


## Layer 2: TCP Connection Establishment (3-Way Handshake)

At this point:
- We have an **IP address** from DNS
- We know we must talk to **port 443**
- We are about to create a **reliable byte stream** (it refers to a byte stream in which the bytes which emerge from the communication channel at the recipient are exactly the same, and in exactly the same order, as they were when the sender inserted them into the channel.)

TLS **cannot start** until TCP exists.

## What problem TCP solves (brief, precise)

IP gives you:
- Best-effort packet delivery
- No ordering
- No retransmissions
- No notion of a “connection”

	While an **IP address** is the identifier (the "house address"), the **Internet Protocol (IP)** is the service (the "postal system") that uses those addresses. 
	
	The "Best-Effort" delivery model exists specifically because IP is designed to be as simple as possible so it can run over any physical network (fiber, copper, satellite, or even carrier pigeons).
	- **Encapsulation:** It wraps your data into a "packet" (or datagram) that includes a header with the destination IP address.
	- **Independent Routing:** Each packet is treated as a completely separate entity. Routers look at the destination address on each individual packet and forward it toward the next hop.
	- **Simple Discarding:** If a router becomes congested or a packet is corrupted, the router simply **drops** the packet. It does not try to fix it, ask for a resend, or even notify the sender in many cases.
	- **No State:** Because IP is "connectionless," it doesn't remember previous packets. If packet A and packet B are part of the same email, IP doesn't know that; it just sees two separate boxes moving to the same address.

TCP adds:
- Reliability
- Ordering
- Congestion control
- A bidirectional stream abstraction

TLS assumes all of this.

## The 3-way handshake (exactly what happens)

### 1. SYN (client → server)

- **What it is:** **SYN** is a "control flag" (a single bit) in the TCP header.
- **What it does:** It tells the receiver: "I want to start a connection and synchronize our starting points". It is only used during the handshake to establish the **Initial Sequence Number (ISN)**
- “I want to talk”    
- Includes:
    - Client initial sequence number
    - TCP options (MSS, window scaling, SACK, etc.)

### 2. SYN-ACK (server → client)

- “I heard you and I’m willing”
- Includes:
    - Server initial sequence number
    - Acknowledges client’s SYN

### 3. ACK (client → server)

- “Connection established”

At this point:
- Both sides agree on:
    - Sequence numbers
    - Flow control parameters
- A TCP connection **exists**

Still:
- Everything so far is **plaintext**
- An observer can see:
    - Source IP
    - Destination IP
    - Port 443
    - Timing and packet sizes

### Stuff I don't understand yet :<
**Sequence Number & ISN**
- **Sequence Number:** A 32-bit counter that tracks every **byte** sent in a stream. If you send 1,000 bytes, the sequence number increases by 1,000. It allows the receiver to reassemble data in the correct order even if packets arrive out of sequence.
- **Initial Sequence Number (ISN):** A random starting number (0 to 4.2 billion) generated by each side's operating system.
    - **Why random?** If it started at 0 every time, an attacker could guess the next number and "inject" malicious data into your session (session hijacking)

**MSS (Maximum Segment Size)** 
- **What it is:** The largest amount of actual **data** (payload) a device can accept in a single packet, excluding the TCP and IP headers.
- **Calculation:** Typically, MSS = MTU - 40 bytes (20 for IP header + 20 for TCP header)
- **Standard Value:** On most Ethernet networks, the Maximum Transmission Unit (MTU) is 1,500 bytes, so the standard **MSS is 1,460 bytes**

**Window Scaling** 
- **The Problem:** The original TCP header only has 16 bits for the "Window Size," meaning it can only signal a buffer of up to 65,535 bytes (64 KB). On modern high-speed fiber or satellite links, this is too small—the sender would spend most of its time waiting for ACKs before it could send more data.
- **The Solution:** Window Scaling is a "multiplier" negotiated in the handshake. It allows the 64 KB window to be scaled up (up to 2 ^14 times) to a maximum of ~1 GB.

**SACK (Selective Acknowledgment)**
- **Traditional ACK:** In standard TCP, if you lose packet #3 but receive #4 and #5, you can only acknowledge up to #2. The sender must then re-send #3, #4, and #5, even though you already have #4 and #5.
- **SACK:** This option allows the receiver to say: "I'm still missing #3, but I successfully received #4 and #5". The sender then **only** retransmits #3, saving bandwidth and time. 

**Flow Control Parameters**
- **What they are:** Mechanisms that prevent a fast sender from overwhelming a slow receiver.
- **Receive Window (RWND):** The most important parameter, advertised by the receiver to say: "I currently have X bytes of empty space in my buffer. Do not send more than that".
- **Dynamic Nature:** Unlike MSS (which is set at the start), the Window Size changes constantly during the session as the application reads data out of the buffer.

## Important clarification (common confusion)

**TCP does NOT know or care about TLS.**
From TCP’s perspective:
- TLS handshake bytes are just data
- HTTP bytes are just data
- Encrypted or not — irrelevant

TCP is blind to meaning.

---
## Performance note (why this matters)

This handshake costs:
- **1 RTT** (round-trip time)

Modern optimizations:
- TCP Fast Open (limited use)    
- TLS 1.3 reduces _additional_ RTTs later

But TCP itself still has this base cost.

---

## State after this layer

We now have:
- A reliable, ordered pipe
- No identity verification
- No encryption
- No secrecy

Think of it as:

> “A private phone line with no privacy guarantees.”

---
## Key takeaway at this layer

- TCP creates **connectivity**, not **security**
- TLS will now ride _on top_ of this connection
    
- Anyone watching can still see metadata