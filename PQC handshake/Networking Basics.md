### Host

A **host** is any networked device capable of sending and/or receiving data on a network. Examples include laptops, smartphones, servers, IoT devices, printers, and virtual machines.

Key point: a host is defined by its participation in a network, not by what role it plays.

---

### Client and Server

A **client** is a host that initiates a request. A **server** is a host that listens for requests and sends responses.

Important clarification:

- These are **roles**, not types of machines.
    
- The same physical device can be a client in one interaction and a server in another (e.g., your laptop acting as a web client and later hosting a local web server).
    

---

### IP Address

An **IP address** is a logical identifier assigned to a network interface so that packets can be routed to and from it.

For IPv4:

- Length: **32 bits**
    
- Written as four **octets** (8 bits each) in dotted-decimal notation
    
- Example: `10.24.21.1`
    

Binary representation example (corrected):

- `10.24.21.1`
    
- `00001010.00011000.00010101.00000001`
    

Each octet ranges from **0–255** (2⁸ − 1).

IPv4 address space:

- Total addresses: 2³² ≈ **4.29 billion** (not 255⁴, though the order of magnitude intuition is fine)
    

IPv6:

- Length: **128 bits**
    
- Designed to solve address exhaustion and improve routing and autoconfiguration
    

---

### Network

A **network** is a collection of hosts that can exchange data using a common communication medium and protocol.

Examples:

- Home network (phones, laptops, printers)
    
- Office LAN
    
- Mobile carrier network
    
- The public Internet (a network of networks)
    

Wi‑Fi is **not** a network itself; it is a **wireless access technology** used to connect hosts to a network.

---

### Switch

A **switch** connects multiple hosts within the **same Layer‑2 network** (same broadcast domain).

Key properties:

- Operates primarily at **OSI Layer 2 (Data Link)**
    
- Uses **MAC addresses** to forward Ethernet frames
    
- Does not understand IP routing
    

A switch enables efficient local communication without flooding traffic unnecessarily.

---

### Router

A **router** connects **different IP networks**.

Key properties:

- Operates at **OSI Layer 3 (Network)**
    
- Makes forwarding decisions based on **IP addresses**
    
- Acts as the default gateway for hosts leaving their local network
    

Important correction:

- A router’s IP address is **not set by the manufacturer**.
    
- It is assigned by configuration (static or dynamic) on each interface.
    

---

### Subnet

A **subnet** is a logical subdivision of an IP network.

Purpose:

- Reduce broadcast traffic
    
- Improve security isolation
    
- Simplify management
    

Defined using:

- IP address
    
- Subnet mask / CIDR prefix (e.g., `/24`)
    

Example:

- `192.168.1.0/24` → 256 addresses, 254 usable hosts
    

---

### Private IP Addresses

Private IPs are **non‑routable** on the public Internet and are used for internal networks.

RFC 1918 ranges:

- `10.0.0.0/8`
    
- `172.16.0.0/12`
    
- `192.168.0.0/16`
    

Assigned by:

- DHCP servers (often your router)
    

Private IPs require NAT to communicate with the public Internet.

---

### NAT (Network Address Translation)

**NAT** allows multiple private hosts to share one (or a few) public IP addresses.

What actually happens:

- The router replaces the **source IP and source port** of outgoing packets
    
- Maintains a **translation table** (more precisely, a NAT or connection tracking table)
    
- Uses ports to demultiplex return traffic
    

This is technically **PAT (Port Address Translation)**, which is what most home routers implement.

Security note:

- NAT provides _incidental_ protection, not true security
    
- Stateful firewalls provide the real protection
    

---

## How a Request Actually Travels (High-Level)

1. Application generates data (e.g., HTTP request)
    
2. Data is wrapped layer by layer (encapsulation)
    
3. Packet is sent to default gateway (router)
    
4. Router performs NAT and forwards packet
    
5. Packet traverses multiple routers across the Internet
    
6. Destination server processes request
    
7. Response follows the reverse path
    

This process is formally explained using the **OSI model** and the **TCP/IP model**.

---

## OSI Model – The Journey of a Request

### Layer 7 – Application

- Protocols: HTTP, HTTPS, FTP, SMTP, DNS
    
- Example: Browser creates an HTTP GET request
    

### Layer 6 – Presentation

- Encoding, compression, encryption
    
- Example: TLS encrypts HTTP data
    

### Layer 5 – Session

- Session establishment and teardown
    
- Often merged into Layer 7 in real implementations
    

### Layer 4 – Transport

- Protocols: TCP, UDP
    
- Adds ports, sequencing, reliability
    
- Example: TCP segments the data
    

### Layer 3 – Network

- Protocol: IP
    
- Adds source and destination IP addresses
    
- Routers operate here
    

### Layer 2 – Data Link

- Protocols: Ethernet, Wi‑Fi
    
- Adds MAC addresses
    
- Switches operate here
    

### Layer 1 – Physical

- Bits on the wire: voltages, radio waves, fiber light pulses
    

Encapsulation occurs as data moves **down** the stack; decapsulation occurs as it moves **up** on receipt.

---

### Dumbed down notes for self

#### Definitions 
- `host` is any device that can send and receive traffic (request and response). It could be a smartphone, IOT, tablet, laptop etc. 
- `server`, since a host can be any device by definition it can also be a client or a server (a server is just a computer that is configured to receive and send responses). 
- `ip address`, every host has an IP address to uniquely identify them. So when a client is sending a request to a sever, both hosts' IP address are included. (just like how you would in a letter) 
- `network`, in order for hosts to communicate with one another you would typically need to be connected to a network. A network is just a group of devices that are interconnected. - `switch` facilitates communication between hosts that are under the same network. 
- `router` facilitates communication between hosts that are not under the same network. Every router has its own individual IP address set by the manufacturer. 
- `sub-net`refer to networks inside of a network. 
- `NAT` Network address translation, allows multiple devices on a private network using private IPs like 192.168.x.x to share a single public IP address when accessing the internet, conserving IPv4 addresses and providing security by hiding internal devices 
- `private IP` unique identifier for devices in a local network for internal communication, assigned by router and not accessible from the public internet. These non-routable addresses (e.g. 192.168.x.x, 10.x.x.x) allow devices to talk to each other and the internet via NAT.
###### IP address
Say for example -> `10.24.21.1`
	It isn't randomly generated. Its a group of 32 bits that were split into octets (1 byte consists of 8 bits!). So `10011001100010100001001010100010` becomes `1001 1001 . 1000 1010 . 0001 0010. 1010 0010` and then... `x.x.x.x` 
Maximum number per section is 2^8 - 1 or 255. This can only hold around (255^4 or ~4.3 billion) (IPv4). Then IPV6 was invented, which can hold a lot more.  Let's not digress...

###### Network
Every family member has a phone, the house has a printer, a fridge, some laptops. A lot of these devices are under a network. Another example, while at work we connect to wi-fi. Wi-fi is a way to wirelessly connect a device to a network. And as we know once you have connected to a network then you can start using your favorite apps like instagram, facebook etc. But here we have assumed something, like we have our own network, does that mean companies have their own network as well? Yes, in order to communicate with another host on the wire you need to be in a network. So in order for us to use instagram, it also has to be connected to a network to send and receive data. 

When trying to use a printer on the same network, hosts that are under the same network and communicate with one another need a switch. 

When trying to use instagram, that isn't connected to the same network as our personal network. In that case we would use something that is called a router. Our router would have to talk to instagram's router to exchange information: send requests and responses.  
	Now when a computer joins a network and wants to communicate with another network by sending a request, this request has to go through a huge process. Request when sent has an IP address attached to it, so that the host that is receiving this data knows who to send this response to. But just before this request leaves the router, the router acts as a gateway, it will have a *transformation table* where it will write down that host in the network sent this request and instead of using the host's IP, the router will attach it's own IP to the request. And when a response is received, the router will know which specific host it was meant to be sent to because of this table. This translation of IP addresses is also known as NAT, which the router as explained performs.
	
Networks can have networks inside of a network. Say you work at google, it has a ton of different teams all over the world, each team has networks of their own but they still fall under the google umbrella, these networks inside of a network are also referred to as **sub-nets**. Sub-nets are used for better security and management.

## Recommended Learning Path (High Confidence)

### Foundational (Conceptual)

- _Computer Networking: A Top‑Down Approach_ – Kurose & Ross
    
- _Networking 101_ by Cloudflare (documentation)
    

### Practical + Visual

- Wireshark Official Docs + packet capture labs
    
- Cisco NetAcad: Introduction to Networks
    

### Protocol-Level Depth

- RFCs (especially for IP, TCP, DNS, HTTP)
    
- _TCP/IP Illustrated, Volume 1_ – W. Richard Stevens
    

### Hands-On (Strongly Recommended)

- Capture traffic with Wireshark
    
- Trace routes (`traceroute`, `mtr`)
    
- Build a small LAN with VLANs and subnets
    
- Observe NAT tables on a router