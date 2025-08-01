# 🧠 Naren GPT - Your Personal Local AI Chat Assistant

**Naren GPT** is a self-hosted, privacy-first conversational assistant that brings ChatGPT-like capabilities directly to your desktop — no subscriptions, no limits, no cloud dependencies. Powered by [Ollama](https://ollama.com/) it lets you run powerful LLMs (like LLaMA 3, Qwen, Mistral, etc.) locally with a clean, persistent chat interface.

---

![ai-llm](https://github.com/user-attachments/assets/cf1e82c4-0d5b-4447-91d3-a776590ce790)

👉🏼 https://github.com/naren4b/naren-gpt

## ✨ Features

- ✅ Runs locally — your data never leaves your machine
- ✅ No per-token or monthly subscription costs
- ✅ Works offline — even without internet
- ✅ No rate limits or usage throttling
- ✅ Faster, low-latency responses
- ✅ Easy model switching with [Ollama](https://ollama.com/)
- ✅ Use arbitrary prompt templates, agents, and pipelines
- ✅ Extend with voice, vision, or image generation
- ✅ Compatible with CPUs and GPUs — no special hardware needed

---

## 🏁 Getting Started

### 1. Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com/) installed `curl -fsSL https://ollama.com/install.sh | sh`
- At least 8–16 GB RAM for optimal performance (depending on model)
- Install streamlit `pip install streamlit`

### 2. Clone and Run
```bash
# Server Mode
ollama serve
# pull the model 
ollama pull llama3

curl http://127.0.0.1:11434/api/tags
git clone https://github.com/yourusername/naren-gpt.git
cd naren-gpt
# python3 -m pip install --upgrade pip
pip install -r requirements.txt
bash run.sh
```

# Open The browser 

http://localhost:8501
<img width="1910" height="933" alt="image" src="https://github.com/user-attachments/assets/e3ccfa64-f744-4585-b172-38a64353fb8f" />


*_It will be slow in local machines_ 















# Naren GPT – A Local AI Chat App using Streamlit + Ollama + LLMs

Naren GPT is a lightweight, locally hosted AI assistant built with **Streamlit** and powered by **Ollama** and open-source **LLMs like LLaMA 3**. It provides a clean, persistent chat interface — similar to ChatGPT — but with full control, privacy, and offline functionality.

# When to Self-Host?
Scale: Cost-effective once GPU utilization is high.

Performance: Better for specialized workloads (e.g., RAG, embeddings).

Privacy/Sovereignty: Legal or regulatory constraints, on-prem, hybrid/multi-cloud.

## 🚀 Features

- 🧠 Supports local LLMs (LLaMA 3, Mistral, etc.)
- 💬 Persistent multi-turn chat with conversation memory
- 🎨 Simple, clean UI built using Streamlit
- 🔒 Runs completely offline – your data stays with you
- ⚙️ Easily customizable and extendable
