from typing import List, Optional
from .models import Rule, PacketInfo


def rule_matches(packet: PacketInfo, rule: Rule) -> bool:
    """Verifica si un paquete coincide con una regla."""
    rule_src_ip = rule.src_ip if isinstance(rule, Rule) else rule.get("src_ip")
    rule_dst_ip = rule.dst_ip if isinstance(rule, Rule) else rule.get("dst_ip")
    rule_protocol = rule.protocol if isinstance(rule, Rule) else rule.get("protocol")
    rule_src_port = rule.src_port if isinstance(rule, Rule) else rule.get("src_port")
    rule_dst_port = rule.dst_port if isinstance(rule, Rule) else rule.get("dst_port")

    if rule_src_ip and rule_src_ip != packet.src_ip:
        return False
    if rule_dst_ip and rule_dst_ip != packet.dst_ip:
        return False
    if rule_protocol and rule_protocol.upper() != packet.protocol.upper():
        return False
    if rule_src_port and rule_src_port != packet.src_port:
        return False
    if rule_dst_port and rule_dst_port != packet.dst_port:
        return False
    return True


def evaluate(packet: PacketInfo, rules: List[Rule]) -> str:
    """Evalúa un paquete contra reglas y retorna acción (allow/block/report)."""
    matches = [r for r in rules if rule_matches(packet, r)]

    if not matches:
        return "allow"

    def get_priority(r):
        return r.priority if isinstance(r, Rule) else r.get("priority", 0)

    highest_priority = max(matches, key=get_priority)
    action = highest_priority.action if isinstance(highest_priority, Rule) else highest_priority.get("action", "allow")
    return action
