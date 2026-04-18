from pox.core import core
import pox.openflow.libopenflow_01 as of

log = core.getLogger()

BLOCKED_SRC = "10.0.0.1"
BLOCKED_DST = "10.0.0.2"

def _handle_PacketIn(event):
    packet = event.parsed

    if not packet.parsed:
        return

    ip = packet.find('ipv4')

    if ip:
        src = str(ip.srcip)
        dst = str(ip.dstip)

        # 🚫 BLOCK CONDITION
        if src == BLOCKED_SRC and dst == BLOCKED_DST:
            log.info("BLOCKED: %s -> %s", src, dst)
            return   # ❌ DO NOTHING → packet dropped

    # ✅ ALLOW OTHER TRAFFIC
    msg = of.ofp_packet_out()
    msg.data = event.ofp
    msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
    event.connection.send(msg)

def launch():
    core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
    log.info("Firewall started...")
