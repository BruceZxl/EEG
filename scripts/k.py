def k(cls, *names):
    for name in names:
        print(f"k_{name} = \"{name}\"")
    print()
    op, cl = "{", "}"
    saves = ", ".join([f"{cls}.k_{name}: self.{name}" for name in names])
    print(f"""    def to_json(self) -> JsonObjectType:
        return super().to_json() | {op}{saves}{cl}
    """)


# k("ComponentAxis", "components")
# k("ChannelDef", "unit", "unit_m")
k("Tensor", "_kind", "shape_def")