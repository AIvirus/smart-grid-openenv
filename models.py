from typing import Literal, Optional
from pydantic import Field, BaseModel
from openenv.core.env_server.types import Action, Observation

class GridAction(Action):
    """Action for the Smart Grid - managing energy flow."""
    command: Literal["charge_battery", "discharge_battery", "buy_from_grid", "do_nothing"] = Field(
        ..., description="The action to take with the energy."
    )
    amount_mw: float = Field(
        default=0.0, description="Amount of Megawatts (MW) to transfer."
    )

class GridObservation(Observation):
    """Observation of the current city grid state."""
    time_of_day_hour: int = Field(default=12, description="Current hour (0-23)")
    city_load_mw: float = Field(default=0.0, description="Current power demand from the city")
    solar_generation_mw: float = Field(default=0.0, description="Current power from solar panels")
    battery_charge_mwh: float = Field(default=0.0, description="Current energy stored in the battery")
    battery_capacity_mwh: float = Field(default=100.0, description="Maximum battery capacity")
    grid_price_per_mwh: float = Field(default=50.0, description="Current price of electricity on the main grid")
    budget_remaining: float = Field(default=1000.0, description="City's remaining energy budget")
    blackout_occurred: bool = Field(default=False, description="True if demand was not met")
    message: str = Field(default="", description="Status message from the grid control system")

# # Copyright (c) Meta Platforms, Inc. and affiliates.
# # All rights reserved.
# #
# # This source code is licensed under the BSD-style license found in the
# # LICENSE file in the root directory of this source tree.

# """
# Data models for the Smart Grid Env Environment.

# The smart_grid_env environment is a simple test environment that echoes back messages.
# """

# from openenv.core.env_server.types import Action, Observation
# from pydantic import Field


# class SmartGridAction(Action):
#     """Action for the Smart Grid Env environment - just a message to echo."""

#     message: str = Field(..., description="Message to echo back")


# class SmartGridObservation(Observation):
#     """Observation from the Smart Grid Env environment - the echoed message."""

#     echoed_message: str = Field(default="", description="The echoed message")
#     message_length: int = Field(default=0, description="Length of the echoed message")
