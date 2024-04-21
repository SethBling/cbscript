class scratch_tracker:
    def __init__(self, global_context):
        self.scratch = {}
        self.temp = {}
        self.global_context = global_context
        self.scratch_allocation = 0
        self.temp_allocation = 0
        self.prefix = ""

    def get_temp_var(self):
        for key in self.temp.keys():
            if self.temp[key] == False:
                self.temp[key] = True
                return "temp" + str(key)

        newScratch = len(self.temp.keys())
        self.temp[newScratch] = True

        new_length = len(self.temp.keys())
        if new_length > self.temp_allocation:
            self.temp_allocation = new_length
            self.global_context.allocate_temp(new_length)

        return f"temp{newScratch}"

    def free_temp_var(self, id):
        num = int(id[len("temp") :])

        self.temp[num] = False

    def get_scratch(self):
        for key in self.scratch.keys():
            if self.scratch[key] == False:
                self.scratch[key] = True
                return f"{self.prefix}_scratch{key}"

        newScratch = len(self.scratch.keys())
        self.scratch[newScratch] = True

        new_length = len(self.scratch.keys())
        if new_length > self.scratch_allocation:
            self.scratch_allocation = new_length
            self.global_context.allocate_scratch(self.prefix, new_length)

        return f"{self.prefix}_scratch{newScratch}"

    def get_scratch_vector(self):
        return [self.get_scratch() for i in range(3)]

    def get_prefix(self):
        return f"{self.prefix}_scratch"

    def is_scratch(self, id):
        scratch_prefix = self.get_prefix()

        return id.startswith(scratch_prefix)

    def free_scratch(self, id):
        if not self.is_scratch(id):
            return

        scratch_prefix = self.get_prefix()
        num = int(id[len(scratch_prefix) :])

        self.scratch[num] = False

    def get_allocated_variables(self):
        ret = [
            f"{self.prefix}_scratch{i}" for i in range(self.scratch_allocation)
        ]
        ret += [f"temp{i}" for i in range(self.temp_allocation)]

        return ret

    def get_active_objectives(self):
        all_objectives = []
        for num in self.scratch:
            if self.scratch[num]:
                all_objectives.append(f"{self.prefix}_scratch{num}")

        for num in self.temp:
            if self.temp[num]:
                all_objectives.append(f"temp{num}")

        return all_objectives
