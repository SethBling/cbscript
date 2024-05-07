from .block_base import block_base


class selector_definition_block(block_base):
    def __init__(self, line, id, fullselector, uuid, items):
        self.line = line
        self.id = id
        self.uuid = uuid
        self.fullselector = fullselector
        self.items = items

    def compile(self, func):
        selector = func.set_atid(self.id, self.fullselector)
        selector.uuid = self.uuid

        for type, val in self.items:
            if type == "Tag":
                selector.tag = val
            elif type == "Path":
                path_id, path, data_type, scale = val
                if scale == None:
                    scale = func.scale
                else:
                    scale = scale.get_value(func)
                selector.paths[path_id] = (path, data_type, scale)
            elif type == "VectorPath":
                vector_id, path, data_type, scale = val
                if scale == None:
                    scale = func.scale
                else:
                    scale = scale.get_value(func)
                selector.vector_paths[vector_id] = (path, data_type, scale)
            elif type == "Method":
                func_section = val
                func_section.self_selector = "@" + self.id
                func_section.compile(func)
            elif type == "Pointer":
                pointer_id, pointer_selector = val
                selector.pointers[pointer_id] = pointer_selector
            elif type == "Array":
                def_block = val
                def_block.compile(func)
            elif type == "Predicate":
                def_block = val
                def_block.compile(func)
                selector.predicates[def_block.name] = True
            else:
                raise ValueError(
                    f'Unknown selector item type "{type}" in selector definition at line {get_line(line)}'
                )
