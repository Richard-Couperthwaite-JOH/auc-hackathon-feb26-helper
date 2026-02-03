# Project Overview

This repository contains tools and dashboards developed for the AUC Hackathon. Below is a summary of the available tools, dashboards, and instructions to set up the environment.

---

## Tool Examples

1. **LangGraph**
   - A tool for building and managing state graphs.
   - Documentation: [LangGraph Documentation](https://www.langchain.com/langgraph)

2. **OpenAI Agents SDK**
   - A framework for integrating OpenAI agents.
   - Documentation: [OpenAI Agents SDK Documentation](https://openai.github.io/openai-agents-python/agents/)

3. **CrewAI**
   - A utility for performing advanced calculations.
   - Documentation: [CrewAI Documentation](https://docs.crewai.com/)

4. **AG2 (AutoGen)**
   - A utility for performing advanced calculations.
   - Documentation: [AutoGen Documentation](https://docs.ag2.ai/latest/?utm_referrer=https%3A%2F%2Fpypi.org%2F)

---

## Setting Up the Environment

1. Install the required dependencies:
   ```bash
   uv sync
   ```

2. Run the desired dashboard:
   - For streamlit:
     ```bash
     uv run streamlit run streamlit/dashboard.py
     ```
   - For gradio:
     ```bash
     uv run gradio/dashboard.py
     ```

For further details, refer to the respective documentation links provided above.