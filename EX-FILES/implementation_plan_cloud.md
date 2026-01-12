# Veda AI: Cloud-Native Hybrid Architecture Plan

## 1. Objective
Eliminate all local system dependencies (Ollama running on localhost) by fully leveraging the **Ollama Cloud API**. This ensures the backend is 100% stateless, deployable to any cloud provider (Render, AWS), and highly reliable 24/7.

## 2. Architecture Shift

| Feature | Old (Local) | New (Cloud Native) |
| :--- | :--- | :--- |
| **Deep Reasoning** | User's Laptop (DeepSeek R1) | **Ollama Cloud** (DeepSeek R1) |
| **Fast Chat** | User's Laptop (Phi-3) | **Groq Cloud** (Llama 3.3 70B) |
| **Vision** | User's Laptop (Llama Vision) | **Gemini** (Flash 2.0) |
| **Availability** | Only when Laptop is ON | **24/7 Global Availability** |
| **Performance** | Limited by Laptop VRAM | **Enterprise Cloud GPU Speed** |

## 3. Implementation Steps

### Step 1: Service Renaming & Cleanup
*   **Rename** `local_llm.py` to `ollama_service.py` to reflect its new role as a cloud connector.
*   **Remove** strictly local checks (OS detection, localhost pings).
*   **Enforce** Cloud Connection: The service will fail hard (or fallback to OpenAI) if the key is invalid, rather than failing silently to localhost.

### Step 2: Model Router Optimization ("The Brain")
We will implement a **Task-Based Routing Matrix** to maximize quality and minimize cost:

| Task Type | Primary Model | Provider | Why? |
| :--- | :--- | :--- | :--- |
| **Complex Medical Query** | `deepseek-r1` | **Ollama Cloud** | Best-in-class reasoning (Chain of Thought) |
| **Diet Planning/Charts** | `deepseek-r1` | **Ollama Cloud** | Excellent at structured planning logic |
| **General Chat/Motivation** | `llama-3.3-70b` | **Groq** | Insane Speed (300 tokens/sec) |
| **Image/Food Analysis** | `gemini-2.0-flash` | **Gemini** | Native Multimodal Vision capabilities |
| **Hard Fallback** | `gpt-4o` | **OpenAI** | Ultimate reliability if others fail |

### Step 3: Verification Script
*   Create `scripts/test_cloud_connection.py` to verify:
    1.  Ollama Cloud Auth
    2.  Groq Auth
    3.  Gemini Auth
    4.  Router Decision Logic

### Step 4: Deployment Configuration
*   Update `render.yaml` to explicitly include `OLLAMA_API_KEY`.
*   This ensures that when we push to GitHub/Render, the cloud service knows how to access the reasoning models.

## 4. Next Actions
1.  **Refactor**: Convert `LocalLLMService` -> `OllamaCloudService`.
2.  **Verify**: Run the connection test.
3.  **Push**: Commit changes to Git.
