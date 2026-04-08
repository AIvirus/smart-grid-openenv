from typing import Dict
from openenv.core import EnvClient
from openenv.core.client_types import StepResult
from openenv.core.env_server.types import State

from models import GridAction, GridObservation

class SmartGridEnvClient(EnvClient[GridAction, GridObservation, State]):
    def _step_payload(self, action: GridAction) -> Dict:
        return {
            "command": action.command,
            "amount_mw": action.amount_mw
        }

    def _parse_result(self, payload: Dict) -> StepResult[GridObservation]:
        obs_data = payload.get("observation", {})
        observation = GridObservation(**obs_data)
        return StepResult(
            observation=observation,
            reward=payload.get("reward", 0.0),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: Dict) -> State:
        return State(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
        )

# # Copyright (c) Meta Platforms, Inc. and affiliates.
# # All rights reserved.
# #
# # This source code is licensed under the BSD-style license found in the
# # LICENSE file in the root directory of this source tree.

# """Smart Grid Env Environment Client."""

# from typing import Dict

# from openenv.core import EnvClient
# from openenv.core.client_types import StepResult
# from openenv.core.env_server.types import State

# from .models import SmartGridAction, SmartGridObservation


# class SmartGridEnv(
#     EnvClient[SmartGridAction, SmartGridObservation, State]
# ):
#     """
#     Client for the Smart Grid Env Environment.

#     This client maintains a persistent WebSocket connection to the environment server,
#     enabling efficient multi-step interactions with lower latency.
#     Each client instance has its own dedicated environment session on the server.

#     Example:
#         >>> # Connect to a running server
#         >>> with SmartGridEnv(base_url="http://localhost:8000") as client:
#         ...     result = client.reset()
#         ...     print(result.observation.echoed_message)
#         ...
#         ...     result = client.step(SmartGridAction(message="Hello!"))
#         ...     print(result.observation.echoed_message)

#     Example with Docker:
#         >>> # Automatically start container and connect
#         >>> client = SmartGridEnv.from_docker_image("smart_grid_env-env:latest")
#         >>> try:
#         ...     result = client.reset()
#         ...     result = client.step(SmartGridAction(message="Test"))
#         ... finally:
#         ...     client.close()
#     """

#     def _step_payload(self, action: SmartGridAction) -> Dict:
#         """
#         Convert SmartGridAction to JSON payload for step message.

#         Args:
#             action: SmartGridAction instance

#         Returns:
#             Dictionary representation suitable for JSON encoding
#         """
#         return {
#             "message": action.message,
#         }

#     def _parse_result(self, payload: Dict) -> StepResult[SmartGridObservation]:
#         """
#         Parse server response into StepResult[SmartGridObservation].

#         Args:
#             payload: JSON response data from server

#         Returns:
#             StepResult with SmartGridObservation
#         """
#         obs_data = payload.get("observation", {})
#         observation = SmartGridObservation(
#             echoed_message=obs_data.get("echoed_message", ""),
#             message_length=obs_data.get("message_length", 0),
#             done=payload.get("done", False),
#             reward=payload.get("reward"),
#             metadata=obs_data.get("metadata", {}),
#         )

#         return StepResult(
#             observation=observation,
#             reward=payload.get("reward"),
#             done=payload.get("done", False),
#         )

#     def _parse_state(self, payload: Dict) -> State:
#         """
#         Parse server response into State object.

#         Args:
#             payload: JSON response from state request

#         Returns:
#             State object with episode_id and step_count
#         """
#         return State(
#             episode_id=payload.get("episode_id"),
#             step_count=payload.get("step_count", 0),
#         )
