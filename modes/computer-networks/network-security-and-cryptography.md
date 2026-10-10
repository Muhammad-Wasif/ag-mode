# Network Security, Cryptography, and Traffic Engineering

## 1. Cryptographic Network Security Protocols
In computer-networks, data traveling across physical wires or the air must be assumed compromised.
- **IPsec (Internet Protocol Security):** The AI must architect robust Site-to-Site VPNs using IPsec. Understand the distinction between Transport Mode (encrypting only payload, used host-to-host) and Tunnel Mode (encrypting the entire IP packet, used gateway-to-gateway). Rigorously configure the IKEv2 negotiation phases, enforcing strong Diffie-Hellman groups and AES-256-GCM for the ESP (Encapsulating Security Payload).
- **TLS/SSL Infrastructure:** Architect enterprise PKI (Public Key Infrastructure). The AI must mandate TLS 1.3 for all Layer 7 traffic. Ensure proper certificate chain validation and implement OCSP Stapling to verify certificate revocation status without introducing DNS latency.
- **MACsec (802.1AE):** For extreme security environments, the AI must implement Layer 2 encryption (MACsec). Unlike IPsec, MACsec secures data instantly on the physical link between switches, neutralizing rogue devices physically plugged into the corporate network from intercepting traffic.

## 2. Deep Network Segmentation and Access Control
- **VLANs and VRFs:** Segregation is mandatory. The AI must assign distinct Broadcast Domains (VLANs) for different security zones (e.g., Guest WiFi, Corporate Desktops, VoIP Phones, IoT Sensors). To strictly separate routing tables on the same physical router, implement Virtual Routing and Forwarding (VRF).
- **Access Control Lists (ACLs):** Deploy strict extended ACLs at the network boundary. ACLs must be stateless (for raw speed) or stateful (via firewalls). The AI must always place the most specific, frequently matched rules at the top of the ACL to optimize hardware TCAM lookup times, and explicitly configure the implicit deny any any at the bottom.

## 3. Traffic Engineering and Quality of Service (QoS)
Bandwidth is finite. The AI must architect QoS mechanisms to guarantee network performance for critical applications during catastrophic congestion.
- **Classification and Marking:** Traffic must be classified as close to the source as possible. Map critical voice traffic to DSCP Expedited Forwarding (EF) and bulk data transfers to Best Effort (BE).
- **Queuing and Scheduling:** When hardware buffers fill up, the router must decide which packets to drop. The AI must configure Low Latency Queuing (LLQ) to give strict priority to Voice/Video, while utilizing Weighted Fair Queuing (WFQ) to prevent large TCP flows from starving smaller, interactive SSH sessions.
- **Traffic Shaping and Policing:** Architect Policers to aggressively drop packets exceeding the Service Level Agreement (SLA). Use Shapers to buffer and smooth bursty traffic, preventing downstream packet loss entirely.