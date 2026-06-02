import json
from datetime import datetime, timezone
from pathlib import Path


LOG_PATH = Path(__file__).with_name("agent_logs.jsonl")
RUNS_DIR = Path(__file__).with_name("runs")


def log_event(event_type, payload):
    record = {
        "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "event_type": event_type,
        "payload": payload,
    }
    with LOG_PATH.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")


def save_run(state):
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = RUNS_DIR / f"run_{timestamp}.json"
    data = {
        "goal": state.goal,
        "plan": state.plan,
        "steps": state.steps,
        "status": state.status,
        "final_answer": state.final_answer,
        "error_count": state.error_count,
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
