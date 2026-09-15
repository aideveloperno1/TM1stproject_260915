def main() -> None:
    """로컬 실행: uv run policy-signal-map"""
    import uvicorn

    uvicorn.run("policy_signal_map.app:app", host="127.0.0.1", port=8000, reload=True)
