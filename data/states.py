from aiogram.fsm.state import StatesGroup, State


class CurrentState(StatesGroup):
    in_progress = State(state="parsing in progress")
    available = State(state="available")
