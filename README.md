# SDN Project using Mininet and POX Controller

## 📌 Problem Statement
Implement an SDN-based network using Mininet and POX controller to:
- Handle ARP requests
- Enable host discovery
- Implement firewall (blocking traffic)

---

## 🛠️ Setup Instructions

1. Start POX controller:
   ./pox.py log.level --DEBUG openflow.of_01 misc.arp_controller

2. Start Mininet:
   sudo mn --topo single,3 --mac --controller remote

---

## ⚙️ Features Implemented

- ARP handling (host discovery)
- Flow rule installation
- Firewall (blocking h1 → h2)
- Packet_in handling
- Match-Action logic

---

## 🧪 Test Scenarios

### ✅ Scenario 1: Normal Communication
Command:
mininet> pingall

Result:
0% packet loss

![Ping Success](sdn-screenshots/s1.png)

---

### ❌ Scenario 2: Firewall Blocking
Command:
mininet> h1 ping h2

Result:
Destination Host Unreachable

![Ping Failure](sdn-screenshots/s6b.png)

---

## 📊 Performance Analysis

- Ping results show 0% packet loss indicating reliable communication.
- Iperf shows throughput of approximately X Mbits/sec demonstrating efficient network performance.
- Flow tables confirm that rules are installed dynamically, reducing controller overhead.
- ARP tables confirm successful host discovery.

This demonstrates correct SDN behavior and efficient network operation.

### Flow Table
![Flow Table](sdn-screenshots/s2.png)

### ARP Table
![ARP Table](sdn-screenshots/s3.png)

### Iperf Output
![Iperf](sdn-screenshots/s5.png)

---
## 🔁 Flow Rule Logic

The controller processes packet_in events and installs flow rules in the switch.

Match fields:
- Source MAC address
- Destination MAC address
- Input port

Actions:
- Forward packets to the correct output port

This reduces repeated packet_in events and improves performance.

## ✅ Validation

- Verified connectivity using ping
- Verified ARP learning using arp -n
- Verified flow rules using ovs-ofctl dump-flows
- Verified performance using iperf

## 📚 References

- Mininet Official Documentation
- POX Controller Documentation
- OpenFlow Specification
- Computer Networks – Andrew S. Tanenbaum
