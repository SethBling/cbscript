from cb_script.variable_types.scoreboard_var import scoreboard_var


class vector_here_expr(object):
    def __init__(self, scale):
        self.scale = scale

    def compile(self, func, assignto):
        if self.scale == None:
            scale = func.scale
        else:
            scale = self.scale.get_value(func)

        func.register_objective("_age")
        func.add_command("scoreboard players add @e _age 1")
        func.add_command("summon area_effect_cloud")
        func.add_command("scoreboard players add @e _age 1")

        return_components = []
        for i in range(3):
            if assignto == None:
                return_components.append(
                    scoreboard_var("Global", func.get_scratch())
                )
            else:
                return_components.append(assignto[i])

            func.add_command(
                f"execute store result score Global {return_components[i].objective} run data get entity @e[_age==1,limit=1] Pos[{i}] {scale}"
            )

        func.add_command("/kill @e[_age==1]")

        return return_components
