from ply import *
import traceback
import scriptlex
from block_types.advancement_definition_block import advancement_definition_block
from block_types.array_definition_block import array_definition_block
from block_types.block_definition_block import block_definition_block
from block_types.block_switch_block import block_switch_block
from block_types.block_id_switch_block import block_id_switch_block
from block_types.block_tag_block import block_tag_block
from block_types.clock_section import clock_section
from block_types.command_block import command_block
from block_types.comment_block import comment_block
from block_types.create_block import create_block
from block_types.define_name_block import define_name_block
from block_types.entity_tag_block import entity_tag_block
from block_types.execute_block import execute_block
from block_types.for_index_block import for_index_block
from block_types.for_selector_block import for_selector_block
from block_types.function_call_block import function_call_block
from block_types.function_section import function_section
from block_types.import_block import import_block
from block_types.item_tag_block import item_tag_block
from block_types.loot_table_definition_block import loot_table_definition_block
from block_types.macro_call_block import macro_call_block
from block_types.macro_section import macro_section
from block_types.method_call_block import method_call_block
from block_types.move_block import move_block
from block_types.nbt_data_block import nbt_data_block
from block_types.nbt_remove_block import nbt_remove_block
from block_types.pop_block import pop_block
from block_types.pointer_decl_block import pointer_decl_block
from block_types.predicate_definition_block import predicate_definition_block
from block_types.print_block import print_block
from block_types.push_block import push_block
from block_types.python_assignment_block import python_assignment_block
from block_types.python_for_block import python_for_block
from block_types.python_if_block import python_if_block
from block_types.python_import_block import python_import_block
from block_types.python_tuple_assignment_block import python_tuple_assignment_block
from block_types.reset_section import reset_section
from block_types.scoreboard_assignment_block import scoreboard_assignment_block
from block_types.selector_assignment_block import selector_assignment_block
from block_types.selector_definition_block import selector_definition_block
from block_types.shaped_recipe_block import shaped_recipe_block
from block_types.switch_block import switch_block
from block_types.tell_block import tell_block
from block_types.template_function_call_block import template_function_call_block
from block_types.template_function_section import template_function_section
from block_types.title_block import title_block
from block_types.vector_assignment_block import vector_assignment_block
from block_types.vector_assignment_scalar_block import vector_assignment_scalar_block
from block_types.while_block import while_block
from data_types.block_case import block_case
from data_types.const_number import const_number
from data_types.const_string import const_string
from data_types.number_macro_path import number_macro_path
from data_types.python_identifier import python_identifier
from data_types.interpreted_python import interpreted_python
from data_types.relcoord_vector import relcoord_vector
from data_types.relcoord import relcoord
from data_types.relcoords import relcoords
from nbt_types.block_nbt_path import block_nbt_path
from nbt_types.entity_nbt_path import entity_nbt_path
from nbt_types.nbt_json import nbt_json
from nbt_types.storage_nbt_path import storage_nbt_path
from scalar_expressions.binop_expr import binop_expr
from scalar_expressions.create_expr import create_expr
from scalar_expressions.dot_expr import dot_expr
from scalar_expressions.func_expr import func_expr
from scalar_expressions.method_expr import method_expr
from scalar_expressions.unary_expr import unary_expr
from variable_types.array_const_var import array_const_var
from variable_types.array_expr_var import array_expr_var
from variable_types.block_path_var import block_path_var
from variable_types.command_var import command_var
from variable_types.scale_var import scale_var
from variable_types.scoreboard_var import scoreboard_var
from variable_types.selector_id_var import selector_id_var
from variable_types.storage_path_var import storage_path_var
from variable_types.virtualint_var import virtualint_var
from vector_expressions.sel_vector_var_expr import sel_vector_var_expr
from vector_expressions.vector_binop_scalar_expr import vector_binop_scalar_expr
from vector_expressions.vector_binop_vector_expr import vector_binop_vector_expr
from vector_expressions.vector_expr import vector_expr
from vector_expressions.vector_here_expr import vector_here_expr
from vector_expressions.vector_var_const_vector import vector_var_const_vector
from vector_expressions.vector_var_expr import vector_var_expr
import mcfunction

tokens = scriptlex.tokens

precedence = (
			   ('left', 'PLUS','MINUS'),
			   ('left', 'TIMES','DIVIDE','MOD'),
			   ('left', 'POWER'),
			   ('right','UMINUS'),
			   ('left', 'VECTOR'),
			   ('left', 'COMP'),
)

#### Parsed
def p_parsed_assignment(p):
	'''parsed : program'''
	p[0] = ('program', p[1])

def p_parsed_lib(p):
	'''parsed : import lib'''
	p[0] = ('lib', p[2])
	
def p_parsed_expr(p):
	'''parsed : expr'''
	p[0] = ('expr', p[1])
	
#### Program
def p_program(p):
	'''program : optcomments dir string newlines optdesc optscale top_level_blocks'''
	p[0] = {}
	p[0]['dir'] = p[3]
	p[0]['desc'] = p[5]
	p[0]['scale'] = p[6]
	p[0]['lines'] = p[7]
	
### Lib
def p_lib(p):
	'''lib : top_level_blocks'''
	p[0] = {}
	p[0]['lines'] = p[1]

#### Optdesc
def p_optdesc(p):
	'''optdesc : desc string newlines
			   | empty'''
	if len(p) < 4:
		p[0] = 'No Description'
	else:
		p[0] = p[2]
	
#### Optscale
def p_optscale(p):
	'''optscale : scale integer newlines'''
	p[0] = int(p[2])

def p_optscale_none(p):
	'''optscale : empty'''
	p[0] = 1000
	
#### Sections
def p_section_commented(p):
	'''section_commented : optcomments section'''
	
	# TODO: Put the comments into the sections
	p[0] = p[2]
	

def p_optcomments(p):
	'''optcomments : COMMENT optnewlines optcomments'''
	p[0] = [p[1]] + p[3]
	
def p_optcomments_empty(p):
	'''optcomments : empty'''
	p[0] = []
	
def p_section(p):
	'''section : clocksection
			   | functionsection
			   | resetsection
			   | macrosection
			   | template_function_section'''
	p[0] = p[1]

#### Reset Section	
def p_resetsection(p):
	'''resetsection : reset newlines blocklist end'''
	p[0] = reset_section(p.lineno(1), p[3])
	
	
def validate_mcfunction_name(str):
	for ch in str:
		if ch.isupper():
			print('"{0}" is not a valid mcfunction name.'.format(str))
			raise SyntaxError()
	
#### Clock Section
def p_clocksection(p):
	'''clocksection : clock ID newlines blocklist end'''
	validate_mcfunction_name(p[2])
	
	p[0] = clock_section(p.lineno(1), p[2], p[4])
	
#### Function Section
def p_functionsection(p):
	'''functionsection : function FUNCTIONID id_list RPAREN newlines blocklist end'''
	validate_mcfunction_name(p[2])

	p[0] = function_section(p.lineno(1), p[2], p[3], p[6])

#### Template Function Section
def p_template_function_section(p):
	'''template_function_section : function ID LCURLY macro_params RCURLY LPAREN id_list RPAREN newlines blocklist end'''
	validate_mcfunction_name(p[2])
	
	p[0] = template_function_section(p.lineno(1), p[2], p[4], p[7], p[10])

#### Macro section
def p_macrosection(p):
	'''macrosection : macro DOLLAR FUNCTIONID macro_args newlines blocklist end'''
	
	p[0] = macro_section(p.lineno(1), p[3], p[4], p[6])

def p_macro_args(p):
	'''macro_args : macro_params RPAREN'''
	p[0] = p[1]
	
def p_macro_args_empty(p):
	'''macro_args : empty'''
	p[0] = []

def p_macro_params(p):
	'''macro_params : DOLLAR ID COMMA macro_params'''
	p[0] = [p[2]] + p[4]

def p_macro_params_one(p):
	'''macro_params : DOLLAR ID'''
	p[0] = [p[2]]
	
def p_macro_params_empty(p):
	'''macro_params : empty'''
	p[0] = []

#### Function call
def p_function_call_namespace(p):
	'''function_call : ID COLON FUNCTIONID exprlist RPAREN opt_with_macros'''
	p[0] = function_call_block(p.lineno(1), p[1]+p[2]+p[3], p[4], p[6])

def p_function_call(p):
	'''function_call : FUNCTIONID exprlist RPAREN opt_with_macros'''
	p[0] = function_call_block(p.lineno(1), p[1], p[2], p[4])

def p_method_call(p):
	'''method_call : fullselector DOT FUNCTIONID exprlist RPAREN opt_with_macros'''
	p[0] = method_call_block(p.lineno(1), p[1], p[3], p[4], [6])

def p_opt_with_macros_true(p):
	'''opt_with_macros : with macros'''
	p[0] = True

def p_opt_with_macros_false(p):
	'''opt_with_macros : empty'''
	p[0] = False
	
#### Expression list
def p_exprlist_multiple(p):
	'''exprlist : exprlist COMMA expr'''
	p[0] = p[1]
	p[0].append(p[3])
	
def p_exprlist_single(p):
	'''exprlist : expr'''
	p[0] = [p[1]]

def p_exprlist_empty(p):
	'''exprlist : empty'''
	p[0] = []

#### Template Function Call
def p_template_function_call(p):
	'''template_function_call : ID LCURLY macro_call_params RCURLY LPAREN exprlist RPAREN opt_with_macros'''
	p[0] = template_function_call_block(p.lineno(1), p[1], p[3], p[6], p[8])
	
#### Macro call	
def p_macro_call(p):
	'''macro_call : DOLLAR FUNCTIONID macro_call_args'''
	p[0] = macro_call_block(p.lineno(1), p[2], p[3])
	
def p_macro_call_args(p):
	'''macro_call_args : macro_call_params RPAREN'''
	p[0] = p[1]
	
def p_macro_call_args_empty(p):
	'''macro_call_args : empty'''
	p[0] = []
	
def p_macro_call_params(p):
	'''macro_call_params : macro_call_param COMMA macro_call_params'''
	p[0] = [p[1]] + p[3]

def p_macro_call_params_one(p):
	'''macro_call_params : macro_call_param'''
	p[0] = [p[1]]
	
def p_macro_call_params_empty(p):
	'''macro_call_params : empty'''
	p[0] = []
	
def p_macro_call_param_number(p):
	'''macro_call_param : const_value'''
	p[0] = p[1]
	
#### Newlines
def p_newlines(p):
	'''newlines : NEWLINE newlines
				| NEWLINE'''
	p[0] = None
	
def p_optnewlines(p):
	'''optnewlines : newlines
				   | empty'''
				   
#### Identifier List
def p_id_list(p):
	'''id_list : ID COMMA id_list'''
	p[0] = [p[1]] + p[3]

def p_id_list_one(p):
	'''id_list : ID'''
	p[0] = [p[1]]

def p_id_list_empty(p):
	'''id_list : empty'''
	p[0] = []
	
#### Top Level Blocks
def p_top_level_blocks(p):
	'''top_level_blocks : pythonassignment newlines top_level_blocks
						| python_tuple_assignment newlines top_level_blocks
						| selector_assignment newlines top_level_blocks
						| selector_define_block newlines top_level_blocks
						| block_define_block newlines top_level_blocks
						| blocktag newlines top_level_blocks
						| entitytag newlines top_level_blocks
						| itemtag newlines top_level_blocks
						| array_definition newlines top_level_blocks
						| import_statement newlines top_level_blocks
						| python_import_statement newlines top_level_blocks
						| print_block newlines top_level_blocks
						| pointer_decl newlines top_level_blocks
						| shaped_recipe newlines top_level_blocks
						| advancement_definition newlines top_level_blocks
						| loot_table_definition newlines top_level_blocks
						| predicate_definition newlines top_level_blocks
						| section_commented newlines top_level_blocks'''
	p[0] = [p[1]] + p[3]
	
def p_top_level_blocks_comment(p):
	'''top_level_blocks : COMMENT newlines top_level_blocks'''
	p[0] = p[3]

def p_top_level_blocks_empty(p):
	'''top_level_blocks : empty'''
	p[0] = []

#### Import	
def p_import_statement(p):
	'''import_statement : import ID'''
	p[0] = import_block(p.lineno(1), p[2])

#### Import	
def p_python_import_statement(p):
	'''python_import_statement : import ID DOT ID'''
	if p[4] == 'py':
		p[0] = python_import_block(p.lineno(1), p[2])
	elif p[4] == 'cblib':
		p[0] = import_block(p.lineno(1), p[2])
	else:
		raise SyntaxError('Unknown import file type: "{}.{}"'.format(p[2], p[4]))
	
#### Variable
def p_variable_selector(p):
	'''variable : fullselector DOT ID
				| ID DOT ID'''
	p[0] = scoreboard_var(p[1], p[3])
	
def p_variable_global(p):
	'''variable : ID'''
	p[0] = scoreboard_var('Global', p[1])
	
def p_variable_array_const(p):
	'''variable : ID LBRACK virtualinteger RBRACK'''
	p[0] = array_const_var('Global', p[1], p[3])

def p_variable_array_expr(p):
	'''variable : ID LBRACK expr RBRACK'''
	p[0] = array_expr_var('Global', p[1], p[3])

def p_variable_array_const_selector(p):
	'''variable : fullselector DOT ID LBRACK virtualinteger RBRACK'''
	p[0] = array_const_var(p[1], p[3], p[5])
	
def p_variable_array_expr_selector(p):
	'''variable : fullselector DOT ID LBRACK expr RBRACK'''
	p[0] = array_expr_var(p[1], p[3], p[5])
	
def p_variable_block_path_nocoords(p):
	'''variable : LBRACK ID RBRACK DOT ID'''
	p[0] = block_path_var(p[2], p[5], None, [])

def p_variable_block_path_coords(p):
	'''variable : LBRACK ID at relcoords RBRACK DOT ID'''
	p[0] = block_path_var(p[2], p[7], p[4], [])

def p_variable_block_macro_path_nocoords(p):
	'''variable : LBRACK ID RBRACK DOT ID LBRACK macro_call_params RBRACK'''
	p[0] = block_path_var(p[2], p[5], None, p[7])

def p_variable_block_macro_path_coords(p):
	'''variable : LBRACK ID at relcoords RBRACK DOT ID LBRACK macro_call_params RBRACK'''
	p[0] = block_path_var(p[2], p[7], p[4], p[9])
	
def p_variable_virtualint(p):
	'''variable : virtualinteger'''
	p[0] = virtualint_var(p[1])
	
def p_variable_scale(p):
	'''variable : scale'''
	p[0] = scale_var()
	
def p_variable_selector_ref(p):
	'''variable : REF fullselector'''
	p[0] = selector_id_var(p[2])
	
def p_variable_command(p):
	'''variable : success NEWLINE COMMAND
	            | result NEWLINE COMMAND'''
	p[0] = command_var(p[1], p[3])
	
def p_variable_storage(p):
	'''variable : COLON data_path'''
	p[0] = storage_path_var(None, p[2])
	
def p_variable_storage_target(p):
	'''variable : ID COLON data_path'''
	p[0] = storage_path_var(p[1], p[3])
	
#### Blocklist
def p_optcomment(p):
	'''optcomment : COMMENT'''
	p[0] = [comment_block(p.lineno(1), p[1])]
	
def p_optcomment_empty(p):
	'''optcomment : empty'''
	p[0] = []

def p_blocklist_multiple(p):
	'''blocklist : codeblock optcomment newlines blocklist'''
	p[0] = p[2] + [p[1]] + p[4]

def p_blocklist_empty(p):
	'''blocklist : empty'''
	p[0] = []

#### Block
def p_block_comment(p):
	'''codeblock : COMMENT'''
	p[0] = comment_block(p.lineno(1), p[1])

def p_block_command(p):
	'''codeblock : COMMAND'''
	p[0] = command_block(p.lineno(1), p[1])
	
def p_block_move(p):
	'''codeblock : move fullselector relcoords'''
	p[0] = move_block(p.lineno(1), p[2], p[3])

def p_block_for(p):
	'''codeblock : for DOLLAR ID in const_value newlines blocklist end'''
	p[0] = python_for_block(p.lineno(1), [p[3]], p[5], p[7])
	
def p_block_for_tuple(p):
	'''codeblock : for python_tuple in const_value newlines blocklist end'''
	p[0] = python_for_block(p.lineno(1), p[2], p[4], p[6])
	
def p_block_print(p):
	'''codeblock : print_block'''
	p[0] = p[1]
	
def p_print_block(p):
	'''print_block : PRINT const_value RPAREN'''
	p[0] = print_block(p.lineno(1), p[2])
	
#### Execute
def p_else_list_empty(p):
	'''else_list : empty'''
	p[0] = []

def p_else_list(p):
	'''else_list : else_item else_list'''
	p[0] = [p[1]] + p[2]

def p_else_item_execute(p):
	'''else_item : else execute_items newlines blocklist'''
	p[0] = (p[2], p[4])
	
def p_else_item_empty(p):
	'''else_item : else newlines blocklist'''
	p[0] = (None, p[3])

def p_block_if_command(p):
	'''codeblock : if const_value newlines blocklist else_list end'''
	p[0] = python_if_block(p.lineno(1), p[2], p[4], p[5])

def p_execute_as_id_global(p):
	'''codeblock : as variable newlines blocklist else_list end'''
	p[0] = execute_block(p.lineno(1), [('AsId', (p[2], None))], p[4], p[5])

def p_execute_as_id_type_global(p):
	'''codeblock : as variable LPAREN ATID RPAREN newlines blocklist else_list end'''
	p[0] = execute_block(p.lineno(1), [('AsId', (p[2], p[4]))], p[7], p[8])

def p_execute_as_id_do_global(p):
	'''codeblock : as variable do codeblock else_list'''
	p[0] = execute_block(p.lineno(1), [('AsId', (p[2], None))], [p[4]])

def p_execute_as_id_do_type_global(p):
	'''codeblock : as variable LPAREN ATID RPAREN do codeblock'''
	p[0] = execute_block(p.lineno(1), [('AsId', (p[2], p[4]))], [p[7]])

def p_execute_as_create(p):
	'''codeblock : as create_block newlines blocklist else_list end'''
	p[0] = execute_block(p.lineno(1), [('AsCreate', p[2])], p[4])

def p_execute_as_create_do(p):
	'''codeblock : as create_block do codeblock'''
	p[0] = execute_block(p.lineno(1), [('AsCreate', p[2])], [p[4]])
	
def p_execute_chain(p):
	'''codeblock : execute_items newlines blocklist else_list end'''
	p[0] = execute_block(p.lineno(1), p[1], p[3], p[4])
	
def p_execute_chain_inline(p):
	'''codeblock : execute_items do codeblock
				 | execute_items then codeblock'''
	p[0] = execute_block(p.lineno(1), p[1], [p[3]])

#### Execute Items	
def p_execute_items_one(p):
	'''execute_items : execute_item'''
	p[0] = [p[1]]
	
def p_execute_items(p):
	'''execute_items : execute_item execute_items'''
	p[0] = [p[1]] + p[2]
	
def p_execute_if_condition(p):
	'''execute_item : if conditions'''
	p[0] = ('If', p[2])

def p_execute_unless_condition(p):
	'''execute_item : unless conditions'''
	p[0] = ('Unless', p[2])
	
def p_execute_as(p):
	'''execute_item : as fullselector'''
	p[0] = ('As', p[2])

def p_execute_rotated(p):
	'''execute_item : rotated fullselector'''
	p[0] = ('Rotated', p[2])
	
def p_execute_facing_coords(p):
	'''execute_item : facing relcoords'''
	p[0] = ('FacingCoords', p[2])
	
def p_execute_facing_entity(p):
	'''execute_item : facing fullselector'''
	p[0] = ('FacingEntity', p[2])

def p_execute_align(p):
	'''execute_item : align ID'''
	if p[2] not in ['x','y','z','xy','xz','yz','xyz']:
		raise SyntaxError('Must align to a combination of x, y, and z axes, not "{}", at line {}'.format(p[2], p.lineno(2)))
	p[0] = ('Align', p[2])
	
def p_opt_anchor(p):
	'''opt_anchor : eyes
	              | feet'''
	p[0] = p[1]
	
def p_opt_anchor_empty(p):
	'''opt_anchor : empty'''
	p[0] = None
	
def p_execute_at_selector(p):
	'''execute_item : at fullselector opt_anchor'''
	p[0] = ('At', (p[2], None, p[3]))
	
def p_execute_at_relcoords(p):
	'''execute_item : at opt_anchor relcoords'''
	p[0] = ('At', (None, p[3], p[2]))
	
def p_execute_at_selector_relcoords(p):
	'''execute_item : at fullselector opt_anchor relcoords'''
	p[0] = ('At', (p[2], p[4], p[3]))
	
def p_execute_at_vector(p):
	'''execute_item : at vector_expr'''
	p[0] = ('AtVector', (None, p[2]))

def p_execute_at_vector_scale(p):
	'''execute_item : at LPAREN const_value RPAREN vector_expr'''
	p[0] = ('AtVector', (p[3], p[5]))

def p_execute_in_dimension(p):
	'''execute_item : in overworld
					| in the_end
					| in the_nether'''
	p[0] = ('In', p[2])

#### For selector	
def p_for_selector(p):
	'''codeblock : for ATID in fullselector newlines blocklist end'''
	p[0] = for_selector_block(p.lineno(1), p[2], p[4], p[6])

#### Conditions
def p_conditions_one(p):
	'''conditions : condition'''
	p[0] = [p[1]]
	
def p_conditions(p):
	'''conditions : condition and conditions'''
	p[0] = [p[1]] + p[3]

def p_condition_bool_predicate(p):
	'''condition : predicate ID'''
	p[0] = ('predicate', p[2])
	
def p_condition_fullselector(p):
	'''condition : fullselector'''
	p[0] = ('selector', p[1])
	
def p_condition_score(p):
	'''condition : expr LT expr
				 | expr LEQ expr
				 | expr EQUALEQUAL expr
				 | expr GT expr
				 | expr GEQ expr'''
	op = p[2]
	if op == '==':
		op = '='
	p[0] = ('score', (p[1], op, p[3]))	

def p_condition_vector_equality(p):
	'''condition : vector_var EQUALEQUAL vector_var'''
	p[0] = ('vector_equality', (p[1], p[3]))

def p_condition_bool(p):
	'''condition : expr'''
	p[0] = ('score', (p[1], '>', virtualint_var('0')))

def p_condition_not_bool(p):
	'''condition : not expr'''
	p[0] = ('score', (p[2], '<=', virtualint_var(0)))
	
def p_opt_block_state(p):
	'''opt_block_state : LBRACK block_states RBRACK'''
	p[0] = p[1] + p[2] + p[3]
	
def p_opt_block_state_none(p):
	'''opt_block_state : empty'''
	p[0] = ''
	
def p_block_states_one(p):
	'''block_states : ID EQUALS ID
					| ID EQUALS virtualinteger
					| facing EQUALS ID
					| facing EQUALS virtualinteger'''
	p[0] = p[1] + p[2] + p[3]
	
def p_block_states_list(p):
	'''block_states : ID EQUALS ID COMMA block_states
					| ID EQUALS virtualinteger COMMA block_states
					| facing EQUALS ID COMMA block_states
					| facing EQUALS virtualinteger COMMA block_states'''
	p[0] = p[1] + p[2] + p[3] + p[4] + p[5]
	
def p_opt_tile_data(p):
	'''opt_tile_data : json_object'''
	p[0] = p[1]

def p_opt_tile_data_empty(p):
	'''opt_tile_data : empty'''
	p[0] = ''
	
def p_condition_block(p):
	'''condition : block relcoords ID opt_block_state opt_tile_data'''
	p[0] = ('block', (p[2], p[3] + p[4] + p[5]))

def p_condition_block_virtual(p):
	'''condition : block relcoords DOLLAR ID opt_block_state opt_tile_data'''
	p[0] = ('block', (p[2], p[3]+p[4]+p[5]+p[6])) 

def p_condition_block_nocoords(p):
	'''condition : block ID opt_block_state opt_tile_data'''
	p[0] = ('block', (relcoords(), p[2] + p[3] + p[4]))

def p_condition_block_virtual_nocoords(p):
	'''condition : block DOLLAR ID opt_block_state opt_tile_data'''
	p[0] = ('block', (relcoords(), p[2]+p[3]+p[4]+p[5])) 

	
def p_condition_nbt_path(p):
	'''condition : nbt_object
	             | nbt_list'''
	p[0] = ('nbt_path', p[1])
	
#### If python
def p_block_ifelse_command(p):
	'''codeblock : if const_value newlines blocklist else newlines blocklist end'''
	p[0] = python_if_block(p.lineno(1), p[2], p[4], p[7])

#### While
def p_block_while(p):
	'''codeblock : while conditions newlines blocklist end'''
	p[0] = while_block(p.lineno(1), [('If', p[2])], p[4])
	
def p_block_while_execute(p):
	'''codeblock : while conditions execute_items newlines blocklist end'''
	p[0] = while_block(p.lineno(1), [('If', p[2])] + p[3], p[5])

#### For	
def p_block_for_index_by(p):
	'''codeblock : for variable EQUALS expr to expr by expr newlines blocklist end'''
	p[0] = for_index_block(p.lineno(1), p[2], p[4], p[6], p[8], p[10])
	
def p_block_for_index(p):
	'''codeblock : for variable EQUALS expr to expr newlines blocklist end'''
	p[0] = for_index_block(p.lineno(1), p[2], p[4], p[6], None, p[8])
	
#### Switch
def p_switch(p):
	'''codeblock : switch expr newlines cases end'''
	p[0] = switch_block(p.lineno(1), p[2], p[4])
	
def p_cases_one(p):
	'''cases : switch_case newlines'''
	p[0] = [p[1]]
	
def p_cases_multiple(p):
	'''cases : switch_case newlines cases'''
	p[0] = [p[1]] + p[3]
	
def p_switch_case_single(p):
	'''switch_case : case const_value newlines blocklist end'''
	p[0] = ('range', (p[2], p[2], p[4]), p.lineno(1))

def p_switch_case_range(p):
	'''switch_case : case const_value to const_value newlines blocklist end'''
	p[0] = ('range', (p[2], p[4], p[6]), p.lineno(1))
	
def p_switch_case_python(p):
	'''switch_case : case DOLLAR ID in const_value newlines blocklist end'''
	p[0] = ('python', (p[3], p[5], p[7]), p.lineno(1))

#### Block Switch
def p_block_switch(p):
	'''codeblock : switch block opt_coords newlines block_cases end'''
	p[0] = block_switch_block(p.lineno(1), p[3], p[5], False)
	
def p_block_id_switch(p):
	'''codeblock : switch block expr newlines block_cases end'''
	p[0] = block_id_switch_block(p.lineno(1), p[3], p[5], False)

def p_block_data_switch(p):
	'''codeblock : switch block_data opt_coords newlines block_cases end'''
	p[0] = block_switch_block(p.lineno(1), p[3], p[5], True)
	
def p_block_data_id_switch(p):
	'''codeblock : switch block_data expr newlines block_cases end'''
	p[0] = block_id_switch_block(p.lineno(1), p[3], p[5], True)
	
def p_opt_coords(p):
	'''opt_coords : at relcoords'''
	p[0] = p[2]
	
def p_opt_coords_empty(p):
	'''opt_coords : empty'''
	p[0] = relcoords()
	
def p_block_cases_empty(p):
	'''block_cases : empty'''
	p[0] = []
	
def p_block_cases_multi(p):
	'''block_cases : block_case newlines block_cases'''
	p[0] = [p[1]] + p[3]

def p_block_case_default(p):
	'''block_case : default newlines blocklist end'''
	p[0] = block_case(None, None, p[3], True)
	
def p_block_case_specific(p):
	'''block_case : case ID opt_block_properties newlines blocklist end
				  | case TIMES opt_block_properties newlines blocklist end'''
	p[0] = block_case(p[2], p[3], p[5], False)
	
def p_opt_block_properties_empty(p):
	'''opt_block_properties : empty'''
	p[0] = []
	
def p_opt_block_properties(p):
	'''opt_block_properties : LBRACK block_properties RBRACK'''
	p[0] = p[2]
	
def p_block_property(p):
	'''block_property : ID EQUALS ID
					  | ID EQUALS virtualinteger
					  | facing EQUALS ID
					  | facing EQUALS virtualinteger'''
	p[0] = (p[1], p[3])
	
def p_block_properties_one(p):
	'''block_properties : block_property'''
	p[0] = [p[1]]
	
def p_block_properties_multi(p):
	'''block_properties : block_property COMMA block_properties'''
	p[0] = [p[1]] + p[3]
	
#### Tell/Title	
def p_block_tell(p):
	'''codeblock : tell fullselector string'''
	p[0] = tell_block(p.lineno(1), p[2], p[3])
	
def p_block_title(p):
	'''codeblock : title fullselector string
				 | subtitle fullselector string
				 | actionbar fullselector string'''
	p[0] = title_block(p.lineno(1), p[1], p[2], None, p[3])
	
	
def p_block_title_times(p):
	'''codeblock : title fullselector const_value const_value const_value string
				 | subtitle fullselector const_value const_value const_value string
				 | actionbar fullselector const_value const_value const_value string'''
	p[0] = title_block(p.lineno(1), p[1], p[2], (p[3], p[4], p[5]), p[6])
	
def p_block_selector_assignment(p):
	'''codeblock : selector_assignment
				 | selector_define_block'''
	p[0] = p[1]
	
def p_block_function_call(p):
	'''codeblock : function_call
				 | method_call
				 | macro_call
				 | template_function_call
				 | pythonassignment
				 | python_tuple_assignment'''
	p[0] = p[1]
	
#### Push/pop
def p_block_push(p):
	'''codeblock : push exprlist'''
	p[0] = push_block(p.lineno(1), p[2])
	
def p_var_list_one(p):
	'''var_list : variable'''
	p[0] = [p[1]]
	
def p_var_list_empty(p):
	'''var_list : empty'''
	p[0] = []
	
def p_var_list(p):
	'''var_list : variable COMMA var_list'''
	p[0] = [p[1]] + p[3]
	
def p_block_pop(p):
	'''codeblock : pop var_list'''
	p[0] = pop_block(p.lineno(1), p[2])
	
#### String
def p_string(p):
	'''string : NORMSTRING'''
	p[0] = p[1][1:-1]
	
#### Number
def p_integer(p):
	'''integer : DECIMAL
	           | HEX
			   | BINARY'''
	p[0] = p[1]
	
def p_integer_minus(p):
	'''integer : MINUS DECIMAL
	           | MINUS HEX
			   | MINUS BINARY'''
	p[0] = str(-int(p[2]))

def p_number_integer(p):
	'''number : integer
			  | float_val'''
	p[0] = p[1]
	
def p_float_val(p):
	'''float_val : FLOAT'''
	p[0] = p[1]
	
def p_float_val_minus(p):
	'''float_val : MINUS FLOAT'''
	p[0] = str(-float(p[2]))
	
#### Qualifier list
def p_qualifiers_multiple(p):
	'''qualifiers : qualifiers COMMA qualifier
				  | qualifiers and qualifier'''
	p[0] = p[1] + "," + p[3]

def p_qualifiers_one(p):
	'''qualifiers : qualifier'''
	p[0] = p[1]

def p_qualifiers(p):
	'''qualifiers : empty'''
	p[0] = ""
	
#### Qualifier
def p_qualifier_binop(p):
	'''qualifier : ID EQUALS virtualinteger
				 | ID EQUALS ID
				 | name EQUALS ID
				 | ID EQUALEQUAL virtualinteger
				 | ID GEQ virtualinteger
				 | ID LEQ virtualinteger
				 | ID GT virtualinteger
				 | ID LT virtualinteger
				 | ID EQUALS json_object'''
	p[0] = p[1] + p[2] + p[3]
	
def p_qualifier_builtin(p):
	'''qualifier : ID EQUALS virtualnumber DOT DOT virtualnumber
				 | ID EQUALS DOT DOT virtualnumber
				 | ID EQUALS virtualnumber DOT DOT'''
	p[0] = ''.join(p[1:])

def p_qualifier_empty(p):
	'''qualifier : ID EQUALS'''
	p[0] = p[1] + p[2]
	
def p_qualifier_is_not(p):
	'''qualifier : ID EQUALS NOT ID'''
	p[0] = p[1] + p[2] + p[3] + p[4]

def p_qualifier_is(p):
	'''qualifier : ID'''
	p[0] = p[1]

def p_qualifier_not(p):
	'''qualifier : not ID'''
	p[0] = 'not ' + p[2]

#### Full Selector
def p_fullselector(p):
	'''fullselector : ATID'''
	p[0] = '@{0}[]'.format(p[1])

def p_fullselector_qualifiers(p):
	'''fullselector : ATID LBRACK virtualinteger RBRACK
					| ATID LBRACK qualifiers RBRACK'''
	p[0] = '@{0}[{1}]'.format(p[1], p[3])
	
#### Relative Coordinates
def p_relcoord_number(p):
	'''relcoord : const_value'''
	p[0] = relcoord('', p[1])

def p_relcoord_relnumber(p):
	'''relcoord : TILDE const_value'''
	p[0] = relcoord('~', p[2])
	
def p_relcoord_relzero(p):
	'''relcoord : TILDE
	            | TILDEEMPTY'''
	p[0] = relcoord('~', const_string(''))
	
# Optional Virtual Number
def p_optional_const_value(p):
	'''optional_const_value : const_value'''
	p[0] = p[1]

def p_optional_const_value_empty(p):
	'''optional_const_value : empty'''
	p[0] = const_string('')

#### Local Coordinates
def p_localcoord_localnumber(p):
	'''localcoord : POWER optional_const_value'''
	p[0] = relcoord('^', p[2])
	
# Relcoords
def p_relcoords(p):
	'''relcoords : relcoord relcoord relcoord
				 | localcoord localcoord localcoord'''
	p[0] = relcoords((p[1], p[2], p[3]))
	
def p_relcoords_vector_relative(p):
	'''relcoords : TILDE const_vector
				 | POWER const_vector'''
	p[0] = relcoord_vector(p.lineno(1), p[1], p[2])

def p_relcoords_vector(p):
	'''relcoords : const_vector'''
	p[0] = relcoord_vector(p.lineno(1), '', p[1])
	
		
#### Virtual number    
def p_const_value_interpreted(p):
	'''const_value : DOLLAR string'''
	p[0] = interpreted_python(p[2], p.lineno(1))
	
def p_const_value_expr(p):
	'''const_value : pyexpr'''
	p[0] = interpreted_python(p[1], p.lineno(1))
	
def p_const_vector(p):
	'''const_vector : LT pyexpr GT %prec VECTOR'''
	p[0] = interpreted_python(p[2], p.lineno(1))
	
def p_pyexpr_single(p):
	'''pyexpr : number
	          | NORMSTRING'''
	p[0] = p[1]
	
def p_pyexpr_binop(p):
	'''pyexpr : pyexpr PLUS pyexpr %prec PLUS
	          | pyexpr MINUS pyexpr %prec MINUS
	          | pyexpr TIMES pyexpr %prec TIMES
	          | pyexpr DIVIDE pyexpr %prec DIVIDE
	          | pyexpr MOD pyexpr %prec MOD
	          | pyexpr EQUALEQUAL pyexpr %prec COMP
	          | pyexpr LEQ pyexpr %prec COMP
	          | pyexpr GEQ pyexpr %prec COMP
	          | pyexpr LT pyexpr %prec COMP
	          | pyexpr GT pyexpr %prec COMP'''
	p[0] = p[1] + p[2] + p[3]
	
def p_pyexpr_binop_double(p):
	'''pyexpr : pyexpr NOT EQUALS pyexpr %prec COMP
	          | pyexpr TIMES TIMES pyexpr %prec POWER'''
	p[0] = p[1] + p[2] + p[3] + p[4]
	
def p_pyexpr_binop_spaced(p):
	'''pyexpr : pyexpr or pyexpr
			  | pyexpr and pyexpr'''
	p[0] = p[1] + ' ' + p[2] + ' ' + p[3]
	
def p_pyexpr_unary(p):
	'''pyexpr : MINUS pyexpr'''
	p[0] = p[1] + p[2]
	
def p_pyexpr_expr_list_empty(p):
	'''pyexpr_expr_list : empty'''
	p[0] = ''

def p_pyexpr_expr_list_one(p):
	'''pyexpr_expr_list : pyexpr'''
	p[0] = p[1]

def p_pyexpr_expr_list_multi(p):
	'''pyexpr_expr_list : pyexpr COMMA optnewlines pyexpr_expr_list'''
	p[0] = p[1] + p[2] + p[4]
	
def p_pyexpr_array(p):
	'''pyexpr : LBRACK optnewlines pyexpr_expr_list optnewlines RBRACK
	          | LPAREN optnewlines pyexpr_expr_list optnewlines RPAREN'''
	p[0] = p[1] + p[3] + p[5]
	
def p_pyexpr_function_call(p):
	'''pyexpr : DOLLAR FUNCTIONID optnewlines pyexpr_expr_list optnewlines RPAREN'''
	p[0] = p[2] + '(' + p[4] + p[6]
	
def p_pyexpr_array_lookup(p):
	'''pyexpr : pyexpr LBRACK pyexpr RBRACK'''
	p[0] = p[1] + p[2] + p[3] + p[4]
	
def p_pyexpr_member(p):
	'''pyexpr : pyexpr DOT pyexpr'''
	p[0] = p[1] + p[2] + p[3]
	
def p_pyexpr_pyid(p):
	'''pyid : DOLLAR ID'''
	p[0] = p[2]

def p_pyexpr_var(p):
	'''pyexpr : pyid'''
	p[0] = p[1]
	
def p_pymap_pair(p):
	'''pymap_pair : pyexpr COLON optnewlines pyexpr'''
	p[0] = p[1] + p[2] + p[4]
	
def p_pymap_pair_list_empty(p):
	'''pymap_pair_list : empty'''
	p[0] = ''
	
def p_pymap_pair_list_one(p):
	'''pymap_pair_list : pymap_pair'''
	p[0] = p[1]

def p_pymap_pair_list(p):
	'''pymap_pair_list : pymap_pair COMMA optnewlines pymap_pair_list'''
	p[0] = p[1] + p[2] + p[4]
	
def p_pyexpr_map(p):
	'''pyexpr : LCURLY optnewlines pymap_pair_list optnewlines RCURLY'''
	p[0] = p[1] + p[3] + p[5]

	
#### Virtual integer
def p_virtualinteger_literal(p):
	'''virtualinteger : integer'''
	p[0] = p[1]
	
def p_virtualinteger_symbol(p):
	'''virtualinteger : DOLLAR ID'''
	p[0] = '$' + p[2]
	
#### Virtual number
def p_virtualnumber_literal(p):
	'''virtualnumber : number'''
	p[0] = p[1]
	
def p_virtualnumber_symbol(p):
	'''virtualnumber : DOLLAR ID'''
	p[0] = '$' + p[2]

#### Block tags
def p_blocktag(p):
	'''blocktag : define block_tag ID newlines block_list end'''
	p[0] = block_tag_block(p.lineno(1), p[3], p[5])
	
def p_block_list(p):
	'''block_list : ID newlines block_list'''
	p[0] = [p[1]] + p[3]
	
def p_block_list_one(p):
	'''block_list : ID newlines'''
	p[0] = [p[1]]

#### Block tags
def p_entitytag(p):
	'''entitytag : define entity_tag ID newlines entity_list end'''
	p[0] = entity_tag_block(p.lineno(1), p[3], p[5])
	
def p_entity_list(p):
	'''entity_list : ID newlines entity_list'''
	p[0] = [p[1]] + p[3]
	
def p_entity_list_one(p):
	'''entity_list : ID newlines'''
	p[0] = [p[1]]
	
	
#### Item tags
def p_itemtag(p):
	'''itemtag : define item_tag ID newlines item_list end'''
	p[0] = item_tag_block(p.lineno(1), p[3], p[5])
	
def p_item_list(p):
	'''item_list : ID newlines item_list'''
	p[0] = [p[1]] + p[3]
	
def p_item_list_one(p):
	'''item_list : ID newlines'''
	p[0] = [p[1]]

#### Pointer Declaration
def p_pointer_decl(p):
	'''pointer_decl : ID COLON fullselector'''
	p[0] = pointer_decl_block(p.lineno(0), p[1], p[3])

#### Block definition
def p_block_define_block(p):
	'''block_define_block : define LBRACK ID RBRACK newlines block_definition end'''
	p[0] = block_definition_block(p.lineno(1), p[3], p[6], relcoords())
	
def p_block_define_block_coords(p):
	'''block_define_block : define LBRACK ID RBRACK at relcoords newlines block_definition end'''
	p[0] = block_definition_block(p.lineno(1), p[3], p[8], p[6])
	
def p_block_definition_empty(p):
	'''block_definition : empty'''
	p[0] = []
	
def p_block_definition(p):
	'''block_definition : block_item newlines block_definition'''
	p[0] = [p[1]] + p[3]
	
def p_block_item_path_noscale(p):
	'''block_item : ID COLON data_path data_type'''
	p[0] = number_macro_path(p[1], [], p[3], p[4])
	
def p_block_item_path_scale(p):
	'''block_item : ID COLON data_path data_type const_value'''
	p[0] = number_macro_path(p[1], [], p[3], p[4], p[5])
	
def p_block_item_macro_path_noscale(p):
	'''block_item : ID LBRACK macro_params RBRACK COLON data_path data_type'''
	p[0] = number_macro_path(p[1], p[3], p[6], p[7])

def p_block_item_macro_path_scale(p):
	'''block_item : ID LBRACK macro_params RBRACK COLON data_path data_type const_value'''
	p[0] = number_macro_path(p[1], p[3], p[6], p[7], p[8])
	
#### Selector Assignment
def p_uuid(p):
	'''uuid : integer MINUS integer MINUS integer MINUS integer MINUS integer'''
	p[0] = '{:X}-{:X}-{:X}-{:X}-{:X}'.format(int(p[1]), int(p[3]), int(p[5]), int(p[7]), int(p[9]))

def p_selector_assignment(p):
	'''selector_assignment : ATID EQUALS fullselector'''
	p[0] = selector_assignment_block(p.lineno(1), p[1], p[3])
	
def p_selector_define(p):
	'''selector_define_block : define ATID EQUALS fullselector newlines selector_definition end
	                         | define ATID COLON  fullselector newlines selector_definition end'''
	p[0] = selector_definition_block(p.lineno(1), p[2], p[4], None, p[6])
	
def p_selector_define_uuid(p):
	'''selector_define_block : define ATID COLON uuid LPAREN fullselector RPAREN newlines selector_definition end'''
	p[0] = selector_definition_block(p.lineno(1), p[2], p[6], p[4], p[9])

def p_selector_definition_empty(p):
	'''selector_definition : empty'''
	p[0] = []
	
def p_selector_definition(p):
	'''selector_definition : selector_item newlines selector_definition'''
	p[0] = [p[1]] + p[3]
	
def p_selector_item_tag(p):
	'''selector_item : create json_object'''
	p[0] = ('Tag', p[2])
	
def p_selector_item_path_scale(p):
	'''selector_item : ID EQUALS data_path data_type const_value
	                 | ID COLON  data_path data_type const_value'''
	p[0] = ('Path', (p[1], p[3], p[4], p[5]))
	
def p_selector_item_path(p):
	'''selector_item : ID EQUALS data_path data_type
					 | ID COLON  data_path data_type'''
	p[0] = ('Path', (p[1], p[3], p[4], None))

def p_selector_item_vector_path_scale(p):
	'''selector_item : LT ID GT EQUALS data_path data_type const_value
					 | LT ID GT COLON  data_path data_type const_value'''
	p[0] = ('VectorPath', (p[2], p[5], p[6], p[7]))

def p_selector_item_vector_path(p):
	'''selector_item : LT ID GT EQUALS data_path data_type
					 | LT ID GT COLON data_path data_type'''
	p[0] = ('VectorPath', (p[2], p[5], p[6], None))
	
def p_selector_item_method(p):
	'''selector_item : functionsection'''
	p[0] = ('Method', p[1])
	
def p_selector_pointer(p):
	'''selector_item : ID EQUALS fullselector
					 | ID COLON  fullselector'''
	p[0] = ('Pointer', (p[1], p[3]))
	
def p_selector_array(p):
	'''selector_item : array_definition'''
	p[1].selector_based = True
	p[0] = ('Array', p[1])
	
def p_selector_predicate(p):
	'''selector_item : predicate_definition'''
	p[0]  = ('Predicate', p[1])
	
def p_data_path_id(p):
	'''data_path : ID
				 | facing'''
	p[0] = p[1]
	
def p_data_path_array(p):
	'''data_path : ID LBRACK virtualinteger RBRACK'''
	p[0] = '{0}[{1}]'.format(p[1], p[3])
	
def p_data_path_array_match(p):
	'''data_path : ID LBRACK json_object RBRACK'''
	p[0] = p[1] + p[2] + p[3] + p[4]
	
def p_data_path_object_match(p):
	'''data_path : ID json_object'''
	p[0] = p[1] + p[2]
	
def p_data_path_multi(p):
	'''data_path : data_path DOT data_path'''
	p[0] = '{0}.{1}'.format(p[1], p[3])
	
def p_data_type(p):
	'''data_type : ID'''
	if p[1] not in ['byte', 'double', 'float', 'int', 'long', 'short']:
		raise SyntaxError('Syntax Error: Invalid path type "{}" at line {}.'.format(p.lineno(1)))
	p[0] = p[1]
	
#### Array
def p_array_definition(p):
	'''array_definition : array ID LBRACK const_value RBRACK'''
	p[0] = array_definition_block(p.lineno(1), p[2], const_number(0), p[4], False)
	
def p_array_definition_range(p):
	'''array_definition : array ID LBRACK const_value to const_value RBRACK'''
	p[0] = array_definition_block(p.lineno(1), p[2], p[4], p[6], False)
	
#### Create
def p_block_create(p):
	'''codeblock : create_block'''
	p[0] = p[1]
	
def p_create(p):
	'''create_block : create ATID relcoords'''
	p[0] = create_block(p.lineno(1), p[2], p[3], None)
	
def p_create_nocoords(p):
	'''create_block : create ATID'''
	p[0] = create_block(p.lineno(1), p[2], relcoords(), None)

def p_create_index(p):
	'''create_block : create ATID LBRACK const_value RBRACK relcoords'''
	p[0] = create_block(p.lineno(1), p[2], p[6], p[4])
	
def p_create_index_nocoords(p):
	'''create_block : create ATID LBRACK const_value RBRACK'''
	p[0] = create_block(p.lineno(1), p[2], relcoords(), p[4])

#### Define name
def p_define_name(p):
	'''codeblock : define name ID EQUALS NORMSTRING'''
	p[0] = define_name_block(p.lineno(1), p[3], p[5])
	
#### Python Assignment
def p_pythonassignment_interpreted_string(p):
	'''pythonassignment : DOLLAR ID EQUALS const_value'''
	p[0] = python_assignment_block(p.lineno(1), p[2], p[4])
	
#### Python Tuple Assignment
def p_python_tuple_two(p):
	'''python_tuple : DOLLAR ID COMMA DOLLAR ID'''
	p[0] = [p[2], p[5]]
	
def p_python_tuple_multi(p):
	'''python_tuple : DOLLAR ID COMMA python_tuple'''
	p[0] = [p[2]] + p[4]
	
def p_python_tuple_assignment(p):
	'''python_tuple_assignment : python_tuple EQUALS const_value'''
	p[0] = python_tuple_assignment_block(p.lineno(1), p[1], p[3])

#### NBT Assignment
def p_nbt_assignment(p):
	'''codeblock : nbt_list EQUALS nbt_source
	             | nbt_object EQUALS nbt_source'''
	p[0] = nbt_data_block(p.lineno(1), p[1], 'set', p[3])
	
def p_nbt_merge(p):
	'''codeblock : nbt_object PLUSEQUALS nbt_source'''
	p[0] = nbt_data_block(p.lineno(1), p[1], 'merge', p[3])
	
def p_nbt_append(p):
	'''codeblock : nbt_list PLUSEQUALS nbt_source'''
	p[0] = nbt_data_block(p.lineno(1), p[1], 'append', p[3])
	
def p_nbt_list_entity(p):
	'''nbt_list : fullselector DOT LBRACK data_path RBRACK'''
	p[0] = entity_nbt_path(p[1], p[4])

def p_nbt_list_storage(p):
	'''nbt_list : COLON LBRACK data_path RBRACK'''
	p[0] = storage_nbt_path(None, p[3])
	
def p_nbt_list_storage_target(p):
	'''nbt_list : ID COLON LBRACK data_path RBRACK'''
	p[0] = storage_nbt_path(p[1], p[4])
	
def p_nbt_list_block(p):
	'''nbt_list : block_coords DOT LBRACK data_path RBRACK'''
	p[0] = block_nbt_path(p[1], p[4])
	
def p_nbt_object_entity(p):
	'''nbt_object : fullselector DOT LCURLY data_path RCURLY'''
	p[0] = entity_nbt_path(p[1], p[4])
	
def p_nbt_object_storage(p):
	'''nbt_object : COLON LCURLY data_path RCURLY'''
	p[0] = storage_nbt_path(None, p[3])
	
def p_nbt_object_storage_target(p):
	'''nbt_object : ID COLON LCURLY data_path RCURLY'''
	p[0] = storage_nbt_path(p[1], p[4])
	
def p_nbt_object_block(p):
	'''nbt_object : block_coords DOT LCURLY data_path RCURLY'''
	p[0] = block_nbt_path(p[1], p[4])
	
def p_nbt_source_path_entity(p):
	'''nbt_path : fullselector DOT data_path'''
	p[0] = entity_nbt_path(p[1], p[3])

def p_nbt_source_path_storage(p):
	'''nbt_object : COLON data_path'''
	p[0] = storage_nbt_path(None, p[2])
	
def p_nbt_source_path_storage_target(p):
	'''nbt_object : ID COLON data_path'''
	p[0] = storage_nbt_path(p[1], p[3])
	
def p_nbt_source_path_block(p):
	'''nbt_path : block_coords DOT data_path'''
	p[0] = block_nbt_path(p[1], p[3])
	
def p_nbt_path(p):
	'''nbt_path : nbt_object
				| nbt_list'''
	p[0] = p[1]
	
def p_nbt_source_object(p):
	'''nbt_source : nbt_path'''
	p[0] = p[1]
	
def p_nbt_source_json(p):
	'''nbt_source : json_object'''
	p[0] = nbt_json(p[1])

def p_nbt_source_string(p):
	'''nbt_source : NORMSTRING'''
	p[0] = nbt_json(p[1])
	
def p_block_coords(p):
	'''block_coords : LBRACK relcoords RBRACK'''
	p[0] = p[2]
	
def p_block_coords_empty(p):
	'''block_coords : LBRACK RBRACK'''
	p[0] = relcoords()
	
def p_nbt_remove(p):
	'''codeblock : remove nbt_path'''
	p[0] = nbt_remove_block(p.lineno(1), p[2])

	
#### Assignment
def p_return_expression(p):
	'''codeblock : return expr'''
	p[0] = scoreboard_assignment_block(p.lineno(1), scoreboard_var('Global', 'ReturnValue'), '=', p[2])
	
def p_assignment(p):
	'''codeblock : variable EQUALS expr
				 | variable PLUSEQUALS expr
				 | variable MINUSEQUALS expr
				 | variable TIMESEQUALS expr
				 | variable DIVIDEEQUALS expr
				 | variable MODEQUALS expr'''
	p[0] = scoreboard_assignment_block(p.lineno(1), p[1], p[2], p[3])
	
def p_assignment_unary_default(p):
	'''codeblock : variable PLUSPLUS
				 | variable MINUSMINUS'''
	op = p[2][0]+'='
	operand = virtualint_var('1')
	p[0] = scoreboard_assignment_block(p.lineno(1), p[1], op, operand)

def p_assignment_create(p):
	'''codeblock : variable EQUALS create_block'''
	p[0] = scoreboard_assignment_block(p.lineno(1), p[1], p[2], create_expr(p[3]))
	
#### Vector assignment
def p_vector_assignment_vector(p):
	'''codeblock : vector_var EQUALS vector_expr
				 | vector_var PLUSEQUALS vector_expr
				 | vector_var MINUSEQUALS vector_expr'''
	p[0] = vector_assignment_block(p.lineno(1), p[1], p[2], p[3])
	
def p_vector_assignment_scalar(p):
	'''codeblock : vector_var EQUALS expr
				 | vector_var PLUSEQUALS expr
				 | vector_var MINUSEQUALS expr
				 | vector_var TIMESEQUALS expr
				 | vector_var DIVIDEEQUALS expr
				 | vector_var MODEQUALS expr'''
	p[0] = vector_assignment_scalar_block(p.lineno(1), p[1], p[2], p[3])
	
#### Vector LHS
def p_vector_var_id(p):
	'''vector_var : LT ID GT'''
	p[0] = ('VAR_ID', p[2])

def p_vector_var_sel_id(p):
	'''vector_var : fullselector DOT LT ID GT'''
	p[0] = ('SEL_VAR_ID', (p[1], p[4]))
	
def p_vector_var_components(p):	
	'''vector_var : LT variable COMMA variable COMMA variable GT'''
	p[0] = ('VAR_COMPONENTS', [p[2], p[4], p[6]])
	
def p_vector_var_const_vector(p):
	'''vector_var : const_vector'''
	p[0] = ('VAR_CONST', p[1])

#### Arithmetic expressions
def p_expr_var(p):
	'''expr : variable'''
	p[0] = p[1]

def p_expr_binary(p):
	'''expr : expr PLUS expr
			| expr MINUS expr
			| expr TIMES expr
			| expr DIVIDE expr
			| expr MOD expr'''

	p[0] = binop_expr(p[1], p[2], p[3])
	
def p_expr_power(p):
	'''expr : expr POWER integer'''
	p[0] = binop_expr(p[1], p[2], virtualint_var(p[3]))
	
def p_expr_dot(p):
	'''expr : vector_expr TIMES vector_expr'''
	p[0] = dot_expr(p[1], p[3])

def p_expr_function(p):
	'''expr : function_call'''
	p[0] = func_expr(p[1])

def p_expr_method(p):
	'''expr : method_call'''
	p[0] = method_expr(p[1])
	
def p_expr_group(p):
	'''expr : LPAREN expr RPAREN'''
	p[0] = p[2]

def p_expr_unary(p):
	'''expr : MINUS expr %prec UMINUS'''
	p[0] = unary_expr('-', p[2])
	
	
### Vector expressions
def p_vector_expr_group(p):
	'''vector_expr : LPAREN vector_expr RPAREN'''
	p[0] = p[2]

def p_vector_expr_vector_triplet(p):
	'''vector_expr : LT expr COMMA expr COMMA expr GT'''
	p[0] = vector_expr((p[2], p[4], p[6]))
	
def p_vector_expr_vector_unit(p):
	'''vector_expr : LT ID GT'''
	p[0] = vector_var_expr(p[2])
	
def p_vector_expr_const_vector(p):
	'''vector_expr : const_vector'''
	p[0] = vector_var_const_vector(p[1])
	
def p_vector_expr_selector_vector(p):
	'''vector_expr : fullselector DOT LT ID GT'''
	p[0] = sel_vector_var_expr(p[1], p[4])
	
def p_vector_expr_binop_vector(p):
	'''vector_expr : vector_expr PLUS vector_expr
				   | vector_expr MINUS vector_expr'''
	p[0] = vector_binop_vector_expr(p[1], p[2], p[3])
	
def p_vector_expr_binop_scalar(p):
	'''vector_expr : vector_expr PLUS expr
				   | vector_expr MINUS expr
				   | vector_expr TIMES expr
				   | vector_expr DIVIDE expr
				   | vector_expr MOD expr'''
	p[0] = vector_binop_scalar_expr(p[1], p[2], p[3])
	
def p_vector_expr_binop_scalar_reversed(p):
	'''vector_expr : expr PLUS vector_expr
				   | expr TIMES vector_expr'''
	p[0] = vector_binop_scalar_expr(p[3], p[2], p[1])
	
def p_vector_expr_negative(p):
	'''vector_expr : MINUS vector_expr'''
	p[0] = vector_binop_scalar_expr(p[2], '*', virtualint_var(-1))
	
def p_vector_expr_here(p):
	'''vector_expr : here'''
	p[0] = vector_here_expr(None)

def p_vector_expr_here_scale(p):
	'''vector_expr : here LPAREN const_value RPAREN'''
	p[0] = vector_here_expr(p[3])
	
#### Json (can't implement until COLON is an available token)
def p_json_object(p):
	'''json_object : LCURLY optnewlines json_members optnewlines RCURLY'''
	p[0] = p[1] + p[3] + p[5]
	
def p_json_members(p):
	'''json_members : json_pair'''
	p[0] = p[1]
	
def p_json_members_multi(p):
	'''json_members : json_pair COMMA optnewlines json_members'''
	p[0] = p[1] + p[2] + p[4]
	
def p_json_members_empty(p):
	'''json_members : empty'''
	p[0] = ''
	
def p_json_pair(p):
	'''json_pair : ID COLON optnewlines json_value
				 | string COLON optnewlines json_value
				 | facing COLON optnewlines json_value
				 | block COLON optnewlines json_value
				 | predicate COLON optnewlines json_value'''
	p[0] = '"' + p[1] + '"' + p[2] + p[4]
	
def p_json_value(p):
	'''json_value : number
				  | json_object
				  | json_array
				  | json_literal_array
				  | true
				  | false'''
	p[0] = p[1]
	
def p_json_value_dollar_id(p):
	'''json_value : DOLLAR ID'''
	p[0] = p[1] + p[2]
	
def p_json_value_typed_number(p):
	'''json_value : number ID'''
	if p[2].lower() not in ['b', 'f', 's', 'd', 'l']:
		raise SyntaxError('Invalid type "{}" for number "{}" at line {}'.format(p[2], p[1], p.lineno(1)))
		
	p[0] = p[1] + p[2]
	
def p_json_value_string(p):
	'''json_value : string'''
	p[0] = '"' + p[1] + '"'
	
def p_json_array(p):
	'''json_array : LBRACK optnewlines json_elements optnewlines RBRACK'''
	p[0] = p[1] + p[3] + p[5]
	
def p_json_elements(p):
	'''json_elements : json_value'''
	p[0] = p[1]
	
def p_json_elements_multi(p):
	'''json_elements : json_value COMMA optnewlines json_elements'''
	p[0] = p[1] + p[2] + p[4]
	
def p_json_elements_empty(p):
	'''json_elements : empty'''
	p[0] = ''

def p_json_literal_array(p):
	'''json_literal_array : LBRACK optnewlines ID SEMICOLON optnewlines json_literal_elements optnewlines RBRACK'''
	if p[3].lower() not in ['b', 'i', 'l']:
		raise SyntaxError('Invalid type "{}" for literal array at line {}'.format(p[3], p.lineno(1)))

	p[0] = p[1] + p[3] + p[4] + p[6] + p[8]

def p_json_literal_element_one(p):
	'''json_literal_elements : json_literal_value'''
	p[0] = p[1]
	
def p_json_literal_elements_multi(p):
	'''json_literal_elements : json_literal_value COMMA optnewlines json_literal_elements'''
	p[0] = p[1] + p[2] + p[4]
	
def p_json_literal_elements_empty(p):
	'''json_literal_elements : empty'''
	p[0] = ''

def p_json_literal_value(p):
	'''json_literal_value : number'''
	p[0] = p[1]
	
def p_json_literal_value_dollar_id(p):
	'''json_literal_value : DOLLAR ID'''
	p[0] = p[1] + p[2]
	
#### Crafting recipes
def p_shaped_recipe(p):
	'''shaped_recipe : shaped recipe newlines recipe_lines keys newlines recipe_key_list end newlines result COLON const_value ID newlines end'''
	p[0] = shaped_recipe_block(p.lineno(1), p[4], p[7], p[12], p[13])
	
def p_recipe_lines(p):
	'''recipe_lines : string newlines recipe_lines'''
	p[0] = [p[1]] + p[3]
	
def p_recipe_lines_empty(p):
	'''recipe_lines : empty'''
	p[0] = []

def p_recipe_key_item(p):
	'''recipe_key_item : ID EQUALS ID COLON ID'''
	if len(p[1]) != 1:
		raise SyntaxError('Recipe key "{}" at line {} is not a single character.'.format(p[1], p.lineno(1)))
		
	if p[3] not in ['item', 'tag']:
		raise SyntaxError('Recipe key type "{}" at line {} must be "block" or "tag".'.format(p[3], p.lineno(1)))
	
	p[0] = (p[1], p[3], p[5])
	
def p_recipe_key_list(p):
	'''recipe_key_list : recipe_key_item newlines recipe_key_list'''
	p[0] = [p[1]] + p[3]
	
def p_recipe_key_list_empty(p):
	'''recipe_key_list : empty'''
	p[0] = []
	
#### Advancements
def p_advancement_definition(p):
	'''advancement_definition : advancement ID json_object'''
	p[0] = advancement_definition_block(p.lineno(1), p[2], p[3])
	


#### Loot Tables
def p_loot_table_type(p):
	'''loot_table_type : block'''
	types = {
		'block': 'blocks',
	}
	if p[1] not in types:
		raise SyntaxError('Invalid loot table type "{}" at line {}.'.format(p[1], p.lineno(1)))
		
	p[0] = types[p[1]]
	
def p_loot_table_definition(p):
	'''loot_table_definition : loot_table loot_table_type ID json_object'''
	p[0] = loot_table_definition_block(p.lineno(1), p[2], p[3], p[4])

def p_loot_table_definition(p):
	'''loot_table_definition : loot_table loot_table_type ID COLON ID json_object'''
	p[0] = loot_table_definition_block(p.lineno(1), p[2], p[3] + p[4] + p[5], p[6])
	
#### Predicates
def p_predicate_definition(p):
	'''predicate_definition : predicate ID json_object'''
	p[0] = predicate_definition_block(p.lineno(1), p[2], p[3])
	
#### Empty
def p_empty(p):
	'''empty : '''

def p_error(p):
	if p == None:
		raise SyntaxError('Syntax error: unexpected End of File')
	else:
		raise SyntaxError('Syntax error at line {} column {}. Unexpected {} symbol "{}" in state {}.'.format(p.lineno, scriptlex.find_column(bparser.data, p), p.type, p.value.replace('\n', '\\n'), bparser.state))

bparser = yacc.yacc()

def parse(data,debug=0):
	scriptlex.lexer.lineno = 1
	bparser.error = 0
	bparser.data = data
	try:
		p = bparser.parse(data,debug=debug,tracking=True)
		return p
	except SyntaxError as e:
		print(e)
	except Exception as e:
		print(traceback.format_exc())