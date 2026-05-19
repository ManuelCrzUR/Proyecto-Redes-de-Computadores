from typing import List, Dict, Optional


def rule_matches(packet: Dict, rule: Dict) -> bool:
    """Verifica si un paquete coincide con una regla."""
    if rule.get("src_ip") and rule["src_ip"] != packet.get("src_ip"):
        return False
    if rule.get("dst_ip") and rule["dst_ip"] != packet.get("dst_ip"):
        return False
    if rule.get("protocol") and rule["protocol"].upper() != packet.get("protocol", "").upper():
        return False
    if rule.get("src_port") and rule["src_port"] != packet.get("src_port"):
        return False
    if rule.get("dst_port") and rule["dst_port"] != packet.get("dst_port"):
        return False
    return True


def evaluate(packet: Dict, rules: List[Dict]) -> str:
    """Evalúa un paquete contra reglas locales y retorna acción."""
    matches = [r for r in rules if rule_matches(packet, r)]

    if not matches:
        return "allow"

    highest_priority = max(matches, key=lambda r: r.get("priority", 0))
    return highest_priority.get("action", "allow")
