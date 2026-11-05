import os, datetime, subprocess
from dotenv import load_dotenv
load_dotenv()

def pick_client():
    if os.getenv("ANTHROPIC_API_KEY"):
        import anthropic
        return ("anthropic", anthropic.Anthropic())
    if os.getenv("OPENAI_API_KEY"):
        import openai
        return ("openai", openai.OpenAI())
    return ("ollama", None)

TOOLS = {
 "write_file": lambda p,c: open(p,"w").write(c) or "written",
 "read_file": lambda p: open(p).read(),
 "shell": lambda cmd: subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT),
 "date": lambda: datetime.datetime.now().isoformat(),
}

def run_task(task):
    provider, client = pick_client()
    memory = []
    if provider == "anthropic":
        resp = client.messages.create(
            model="claude-opus-4-5", max_tokens=1024,
            messages=[{"role":"user","content":task}],
            tools=[{"name":k,"description":k,"input_schema":{"type":"object","properties":{}}} for k in TOOLS])
        memory.append(resp)
    elif provider == "openai":
        resp = client.chat.completions.create(model="gpt-4o", messages=[{"role":"user","content":task}])
        memory.append(resp)
    else:
        import urllib.request, json
        data = json.dumps({"model":"qwen2.5:3b","prompt":task,"stream":False}).encode()
        r = urllib.request.urlopen("http://localhost:11434/api/generate", data=data)
        memory.append(json.loads(r.read()))
    # demo end-to-end
    fn = "/tmp/kilo/demo.txt"
    os.makedirs("/tmp/kilo", exist_ok=True)
    TOOLS["write_file"](fn, TOOLS["date"]())
    print("wrote", fn)
    print("read back:", TOOLS["read_file"](fn))
    return memory

if __name__ == "__main__":
    run_task("create a file with the current date, then read it back")
