from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.packet import arp, ethernet
from pox.lib.addresses import IPAddr

# Initialize logger for debugging
log = core.getLogger()

# ARP Table to store mapping: IP address -> MAC address
arp_table = {}

def _handle_PacketIn(event):
    # Extract the incoming packet
    packet = event.parsed

    # If packet is not parsed correctly, ignore it
    if not packet:
        return

    # Try to find if the packet is an ARP packet
    arp_packet = packet.find('arp')

    # ===================== ARP HANDLING =====================
    if arp_packet:
        # Extract source and destination IP addresses
        src_ip = str(arp_packet.protosrc)
        dst_ip = str(arp_packet.protodst)

        # Learn and store source IP to MAC mapping in ARP table
        arp_table[src_ip] = packet.src
        log.debug("Learned: %s -> %s", src_ip, packet.src)

        # If destination IP is already known in ARP table
        # Generate and send ARP reply directly
        if dst_ip in arp_table:
            log.debug("Sending ARP reply for %s", dst_ip)

            # Create ARP reply packet
            reply = arp()
            reply.opcode = arp.REPLY               # ARP reply opcode
            reply.hwsrc = arp_table[dst_ip]        # Source MAC (destination's MAC)
            reply.hwdst = packet.src               # Destination MAC (original sender)
            reply.protosrc = IPAddr(dst_ip)        # Source IP (destination IP)
            reply.protodst = IPAddr(src_ip)        # Destination IP (original sender IP)

            # Create Ethernet frame to carry ARP reply
            eth = ethernet()
            eth.type = ethernet.ARP_TYPE           # Set Ethernet type as ARP
            eth.src = arp_table[dst_ip]            # Source MAC address
            eth.dst = packet.src                   # Destination MAC address
            eth.payload = reply                    # Attach ARP reply

            # Create OpenFlow packet_out message to send packet
            msg = of.ofp_packet_out()
            msg.data = eth.pack()                 # Pack Ethernet frame into bytes
            msg.actions.append(of.ofp_action_output(port=event.port))  # Send back to requesting port

            # Send the message to the switch
            event.connection.send(msg)

        # If destination IP is not known, flood the ARP request
        else:
            log.debug("Flooding ARP request for %s", dst_ip)

            msg = of.ofp_packet_out()
            msg.data = event.ofp                  # Original packet
            msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))  # Flood to all ports

            event.connection.send(msg)

    # ===================== DATA PACKET FORWARDING =====================
    else:
        # For non-ARP packets (like ICMP ping),
        # flood the packet so communication can happen
        msg = of.ofp_packet_out()
        msg.data = event.ofp
        msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))

        event.connection.send(msg)


def launch():
    # Entry point of the controller
    log.info("Starting ARP Controller...")

    # Register PacketIn event handler
    core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
