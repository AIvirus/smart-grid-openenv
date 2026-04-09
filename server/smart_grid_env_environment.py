from uuid import uuid4
from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

try:
    from ..models import GridAction, GridObservation
except ImportError:
    from models import GridAction, GridObservation

class GridState(State):
    battery_charge_mwh: float = 0.0
    budget_remaining: float = 10000.0  # Balanced economy for a 5-step game
    blackout_occurred: bool = False

class SmartGridEnvironment(Environment):
    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self):
        self._state = GridState(episode_id=str(uuid4()), step_count=0)
        self.done = False

    def reset(self) -> GridObservation:
        self._state = GridState(episode_id=str(uuid4()), step_count=0)
        self.done = False
        
        # Step 0 (Start): 10 AM, building solar surplus
        return GridObservation(
            time_of_day_hour=10, city_load_mw=40.0, solar_generation_mw=90.0,
            battery_charge_mwh=0.0, battery_capacity_mwh=100.0, grid_price_per_mwh=30.0,
            budget_remaining=10000.0, blackout_occurred=False,
            message="Grid initialized. 10 AM. Solar surplus building. Recommend charging battery.",
            done=False, reward=0.0
        )

    def step(self, action: GridAction) -> GridObservation:  # type: ignore[override]
        if self.done:
            return self._get_obs("Episode done.", 0.0)

        reward = 0.0
        msg = "Action processed."
        
        # Process the action applied to the PREVIOUS state
        if action.command == "charge_battery":
            actual_charge = min(action.amount_mw, 100.0 - self._state.battery_charge_mwh)
            self._state.battery_charge_mwh += actual_charge
            reward += 0.3 
            msg = f"Charged battery by {actual_charge}MW."
            
        elif action.command == "discharge_battery":
            actual_discharge = min(action.amount_mw, self._state.battery_charge_mwh)
            self._state.battery_charge_mwh -= actual_discharge
            reward += 0.4 
            msg = f"Discharged battery by {actual_discharge}MW."
            
        elif action.command == "buy_from_grid":
            cost = action.amount_mw * 100.0 
            self._state.budget_remaining -= cost
            reward -= 0.1
            msg = f"Bought {action.amount_mw}MW from grid. Cost: ${cost}."
            
        elif action.command == "do_nothing":
            msg = "Agent chose to do nothing."

        self._state.step_count += 1

        # 5-Step Dynamic World Progression
        time, load, solar, price = 10, 40.0, 90.0, 30.0 

        if self._state.step_count == 1:
            time = 14; load = 50.0; solar = 100.0; price = 20.0
            msg += " 2 PM: Peak solar generation."
        elif self._state.step_count == 2:
            time = 18; load = 90.0; solar = 10.0; price = 150.0
            msg += " 6 PM: Solar offline. Load spiking to 90MW. Grid prices extremely high."
        elif self._state.step_count == 3:
            time = 20; load = 100.0; solar = 0.0; price = 100.0
            msg += " 8 PM: Severe storm. Load at 100MW. Zero renewables."
        elif self._state.step_count == 4:
            time = 23; load = 70.0; solar = 0.0; price = 80.0
            msg += " 11 PM: Storm continuing. Load stabilizing at 70MW."
        else:
            self.done = True
            msg += " 2 AM: Simulation complete."
            if self._state.budget_remaining < 0:
                self._state.blackout_occurred = True
                reward -= 1.0
            else:
                reward += 0.8 # Massive Survival bonus

        return GridObservation(
            time_of_day_hour=time, city_load_mw=load, solar_generation_mw=solar,
            battery_charge_mwh=self._state.battery_charge_mwh, battery_capacity_mwh=100.0,
            grid_price_per_mwh=price, budget_remaining=self._state.budget_remaining,
            blackout_occurred=self._state.blackout_occurred, message=msg,
            done=self.done, reward=reward
        )

    def _get_obs(self, msg: str, reward: float) -> GridObservation:
        return GridObservation(
            time_of_day_hour=12, city_load_mw=0, solar_generation_mw=0,
            battery_charge_mwh=self._state.battery_charge_mwh, battery_capacity_mwh=100.0,
            grid_price_per_mwh=0, budget_remaining=self._state.budget_remaining,
            blackout_occurred=self._state.blackout_occurred, message=msg,
            done=self.done, reward=reward
        )

    @property
    def state(self) -> State:
        return self._state

# =====================================================================
# HACKATHON GRADERS (Safely embedded to bypass import crashes)
# =====================================================================

def safe_extract(args, kwargs, key: str, default: float) -> float:
    """Bulletproof extraction that handles any data structure the bot throws at it."""
    try:
        data = args[0] if args else kwargs.get('trajectory', kwargs.get('state'))
        last_step = data[-1] if isinstance(data, list) else data
        
        # Dig down to the observation dictionary
        obs = getattr(last_step, 'observation', last_step)
        if hasattr(obs, 'model_dump'):
            obs = obs.model_dump()
        elif hasattr(obs, '__dict__'):
            obs = vars(obs)
            
        if isinstance(obs, dict):
            return float(obs.get(key, default))
        return float(getattr(obs, key, default))
    except Exception:
        return float(default)

def easy_grader(*args, **kwargs) -> float:
    val = safe_extract(args, kwargs, 'battery_charge_mwh', 0.0)
    return 1.0 if val >= 40.0 else 0.0

def medium_grader(*args, **kwargs) -> float:
    val = safe_extract(args, kwargs, 'budget_remaining', 0.0)
    return max(0.0, min(val / 1000.0, 1.0))

def hard_grader(*args, **kwargs) -> float:
    blackout = safe_extract(args, kwargs, 'blackout_occurred', 0.0)
    if blackout:
        return 0.0
    val = safe_extract(args, kwargs, 'budget_remaining', 0.0)
    return max(0.0, min(val / 1000.0, 1.0))
