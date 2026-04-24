"""LLM Router — routes to Demo/Ollama/API backends."""
import os, json
from pathlib import Path

class LLMRouter:
    def __init__(self, mode="demo", **kw):
        self.mode = mode; self.config = kw
        if mode == "api": self._init_api(**kw)
        elif mode == "ollama": self.ollama_url = kw.get("ollama_url","http://localhost:11434"); self.ollama_model = kw.get("ollama_model","mistral")

    def _init_api(self, **kw):
        self.api_provider = kw.get("api_provider","openai"); self.api_key = kw.get("api_key", os.getenv("OPENAI_API_KEY"))
        if self.api_provider == "openai":
            from openai import OpenAI; self.client = OpenAI(api_key=self.api_key); self.model = kw.get("model","gpt-4o")
        elif self.api_provider == "anthropic":
            import anthropic; self.client = anthropic.Anthropic(api_key=self.api_key); self.model = kw.get("model","claude-sonnet-4-20250514")

    def generate(self, prompt, system_prompt="", **kw):
        if self.mode == "demo":
            if "eligibility" in prompt.lower() or "criteria" in prompt.lower():
                return json.dumps({"rules":[{"field":"ECOG","operator":"in","value":[0,1]}],"criteria_type":"inclusion"})
            return "Demo mode placeholder."
        elif self.mode == "ollama":
            import requests
            full = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            r = requests.post(f"{self.ollama_url}/api/generate", json={"model":self.ollama_model,"prompt":full,"stream":False,"options":{"temperature":kw.get("temperature",0.1)}}, timeout=120)
            r.raise_for_status(); return r.json()["response"]
        elif self.mode == "api":
            if self.api_provider == "openai":
                msgs = ([{"role":"system","content":system_prompt}] if system_prompt else []) + [{"role":"user","content":prompt}]
                return self.client.chat.completions.create(model=self.model, messages=msgs, temperature=kw.get("temperature",0.1), max_tokens=2000).choices[0].message.content
            elif self.api_provider == "anthropic":
                return self.client.messages.create(model=self.model, max_tokens=2000, system=system_prompt or "", messages=[{"role":"user","content":prompt}]).content[0].text

    def generate_vision(self, prompt, image_b64, **kw):
        if self.mode == "demo": return json.dumps({"lab_values":{"ANC":{"value":2100,"unit":"cells/uL"}}})
        elif self.mode == "ollama":
            import requests
            r = requests.post(f"{self.ollama_url}/api/generate", json={"model":"llava","prompt":prompt,"images":[image_b64],"stream":False}, timeout=120)
            r.raise_for_status(); return r.json()["response"]
        elif self.mode == "api":
            if self.api_provider == "openai":
                return self.client.chat.completions.create(model="gpt-4o", messages=[{"role":"user","content":[{"type":"text","text":prompt},{"type":"image_url","image_url":{"url":f"data:image/png;base64,{image_b64}"}}]}], max_tokens=2000).choices[0].message.content

    def is_available(self):
        try:
            if self.mode == "demo": return True
            elif self.mode == "ollama":
                import requests; return requests.get(f"{self.ollama_url}/api/tags", timeout=5).status_code == 200
            elif self.mode == "api": return bool(self.api_key)
        except: return False
