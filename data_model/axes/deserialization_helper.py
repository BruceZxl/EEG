_registry = None
_k_kind = "_kind"


def _get_registry():
    global _registry
    if _registry is not None:
        return _registry
    from . import Axis, BandAxis, BatchAxis, ChannelAxis, ComponentAxis
    from . import ContinuousTimeAxis, EChannelAxis, FrequencyAxis, RealAxis, TimeAxis
    from . import ComponentDef, ChannelDef, EChannelDef
    _registry = {
        kind.__name__: kind
        for kind in [
            Axis, BandAxis, BatchAxis, ChannelAxis, ComponentAxis, ContinuousTimeAxis,
            EChannelAxis, FrequencyAxis, RealAxis, TimeAxis,
            ComponentDef, ChannelDef, EChannelDef
        ]}
    return _registry


def resolve(obj):
    return _get_registry()[obj.pop(_k_kind)].from_json(obj)


def resolve_nested(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            obj[k] = resolve_nested(v)
        kind = obj.get(_k_kind)
        if kind is not None:
            obj = resolve(obj)
    elif isinstance(obj, list):
        for i, e in enumerate(obj):
            obj[i] = resolve_nested(e)
    return obj


def add_kind(self, obj):
    obj[_k_kind] = type(self).__qualname__
    return obj
