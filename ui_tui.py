from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Input, Log
from textual.containers import Container, Horizontal, Vertical

class SpoonFeedrTUI(App):
    CSS = """
    Screen {
        layout: vertical;
    }

    #main_container {
        height: 1fr;
        layout: horizontal;
    }

    #sidebar {
        width: 30;
        background: $panel;
        border-right: solid $accent;
    }

    #chat_area {
        width: 1fr;
        layout: vertical;
    }

    #chat_log {
        height: 1fr;
        border: solid $primary;
    }

    Input {
        dock: bottom;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="main_container"):
            with Vertical(id="sidebar"):
                yield Static(" [ TELEMETRY ] ", id="telemetry_header")
                yield Log(id="telemetry_log")
                yield Static(" [ MEMORY ] ", id="memory_header")
                yield Log(id="memory_log")
            with Vertical(id="chat_area"):
                yield Log(id="chat_log")
                yield Input(placeholder="Vibe your request here...")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#telemetry_log").write_line("👶 Baby Sitter active.")
        self.query_one("#memory_log").write_line("🧠 Project context loaded.")
        from core.orchestrator import create_spoon_feedr_graph
        self.graph = create_spoon_feedr_graph()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        user_text = event.value
        self.query_one("#chat_log").write_line(f"User: {user_text}")
        event.input.value = ""

        self.query_one("#telemetry_log").write_line(f"🚀 Processing: {user_text}")

        from langchain_core.messages import HumanMessage
        initial_state = {
            "messages": [HumanMessage(content=user_text)],
            "current_step": 0
        }

        # Run graph and update UI logs
        try:
            for event in self.graph.stream(initial_state):
                for node_name, state_update in event.items():
                    self.query_one("#telemetry_log").write_line(f"⚙️ Node: {node_name}")
                    if "context" in state_update:
                        self.query_one("#chat_log").write_line(f"Spoon Feedr: {list(state_update['context'].values())[0]}")
        except Exception as e:
            self.query_one("#telemetry_log").write_line(f"❌ Error: {e}")

if __name__ == "__main__":
    app = SpoonFeedrTUI()
    app.run()
