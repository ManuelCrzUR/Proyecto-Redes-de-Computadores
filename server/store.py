from typing import Dict, List, Optional
from datetime import datetime
from .models import Rule, Node, Event


class Store:
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.rules: Dict[str, Rule] = {}
        self.events: List[Event] = []

    def add_or_update_node(self, name: str, node: Node) -> None:
        node.last_seen = datetime.utcnow()
        self.nodes[name] = node

    def get_nodes(self) -> List[Node]:
        return list(self.nodes.values())

    def add_rule(self, rule: Rule) -> None:
        self.rules[rule.id] = rule

    def get_rules(self) -> List[Rule]:
        return list(self.rules.values())

    def delete_rule(self, rule_id: str) -> bool:
        if rule_id in self.rules:
            del self.rules[rule_id]
            return True
        return False

    def add_event(self, event: Event) -> None:
        event.timestamp = datetime.utcnow()
        self.events.append(event)

    def get_events(self, limit: int = 100) -> List[Event]:
        return self.events[-limit:]

    def clear_events(self) -> None:
        self.events = []


store = Store()
