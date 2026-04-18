from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.packet import arp, ethernet
from pox.lib.addresses import IPAddr

log = core.getLogger()

# ARP Table: IP -> MAC
arp_table = {}

def _handle_PacketIn(event):
    packet = event.parsed
    if not packet:
        return

    arp_packet = packet.find('arp')

    # ===================== ARP HANDLING =====================
    if arp_packet:
        src_ip = str(arp_packet.protosrc)
        dst_ip = str(arp_packet.protodst)

        # Learn source IP -> MAC
        arp_table[src_ip] = packet.src
        log.debug("Learned: %s -> %s", src_ip, packet.src)

        # ✅ If destination known → send ARP reply
        if dst_ip in arp_table:
            log.debug("Sending ARP reply for %s", dst_ip)

            reply = arp()
            reply.opcode = arp.REPLY
            reply.hwsrc = arp_table[dst_ip]
            reply.hwdst = packet.src
            reply.protosrc = IPAddr(dst_ip)
            reply.protodst = IPAddr(src_ip)

            eth = ethernet()
            eth.type = ethernet.ARP_TYPE
            eth.src = arp_table[dst_ip]
            eth.dst = packet.src
            eth.payload = reply

            msg = of.ofp_packet_out()
            msg.data = eth.pack()
            msg.actions.append(of.ofp_action_output(port=event.port))
            event.connection.send(msg)

        # ❗ If destination unknown → flood
        else:
            log.debug("Flooding ARP request for %s", dst_ip)

            msg = of.ofp_packet_out()
            msg.data = event.ofp
            msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
            event.connection.send(msg)

    # ===================== DATA PACKET FORWARDING =====================
    else:
        # 🔥 THIS FIXES PING (VERY IMPORTANT)
        msg = of.ofp_packet_out()
        msg.data = event.ofp
        msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
        event.connection.send(msg)


def launch():
    log.info("Starting ARP Controller...")
    core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
