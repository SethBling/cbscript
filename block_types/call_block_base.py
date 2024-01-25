from block_base import block_base

class call_block_base(block_base):
    def compile_with_macro_items(self, func):
        if self.with_macro_items == None:
            return
        
        for item in self.with_macro_items:
            if item[0] == 'expr':
                id = item[1]
                expr = item[2]

                expr_value_var = expr.compile(func)
                func.add_command('execute store result storage {}:global args.{} int 1 run scoreboard players get {} {}'.format(func.namespace, id, expr_value_var.selector, expr_value_var.objective))

            elif item[0] == 'string':
                id = item[1]
                str = item[2]

                func.add_command('data modify storage {}:global args.{} set value {}'.format(func.namespace, id, str))
