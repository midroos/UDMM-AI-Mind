import streamlit as st
import json
import os
import asyncio
import threading
import queue
import time
from websockets.client import connect as ws_connect
from websockets.exceptions import ConnectionClosed
import networkx as nx
from pyvis.network import Network
from typing import Dict, Any

# --- Configuration ---
CONFIG_FILE = "config.json"
CHAT_URI = "ws://localhost:8000/ws/chat"
STREAM_URI = "ws://localhost:8000/stream/cycle"

# --- API Key Management ---
def load_keys():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_keys(google_key, openai_key):
    keys = {"google_api_key": google_key, "openai_api_key": openai_key}
    with open(CONFIG_FILE, "w") as f:
        json.dump(keys, f, indent=4)

# --- WebSocket Connection Logic ---
class AgentConnector:
    def __init__(self, loop, chat_queue, stream_queue):
        self._loop = loop
        self._chat_queue = chat_queue
        self._stream_queue = stream_queue
        self._chat_ws = None
        self._stream_ws = None
        self._listener_tasks = []

    async def _listen(self, ws, q):
        try:
            while True:
                raw_data = await ws.recv()
                data = json.loads(raw_data)
                q.put(data)
        except (ConnectionClosed, asyncio.CancelledError):
            pass

    async def _heartbeat(self):
        while True:
            if self._stream_ws:
                try:
                    await self._stream_ws.send(json.dumps({"perception": "heartbeat"}))
                except ConnectionClosed:
                    break
            await asyncio.sleep(1)

    async def connect(self):
        try:
            self._chat_ws = await ws_connect(CHAT_URI)
            self._stream_ws = await ws_connect(STREAM_URI)

            chat_listener = self._loop.create_task(self._listen(self._chat_ws, self._chat_queue))
            stream_listener = self._loop.create_task(self._listen(self._stream_ws, self._stream_queue))
            heartbeat_task = self._loop.create_task(self._heartbeat())
            self._listener_tasks = [chat_listener, stream_listener, heartbeat_task]

            return True
        except Exception as e:
            st.error(f"Connection failed: {e}")
            return False

    def send_chat_message(self, message):
        if self._chat_ws:
            asyncio.run_coroutine_threadsafe(self._chat_ws.send(message), self._loop)

    def disconnect(self):
        for task in self._listener_tasks:
            task.cancel()
        if self._chat_ws:
            asyncio.run_coroutine_threadsafe(self._chat_ws.close(), self._loop)
        if self._stream_ws:
            asyncio.run_coroutine_threadsafe(self._stream_ws.close(), self._loop)

def start_background_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

# --- UI Rendering Functions ---
def draw_status_panel(data: Dict[str, Any], placeholder):
    with placeholder.container():
        body_after = data.get("result", {}).get("body_after", {})
        emotion_signal = data.get("emotion_signal", 0)

        col1, col2 = st.columns(2)
        col1.metric("Position (X)", f"{body_after.get('x', 0):.2f}")
        col2.metric("Position (Y)", f"{body_after.get('y', 0):.2f}")

        st.progress(body_after.get('energy', 0), text=f"Energy: {body_after.get('energy', 0)*100:.0f}%")
        st.progress(emotion_signal, text=f"Arousal: {emotion_signal*100:.0f}%")

def draw_semantic_graph(data: Dict[str, Any], placeholder):
    with placeholder.container():
        graph_data = data.get("semantic_graph")
        if not graph_data or not graph_data.get("nodes"):
            st.write("No semantic graph data available.")
            return

        net = Network(height="400px", width="100%", notebook=True, cdn_resources="in_line", directed=True)

        for node in graph_data["nodes"]:
            color = "#007bff" if node.get("type") == "concept" else "#28a745"
            net.add_node(node["id"], label=node["label"], title=node["title"], color=color)

        for edge in graph_data["edges"]:
            net.add_edge(edge["source"], edge["target"], label=edge["label"])

        try:
            net.save_graph("semantic_graph.html")
            with open("semantic_graph.html", "r", encoding="utf-8") as f:
                st.components.v1.html(f.read(), height=420)
        except Exception as e:
            st.error(f"Could not generate graph: {e}")

def draw_intent_tree(data: Dict[str, Any], placeholder):
    with placeholder.container():
        intent = data.get("active_goals")
        if not intent:
            st.write("No active goals.")
            return

        ultimate = intent.get("ultimate", {})
        st.write(f"**Ultimate Goal:** Target ({ultimate.get('x', 0):.1f}, {ultimate.get('y', 0):.1f})")

        current_idx = intent.get("current_index", -1)
        for i, subgoal in enumerate(intent.get("subgoals", [])):
            target = f"({subgoal.get('target_x', 0):.1f}, {subgoal.get('target_y', 0):.1f})"
            label = f"Subgoal {i+1}: {subgoal.get('associated_concept') or target}"

            if subgoal.get('completed'):
                st.info(f"✅ {label}")
            elif i == current_idx:
                st.success(f"➡️ {label} (In Progress)")
            else:
                st.write(f"⚪ {label}")

# --- UI Setup & Main Loop ---
st.set_page_config(layout="wide")
st.title("UDMM Agent UI")

# Initialize session state
if "connector" not in st.session_state:
    st.session_state.loop = asyncio.new_event_loop()
    st.session_state.chat_queue = queue.Queue()
    st.session_state.stream_queue = queue.Queue()
    st.session_state.connector = AgentConnector(st.session_state.loop, st.session_state.chat_queue, st.session_state.stream_queue)
    st.session_state.thread = threading.Thread(target=start_background_loop, args=(st.session_state.loop,), daemon=True)
    st.session_state.thread.start()
    st.session_state.latest_stream_data = None
    st.session_state.messages = []

if "connected" not in st.session_state:
    st.session_state.connected = False

# --- Sidebar ---
st.sidebar.title("Configuration")
with st.sidebar.expander("Connection", expanded=True):
    if st.session_state.connected:
        st.success("Connected")
        if st.button("Disconnect"):
            st.session_state.connector.disconnect()
            st.session_state.connected = False
            st.rerun()
    else:
        st.warning("Disconnected")
        if st.button("Connect"):
            future = asyncio.run_coroutine_threadsafe(st.session_state.connector.connect(), st.session_state.loop)
            st.session_state.connected = future.result()
            if not st.session_state.connected:
                st.error("Failed to establish connection.")
            st.rerun()

with st.sidebar.expander("API Keys"):
    api_keys = load_keys()
    google_key_input = st.text_input("Google Search API Key", type="password", value=api_keys.get("google_api_key", ""))
    openai_key_input = st.text_input("OpenAI API Key", type="password", value=api_keys.get("openai_api_key", ""))
    if st.button("Save API Keys"):
        save_keys(google_key_input, openai_key_input)
        st.sidebar.success("API keys saved!")

# --- Main UI Layout ---
if st.session_state.connected:
    st.success("Connected to Agent WebSocket endpoints. Receiving live data...")

    col1, col2 = st.columns([2, 1]) # Give more space to the graph and status

    with col1:
        with st.expander("Agent Status & Vitals", expanded=True):
            status_placeholder = st.empty()
        with st.expander("Semantic Memory Graph"):
            graph_placeholder = st.empty()

    with col2:
        with st.expander("Hierarchical Intent", expanded=True):
            intent_placeholder = st.empty()

        chat_container = st.container(height=500, border=True)
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        if prompt := st.chat_input("Send a message to the agent..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            # Display user message immediately
            with chat_container:
                 with st.chat_message("user"):
                    st.markdown(prompt)

            st.session_state.connector.send_chat_message(prompt)
            # No rerun here, wait for agent response to trigger rerun

    # Main UI update loop
    while True:
        # Process stream queue for live components
        try:
            stream_data = st.session_state.stream_queue.get_nowait()
            st.session_state.latest_stream_data = stream_data
        except queue.Empty:
            pass

        if st.session_state.latest_stream_data:
            data = st.session_state.latest_stream_data
            draw_status_panel(data, status_placeholder)
            draw_semantic_graph(data, graph_placeholder)
            draw_intent_tree(data, intent_placeholder)

        # Process chat queue for new messages
        try:
            chat_data = st.session_state.chat_queue.get_nowait()
            if chat_data.get("type") != "user":
                role = chat_data.get("type", "assistant")
                content = chat_data.get("text") or json.dumps(chat_data)
                st.session_state.messages.append({"role": role, "content": content})
                st.rerun()
        except queue.Empty:
            pass

        time.sleep(0.1)

else:
    st.warning("Not connected. Click 'Connect to Agent' in the sidebar to begin.")
