class with_items(object):
    def __init__(self, line, items):
        self.line = line
        self.items = items

    def compile(self, func):
        for item in self.items:
            if item[0] == 'expr':
                id = item[1]
                expr = item[2]

                expr_value_var = expr.compile(func)

                const_value = expr_value_var.get_const_value(func)
                
                if const_value != None:
                    func.add_command('data modify storage {}:global args.{} set value {}'.format(func.namespace, id, const_value))
                else:                
                    func.add_command('execute store result storage {}:global args.{} int 1 run scoreboard players get {} {}'.format(func.namespace, id, expr_value_var.selector, expr_value_var.objective))

            elif item[0] == 'string':
                id = item[1]
                str = item[2]

                func.add_command('data modify storage {}:global args.{} set value {}'.format(func.namespace, id, str))