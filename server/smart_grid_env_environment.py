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

# # Copyright (c) Meta Platforms, Inc. and affiliates.
# # All rights reserved.
# #
# # This source code is licensed under the BSD-style license found in the
# # LICENSE file in the root directory of this source tree.

# """
# Smart Grid Env Environment Implementation.

# A simple test environment that echoes back messages sent to it.
# Perfect for testing HTTP server infrastructure.
# """

# from uuid import uuid4

# from openenv.core.env_server.interfaces import Environment
# from openenv.core.env_server.types import State

# try:
#     from ..models import SmartGridAction, SmartGridObservation
# except ImportError:
#     from models import SmartGridAction, SmartGridObservation


# class SmartGridEnvironment(Environment):
#     """
#     A simple echo environment that echoes back messages.

#     This environment is designed for testing the HTTP server infrastructure.
#     It maintains minimal state and simply echoes back whatever message it receives.

#     Example:
#         >>> env = SmartGridEnvironment()
#         >>> obs = env.reset()
#         >>> print(obs.echoed_message)  # "Smart Grid Env environment ready!"
#         >>>
#         >>> obs = env.step(SmartGridAction(message="Hello"))
#         >>> print(obs.echoed_message)  # "Hello"
#         >>> print(obs.message_length)  # 5
#     """

#     # Enable concurrent WebSocket sessions.
#     # Set to True if your environment isolates state between instances.
#     # When True, multiple WebSocket clients can connect simultaneously, each
#     # getting their own environment instance (when using factory mode in app.py).
#     SUPPORTS_CONCURRENT_SESSIONS: bool = True

#     def __init__(self):
#         """Initialize the smart_grid_env environment."""
#         self._state = State(episode_id=str(uuid4()), step_count=0)
#         self._reset_count = 0

#     def reset(self) -> SmartGridObservation:
#         """
#         Reset the environment.

#         Returns:
#             SmartGridObservation with a ready message
#         """
#         self._state = State(episode_id=str(uuid4()), step_count=0)
#         self._reset_count += 1

#         return SmartGridObservation(
#             echoed_message="Smart Grid Env environment ready!",
#             message_length=0,
#             done=False,
#             reward=0.0,
#         )

#     def step(self, action: SmartGridAction) -> SmartGridObservation:  # type: ignore[override]
#         """
#         Execute a step in the environment by echoing the message.

#         Args:
#             action: SmartGridAction containing the message to echo

#         Returns:
#             SmartGridObservation with the echoed message and its length
#         """
#         self._state.step_count += 1

#         message = action.message
#         length = len(message)

#         # Simple reward: longer messages get higher rewards
#         reward = length * 0.1

#         return SmartGridObservation(
#             echoed_message=message,
#             message_length=length,
#             done=False,
#             reward=reward,
#             metadata={"original_message": message, "step": self._state.step_count},
#         )

#     @property
#     def state(self) -> State:
#         """
#         Get the current environment state.

#         Returns:
#             Current State with episode_id and step_count
#         """
#         return self._state
