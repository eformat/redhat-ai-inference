#!/usr/bin/env python3
"""A minimal chat client for the Model-as-a-Service endpoint from Module 3."""
import json, os, sys, time
import urllib.error
import urllib.request

API_URL = os.environ.get("MAAS_URL", "").rstrip("/")
API_KEY = os.environ.get("MAAS_API_KEY", "")
MODEL = os.environ.get("MAAS_MODEL", "")
PROMPT = os.environ.get("MAAS_PROMPT", "Explain Model-as-a-Service in one sentence.")
INTERVAL = int(os.environ.get("MAAS_INTERVAL", "0"))
SYSTEM = "You are a concise assistant."

def chat_completions(model, messages, max_tokens=256):
    """POST one Chat Completions request and return the parsed response."""
    payload = json.dumps({"model": model, "messages": messages, "max_tokens": max_tokens}).encode("utf-8")
    request = urllib.request.Request(
        f"{API_URL}/v1/chat/completions", data=payload, method="POST",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))

def discover_model():
    """Return the first ready model ID from the /v1/models catalog."""
    request = urllib.request.Request(f"{API_URL}/v1/models", headers={"Authorization": f"Bearer {API_KEY}"})
    with urllib.request.urlopen(request, timeout=30) as response:
        catalog = json.loads(response.read().decode("utf-8"))
    ready = [m for m in catalog.get("data", []) if m.get("ready", True)]
    if not ready:
        raise RuntimeError("no ready models in the catalog — check Module 3")
    return ready[0]["id"]

def print_completion(completion):
    """Print one completion and its token usage."""
    choice = completion["choices"][0]
    usage = completion.get("usage", {})
    print(f"assistant> {choice['message']['content'].strip()}")
    print(f"[tokens: {usage.get('prompt_tokens', '?')} in / {usage.get('completion_tokens', '?')} out]")

def run_interactive(model):
    """Chat loop: read prompts from the terminal until you type quit."""
    print("Chat client ready. Type a prompt, or 'quit' to exit.")
    history = []
    while True:
        try:
            user_input = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not user_input or user_input.lower() in ("quit", "exit"):
            break
        messages = [{"role": "system", "content": SYSTEM}] + history + [{"role": "user", "content": user_input}]
        try:
            completion = chat_completions(model, messages)
        except urllib.error.HTTPError as exc:
            print(f"HTTP {exc.code}: {exc.reason} — check your endpoint URL and API key")
            continue
        except urllib.error.URLError as exc:
            print(f"endpoint unreachable: {exc}")
            continue
        print_completion(completion)
        history += [{"role": "user", "content": user_input},
                    {"role": "assistant", "content": completion["choices"][0]["message"]["content"]}]
    print("Bye!")

def run_request_loop(model):
    """Deployed mode: send PROMPT every INTERVAL seconds and log results."""
    print(f"Request loop started — one completion every {INTERVAL}s.")
    while True:
        messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": PROMPT}]
        try:
            completion = chat_completions(model, messages)
            print_completion(completion)
        except urllib.error.HTTPError as exc:
            print(f"HTTP {exc.code}: {exc.reason} — check your endpoint URL and API key")
        except urllib.error.URLError as exc:
            print(f"endpoint unreachable: {exc}")
        time.sleep(INTERVAL)

def main():
    if not API_URL or not API_KEY:
        sys.exit("Set MAAS_URL and MAAS_API_KEY before starting the client.")
    model = MODEL or discover_model()
    print(f"Using model: {model}")
    if INTERVAL > 0:
        run_request_loop(model)
    else:
        run_interactive(model)

if __name__ == "__main__":
    main()
