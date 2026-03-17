from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class WizardStates(StatesGroup):
    platform = State()
    niche = State()
    product = State()
    audience = State()
    goal = State()
    tone = State()
    length = State()
    summary = State()
    generating_demo = State()
    demo_shown = State()
    generating_full = State()
