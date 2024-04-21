from .block_base import block_base


class call_block_base(block_base):
    def compile_with_macro_items(self, func):
        if self.with_macro_items == None:
            return

        self.with_macro_items.compile(func)
