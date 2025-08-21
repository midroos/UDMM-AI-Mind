# ui_agent.py
# UDMM Agent Dashboard (Streamlit)
# ---------------------------------------------------------
# Features:
# - Live WebSocket stream from FastAPI (/stream)
# - Body state (pos/energy/arousal), episodic ticks
# - Semantic Memory graph (PyVis + NetworkX)
# - Hierarchical Intent tree visualization
# - Deep Chat bound to agent dialogue API with semantic assist
# - API Keys management (via /config/keys if available + local config.json)
# ---------------------------------------------------------

import os
import json
import time
import queue
import threading
import tempfile
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import streamlit as st
import requests

# Lazy imports for optional deps (avoid import crash before pip install)
def lazy_imports():
    global websockets, asyncio, nx, Network, components
    import importlib
    websockets = importlib.import_module("websockets")
    asyncio = importlib.import_module("asyncio")
    nx = importlib.import_module("networkx")
    from pyvis.network import Network
    components = importlib.import_module("streamlit.components.v1")
    return Network

Network = None  # assigned in lazy_imports()

# ---------------------------
# Defaults & Helpers
# ---------------------------
DEFAULT_API_BASE = os.environ.get("UDMM_API_BASE", "http://127.0.0.1:8000")
DEFAULT_WS_URL = os.environ.get("UDMM_WS_URL", "ws://127.0.0.1:8000/stream")
CONFIG_PATH = os.path.join(os.getcwd(), "config.json")

@dataclass
class AppConfig:
    api_base: str = DEFAULT_API_BASE
    ws_url: str = DEFAULT_WS_URL
    google_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    huggingface_api_key: Optional[str] = None

    def to_dict(self):
        return {
            "api_base": self.api_base,
            "ws_url": self.ws_url,
            "google_api_key": self.google_api_key or "",
            "openai_api_key": self.openai_api_key or "",
            "huggingface_api_key": self.huggingface_api_key or "",
        }

# ---------------------------
# Config load/save
# ---------------------------
def load_local_config() -> AppConfig:
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            return AppConfig(**data)
        except Exception:
            pass
    return AppConfig()

def save_local_config(cfg: AppConfig):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg.to_dict(), f, ensure_ascii=False, indent=2)

# ---------------------------
# API helpers
# ---------------------------
def api_get(path: str, base: str) -> Optional[Dict[str, Any]]:
    try:
        r = requests.get(f"{base.rstrip('/')}/{path.lstrip('/')}", timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception:
        return None
    return None

def api_post(path: str, base: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    try:
        r = requests.post(f"{base.rstrip('/')}/{path.lstrip('/')}", json=payload, timeout=15)
        if r.status_code in (200, 201):
            return r.json()
        else:
            # return error envelope
            return {"status": "error", "code": r.status_code, "text": r.text}
    except Exception as e:
        return {"status": "error", "text": str(e)}

# Try to fetch keys presence from backend
def refresh_keys_from_backend(cfg: AppConfig) -> Dict[str, bool]:
    data = api_get("/config/keys", cfg.api_base)
    if isinstance(data, dict) and data:
        return {
            "google_api_key": bool(data.get("google_api_key", False)),
            "openai_api_key": bool(data.get("openai_api_key", False)),
            "huggingface_api_key": bool(data.get("huggingface_api_key", False)),
        }
    # fallback to local
    return {
        "google_api_key": bool(cfg.google_api_key),
        "openai_api_key": bool(cfg.openai_api_key),
        "huggingface_api_key": bool(cfg.huggingface_api_key),
    }

def update_key_backend(cfg: AppConfig, service: str, key: str) -> bool:
    # Try backend first
    resp = api_post("/config/keys", cfg.api_base, {"service": service, "key": key})
    if isinstance(resp, dict) and resp.get("status") == "success":
        return True
    return False

# ---------------------------
# WebSocket streaming thread
# ---------------------------
class StreamThread(threading.Thread):
    def __init__(self, ws_url: str, out_queue: "queue.Queue[Dict[str, Any]]"):
        super().__init__(daemon=True)
        self.ws_url = ws_url
        self.out_queue = out_queue
        self._stop_flag = threading.Event()

    def stop(self):
        self._stop_flag.set()

    def run(self):
        # Each thread needs its own loop
        NetworkLocal = lazy_imports()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._run_ws())

    async def _run_ws(self):
        while not self._stop_flag.is_set():
            try:
                async with websockets.connect(self.ws_url) as ws:
                    # Optionally, send a hello to subscribe specific streams
                    # await ws.send(json.dumps({"type": "subscribe", "channels": ["agent_cycle"]}))
                    while not self._stop_flag.is_set():
                        msg = await ws.recv()
                        try:
                            data = json.loads(msg)
                        except Exception:
                            data = {"raw": msg}
                        self.out_queue.put(data)
            except Exception as e:
                # backoff before reconnect
                self.out_queue.put({"type": "ws_status", "status": "disconnected", "error": str(e)})
                time.sleep(1.5)
            else:
                self.out_queue.put({"type": "ws_status", "status": "closed"})
                time.sleep(1.0)

# ---------------------------
# UI Rendering helpers
# ---------------------------
def render_body_panel(col, body_after: Dict[str, Any], emotion: float, energy: Optional[float]):
    x = body_after.get("x", 0.0)
    y = body_after.get("y", 0.0)
    col.metric("Position", f"({x:.2f}, {y:.2f})")
    col.metric("Arousal", f"{emotion:.3f}")
    if energy is not None:
        col.metric("Energy", f"{energy:.2f}")

def render_semantic_graph(placeholder, concepts: List[Dict[str, Any]], links: List[Dict[str, Any]]):
    # Build graph
    G = nx.Graph()
    for c in concepts or []:
        nid = c.get("id") or c.get("name") or c.get("label")
        if not nid:
            continue
        G.add_node(nid, title=json.dumps(c, ensure_ascii=False), label=c.get("label") or c.get("name") or str(nid))
    for e in links or []:
        src = e.get("source") or e.get("from") or e.get("from_node")
        tgt = e.get("target") or e.get("to") or e.get("to_node")
        if src and tgt:
            G.add_edge(src, tgt, title=e.get("type") or e.get("relation") or "")

    nt = Network(height="500px", width="100%", directed=False)
    nt.barnes_hut()
    nt.from_nx(G)
    tmp_html = os.path.join(tempfile.gettempdir(), "udmm_semantic_graph.html")
    nt.save_graph(tmp_html)
    with open(tmp_html, "r", encoding="utf-8") as f:
        components.html(f.read(), height=520, scrolling=True)

def render_goal_tree(goals: List[Dict[str, Any]]):
    def _node(g: Dict[str, Any], depth: int = 0):
        name = g.get("name") or g.get("description") or g.get("id", "goal")
        status = g.get("status") or g.get("state") or "pending"
        progress = g.get("progress", 0.0)
        indent = "  " * depth
        st.markdown(f"{indent}• **{name}** — _{status}_ ({int(progress*100)}%)")
        for ch in g.get("subgoals") or g.get("children") or []:
            _node(ch, depth + 1)
    if not goals:
        st.info("لا توجد أهداف نشطة حالياً.")
        return
    for g in goals:
        with st.expander(g.get("name") or g.get("description") or g.get("id", "goal"), expanded=True):
            _node(g, 0)

def render_chat_section(api_base: str):
    st.subheader("💬 الدردشة العميقة مع الوكيل")
    if "chat" not in st.session_state:
        st.session_state.chat = []
    user_text = st.text_input("اكتب رسالتك للوكيل", key="chat_input")
    cols = st.columns([1, 1, 5])
    send_btn = cols[0].button("إرسال")
    clear_btn = cols[1].button("مسح المحادثة")

    if clear_btn:
        st.session_state.chat = []
        st.experimental_rerun()

    if send_btn and user_text.strip():
        st.session_state.chat.append(("user", user_text.strip()))
        # Try Dialogue API first
        resp = api_post("/dialogue/chat", api_base, {"text": user_text.strip()})
        if not isinstance(resp, dict) or resp.get("status") == "error":
            # Fallback: try a generic /dialogue/say
            resp2 = api_post("/dialogue/say", api_base, {"text": user_text.strip()})
            if isinstance(resp2, dict) and resp2.get("reply"):
                agent_reply = resp2["reply"]
            else:
                # As a last resort, echo + optional semantic assist
                agent_reply = "لم أستطع الوصول لوحدة الحوار. سأحاول استخدام الذاكرة الدلالية لاحقاً."
        else:
            agent_reply = resp.get("reply") or resp.get("text") or str(resp)

        st.session_state.chat.append(("agent", agent_reply))

    # Display chat history
    for role, txt in st.session_state.chat[-50:]:
        if role == "user":
            st.chat_message("user").markdown(txt)
        else:
            st.chat_message("assistant").markdown(txt)

# ---------------------------
# Streamlit App
# ---------------------------
st.set_page_config(page_title="UDMM Agent Dashboard", layout="wide")
st.title("🤖 UDMM-AI-Mind — Agent Dashboard")

# Load config
cfg = load_local_config()

# Sidebar settings
with st.sidebar:
    st.header("⚙️ الإعدادات")
    cfg.api_base = st.text_input("API Base URL", value=cfg.api_base, help="مثال: http://127.0.0.1:8000")
    cfg.ws_url = st.text_input("WebSocket URL", value=cfg.ws_url, help="مثال: ws://127.0.0.1:8000/stream")

    st.markdown("---")
    st.subheader("🔑 مفاتيح API")
    # Fetch current status from backend
    keys_state = refresh_keys_from_backend(cfg)
    st.write("الحالة الحالية:")
    st.write({k: ("✓" if v else "✗") for k, v in keys_state.items()})

    svc = st.selectbox("الخدمة", ["google", "openai", "huggingface"])
    new_key = st.text_input("المفتاح الجديد", type="password")

    colk1, colk2 = st.columns(2)
    if colk1.button("حفظ المفتاح"):
        ok = update_key_backend(cfg, svc, new_key)
        if not ok:
            # fallback to local store if backend not available
            if svc == "google":
                cfg.google_api_key = new_key
            elif svc == "openai":
                cfg.openai_api_key = new_key
            else:
                cfg.huggingface_api_key = new_key
            save_local_config(cfg)
            st.success("تم حفظ المفتاح محليًا (config.json).")
        else:
            st.success("تم تحديث المفتاح عبر الـ API.")
    if colk2.button("حفظ الإعدادات"):
        save_local_config(cfg)
        st.success("تم حفظ الإعدادات.")

    st.markdown("---")
    st.caption("تأكد من تشغيل FastAPI:\n`uvicorn src.udmm2.api.app:app --reload`")

# Layout
col_left, col_mid, col_right = st.columns([1.2, 1.6, 1.2])

with col_left:
    st.subheader("🧠 حالة الجسد & الإشارة العاطفية")
    pos_placeholder = st.empty()
    arousal_placeholder = st.empty()
    energy_placeholder = st.empty()
    st.markdown("---")
    st.subheader("🎯 القصد الهرمي")
    goals_container = st.container()

with col_mid:
    st.subheader("🕸️ الذاكرة الدلالية (خريطة)")
    graph_container = st.container()
    st.markdown("---")
    st.subheader("📡 البث الحي (Logs)")
    logs = st.empty()

with col_right:
    render_chat_section(cfg.api_base)

# Stream control
if "stream_queue" not in st.session_state:
    st.session_state.stream_queue = queue.Queue()
if "stream_thread" not in st.session_state:
    st.session_state.stream_thread = None
if "stream_running" not in st.session_state:
    st.session_state.stream_running = False

col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)
if not st.session_state.stream_running:
    if col_ctrl1.button("▶️ بدء البث"):
        st.session_state.stream_thread = StreamThread(cfg.ws_url, st.session_state.stream_queue)
        st.session_state.stream_thread.start()
        st.session_state.stream_running = True
else:
    if col_ctrl2.button("⏹️ إيقاف البث"):
        if st.session_state.stream_thread:
            st.session_state.stream_thread.stop()
            st.session_state.stream_thread = None
        st.session_state.stream_running = False

col_ctrl3.button("🔄 تحديث يدوي")

# Live loop (poll queue)
# Note: Streamlit reruns the script; we use a short poll with time.sleep inside while loops is discouraged.
# Instead, fetch up to N messages each rerun.
def drain_queue(q: "queue.Queue[Dict[str, Any]]", max_n=20) -> List[Dict[str, Any]]:
    items = []
    for _ in range(max_n):
        try:
            items.append(q.get_nowait())
        except queue.Empty:
            break
    return items

# Keep a small ring buffer of last messages
if "last_msgs" not in st.session_state:
    st.session_state.last_msgs = []

incoming = drain_queue(st.session_state.stream_queue, max_n=50)
if incoming:
    st.session_state.last_msgs.extend(incoming)
    st.session_state.last_msgs = st.session_state.last_msgs[-200:]  # cap

# Render logs
if st.session_state.last_msgs:
    view = []
    for m in st.session_state.last_msgs[-30:]:
        ts = m.get("timestamp") or m.get("t") or ""
        tag = m.get("type") or m.get("event") or "msg"
        view.append(f"[{tag}] {ts} → {json.dumps(m, ensure_ascii=False)[:400]}")
    logs.code("\n".join(view), language="text")

# Extract latest frame-like message for panels
def pick_latest_frame(msgs: List[Dict[str, Any]]) -> Dict[str, Any]:
    # Heuristics: prefer ones with body_after/expectations/active_goals
    for m in reversed(msgs):
        if isinstance(m, dict) and (m.get("body_after") or m.get("active_goals") or m.get("expectations")):
            return m
    return msgs[-1] if msgs else {}

latest = pick_latest_frame(st.session_state.last_msgs)

# Update body panel
body_after = latest.get("body_after", {}) if isinstance(latest, dict) else {}
emotion_signal = latest.get("emotion_signal", 0.0) if isinstance(latest, dict) else 0.0
energy_val = None
if isinstance(body_after, dict):
    energy_val = body_after.get("energy")

with col_left:
    render_body_panel(pos_placeholder, body_after, float(emotion_signal or 0.0), energy_val)

# Update semantic graph
with col_mid:
    # Expect latest semantic snapshot shape:
    # {"semantic_memory": {"concepts":[{id,label,...}, ...], "links":[{source,target,type}, ...]}}
    sem = latest.get("semantic_memory") if isinstance(latest, dict) else None
    if isinstance(sem, dict):
        with graph_container:
            render_semantic_graph(graph_container, sem.get("concepts") or [], sem.get("links") or [])

# Update hierarchical goals
with col_left:
    ag = latest.get("active_goals") if isinstance(latest, dict) else None
    with goals_container:
        if isinstance(ag, list):
            render_goal_tree(ag)
        else:
            st.caption("بانتظار بيانات الأهداف من البث…")

st.caption("جاهز. لتشغيل الخادم الخلفي: `uvicorn src.udmm2.api.app:app --reload`  — ثم اضغط تشغيل البث من الأعلى.")
