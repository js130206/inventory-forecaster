# 📦 AI-Driven Raw Material Procurement Forecaster

## 🚀 Overview
A real-time raw material procurement forecaster designed to prevent stockouts in small business and F&B supply chains. Built under hackathon constraints.

## 🤖 How IBM Bob Was Used in the Development Process
We leveraged IBM Bob as our primary AI co-pilot and architectural engine:
1. **Ideation & Prompting:** We used IBM Bob to rapidly architect a single-file Streamlit dashboard calculating stock depletion rates and supply chain bottlenecks.
2. **Code Generation & Optimization:** Bob generated the core pandas data processing pipeline, automatically implementing safety handlers to prevent division-by-zero errors when tracking zero-usage items.
3. **Refactoring & Validation:** Edge-case constraints were fed back into IBM Bob to ensure clean memory management and robust error handling before final deployment.

## 🛠️ Tech Stack
* Python
* Streamlit
* Pandas
