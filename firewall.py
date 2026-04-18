from pox.core import core
import pox.openflow.libopenflow_01 as of

# Initialize logger for debugging and monitoring
log = core.getLogger()

# Define blocked source and destination IPs
BLOCKED_SRC = "10.0.0.1"
BLOCKED_DST = "10.0.0.2"

def _handle_PacketIn(event):
    # Extract the incoming packet from the event
    packet = event.parsed

    # If packet is not parsed correctly, ignore it
    if not packet.parsed:
        return

    # Try to find IPv4 packet inside the Ethernet frame
    ip = packet.find('ipv4')

    # If the packet contains an IPv4 header
    if ip:
        # Extract source and destination IP addresses
        src = str(ip.srcip)
        dst = str(ip.dstip)

        # ===================== BLOCK CONDITION =====================
        # If traffic matches blocked source and destination
        if src == BLOCKED_SRC and dst == BLOCKED_DST:
            log.info("BLOCKED: %s -> %s", src, dst)

            # Do nothing → packet is dropped (not forwarded)
            return

    # ===================== ALLOW OTHER TRAFFIC =====================
    # For all other packets, forward by flooding
    msg = of.ofp_packet_out()
    msg.data = event.ofp                          # Original packet data
    msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))  # Send to all ports

    # Send packet to switch for forwarding
    event.connection.send(msg)

def launch():
    # Register PacketIn event handler with the controller
    core.openflow.addListenerByName("PacketIn", _handle_PacketIn)

    # Log that firewall controller has started
    log.info("Firewall started...")
