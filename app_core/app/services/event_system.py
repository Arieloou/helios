from typing import Callable, Dict, List, Any


class EventSystem:
    _events: Dict[str, List[Callable]] = {}

    @classmethod
    def register(cls, event_name: str, callback: Callable) -> None:
        if event_name not in cls._events:
            cls._events[event_name] = []
        cls._events[event_name].append(callback)

    @classmethod
    def unregister(cls, event_name: str, callback: Callable) -> None:
        if event_name in cls._events:
            cls._events[event_name] = [cb for cb in cls._events[event_name] if cb != callback]

    @classmethod
    def emit(cls, event_name: str, data: Any = None) -> None:
        if event_name in cls._events:
            for callback in cls._events[event_name]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"Error dispatching event {event_name}: {e}")

    @classmethod
    def clear(cls, event_name: str = None) -> None:
        if event_name:
            cls._events[event_name] = []
        else:
            cls._events = {}


events = EventSystem()


def emit_maturity_changed(assessment_id: str, control_id: str, maturity: float):
    events.emit("maturity_changed", {
        "assessment_id": assessment_id,
        "control_id": control_id,
        "maturity": maturity,
    })


def emit_mapping_updated(mapping_id: str, assessment_id: str):
    events.emit("mapping_updated", {
        "mapping_id": mapping_id,
        "assessment_id": assessment_id,
    })


def emit_asset_modified(asset_id: str, assessment_id: str):
    events.emit("asset_modified", {
        "asset_id": asset_id,
        "assessment_id": assessment_id,
    })


def on_maturity_changed(callback: Callable):
    events.register("maturity_changed", callback)
    return callback


def on_mapping_updated(callback: Callable):
    events.register("mapping_updated", callback)
    return callback


def on_asset_modified(callback: Callable):
    events.register("asset_modified", callback)
    return callback