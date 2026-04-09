from uuid import uuid4
from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

try:
    from ..models import GridAction, GridObservation
except ImportError:
    from models import GridAction, GridObservation

class GridState(State):
    battery_charge_mwh: float = 0.0
    budget_remaining: float = 10000.0
    blackout_occurred: bool = False

class SmartGridEnvironment(Environment):
    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self):
        self._state = GridState(episode_id=str(uuid4()), step_count=0)
        self.done = False
        self._task_id = "hard_storm_survival"

    def reset(self, task_id: str = "hard_storm_survival", **kwargs) -> GridObservation:
        self._state = GridState(episode_id=str(uuid4()), step_count=0)
        self.done = False
        self._task_id = task_id
        
        # --- DYNAMIC TASK CONFIGURATION ---
        if self._task_id == "easy_surplus":
            self._state.budget_remaining = 1000.0
            return GridObservation(
                time_of_day_hour=12, city_load_mw=40.0, solar_generation_mw=100.0,
                battery_charge_mwh=0.0, battery_capacity_mwh=100.0, grid_price_per_mwh=30.0,
                budget_remaining=self._state.budget_remaining, blackout_occurred=False,
                message="Task: Surplus Storage. 12 PM. High solar surplus detected. Charge battery.",
                done=False, reward=0.0
            )
        elif self._task_id == "medium_peak":
            self._state.battery_charge_mwh = 50.0  # Start with some charge to shave the peak
            self._state.budget_remaining = 1000.0
            return GridObservation(
                time_of_day_hour=18, city_load_mw=90.0, solar_generation_mw=10.0,
                battery_charge_mwh=self._state.battery_charge_mwh, battery_capacity_mwh=100.0, grid_price_per_mwh=150.0,
                budget_remaining=self._state.budget_remaining, blackout_occurred=False,
                message="Task: Peak Shaving. 6 PM. Demand spike detected. Grid prices extremely high. Discharge battery.",
                done=False, reward=0.0
            )
        else:
            self._state.budget_remaining = 10000.0
            return GridObservation(
                time_of_day_hour=10, city_load_mw=40.0, solar_generation_mw=90.0,
                battery_charge_mwh=0.0, battery_capacity_mwh=100.0, grid_price_per_mwh=30.0,
                budget_remaining=self._state.budget_remaining, blackout_occurred=False,
                message="Task: Survive the Storm. 10 AM. Solar surplus building. Prepare for evening storm.",
                done=False, reward=0.0
            )

    def step(self, action: GridAction) -> GridObservation:  # type: ignore[override]
        if self.done:
            return self._get_obs("Episode done.", 0.0)

        reward = 0.0
        msg = "Action processed."
        
        # Process physical energy transfer
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
            reward += 0.0 
            msg = f"Bought {action.amount_mw}MW from grid. Cost: ${cost}."
            
        elif action.command == "do_nothing":
            msg = "Agent chose to do nothing."

        self._state.step_count += 1

        # --- DYNAMIC TASK PROGRESSION ---
        if self._task_id == "easy_surplus" or self._task_id == "medium_peak":
            self.done = True
            msg += " Simulation complete (1 Step)."
            return self._get_obs(msg, reward)
            
        else:
            # 5-Step Dynamic World Progression (Hard Task)
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