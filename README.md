---
title: Smart Grid Dispatcher Environment
emoji: ⚡
colorFrom: yellow
colorTo: green
sdk: docker
pinned: false
app_port: 8000
base_path: /web
tags:
  - openenv
---

# ⚡ Smart Grid Dispatcher (OpenEnv)

## 1. Overview & Motivation
The **Smart Grid Dispatcher** is a cyber-physical Reinforcement Learning environment built for the MetaScaler OpenEnv Hackathon. 

**Motivation:** Grid stability and energy arbitrage are multi-billion-dollar real-world challenges. Unlike traditional software-based automation environments, this environment tests an LLM's ability to act as an automated dispatcher, balancing renewable energy generation (solar), physical battery storage constraints, and volatile market pricing to prevent city-wide blackouts.

## 2. Observation & Action Spaces

**Observation Space (`GridObservation`):**
The agent receives real-time telemetry representing the physical grid state:
* `time_of_day_hour` (int): Current hour (0-23).
* `city_load_mw` (float): Current power demand.
* `solar_generation_mw` (float): Current solar power.
* `battery_charge_mwh` (float): Energy stored in the battery (Max 100).
* `grid_price_per_mwh` (float): Dynamic cost to buy main grid power.
* `budget_remaining` (float): The city's remaining financial budget.
* `blackout_occurred` (bool): Failsafe flag.

**Action Space (`GridAction`):**
The agent executes one action per step:
* `command` (Literal): `charge_battery`, `discharge_battery`, `buy_from_grid`, or `do_nothing`.
* `amount_mw` (float): The amount of Megawatts to transfer.

## 3. Task Descriptions & Difficulty
1. **Surplus Storage (Easy):** The agent must identify a noon solar surplus and charge the battery.
2. **Peak Shaving (Medium):** The agent must discharge the battery to cover a 6 PM demand spike, avoiding purchasing power at peak-hour prices.
3. **Survive the Storm (Hard):** A 5-step scenario where the agent must build a battery reserve during the day, deploy it efficiently during a severe evening storm (0MW solar), and strategically buy from the grid just before bankruptcy.

## 4. Baseline Performance Scores
Using `llama-3.3-70b-versatile` as the baseline model, the agent successfully navigates the Hard task (Survive the Storm) over 5 steps.
* **Success Rate:** True
* **Average Score:** 0.420
* **Rewards Trajectory:** [0.30, 0.30, 0.40, 0.40, 0.70]
*(Meaningful Reward Function: partial points for efficient battery usage, penalties for expensive grid purchases, and a large survival bonus for finishing the episode without triggering a blackout).*

## 5. Setup & Usage Instructions

### Local Execution
1. Clone this repository and ensure `openenv-core` is installed.
2. Create a `.env` file with `API_BASE_URL`, `MODEL_NAME`, and `HF_TOKEN`.
3. Start the environment server: `uvicorn server.app:app --port 8000`
4. Run the baseline evaluation in a separate terminal: `python inference.py`

### Project Structure
* `openenv.yaml`: OpenEnv manifest and Graders
* `models.py`: Action and Observation Pydantic models
* `client.py` / `inference.py`: Baseline evaluation scripts
* `server/smart_grid_env_environment.py`: Core physics engine