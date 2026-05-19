from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List
import uuid
import os

from .models import Rule, Node, Event, RegisterRequest, PacketInfo
from .store import store
from .rules_engine import evaluate

app = FastAPI(title="SDN Firewall Controller")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir interfaz web estática
interface_path = os.path.join(os.path.dirname(__file__), "..", "interface")
if os.path.exists(interface_path):
    app.mount("/static", StaticFiles(directory=interface_path), name="static")


@app.post("/register")
def register_node(req: RegisterRequest):
    """Registra un nodo cliente."""
    node = Node(name=req.name, ip=req.ip, listen_port=req.listen_port)
    store.add_or_update_node(req.name, node)
    return {"status": "registered", "node": node}


@app.get("/nodes")
def get_nodes() -> List[Node]:
    """Lista todos los nodos registrados."""
    return store.get_nodes()


@app.get("/rules")
def get_rules() -> List[Rule]:
    """Lista todas las reglas activas."""
    return store.get_rules()


@app.post("/rules")
def create_rule(rule: Rule):
    """Crea una nueva regla."""
    if not rule.id:
        rule.id = str(uuid.uuid4())[:8]
    store.add_rule(rule)
    return {"status": "created", "rule": rule}


@app.delete("/rules/{rule_id}")
def delete_rule(rule_id: str):
    """Elimina una regla por ID."""
    deleted = store.delete_rule(rule_id)
    if deleted:
        return {"status": "deleted", "rule_id": rule_id}
    return {"status": "not_found", "rule_id": rule_id}


@app.post("/events")
def report_event(event: Event):
    """Registra un evento reportado por un cliente."""
    if not event.id:
        event.id = str(uuid.uuid4())[:8]
    store.add_event(event)
    return {"status": "logged", "event": event}


@app.get("/events")
def get_events(limit: int = 100) -> List[Event]:
    """Lista eventos recientes."""
    return store.get_events(limit)


@app.get("/")
def root():
    """Redirige a la interfaz web."""
    return {"message": "SDN Firewall Controller", "docs": "/docs", "interface": "/static/index.html"}
