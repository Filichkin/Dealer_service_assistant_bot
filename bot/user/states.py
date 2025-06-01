from aiogram.fsm.state import StatesGroup, State


class VinSteps(StatesGroup):
    vin = State()


class PartSteps(StatesGroup):
    part_number = State()


class MaintenanceSteps(StatesGroup):
    vin = State()
