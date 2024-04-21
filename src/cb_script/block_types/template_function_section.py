from .block_base import block_base


class template_function_section(block_base):
    def __init__(self, line, name, macro_params, params, lines):
        self.line = line
        self.name = name
        self.macro_params = macro_params
        self.params = params
        self.lines = lines

    def compile(self, func):
        None

    def register(self, global_context):
        global_context.template_functions[self.name] = (
            self.macro_params,
            self.params,
            self.lines,
        )
        global_context.register_function_params(self.name, self.params)

    @property
    def block_name(self):
        return f'template function "{self.name}"'
