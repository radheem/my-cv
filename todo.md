# Project TODOs & Technical Limitations

## Known Limitations

### 1. Sequential Application Creation under Local/Small LLMs
*   **Limitation**: Running multiple application tailoring jobs concurrently or in rapid sequential succession is highly constrained when utilizing smaller, locally hosted LLM models (e.g., Ollama / Llama 3 models running on limited VRAM). 
*   **Behavior**: Serial execution is fully supported and enforced by our background Model Context Protocol FIFO Queue. However, sequentially batch-compiling 3 or more heavy applications back-to-back still results in context inflation and performance degradation over time on consumer-grade hardware.
*   **Best Practice**: For optimal performance and flawless output formatting, submit tailoring requests one-by-one, leaving a brief cooldown pause (e.g., 1–2 minutes) between submissions to let the local LLM model fully offload context and quiet down.
