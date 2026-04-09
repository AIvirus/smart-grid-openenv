# inference.py

import os
import json
import textwrap
import asyncio
from typing import List, Optional
from openai import OpenAI

# Absolute imports
from client import SmartGridEnvClient
from models import GridAction

# --- STRICT CHECKLIST COMPLIANCE ---
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.groq.com/openai/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")
HF_TOKEN = os.getenv("HF_TOKEN")  # No defaults, exact name required by judges

TASK_NAME = os.getenv("SMART_GRID_TASK", "hard_storm_survival")
BENCHMARK = "smart_grid_env"
MAX_STEPS = 5
MAX_POSSIBLE_REWARD = 2.0  # Used to normalize the final score

SYSTEM_PROMPT = textwrap.dedent(
    """
    You are an AI Smart Grid Dispatcher.
    RULES:
    1. If solar_generation_mw is much higher than city_load_mw, output {"command": "charge_battery", "amount_mw": 50.0}
    2. If city_load_mw > solar_generation_mw AND battery_charge_mwh > 0, output {"command": "discharge_battery", "amount_mw": 50.0}
    3. If city_load_mw > solar_generation_mw AND battery_charge_mwh == 0, output {"command": "buy_from_grid", "amount_mw": 100.0}
    4. If none of the above apply, output {"command": "do_nothing", "amount_mw": 0.0}
    CRITICAL: Output EXACTLY ONE JSON object. No extra text.
    """
).strip()

def log_start(task: str, env: str, model: str):
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]):
    error_val = error if error else "null"
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={error_val}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: List[float]):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)

async def main():
    client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)
    env = SmartGridEnvClient(base_url="http://localhost:8000")
    
    # FIX: Initialize these variables so the `finally` block doesn't crash on failure
    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False
    
    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)
    
    try:
        result = await env.reset()
        
        for step in range(1, MAX_STEPS + 1):
            if result.done:
                break
                
            obs_dict = result.observation.model_dump()
            
            try:
                # Ask the LLM what to do based on the current grid state
                completion = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": f"Current Grid State: {json.dumps(obs_dict)}"}
                    ],
                    temperature=0.0
                )
                response_text = completion.choices[0].message.content.strip()
                
                # Robust Markdown stripping
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].strip()
                
                # Robust multi-JSON filtering
                if '}\n{' in response_text:
                    response_text = response_text.split('}\n{')[0] + '}'
                elif '}{' in response_text:
                    response_text = response_text.split('}{')[0] + '}'
                    
                action_data = json.loads(response_text)
                if isinstance(action_data, list):
                    action_data = action_data[0]
                
                agent_action = GridAction(**action_data)
                action_str = f"{agent_action.command}({agent_action.amount_mw}MW)"
                error = None
                
            except Exception as e:
                # Fallback action if the AI outputs garbage text
                agent_action = GridAction(command="do_nothing", amount_mw=0.0)
                action_str = "do_nothing(0.0MW)"
                clean_error = str(e).replace('\n', ' ')
                error = f"Err: {clean_error}"[:50] 

            # Execute step on the server
            result = await env.step(agent_action)
            reward = result.reward or 0.0
            done = result.done
            
            rewards.append(reward)
            steps_taken = step
            
            log_step(step=step, action=action_str, reward=reward, done=done, error=error)
            
            if done:
                break
                
        # FIX: Calculate final score and strictly clamp between [0.0, 1.0]
        raw_score = sum(rewards) / MAX_POSSIBLE_REWARD
        score = min(max(raw_score, 0.0), 1.0)
        success = score > 0.0
        
    except Exception as run_error:
        print(f"[DEBUG] Execution Error: {run_error}")
        
    finally:
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

if __name__ == "__main__":
    asyncio.run(main())
