from ply import *
import scriptlex
from block_types.array_definition_block import array_definition_block
from block_types.block_definition_block import block_definition_block
from block_types.block_tag_block import block_tag_block
from block_types.command_block import command_block
from block_types.comment_block import comment_block
from block_types.create_block import create_block
from block_types.execute_block import execute_block
from block_types.for_index_block import for_index_block
from block_types.for_selector_block import for_selector_block
from block_types.function_call_block import function_call_block
from block_types.import_block import import_block
from block_types.macro_call_block import macro_call_block
from block_types.method_call_block import method_call_block
from block_types.move_block import move_block
from block_types.nbt_data_block import nbt_data_block
from block_types.nbt_remove_block import nbt_remove_block
from block_types.pointer_decl_block import pointer_decl_block
from block_types.print_block import print_block
from block_types.python_assignment_block import python_assignment_block
from block_types.python_for_block import python_for_block
from block_types.python_if_block import python_if_block
from block_types.scoreboard_assignment_block import scoreboard_assignment_block
from block_types.selector_assignment_block import selector_assignment_block
from block_types.selector_definition_block import selector_definition_block
from block_types.switch_block import switch_block
from block_types.tell_block import tell_block
from block_types.template_function_call_block import template_function_call_block
from block_types.title_block import title_block
from block_types.vector_assignment_block import vector_assignment_block
from block_types.vector_assignment_scalar_block import vector_assignment_scalar_block
from block_types.while_block import while_block
from data_types.const_number import const_number
from data_types.const_string import const_string
from data_types.number_macro_path import number_macro_path
from data_types.python_identifier import python_identifier
from data_types.interpreted_python import interpreted_python
from data_types.relcoord import relcoord
from data_types.relcoords import relcoords
from nbt_types.nbt_json import nbt_json
from nbt_types.entity_nbt_path import entity_nbt_path
from nbt_types.block_nbt_path import block_nbt_path
from scalar_expressions.binop_expr import binop_expr
from scalar_expressions.create_expr import create_expr
from scalar_expressions.dot_expr import dot_expr
from scalar_expressions.func_expr import func_expr
from scalar_expressions.unary_expr import unary_expr
from variable_types.array_const_var import array_const_var
from variable_types.array_expr_var import array_expr_var
from variable_types.block_path_var import block_path_var
from variable_types.scale_var import scale_var
from variable_types.scoreboard_var import scoreboard_var
from variable_types.selector_id_var import selector_id_var
from variable_types.virtualint_var import virtualint_var
from vector_expressions.sel_vector_var_expr import sel_vector_var_expr
from vector_expressions.vector_binop_scalar_expr import vector_binop_scalar_expr
from vector_expressions.vector_binop_vector_expr import vector_binop_vector_expr
from vector_expressions.vector_expr import vector_expr
from vector_expressions.vector_here_expr import vector_here_expr
from vector_expressions.vector_var_expr import vector_var_expr
import mcfunction

tokens = scriptlex.tokens

precedence = (
			   ('left', 'PLUS','MINUS'),
			   ('left', 'TIMES','DIVIDE','MOD'),
			   ('left', 'POWER'),
			   ('right','UMINUS')
)

#### Parsed
def p_parsed_assignment(p):
	'''parsed : program'''
	p[0] = ('program', p[1])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

def p_parsed_lib(p):
	'''parsed : import lib'''
	p[0] = ('lib', p[2])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_parsed_expr(p):
	'''parsed : expr'''
	p[0] = ('expr', p[1])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
#### Program
def p_program(p):
	'''program : optcomments dir string newlines optdesc optscale optassignments sections'''
	p[0] = {}
	p[0]['dir'] = p[3]
	p[0]['desc'] = p[5]
	p[0]['scale'] = p[6]
	p[0]['assignments'] = p[7]
	p[0]['sections'] = p[8]
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
### Lib
def p_lib(p):
	'''lib : optcomments optassignments sections'''
	p[0] = {}
	p[0]['assignments'] = p[2]
	p[0]['sections'] = p[3]
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

#### Optdesc
def p_optdesc(p):
	'''optdesc : desc string newlines
			   | empty'''
	if len(p) < 4:
		p[0] = 'No Description'
	else:
		p[0] = p[2]
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
#### Optscale
def p_optscale(p):
	'''optscale : scale integer newlines'''
	p[0] = int(p[2])

def p_optscale_none(p):
	'''optscale : empty'''
	p[0] = 1000
	
#### Sections
def p_sections_multiple(p):
	'''sections : section_commented newlines sections'''
	p[0] = [p[1]] + p[3]
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

def p_sections_empty(p):
	'''sections : empty'''
	p[0] = []

def p_section_commented(p):
	'''section_commented : optcomments section'''
	type, name, template_params, params, lines = p[2]
	
	p[0] = type, name, template_params, params, [comment_block(p.lineno(1), '#' + line) for line in p[1]] + lines
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

def p_optcomments(p):
	'''optcomments : COMMENT optnewlines optcomments'''
	p[0] = [p[1]] + p[3]
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
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
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

#### Reset Section	
def p_resetsection(p):
	'''resetsection : reset newlines blocklist end'''
	p[0] = ('reset', 'reset', [], [], p[3])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def validate_mcfunction_name(str):
	for ch in str:
		if ch.isupper():
			print('"{0}" is not a valid mcfunction name.'.format(str))
			raise SyntaxError()
	
#### Clock Section
def p_clocksection(p):
	'''clocksection : clock ID newlines blocklist end'''
	validate_mcfunction_name(p[2])
	
	p[0] = ('clock', p[2], [], [], p[4])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
#### Function Section
def p_functionsection(p):
	'''functionsection : function FUNCTIONID id_list RPAREN newlines blocklist end'''
	validate_mcfunction_name(p[2])

	p[0] = ('function', p[2], [], p[3], p[6])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

#### Template Function Section
def p_template_function_section(p):
	'''template_function_section : function ID LCURLY macro_params RCURLY LPAREN id_list RPAREN newlines blocklist end'''
	validate_mcfunction_name(p[2])
	
	p[0] = ('template_function', p[2], p[4], p[7], p[10])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

#### Macro section
def p_macrosection(p):
	'''macrosection : macro DOLLAR FUNCTIONID macro_args newlines blocklist end'''
	p[0] = ('macro', p[3], [], p[4], p[6])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_macro_args(p):
	'''macro_args : macro_params RPAREN'''
	p[0] = p[1]
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_macro_args_empty(p):
	'''macro_args : empty'''
	p[0] = []

def p_macro_params(p):
	'''macro_params : DOLLAR ID COMMA macro_params'''
	p[0] = [p[2]] + p[4]
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

def p_macro_params_one(p):
	'''macro_params : DOLLAR ID'''
	p[0] = [p[2]]
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_macro_params_empty(p):
	'''macro_params : empty'''
	p[0] = []

#### Function call
def p_function_call_namespace(p):
	'''function_call : ID COLON FUNCTIONID exprlist RPAREN'''
	p[0] = function_call_block(p.lineno(1), p[1]+p[2]+p[3], p[4])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

def p_function_call(p):
	'''function_call : FUNCTIONID exprlist RPAREN'''
	p[0] = function_call_block(p.lineno(1), p[1], p[2])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

def p_method_call(p):
	'''method_call : fullselector DOT FUNCTIONID exprlist RPAREN'''
	p[0] = method_call_block(p.lineno(1), p[1], p[3], p[4])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
#### Expression list
def p_exprlist_multiple(p):
	'''exprlist : exprlist COMMA expr'''
	p[0] = p[1]
	p[0].append(p[3])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_exprlist_single(p):
	'''exprlist : expr'''
	p[0] = [p[1]]
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

def p_exprlist_empty(p):
	'''exprlist : empty'''
	p[0] = []

#### Template Function Call
def p_template_function_call(p):
	'''template_function_call : ID LCURLY macro_call_params RCURLY LPAREN exprlist RPAREN'''
	p[0] = template_function_call_block(p.lineno(1), p[1], p[3], p[6])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
#### Macro call	
def p_macro_call(p):
	'''macro_call : DOLLAR FUNCTIONID macro_call_args'''
	p[0] = macro_call_block(p.lineno(1), p[2], p[3])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_macro_call_args(p):
	'''macro_call_args : macro_call_params RPAREN'''
	p[0] = p[1]
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_macro_call_args_empty(p):
	'''macro_call_args : empty'''
	p[0] = []
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_macro_call_params(p):
	'''macro_call_params : macro_call_param COMMA macro_call_params'''
	p[0] = [p[1]] + p[3]
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

def p_macro_call_params_one(p):
	'''macro_call_params : macro_call_param'''
	p[0] = [p[1]]
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_macro_call_params_empty(p):
	'''macro_call_params : empty'''
	p[0] = []
	
def p_macro_call_param_number(p):
	'''macro_call_param : const_value'''
	p[0] = p[1]
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
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
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

def p_id_list_one(p):
	'''id_list : ID'''
	p[0] = [p[1]]
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

def p_id_list_empty(p):
	'''id_list : empty'''
	p[0] = []
	
#### Optassignments
def p_optassignments_multiple(p):
	'''optassignments : pythonassignment newlines optassignments
					  | selector_assignment newlines optassignments
					  | selector_define_block newlines optassignments
					  | block_define_block newlines optassignments
					  | blocktag newlines optassignments
					  | array_definition newlines optassignments
					  | import_statement newlines optassignments
					  | print_block newlines optassignments
					  | pointer_decl newlines optassignments'''
	p[0] = [p[1]] + p[3]
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_optassignments_comment(p):
	'''optassignments : COMMENT newlines optassignments'''
	p[0] = p[3]
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

def p_optassignments_empty(p):
	'''optassignments : empty'''
	p[0] = []

#### Import	
def p_import_statement(p):
	'''import_statement : import ID'''
	p[0] = import_block(p.lineno(1), p[2])
	
#### Variable
def p_variable_selector(p):
	'''variable : fullselector DOT ID'''
	p[0] = scoreboard_var(p[1], p[3])
	
def p_variable_global(p):
	'''variable : ID'''
	p[0] = scoreboard_var('Global', p[1])
	
def p_variable_array_const(p):
	'''variable : ID LBRACK const_value RBRACK'''
	p[0] = array_const_var(p[1], p[3])
	
def p_variable_array_expr(p):
	'''variable : ID LBRACK expr RBRACK'''
	p[0] = array_expr_var(p[1], p[3])
	
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
	
#### Blocklist
def p_optcomment(p):
	'''optcomment : COMMENT'''
	p[0] = [comment_block(p.lineno(1), p[1])]
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_optcomment_empty(p):
	'''optcomment : empty'''
	p[0] = []

def p_blocklist_multiple(p):
	'''blocklist : codeblock optcomment newlines blocklist'''
	p[0] = p[2] + [p[1]] + p[4]
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

def p_blocklist_empty(p):
	'''blocklist : empty'''
	p[0] = []

#### Block
def p_block_comment(p):
	'''codeblock : COMMENT'''
	p[0] = comment_block(p.lineno(1), p[1])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

def p_block_command(p):
	'''codeblock : COMMAND'''
	p[0] = command_block(p.lineno(1), p[1])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_block_move(p):
	'''codeblock : move fullselector relcoords'''
	p[0] = move_block(p.lineno(1), p[2], p[3])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

def p_block_for(p):
	'''codeblock : for DOLLAR ID in const_value newlines blocklist end'''
	p[0] = python_for_block(p.lineno(1), p[3], p[5], p[7])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_block_print(p):
	'''codeblock : print_block'''
	p[0] = p[1]
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_print_block(p):
	'''print_block : DOLLAR print LPAREN const_value RPAREN'''
	p[0] = print_block(p.lineno(1), p[4])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
#### Execute
def p_execute_as_id_global(p):
	'''codeblock : as variable newlines blocklist end'''
	p[0] = execute_block(p.lineno(1), [('AsId', (p[2], None))], p[4])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

def p_execute_as_id_type_global(p):
	'''codeblock : as variable LPAREN ATID RPAREN newlines blocklist end'''
	p[0] = execute_block(p.lineno(1), [('AsId', (p[2], p[4]))], p[7])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

def p_execute_as_id_do_global(p):
	'''codeblock : as variable do codeblock'''
	p[0] = execute_block(p.lineno(1), [('AsId', (p[2], None))], [p[4]])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

def p_execute_as_id_do_type_global(p):
	'''codeblock : as variable LPAREN ATID RPAREN do codeblock'''
	p[0] = execute_block(p.lineno(1), [('AsId', (p[2], p[4]))], [p[7]])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

def p_execute_as_create(p):
	'''codeblock : as create_block newlines blocklist end'''
	p[0] = execute_block(p.lineno(1), [('AsCreate', p[2])], p[4])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

def p_execute_as_create_do(p):
	'''codeblock : as create_block do codeblock'''
	p[0] = execute_block(p.lineno(1), [('AsCreate', p[2])], [p[4]])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_execute_chain(p):
	'''codeblock : execute_items newlines blocklist end'''
	p[0] = execute_block(p.lineno(1), p[1], p[3])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_execute_chain_inline(p):
	'''codeblock : execute_items do codeblock
				 | execute_items then codeblock'''
	p[0] = execute_block(p.lineno(1), p[1], [p[3]])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

#### Execute Items	
def p_execute_items_one(p):
	'''execute_items : execute_item'''
	p[0] = [p[1]]
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_execute_items(p):
	'''execute_items : execute_item execute_items'''
	p[0] = [p[1]] + p[2]
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_execute_if_condition(p):
	'''execute_item : if conditions'''
	p[0] = ('If', p[2])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

def p_execute_unless_condition(p):
	'''execute_item : unless conditions'''
	p[0] = ('Unless', p[2])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_execute_as(p):
	'''execute_item : as fullselector'''
	p[0] = ('As', p[2])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

def p_execute_rotated(p):
	'''execute_item : rotated fullselector'''
	p[0] = ('Rotated', p[2])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_execute_facing_coords(p):
	'''execute_item : facing relcoords'''
	p[0] = ('FacingCoords', p[2])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_execute_facing_entity(p):
	'''execute_item : facing fullselector'''
	p[0] = ('FacingEntity', p[2])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

def p_execute_align(p):
	'''execute_item : align ID'''
	if p[2] not in ['x','y','z','xy','xz','yz','xyz']:
		raise SyntaxError('Must align to a combination of x, y, and z axes')
	p[0] = ('Align', p[2])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_execute_at_selector(p):
	'''execute_item : at fullselector'''
	p[0] = ('At', (p[2], None))
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_execute_at_relcoords(p):
	'''execute_item : at relcoords'''
	p[0] = ('At', (None, p[2]))
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_execute_at_selector_relcoords(p):
	'''execute_item : at fullselector relcoords'''
	p[0] = ('At', (p[2], p[3]))
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_execute_at_vector(p):
	'''execute_item : at vector_expr'''
	p[0] = ('AtVector', (None, p[2]))
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

def p_execute_at_vector_scale(p):
	'''execute_item : at LPAREN const_value RPAREN vector_expr'''
	p[0] = ('AtVector', (p[3], p[5]))
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

def p_execute_in_dimension(p):
	'''execute_item : in overworld
					| in the_end
					| in the_nether'''
	p[0] = ('In', p[2])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

#### For selector	
def p_for_selector(p):
	'''codeblock : for ATID in fullselector newlines blocklist end'''
	p[0] = for_selector_block(p.lineno(1), p[2], p[4], p[6])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

#### Conditions
def p_conditions_one(p):
	'''conditions : condition'''
	p[0] = [p[1]]
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_conditions(p):
	'''conditions : condition and conditions'''
	p[0] = [p[1]] + p[3]
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

def p_condition_fullselector(p):
	'''condition : fullselector'''
	p[0] = ('selector', p[1])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_condition_score(p):
	'''condition : variable LT variable
				 | variable LEQ variable
				 | variable EQUALEQUAL variable
				 | variable GT variable
				 | variable GEQ variable'''
	op = p[2]
	if op == '==':
		op = '='
	p[0] = ('score', (p[1], op, p[3]))	
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

def p_condition_vector_equality(p):
	'''condition : vector_var EQUALEQUAL vector_var'''
	p[0] = ('vector_equality', (p[1], p[3]))
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

def p_condition_bool(p):
	'''condition : variable'''
	p[0] = ('score', (p[1], '>', virtualint_var('0')))
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

def p_condition_not_bool(p):
	'''condition : not variable'''
	p[0] = ('score', (p[2], '<=', virtualint_var(0)))
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_condition_block(p):
	'''condition : block relcoords ID'''
	p[0] = ('block', (p[2], p[3]))
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

def p_condition_block_virtual(p):
	'''condition : block relcoords DOLLAR ID'''
	p[0] = ('block', (p[2], p[3]+p[4])) 
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
#### If python
def p_block_if_command(p):
	'''codeblock : if const_value newlines blocklist end'''
	p[0] = python_if_block(p.lineno(1), p[2], p[4], None)
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_block_ifelse_command(p):
	'''codeblock : if const_value newlines blocklist else newlines blocklist end'''
	p[0] = python_if_block(p.lineno(1), p[2], p[4], p[7])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

#### While
def p_block_while(p):
	'''codeblock : while conditions newlines blocklist end'''
	p[0] = while_block(p.lineno(1), [('If', p[2])], p[4])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_block_while_execute(p):
	'''codeblock : while conditions execute_items newlines blocklist end'''
	p[0] = while_block(p.lineno(1), [('If', p[2])] + p[3], p[5])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

#### For	
def p_block_for_index_by(p):
	'''codeblock : for variable EQUALS expr to expr by expr newlines blocklist end'''
	p[0] = for_index_block(p.lineno(1), p[2], p[4], p[6], p[8], p[10])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_block_for_index(p):
	'''codeblock : for variable EQUALS expr to expr newlines blocklist end'''
	p[0] = for_index_block(p.lineno(1), p[2], p[4], p[6], None, p[8])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
#### Switch
def p_switch(p):
	'''codeblock : switch expr newlines cases end'''
	p[0] = switch_block(p.lineno(1), p[2], p[4])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_cases_one(p):
	'''cases : switch_case newlines'''
	p[0] = [p[1]]
	
def p_cases_multiple(p):
	'''cases : switch_case newlines cases'''
	p[0] = [p[1]] + p[3]
	
def p_switch_case_single(p):
	'''switch_case : case const_value newlines blocklist end'''
	p[0] = ('range', (p[2], p[2], p[4]))
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

def p_switch_case_range(p):
	'''switch_case : case const_value to const_value newlines blocklist end'''
	p[0] = ('range', (p[2], p[4], p[6]))
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_switch_case_python(p):
	'''switch_case : case DOLLAR ID in const_value newlines blocklist end'''
	p[0] = ('python', (p[3], p[5], p[7]))
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

#### Tell/Title	
def p_block_tell(p):
	'''codeblock : tell fullselector string'''
	p[0] = tell_block(p.lineno(1), p[2], p[3])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_block_title(p):
	'''codeblock : title fullselector string
				 | subtitle fullselector string
				 | actionbar fullselector string'''
	p[0] = title_block(p.lineno(1), p[1], p[2], None, p[3])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
	
def p_block_title_times(p):
	'''codeblock : title fullselector const_value const_value const_value string
				 | subtitle fullselector const_value const_value const_value string
				 | actionbar fullselector const_value const_value const_value string'''
	p[0] = title_block(p.lineno(1), p[1], p[2], (p[3], p[4], p[5]), p[6])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_block_selector_assignment(p):
	'''codeblock : selector_assignment
				 | selector_define_block'''
	p[0] = p[1]
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_block_function_call(p):
	'''codeblock : function_call
				 | method_call
				 | macro_call
				 | template_function_call
				 | pythonassignment'''
	p[0] = p[1]
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
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
		
#### Virtual number    
def p_const_value_interpreted(p):
	'''const_value : DOLLAR string'''
	p[0] = interpreted_python(p[2], p.lineno(1))
	
def p_const_value_expr(p):
	'''const_value : pyexpr'''
	p[0] = interpreted_python(p[1], p.lineno(1))
	
def p_pyexpr_single(p):
	'''pyexpr : number
	          | NORMSTRING'''
	p[0] = p[1]
	
def p_pyexpr_binop(p):
	'''pyexpr : pyexpr PLUS pyexpr
	          | pyexpr MINUS pyexpr
	          | pyexpr TIMES pyexpr
	          | pyexpr DIVIDE pyexpr
	          | pyexpr MOD pyexpr
	          | pyexpr EQUALEQUAL pyexpr
	          | pyexpr LEQ pyexpr
	          | pyexpr GEQ pyexpr
	          | pyexpr LT pyexpr
	          | pyexpr GT pyexpr'''
	p[0] = p[1] + p[2] + p[3]
	
def p_pyexpr_binop_double(p):
	'''pyexpr : pyexpr NOT EQUALS pyexpr
	          | pyexpr TIMES TIMES pyexpr'''
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
	'''pyexpr_expr_list : pyexpr COMMA pyexpr_expr_list'''
	p[0] = p[1] + p[2] + p[3]
	
def p_pyexpr_array(p):
	'''pyexpr : LBRACK pyexpr_expr_list RBRACK
	          | LPAREN pyexpr_expr_list RPAREN'''
	p[0] = p[1] + p[2] + p[3]
	
def p_pyexpr_function_call(p):
	'''pyexpr : DOLLAR FUNCTIONID pyexpr_expr_list RPAREN'''
	p[0] = p[2] + '(' + p[3] + p[4]
	
def p_pyexpr_array_lookup(p):
	'''pyexpr : pyid LBRACK pyexpr RBRACK'''
	p[0] = p[1] + p[2] + p[3] + p[4]
	
def p_pyexpr_pyid(p):
	'''pyid : DOLLAR ID'''
	p[0] = p[2]
	
def p_pyexpr_pyid_member(p):
	'''pyid : pyid DOT ID'''
	p[0] = p[1] + p[2] + p[3]

def p_pyexpr_var(p):
	'''pyexpr : pyid'''
	p[0] = p[1]
	

	
#### Virtual integer
def p_virtualinteger_literal(p):
	'''virtualinteger : integer'''
	p[0] = p[1]
	
def p_virtualinteger_symbol(p):
	'''virtualinteger : DOLLAR ID'''
	p[0] = '$' + p[2]

#### Block tags
def p_blocktag(p):
	'''blocktag : define block ID newlines block_list end'''
	p[0] = block_tag_block(p.lineno(1), p[3], p[5])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_block_list(p):
	'''block_list : ID newlines block_list'''
	p[0] = [p[1]] + p[3]
	
def p_block_list_one(p):
	'''block_list : ID newlines'''
	p[0] = [p[1]]

#### Pointer Declaration
def p_pointer_decl(p):
	'''pointer_decl : ID COLON fullselector'''
	p[0] = pointer_decl_block(p.lineno(0), p[1], p[3])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

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
def p_selector_assignment(p):
	'''selector_assignment : ATID EQUALS fullselector'''
	p[0] = selector_assignment_block(p.lineno(1), p[1], p[3])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_selector_define(p):
	'''selector_define_block : define ATID EQUALS fullselector newlines selector_definition end
	                         | define ATID COLON  fullselector newlines selector_definition end'''
	p[0] = selector_definition_block(p.lineno(1), p[2], p[4], p[6])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_selector_definition_empty(p):
	'''selector_definition : empty'''
	p[0] = []
	
def p_selector_definition(p):
	'''selector_definition : selector_item newlines selector_definition'''
	p[0] = [p[1]] + p[3]
	
def p_selector_item_tag(p):
	'''selector_item : create json_object'''
	p[0] = ('Tag', p[2])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_selector_item_path_scale(p):
	'''selector_item : ID EQUALS data_path data_type const_value
	                 | ID COLON  data_path data_type const_value'''
	p[0] = ('Path', (p[1], p[3], p[4], p[5]))
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_selector_item_path(p):
	'''selector_item : ID EQUALS data_path data_type
					 | ID COLON  data_path data_type'''
	p[0] = ('Path', (p[1], p[3], p[4], None))
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

def p_selector_item_vector_path_scale(p):
	'''selector_item : LT ID GT EQUALS data_path data_type const_value
					 | LT ID GT COLON  data_path data_type const_value'''
	p[0] = ('VectorPath', (p[2], p[5], p[6], p[7]))
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

def p_selector_item_vector_path(p):
	'''selector_item : LT ID GT EQUALS data_path data_type
					 | LT ID GT COLON data_path data_type'''
	p[0] = ('VectorPath', (p[2], p[5], p[6], None))
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_selector_item_method(p):
	'''selector_item : functionsection'''
	p[0] = ('Method', p[1])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_selector_pointer(p):
	'''selector_item : ID EQUALS fullselector
					 | ID COLON  fullselector'''
	p[0] = ('Pointer', (p[1], p[3]))
	
def p_data_path_id(p):
	'''data_path : ID'''
	p[0] = p[1]
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_data_path_array(p):
	'''data_path : ID LBRACK virtualinteger RBRACK'''
	p[0] = '{0}[{1}]'.format(p[1], p[3])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_data_path_multi(p):
	'''data_path : data_path DOT data_path'''
	p[0] = '{0}.{1}'.format(p[1], p[3])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_data_type(p):
	'''data_type : ID'''
	if p[1] not in ['byte', 'double', 'float', 'int', 'long', 'short']:
		raise SyntaxError('Syntax Error: Invalid path type "{}" at line {}.'.format(p.lineno(1)))
	p[0] = p[1]
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
#### Array
def p_array_definition(p):
	'''array_definition : array ID LBRACK const_value RBRACK'''
	p[0] = array_definition_block(p.lineno(1), p[2], const_number(0), p[4])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_array_definition_range(p):
	'''array_definition : array ID LBRACK const_value to const_value RBRACK'''
	p[0] = array_definition_block(p.lineno(1), p[2], p[4], p[6])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
#### Create
def p_block_create(p):
	'''codeblock : create_block'''
	p[0] = p[1]
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_create(p):
	'''create_block : create ATID relcoords'''
	p[0] = create_block(p.lineno(1), p[2], p[3])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_create_nocoords(p):
	'''create_block : create ATID'''
	p[0] = create_block(p.lineno(1), p[2], relcoords())
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
#### Python Assignment
def p_pythonassignment_interpreted_string(p):
	'''pythonassignment : DOLLAR ID EQUALS const_value'''
	p[0] = python_assignment_block(p.lineno(1), p[2], p[4])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

#### Qualifier list
def p_qualifiers_multiple(p):
	'''qualifiers : qualifiers COMMA qualifier
				  | qualifiers and qualifier'''
	p[0] = p[1] + "," + p[3]
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

def p_qualifiers_one(p):
	'''qualifiers : qualifier'''
	p[0] = p[1]
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

def p_qualifiers(p):
	'''qualifiers : empty'''
	p[0] = ""
	
#### Qualifier
def p_qualifier_integer(p):
	'''qualifier : const_value'''
	p[0] = p[1]
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_qualifier_binop(p):
	'''qualifier : ID EQUALS virtualinteger
				 | ID EQUALS ID
				 | ID EQUALEQUAL virtualinteger
				 | ID GEQ virtualinteger
				 | ID LEQ virtualinteger
				 | ID GT virtualinteger
				 | ID LT virtualinteger
				 | ID EQUALS json_object'''
	p[0] = p[1] + p[2] + p[3]
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_qualifier_builtin(p):
	'''qualifier : ID EQUALS virtualinteger DOT DOT virtualinteger
				 | ID EQUALS DOT DOT virtualinteger
				 | ID EQUALS virtualinteger DOT DOT'''
	p[0] = ''.join(p[1:])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

def p_qualifier_empty(p):
	'''qualifier : ID EQUALS'''
	p[0] = p[1] + p[2]
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_qualifier_is_not(p):
	'''qualifier : ID EQUALS NOT ID'''
	p[0] = p[1] + p[2] + p[3] + p[4]
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

def p_qualifier_is(p):
	'''qualifier : ID'''
	p[0] = p[1]
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

def p_qualifier_not(p):
	'''qualifier : not ID'''
	p[0] = 'not ' + p[2]
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

#### Full Selector
def p_fullselector_symbol(p):
	'''fullselector : ATID
					| ATID LBRACK qualifiers RBRACK'''
	if len(p) == 2:
		p[0] = "@{0}[]".format(p[1])
	else:
		p[0] = "@{0}[{1}]".format(p[1], p[3])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

#### Relative Coordinates
def p_relcoord_number(p):
	'''relcoord : const_value'''
	p[0] = relcoord('', p[1])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

def p_relcoord_relnumber(p):
	'''relcoord : TILDE const_value'''
	p[0] = relcoord('~', p[2])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_relcoord_relzero(p):
	'''relcoord : TILDE
	            | TILDEEMPTY'''
	p[0] = relcoord('~', const_string(''))
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
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
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

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
	
def p_nbt_list_block(p):
	'''nbt_list : block_coords DOT LBRACK data_path RBRACK'''
	p[0] = block_nbt_path(p[1], p[4])
	
def p_nbt_object_entity(p):
	'''nbt_object : fullselector DOT LCURLY data_path RCURLY'''
	p[0] = entity_nbt_path(p[1], p[4])
	
def p_nbt_object_block(p):
	'''nbt_object : block_coords DOT LCURLY data_path RCURLY'''
	p[0] = block_nbt_path(p[1], p[4])
	
def p_nbt_source_path_entity(p):
	'''nbt_path : fullselector DOT data_path'''
	p[0] = entity_nbt_path(p[1], p[3])
	
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
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_assignment(p):
	'''codeblock : variable EQUALS expr
				 | variable PLUSEQUALS expr
				 | variable MINUSEQUALS expr
				 | variable TIMESEQUALS expr
				 | variable DIVIDEEQUALS expr
				 | variable MODEQUALS expr'''
	p[0] = scoreboard_assignment_block(p.lineno(1), p[1], p[2], p[3])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_assignment_unary_default(p):
	'''codeblock : variable PLUSPLUS
				 | variable MINUSMINUS'''
	op = p[2][0]+'='
	operand = virtualint_var('1')
	p[0] = scoreboard_assignment_block(p.lineno(1), p[1], op, operand)
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

def p_assignment_create(p):
	'''codeblock : variable EQUALS create_block'''
	p[0] = scoreboard_assignment_block(p.lineno(1), p[1], p[2], create_expr(p[3]))
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
#### Vector assignment
def p_vector_assignment_vector(p):
	'''codeblock : vector_var EQUALS vector_expr
				 | vector_var PLUSEQUALS vector_expr
				 | vector_var MINUSEQUALS vector_expr'''
	p[0] = vector_assignment_block(p.lineno(1), p[1], p[2], p[3])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_vector_assignment_scalar(p):
	'''codeblock : vector_var EQUALS expr
				 | vector_var PLUSEQUALS expr
				 | vector_var MINUSEQUALS expr
				 | vector_var TIMESEQUALS expr
				 | vector_var DIVIDEEQUALS expr
				 | vector_var MODEQUALS expr'''
	p[0] = vector_assignment_scalar_block(p.lineno(1), p[1], p[2], p[3])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
#### Vector LHS
def p_vector_var_id(p):
	'''vector_var : LT ID GT'''
	p[0] = ('VAR_ID', p[2])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

def p_vector_var_sel_id(p):
	'''vector_var : fullselector DOT LT ID GT'''
	p[0] = ('SEL_VAR_ID', (p[1], p[4]))
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_vector_var_components(p):	
	'''vector_var : LT variable COMMA variable COMMA variable GT'''
	p[0] = ('VAR_COMPONENTS', [p[2], p[4], p[6]])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

#### Arithmetic expressions
def p_expr_var(p):
	'''expr : variable'''
	p[0] = p[1]

def p_expr_binary(p):
	'''expr : expr PLUS expr
			| expr MINUS expr
			| expr TIMES expr
			| expr DIVIDE expr
			| expr MOD expr
			| expr POWER integer'''

	p[0] = binop_expr(p[1], p[2], p[3])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_expr_dot(p):
	'''expr : vector_expr TIMES vector_expr'''
	p[0] = dot_expr(p[1], p[3])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

def p_expr_function(p):
	'''expr : function_call'''
	p[0] = func_expr(p[1])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_expr_group(p):
	'''expr : LPAREN expr RPAREN'''
	p[0] = p[2]
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

def p_expr_unary(p):
	'''expr : MINUS expr %prec UMINUS'''
	p[0] = unary_expr('-', p[2])
	
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
### Vector expressions
def p_vector_expr_paren(p):
	'''vector_expr : LPAREN vector_expr RPAREN'''
	p[0] = p[2]
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

def p_vector_expr_vector_triplet(p):
	'''vector_expr : LT expr COMMA expr COMMA expr GT'''
	p[0] = vector_expr((p[2], p[4], p[6]))
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_vector_expr_vector_unit(p):
	'''vector_expr : LT ID GT'''
	p[0] = vector_var_expr(p[2])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_vector_expr_selector_vector(p):
	'''vector_expr : fullselector DOT LT ID GT'''
	p[0] = sel_vector_var_expr(p[1], p[4])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_vector_expr_binop_vector(p):
	'''vector_expr : vector_expr PLUS vector_expr
				   | vector_expr MINUS vector_expr'''
	p[0] = vector_binop_vector_expr(p[1], p[2], p[3])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_vector_expr_binop_scalar(p):
	'''vector_expr : vector_expr PLUS expr
				   | vector_expr MINUS expr
				   | vector_expr TIMES expr
				   | vector_expr DIVIDE expr
				   | vector_expr MOD expr'''
	p[0] = vector_binop_scalar_expr(p[1], p[2], p[3])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_vector_expr_binop_scalar_reversed(p):
	'''vector_expr : expr PLUS vector_expr
				   | expr TIMES vector_expr'''
	p[0] = vector_binop_scalar_expr(p[3], p[2], p[1])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_vector_expr_negative(p):
	'''vector_expr : MINUS vector_expr'''
	p[0] = vector_binop_scalar_expr(p[2], '*', num_expr(-1))
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
def p_vector_expr_here(p):
	'''vector_expr : here'''
	p[0] = vector_here_expr(None)
	mcfunction.line_numbers.append((p[0], p.lineno(1)))

def p_vector_expr_here_scale(p):
	'''vector_expr : here LPAREN const_value RPAREN'''
	p[0] = vector_here_expr(p[3])
	mcfunction.line_numbers.append((p[0], p.lineno(1)))
	
#### Json (can't implement until COLON is an available token)
def p_json_object(p):
	'''json_object : LCURLY json_members RCURLY'''
	p[0] = p[1] + p[2] + p[3]
	
def p_json_members(p):
	'''json_members : json_pair'''
	p[0] = p[1]
	
def p_json_members_multi(p):
	'''json_members : json_pair COMMA json_members'''
	p[0] = p[1] + p[2] + p[3]
	
def p_json_members_empty(p):
	'''json_members : empty'''
	p[0] = ''
	
def p_json_pair(p):
	'''json_pair : ID COLON json_value
				 | string COLON json_value'''
	p[0] = '"' + p[1] + '"' + p[2] + p[3]
	
def p_json_value(p):
	'''json_value : number
				  | json_object
				  | json_array'''
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
	'''json_array : LBRACK json_elements RBRACK'''
	p[0] = p[1] + p[2] + p[3]
	
def p_json_elements(p):
	'''json_elements : json_value'''
	p[0] = p[1]
	
def p_json_elements_multi(p):
	'''json_elements : json_value COMMA json_elements'''
	p[0] = p[1] + p[2] + p[3]
	
def p_json_elements_empty(p):
	'''json_elements : empty'''
	p[0] = ''
	
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
	p = bparser.parse(data,debug=debug,tracking=True)
	return p

