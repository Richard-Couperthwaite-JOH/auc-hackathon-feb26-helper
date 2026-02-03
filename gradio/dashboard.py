"""
gradio_agent_demo.py
--------------------
A tiny "agentic" demo in Gradio with tool use:
- calculator(expr)
- get_time(tz)
- make_plan(goal)

Run:
  pip install gradio
  python gradio_agent_demo.py
"""

from __future__ import annotations

import ast
import operator as op
import re
from dataclasses import dataclass
from datetime import datetime

import gradio as gr

try:
    from zoneinfo import ZoneInfo  # py>=3.9
except Exception:  # pragma: no cover
    ZoneInfo = None  # type: ignore


# ----------------------------
# Tools
# ----------------------------
_ALLOWED_OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.FloorDiv: op.floordiv,
    ast.Mod: op.mod,
    ast.Pow: op.pow,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
}

CITY_TZ = {
    "johannesburg": "Africa/Johannesburg",
    "cape town": "Africa/Johannesburg",
    "durban": "Africa/Johannesburg",
    "london": "Europe/London",
    "paris": "Europe/Paris",
    "berlin": "Europe/Berlin",
    "new york": "America/New_York",
    "san francisco": "America/Los_Angeles",
    "los angeles": "America/Los_Angeles",
    "tokyo": "Asia/Tokyo",
    "singapore": "Asia/Singapore",
    "sydney": "Australia/Sydney",
}


def safe_calc(expr: str) -> str:
    expr = expr.strip()
    if len(expr) > 200:
        return "Expression too long."

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.Num):
            return node.n
        if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPS:
            return _ALLOWED_OPS[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPS:
            return _ALLOWED_OPS[type(node.op)](_eval(node.operand))
        raise ValueError("Unsupported expression.")

    try:
        tree = ast.parse(expr, mode="eval")
        val = _eval(tree)
        if isinstance(val, float) and abs(val - round(val)) < 1e-12:
            val = round(val)
        return str(val)
    except Exception as e:
        return f"Could not evaluate: {e}"


def get_time(tz_name: str) -> str:
    if ZoneInfo is None:
        return "Timezone support unavailable (need Python 3.9+)."
    try:
        now = datetime.now(ZoneInfo(tz_name))
        return now.strftime("%Y-%m-%d %H:%M:%S (%Z)")
    except Exception as e:
        return f"Could not get time for '{tz_name}': {e}"


def make_plan(goal: str) -> str:
    bullets = [
        "Clarify the goal + success criteria (1–2 sentences).",
        "List the smallest demo-able user flow (3–5 steps).",
        "Pick 1–2 tools/APIs (or mock them) to support the flow.",
        "Build the UI skeleton first (inputs, buttons, results).",
        "Wire the agent loop (decide → tool → observe → answer).",
        "Add a short 'demo script' and 2–3 example prompts.",
    ]
    return "Here’s a quick plan:\n" + "\n".join([f"- {b}" for b in bullets])


# ----------------------------
# Tiny Agent (rule-based)
# ----------------------------
@dataclass
class ToolStep:
    tool: str
    input: str
    result: str


_MATH_RE = re.compile(r"(?P<expr>[-+*/().\d\s]{3,})")


def extract_math_expression(text: str) -> str | None:
    candidates = [m.group("expr").strip() for m in _MATH_RE.finditer(text)]
    for c in candidates:
        if any(ch.isdigit() for ch in c) and any(opch in c for opch in "+-*/"):
            return c.strip(" .,:;!?")
    return None


def find_requested_timezones(text: str, default_tz: str) -> list[tuple[str, str]]:
    lower = text.lower()
    hits: list[tuple[str, str]] = []
    if "time" in lower or "date" in lower:
        for city, tz in CITY_TZ.items():
            if city in lower:
                hits.append((city, tz))
    if not hits and ("time" in lower or "date" in lower):
        hits.append(("your timezone", default_tz))
    return hits


def run_agent(user_text: str, default_tz: str) -> tuple[str, list[ToolStep]]:
    steps: list[ToolStep] = []
    parts: list[str] = []

    for city, tz in find_requested_timezones(user_text, default_tz):
        r = get_time(tz)
        steps.append(ToolStep(tool="get_time", input=tz, result=r))
        parts.append(f"🕒 **{city.title()}**: {r}")

    expr = extract_math_expression(user_text)
    if expr:
        r = safe_calc(expr)
        steps.append(ToolStep(tool="calculator", input=expr, result=r))
        parts.append(f"🧮 **{expr}** = `{r}`")

    lower = user_text.lower()
    if any(k in lower for k in ["plan", "steps", "checklist", "todo", "to-do"]):
        r = make_plan(user_text)
        steps.append(ToolStep(tool="make_plan", input=user_text, result=r))
        parts.append(r)

    if not parts:
        parts.append(
            "I’m a tiny agent demo. I can use tools like **calculator**, **time lookup**, and a **planner**.\n\n"
            "Try:\n"
            "- `What time is it in Tokyo and London?`\n"
            "- `What is (12*7)/3?`\n"
            "- `Give me a plan to demo an agentic model in 24 hours`"
        )

    return "\n\n".join(parts), steps


# ----------------------------
# Gradio UI
# ----------------------------
def chat_fn(message: str, history, default_tz: str, show_tool_trace: bool) -> str:
    reply, steps = run_agent(message, default_tz=default_tz)

    if show_tool_trace and steps:
        trace_lines = []
        for s in steps:
            trace_lines.append(f"🛠️ **{s.tool}**\n- input: `{s.input}`\n- result: `{s.result}`")
        reply = "\n\n".join(trace_lines) + "\n\n---\n\n" + reply

    return reply


with gr.Blocks(title="Agentic Demo (Gradio)") as demo:
    gr.Markdown("# 🤖 Agentic Demo (Gradio)\nTool-using mini-agent: calculator • time lookup • planner")

    with gr.Row():
        default_tz = gr.Dropdown(
            label="Default timezone",
            choices=["Africa/Johannesburg", "UTC", "Europe/London", "America/New_York", "Asia/Tokyo"],
            value="Africa/Johannesburg",
        )
        show_tool_trace = gr.Checkbox(label="Show tool trace", value=True)

    gr.ChatInterface(
        fn=chat_fn,
        additional_inputs=[default_tz, show_tool_trace],
        examples=[
            ["What time is it in Tokyo and Johannesburg?"],
            ["What is (12*7)/3?"],
            ["Give me a plan to demo an agentic model in 24 hours"],
        ],
    )

if __name__ == "__main__":
    demo.launch()
