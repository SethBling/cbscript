from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cb_script.global_context import global_context


class scratch_tracker:
    def __init__(self, global_context: global_context) -> None:
        self.scratch: dict[int, bool] = {}
        self.temp: dict[int, bool] = {}
        self.global_context = global_context
        self.scratch_allocation = 0
        self.temp_allocation = 0
        self.prefix = ""

    def get_temp_var(self) -> str:
        for key in self.temp:
            if not self.temp[key]:
                self.temp[key] = True
                return "temp" + str(key)

        newScratch = len(self.temp)
        self.temp[newScratch] = True

        new_length = len(self.temp)
        if new_length > self.temp_allocation:
            self.temp_allocation = new_length
            self.global_context.allocate_temp(new_length)

        return f"temp{newScratch}"

    def free_temp_var(self, id_: str) -> None:
        num = int(id_[len("temp") :])

        self.temp[num] = False

    def get_scratch(self) -> str:
        for key in self.scratch:
            if not self.scratch[key]:
                self.scratch[key] = True
                return f"{self.prefix}_scratch{key}"

        newScratch = len(self.scratch)
        self.scratch[newScratch] = True

        new_length = len(self.scratch)
        if new_length > self.scratch_allocation:
            self.scratch_allocation = new_length
            self.global_context.allocate_scratch(self.prefix, new_length)

        return f"{self.prefix}_scratch{newScratch}"

    def get_scratch_vector(self) -> list[str]:
        return [self.get_scratch() for i in range(3)]

    def get_prefix(self) -> str:
        return f"{self.prefix}_scratch"

    def is_scratch(self, id_: str) -> bool:
        scratch_prefix = self.get_prefix()

        return id_.startswith(scratch_prefix)

    def free_scratch(self, id_: str) -> None:
        if not self.is_scratch(id_):
            return

        scratch_prefix = self.get_prefix()
        num = int(id[len(scratch_prefix) :])

        self.scratch[num] = False

    def get_allocated_variables(self) -> list[str]:
        ret = [
            f"{self.prefix}_scratch{i}" for i in range(self.scratch_allocation)
        ]
        ret += [f"temp{i}" for i in range(self.temp_allocation)]

        return ret

    def get_active_objectives(self) -> list[str]:
        all_objectives = []
        for num in self.scratch:
            if self.scratch[num]:
                all_objectives.append(f"{self.prefix}_scratch{num}")

        for num in self.temp:
            if self.temp[num]:
                all_objectives.append(f"temp{num}")

        return all_objectives
