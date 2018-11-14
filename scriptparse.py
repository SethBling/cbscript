from ply import *
import scriptlex

tokens = scriptlex.tokens

line_numbers = []

def get_line(parsed):
	for obj, line in line_numbers:
		if obj is parsed:
			return line
			
	return 'Unknown'

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
	line_numbers.append((p[0], p.lineno(1)))

#### Parsed
def p_parsed_expr(p):
	'''parsed : expr'''
	p[0] = ('expr', p[1])
	line_numbers.append((p[0], p.lineno(1)))
	
#### Program
def p_program(p):
	'''program : optcomments dir PYTHON newlines optdesc optscale optassignments sections'''
	p[0] = {}
	p[0]["dir"] = p[3]
	p[0]["desc"] = p[5]
	p[0]["scale"] = p[6]
	p[0]["assignments"] = p[7]
	p[0]["sections"] = p[8]
	line_numbers.append((p[0], p.lineno(1)))

#### Optdesc
def p_optdesc(p):
	'''optdesc : desc PYTHON newlines
			   | empty'''
	if len(p) < 4:
	    p[0] = 'No Description'
	else:
	    p[0] = p[2]
	line_numbers.append((p[0], p.lineno(1)))
	
#### Optscale
def p_optscale(p):
	'''optscale : scale PYTHON newlines'''
	p[0] = int(p[2])

def p_optscale_none(p):
	'''optscale : empty'''
	p[0] = 1000
	
#### Sections
def p_sections_multiple(p):
	'''sections : section_commented newlines sections'''
	p[0] = [p[1]] + p[3]
	line_numbers.append((p[0], p.lineno(1)))

def p_sections_empty(p):
	'''sections : empty'''
	p[0] = []

def p_section_commented(p):
	'''section_commented : optcomments section'''
	type, name, template_params, params, lines = p[2]
	
	p[0] = type, name, template_params, params, [('Comment', '#' + line) for line in p[1]] + lines
	line_numbers.append((p[0], p.lineno(1)))

def p_optcomments(p):
	'''optcomments : COMMENT optnewlines optcomments'''
	p[0] = [p[1]] + p[3]
	line_numbers.append((p[0], p.lineno(1)))
	
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
	line_numbers.append((p[0], p.lineno(1)))

#### Reset Section	
def p_resetsection(p):
	'''resetsection : reset newlines blocklist end'''
	p[0] = ('reset', 'reset', [], [], p[3])
	line_numbers.append((p[0], p.lineno(1)))
	
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
	line_numbers.append((p[0], p.lineno(1)))
	
#### Function Section
def p_functionsection(p):
	'''functionsection : function ID LPAREN id_list RPAREN newlines blocklist end'''
	validate_mcfunction_name(p[2])

	p[0] = ('function', p[2], [], p[4], p[7])
	line_numbers.append((p[0], p.lineno(1)))

#### Template Function Section
def p_template_function_section(p):
	'''template_function_section : function ID LT macro_params GT LPAREN id_list RPAREN newlines blocklist end'''
	validate_mcfunction_name(p[2])
	
	p[0] = ('template_function', p[2], p[4], p[7], p[10])
	line_numbers.append((p[0], p.lineno(1)))

#### Macro section
def p_macrosection(p):
	'''macrosection : macro DOLLAR ID macro_args newlines blocklist end'''
	p[0] = ('macro', p[3], [], p[4], p[6])
	line_numbers.append((p[0], p.lineno(1)))
	
def p_macro_args(p):
	'''macro_args : LPAREN macro_params RPAREN'''
	p[0] = p[2]
	line_numbers.append((p[0], p.lineno(1)))
	
def p_macro_args_empty(p):
	'''macro_args : empty'''
	p[0] = []

def p_macro_params(p):
	'''macro_params : DOLLAR ID COMMA macro_params'''
	p[0] = [p[2]] + p[4]
	line_numbers.append((p[0], p.lineno(1)))

def p_macro_params_one(p):
	'''macro_params : DOLLAR ID'''
	p[0] = [p[2]]
	line_numbers.append((p[0], p.lineno(1)))
	
def p_macro_params_empty(p):
	'''macro_params : empty'''
	p[0] = []
	
#### Newlines
def p_newlines(p):
	'''newlines : NEWLINE newlines
				| NEWLINE'''
	p[0] = None
	line_numbers.append((p[0], p.lineno(1)))
	
def p_optnewlines(p):
	'''optnewlines : newlines
				   | empty'''
				   
#### Identifier List
def p_id_list(p):
	'''id_list : ID COMMA id_list'''
	p[0] = [p[1]] + p[3]
	line_numbers.append((p[0], p.lineno(1)))

def p_id_list_one(p):
	'''id_list : ID'''
	p[0] = [p[1]]
	line_numbers.append((p[0], p.lineno(1)))

def p_id_list_empty(p):
	'''id_list : empty'''
	p[0] = []
	
#### Optassignments
def p_optassignments_multiple(p):
	'''optassignments : pythonassignment newlines optassignments
					  | selectorassignment newlines optassignments
					  | selector_define_block newlines optassignments
					  | blocktag newlines optassignments
					  | array_definition newlines optassignments'''
	p[0] = [p[1]] + p[3]
	line_numbers.append((p[0], p.lineno(1)))
	
def p_optassignments_comment(p):
	'''optassignments : COMMENT newlines optassignments'''
	p[0] = p[3]
	line_numbers.append((p[0], p.lineno(1)))

def p_optassignments_empty(p):
	'''optassignments : empty'''
	p[0] = []

#### Variable
def p_variable_selector(p):
	'''variable : fullselector DOT ID'''
	p[0] = ('Var', (p[1], p[3]))
	
def p_variable_global(p):
	'''variable : ID'''
	p[0] = ('Var', ('Global', p[1]))
	
def p_variable_array_const(p):
	'''variable : ID LBRACK virtualinteger RBRACK'''
	p[0] = ('ArrayConst', (p[1], p[3]))
	
def p_variable_array_expr(p):
	'''variable : ID LBRACK expr RBRACK'''
	p[0] = ('ArrayExpr', (p[1], p[3]))
	
#### Blocklist
def p_optcomment(p):
	'''optcomment : COMMENT'''
	p[0] = [('Comment', p[1])]
	line_numbers.append((p[0], p.lineno(1)))
	
def p_optcomment_empty(p):
	'''optcomment : empty'''
	p[0] = []

def p_blocklist_multiple(p):
	'''blocklist : codeblock optcomment newlines blocklist'''
	p[0] = p[2] + [p[1]] + p[4]
	line_numbers.append((p[0], p.lineno(1)))

def p_blocklist_empty(p):
	'''blocklist : empty'''
	p[0] = []
	
def p_block(p):
	'''codeblock : comment_block
			 | command_block
			 | move_block
			 | create_block
			 | for_block
			 | if_block
			 | trigger_block
			 | execute_block
			 | while_block
			 | switch_block
			 | tell_block
			 | function_call_block
			 | template_function_call
			 | method_call_block
			 | macro_call_block
			 | pythonassignment_block
			 | assignment_block
			 | selectorassignment_block
			 | vector_assignment_block
			 | vector_assignment_scalar_block'''
	p[0] = p[1]
	line_numbers.append((p[0], p.lineno(1)))
	
#### Block
def p_block_comment(p):
	'''comment_block : COMMENT'''
	p[0] = ('Comment', p[1])
	line_numbers.append((p[0], p.lineno(1)))

def p_block_command(p):
	'''command_block : COMMAND'''
	p[0] = ('Command', p[1])
	line_numbers.append((p[0], p.lineno(1)))
	
def p_block_move(p):
	'''move_block : move fullselector relcoords'''
	p[0] = ('Move', (p[2], p[3]))
	line_numbers.append((p[0], p.lineno(1)))

def p_block_for(p):
	'''for_block : for DOLLAR ID in PYTHON newlines blocklist end'''
	p[0] = ('For', (p[3], p[5], p[7]))
	line_numbers.append((p[0], p.lineno(1)))
	
def p_block_trigger(p):
	'''trigger_block : trigger fullselector DOT ID newlines blocklist end'''
	p[0] = ('Trigger', (p[2], p[4], p[6]))
	line_numbers.append((p[0], p.lineno(1)))

#### Execute
def p_execute_as_id_global(p):
	'''codeblock : as variable newlines blocklist end'''
	p[0] = ('Execute', ([('AsId', (p[2], None))], p[4]))
	line_numbers.append((p[0], p.lineno(1)))

def p_execute_as_id_type_global(p):
	'''codeblock : as variable LPAREN ATID RPAREN newlines blocklist end'''
	p[0] = ('Execute', ([('AsId', (p[2], p[4]))], p[7]))
	line_numbers.append((p[0], p.lineno(1)))

def p_execute_as_id_do_global(p):
	'''codeblock : as variable do codeblock'''
	p[0] = ('Execute', ([('AsId', (p[2], None))], [p[4]]))
	line_numbers.append((p[0], p.lineno(1)))

def p_execute_as_id_do_type_global(p):
	'''codeblock : as variable LPAREN ATID RPAREN do codeblock'''
	p[0] = ('Execute', ([('AsId', (p[2], p[4]))], [p[7]]))
	line_numbers.append((p[0], p.lineno(1)))

def p_execute_as_create(p):
	'''codeblock : as create_block newlines blocklist end'''
	p[0] = ('Execute', ([('AsCreate', p[2][1])], p[4]))
	line_numbers.append((p[0], p.lineno(1)))

def p_execute_as_create_do(p):
	'''codeblock : as create_block do codeblock'''
	p[0] = ('Execute', ([('AsCreate', p[2][1])], [p[4]]))
	line_numbers.append((p[0], p.lineno(1)))
	
def p_execute_chain(p):
	'''execute_block : execute_items newlines blocklist end'''
	p[0] = ('Execute', (p[1], p[3]))
	line_numbers.append((p[0], p.lineno(1)))
	
def p_execute_chain_inline(p):
	'''execute_block : execute_items do codeblock
					 | execute_items then codeblock'''
	p[0] = ('Execute', (p[1], [p[3]]))
	line_numbers.append((p[0], p.lineno(1)))

#### Execute Items	
def p_execute_items_one(p):
	'''execute_items : execute_item'''
	p[0] = [p[1]]
	line_numbers.append((p[0], p.lineno(1)))
	
def p_execute_items(p):
	'''execute_items : execute_item execute_items'''
	p[0] = [p[1]] + p[2]
	line_numbers.append((p[0], p.lineno(1)))
	
def p_execute_if_condition(p):
	'''execute_item : if conditions'''
	p[0] = ('If', p[2])
	line_numbers.append((p[0], p.lineno(1)))

def p_execute_unless_condition(p):
	'''execute_item : unless conditions'''
	p[0] = ('Unless', p[2])
	line_numbers.append((p[0], p.lineno(1)))
	
def p_execute_as(p):
	'''execute_item : as fullselector'''
	p[0] = ('As', p[2])
	line_numbers.append((p[0], p.lineno(1)))

def p_execute_rotated(p):
	'''execute_item : rotated fullselector'''
	p[0] = ('Rotated', p[2])
	line_numbers.append((p[0], p.lineno(1)))
	
def p_execute_facing_coords(p):
	'''execute_item : facing relcoords'''
	p[0] = ('FacingCoords', p[2])
	line_numbers.append((p[0], p.lineno(1)))
	
def p_execute_facing_entity(p):
	'''execute_item : facing fullselector'''
	p[0] = ('FacingEntity', p[2])
	line_numbers.append((p[0], p.lineno(1)))

def p_execute_align(p):
	'''execute_item : align ID'''
	if p[2] not in ['x','y','z','xy','xz','yz','xyz']:
		raise ParseError('Must align to a combination of x, y, and z axes')
	p[0] = ('Align', p[2])
	line_numbers.append((p[0], p.lineno(1)))
	
def p_execute_at_selector(p):
	'''execute_item : at fullselector'''
	p[0] = ('At', (p[2], None))
	line_numbers.append((p[0], p.lineno(1)))
	
def p_execute_at_relcoords(p):
	'''execute_item : at relcoords'''
	p[0] = ('At', (None, p[2]))
	line_numbers.append((p[0], p.lineno(1)))
	
def p_execute_at_selector_relcoords(p):
	'''execute_item : at fullselector relcoords'''
	p[0] = ('At', (p[2], p[3]))
	line_numbers.append((p[0], p.lineno(1)))
	
def p_execute_at_vector(p):
	'''execute_item : at vector_expr'''
	p[0] = ('AtVector', (None, p[2]))
	line_numbers.append((p[0], p.lineno(1)))

def p_execute_at_vector_scale(p):
	'''execute_item : at LPAREN virtualnumber RPAREN vector_expr'''
	p[0] = ('AtVector', (p[3], p[5]))
	line_numbers.append((p[0], p.lineno(1)))

def p_execute_in_dimension(p):
    '''execute_item : in overworld
                    | in the_end
                    | in the_nether'''
    p[0] = ('In', p[2])

#### For selector	
def p_for_selector(p):
	'''codeblock : for ATID in fullselector newlines blocklist end'''
	p[0] = ('ForSelector', (p[2], p[4], p[6]))
	line_numbers.append((p[0], p.lineno(1)))

#### Conditions
def p_conditions_one(p):
	'''conditions : condition'''
	p[0] = [p[1]]
	line_numbers.append((p[0], p.lineno(1)))
	
def p_conditions(p):
	'''conditions : condition and conditions'''
	p[0] = [p[1]] + p[3]
	line_numbers.append((p[0], p.lineno(1)))

def p_condition_pointer(p):
	'''condition : variable EQUALEQUAL fullselector'''
	p[0] = ('pointer', (p[1], p[3]))
	line_numbers.append((p[0], p.lineno(1)))

def p_condition_pointer_reversed(p):
	'''condition : fullselector EQUALEQUAL variable'''
	p[0] = ('pointer', (p[3], p[1]))
	line_numbers.append((p[0], p.lineno(1)))
	
def p_condition_fullselector(p):
	'''condition : fullselector'''
	p[0] = ('selector', p[1])
	line_numbers.append((p[0], p.lineno(1)))
	
def p_condition_score(p):
	'''condition : variable LT comparison
				 | variable LEQ comparison
				 | variable EQUALEQUAL comparison
				 | variable GT comparison
				 | variable GEQ comparison'''
	op = p[2]
	if op == '==':
		op = '='
	p[0] = ('score', (p[1], op, p[3]))	
	line_numbers.append((p[0], p.lineno(1)))

def p_condition_vector_equality(p):
	'''condition : vector_var EQUALEQUAL vector_var'''
	p[0] = ('vector_equality', (p[1], p[3]))
	line_numbers.append((p[0], p.lineno(1)))

def p_condition_bool(p):
	'''condition : variable'''
	p[0] = ('score', (p[1], '>', ('num', '0')))
	line_numbers.append((p[0], p.lineno(1)))

def p_condition_not_bool(p):
	'''condition : not variable'''
	p[0] = ('score', (p[2], '<=', ('num', '0')))
	line_numbers.append((p[0], p.lineno(1)))
	
def p_condition_block(p):
	'''condition : block relcoords ID'''
	p[0] = ('block', (p[2], p[3])) 
	line_numbers.append((p[0], p.lineno(1)))
	
# Condition Comparisons
def p_comparison_num(p):
	'''comparison : virtualinteger'''
	p[0] = ('num', p[1])
	line_numbers.append((p[0], p.lineno(1)))
	
def p_comparison_global(p):
	'''comparison : variable'''
	p[0] = ('score', p[1])
	line_numbers.append((p[0], p.lineno(1)))
	
#### If python
def p_block_if_command(p):
	'''if_block : if PYTHON newlines blocklist end'''
	p[0] = ('If', (p[2], p[4], []))
	line_numbers.append((p[0], p.lineno(1)))
	
def p_block_ifelse_command(p):
	'''if_block : if PYTHON newlines blocklist else newlines blocklist end'''
	p[0] = ('If', (p[2], p[4], p[7]))
	line_numbers.append((p[0], p.lineno(1)))

#### While
def p_block_while(p):
	'''while_block : while conditions newlines blocklist end'''
	p[0] = ('While', ([('If', p[2])], p[4]))
	line_numbers.append((p[0], p.lineno(1)))
	
def p_block_while_execute(p):
	'''while_block : while conditions execute_items newlines blocklist end'''
	p[0] = ('While', ([('If', p[2])] + p[3], p[5]))
	line_numbers.append((p[0], p.lineno(1)))

#### For	
def p_block_for_index_by(p):
	'''for_block : for ID EQUALS expr to expr by expr newlines blocklist end'''
	p[0] = ('ForIndex', (p[2], p[4], p[6], p[8], p[10]))
	line_numbers.append((p[0], p.lineno(1)))
	
def p_block_for_index(p):
	'''for_block : for ID EQUALS expr to expr newlines blocklist end'''
	p[0] = ('ForIndex', (p[2], p[4], p[6], None, p[8]))
	line_numbers.append((p[0], p.lineno(1)))
	
#### Switch
def p_switch(p):
	'''switch_block : switch expr newlines cases end'''
	p[0] = ('Switch', (p[2], p[4]))
	line_numbers.append((p[0], p.lineno(1)))
	
def p_cases_one(p):
	'''cases : switch_case newlines'''
	p[0] = [p[1]]
	
def p_cases_multiple(p):
	'''cases : switch_case newlines cases'''
	p[0] = [p[1]] + p[3]
	
def p_switch_case_single(p):
	'''switch_case : case virtualinteger newlines blocklist end'''
	p[0] = ('range', (p[2], p[2], p[4]))
	line_numbers.append((p[0], p.lineno(1)))

def p_switch_case_range(p):
	'''switch_case : case virtualinteger to virtualinteger newlines blocklist end'''
	p[0] = ('range', (p[2], p[4], p[6]))
	line_numbers.append((p[0], p.lineno(1)))
	
def p_switch_case_python(p):
	'''switch_case : case DOLLAR ID in PYTHON newlines blocklist end'''
	p[0] = ('python', (p[3], p[5], p[7]))
	line_numbers.append((p[0], p.lineno(1)))

#### Tell/Title	
def p_block_tell(p):
	'''tell_block : tell fullselector PYTHON'''
	p[0] = ('Tell', (p[2], p[3]))
	line_numbers.append((p[0], p.lineno(1)))
    
def p_block_title(p):
    '''codeblock : title fullselector PYTHON
                 | subtitle fullselector PYTHON
                 | actionbar fullselector PYTHON'''
    p[0] = ('Title', (p[1], p[2], None, p[3]))
    
def p_block_title_times(p):
    '''codeblock : title fullselector virtualinteger virtualinteger virtualinteger PYTHON
                 | subtitle fullselector virtualinteger virtualinteger virtualinteger PYTHON
                 | actionbar fullselector virtualinteger virtualinteger virtualinteger PYTHON'''
    p[0] = ('Title', (p[1], p[2], (p[3], p[4], p[5]), p[6]))
	
def p_block_call(p):
	'''function_call_block : function_call'''
	p[0] = p[1]
	line_numbers.append((p[0], p.lineno(1)))
	
def p_block_method_call(p):
	'''method_call_block : method_call'''
	p[0] = p[1]
	line_numbers.append((p[0], p.lineno(1)))
	
def p_block_macro_call(p):
	'''macro_call_block : macro_call'''
	p[0] = p[1]
	line_numbers.append((p[0], p.lineno(1)))
	
def p_block_assignment(p):
	'''pythonassignment_block : pythonassignment'''
	p[0] = p[1]
	line_numbers.append((p[0], p.lineno(1)))
	
def p_block_math(p):
	'''assignment_block : assignment'''
	p[0] = ('ScoreboardAssignment', p[1])
	line_numbers.append((p[0], p.lineno(1)))
	
def p_block_vector_assignment(p):
	'''vector_assignment_block : vector_assignment'''
	p[0] = ('VectorAssignment', p[1])
	line_numbers.append((p[0], p.lineno(1)))
	
def p_block_vector_assignment_scalar(p):
	'''vector_assignment_scalar_block : vector_assignment_scalar'''
	p[0] = ('VectorAssignmentScalar', p[1])
	line_numbers.append((p[0], p.lineno(1)))
	
def p_block_selectorassignment(p):
	'''selectorassignment_block : selectorassignment'''
	p[0] = p[1]
	line_numbers.append((p[0], p.lineno(1)))

#### Number
def p_number_integer(p):
	'''number : INTEGER
	          | HEX
			  | BINARY'''
	p[0] = p[1]
	line_numbers.append((p[0], p.lineno(1)))
	
def p_number_minus_integer(p):
	'''number : MINUS INTEGER
	          | MINUS HEX
			  | MINUS BINARY'''
	p[0] = str(-int(p[2]))
	line_numbers.append((p[0], p.lineno(1)))
		
def p_number_float(p):
	'''number : FLOAT'''
	p[0] = p[1]
	line_numbers.append((p[0], p.lineno(1)))
	
def p_number_minus_float(p):
	'''number : MINUS FLOAT'''
	p[0] = str(-float(p[2]))
	line_numbers.append((p[0], p.lineno(1)))
		
#### Virtual number    
def p_virtualnumber_literal(p):
	'''virtualnumber : number'''
	p[0] = p[1]
	line_numbers.append((p[0], p.lineno(1)))
	
def p_virtualnumber_symbol(p):
	'''virtualnumber : DOLLAR ID'''
	p[0] = '$' + p[2]
	line_numbers.append((p[0], p.lineno(1)))
	
#### Virtual integer
def p_virtualinteger_literal(p):
	'''virtualinteger : INTEGER
	                  | HEX
					  | BINARY'''
	p[0] = p[1]
	line_numbers.append((p[0], p.lineno(1)))
	
def p_virtualinteger_literal_minus(p):
	'''virtualinteger : MINUS INTEGER
	                  | MINUS HEX
					  | MINUS BINARY'''
	p[0] = str(-int(p[2]))
	line_numbers.append((p[0], p.lineno(1)))

def p_virtualinteger_symbol(p):
	'''virtualinteger : DOLLAR ID'''
	p[0] = '$' + p[2]
	line_numbers.append((p[0], p.lineno(1)))

#### Block tags
def p_blocktag(p):
	'''blocktag : define block ID newlines block_list end'''
	p[0] = ('BlockTag', (p[3], p[5]))
	
def p_block_list(p):
	'''block_list : ID newlines block_list'''
	p[0] = [p[1]] + p[3]
	
def p_block_list_one(p):
	'''block_list : ID newlines'''
	p[0] = [p[1]]

#### Selector Assignment
def p_selectorassignment(p):
	'''selectorassignment : ATID EQUALS fullselector'''
	p[0] = ('SelectorAssignment', (p[1], p[3]))
	line_numbers.append((p[0], p.lineno(1)))
	
def p_selector_define(p):
	'''selector_define_block : define ATID EQUALS fullselector newlines selector_definition end'''
	p[0] = ('SelectorDefinition', (p[2], p[4], p[6]))
	line_numbers.append((p[0], p.lineno(1)))
	
def p_selector_definition_empty(p):
	'''selector_definition : empty'''
	p[0] = []
	
def p_selector_definition(p):
	'''selector_definition : selector_item newlines selector_definition'''
	p[0] = [p[1]] + p[3]
	line_numbers.append((p[0], p.lineno(1)))
	
def p_selector_item_tag(p):
	'''selector_item : create PYTHON'''
	p[0] = ('Tag', p[2])
	line_numbers.append((p[0], p.lineno(1)))
	
def p_selector_item_path_scale(p):
	'''selector_item : ID EQUALS data_path data_type virtualnumber'''
	p[0] = ('Path', (p[1], p[3], p[4], p[5]))
	line_numbers.append((p[0], p.lineno(1)))
	
def p_selector_item_path(p):
	'''selector_item : ID EQUALS data_path data_type'''
	p[0] = ('Path', (p[1], p[3], p[4], None))
	line_numbers.append((p[0], p.lineno(1)))

def p_selector_item_vector_path_scale(p):
	'''selector_item : LT ID GT EQUALS data_path data_type virtualnumber'''
	p[0] = ('VectorPath', (p[2], p[5], p[6], p[7]))
	line_numbers.append((p[0], p.lineno(1)))

def p_selector_item_vector_path(p):
	'''selector_item : LT ID GT EQUALS data_path data_type'''
	p[0] = ('VectorPath', (p[2], p[5], p[6], None))
	line_numbers.append((p[0], p.lineno(1)))
	
def p_selector_item_method(p):
	'''selector_item : functionsection'''
	p[0] = ('Method', p[1])
	line_numbers.append((p[0], p.lineno(1)))
	
def p_data_path_id(p):
	'''data_path : ID'''
	p[0] = p[1]
	line_numbers.append((p[0], p.lineno(1)))
	
def p_data_path_array(p):
	'''data_path : ID LBRACK virtualinteger RBRACK'''
	p[0] = '{0}[{1}]'.format(p[1], p[3])
	line_numbers.append((p[0], p.lineno(1)))
	
def p_data_path_multi(p):
	'''data_path : data_path DOT data_path'''
	p[0] = '{0}.{1}'.format(p[1], p[3])
	line_numbers.append((p[0], p.lineno(1)))
	
def p_data_type(p):
	'''data_type : byte
				 | double
				 | float
				 | int
				 | long
				 | short'''
	p[0] = p[1]
	line_numbers.append((p[0], p.lineno(1)))
	
#### Array
def p_array_definition(p):
	'''array_definition : array ID LBRACK virtualinteger RBRACK'''
	
	p[0] = ('ArrayDefinition', (p[2], '0', p[4]))
	line_numbers.append((p[0], p.lineno(1)))
	
def p_array_definition_range(p):
	'''array_definition : array ID LBRACK virtualinteger to virtualinteger RBRACK'''
	p[0] = ('ArrayDefinition', (p[2], p[4], p[6]))
	line_numbers.append((p[0], p.lineno(1)))
	
#### Create
def p_create(p):
	'''create_block : create ATID relcoords'''
	p[0] = ('Create', (p[2], p[3]))
	line_numbers.append((p[0], p.lineno(1)))
	
def p_create_nocoords(p):
	'''create_block : create ATID'''
	p[0] = ('Create', (p[2], ['~','~','~']))
	line_numbers.append((p[0], p.lineno(1)))
	
#### Python Assignment
def p_pythonassignment(p):
	'''pythonassignment : DOLLAR ID PYTHON'''
	p[0] = ('PythonAssignment', (p[2], p[3]))
	line_numbers.append((p[0], p.lineno(1)))


#### Qualifier list
def p_qualifiers_multiple(p):
	'''qualifiers : qualifiers COMMA qualifier
				  | qualifiers and qualifier'''
	p[0] = p[1] + "," + p[3]
	line_numbers.append((p[0], p.lineno(1)))

def p_qualifiers_one(p):
	'''qualifiers : qualifier'''
	p[0] = p[1]
	line_numbers.append((p[0], p.lineno(1)))

def p_qualifiers(p):
	'''qualifiers : empty'''
	p[0] = ""
	
#### Qualifier
def p_qualifier_integer(p):
	'''qualifier : virtualinteger'''
	p[0] = p[1]
	line_numbers.append((p[0], p.lineno(1)))
	
def p_qualifier_binop(p):
	'''qualifier : ID EQUALS virtualinteger
				 | ID EQUALS ID
				 | ID EQUALEQUAL virtualinteger
				 | ID GEQ virtualinteger
				 | ID LEQ virtualinteger
				 | ID GT virtualinteger
				 | ID LT virtualinteger'''
	p[0] = p[1] + p[2] + p[3]
	line_numbers.append((p[0], p.lineno(1)))
	
def p_qualifier_builtin(p):
	'''qualifier : ID EQUALS virtualinteger DOT DOT virtualinteger
				 | ID EQUALS DOT DOT virtualinteger
				 | ID EQUALS virtualinteger DOT DOT'''
	p[0] = ''.join(p[1:])
	line_numbers.append((p[0], p.lineno(1)))

def p_qualifier_empty(p):
	'''qualifier : ID EQUALS'''
	p[0] = p[1] + p[2]
	line_numbers.append((p[0], p.lineno(1)))
	
def p_qualifier_is_not(p):
	'''qualifier : ID EQUALS NOT ID'''
	p[0] = p[1] + p[2] + p[3] + p[4]
	line_numbers.append((p[0], p.lineno(1)))

def p_qualifier_is(p):
	'''qualifier : ID'''
	p[0] = p[1]
	line_numbers.append((p[0], p.lineno(1)))

def p_qualifier_not(p):
	'''qualifier : not ID'''
	p[0] = 'not ' + p[2]
	line_numbers.append((p[0], p.lineno(1)))

#### Full Selector
def p_fullselector_symbol(p):
	'''fullselector : ATID
	                | ATID LBRACK qualifiers RBRACK'''
	if len(p) == 2:
		p[0] = "@{0}[]".format(p[1])
	else:
		p[0] = "@{0}[{1}]".format(p[1], p[3])
	line_numbers.append((p[0], p.lineno(1)))

#### Relative Coordinates
def p_relcoord_number(p):
	'''relcoord : virtualnumber'''
	p[0] = p[1]
	line_numbers.append((p[0], p.lineno(1)))

def p_relcoord_relnumber(p):
	'''relcoord : TILDE virtualnumber'''
	p[0] = '~' + p[2]
	line_numbers.append((p[0], p.lineno(1)))
	
def p_relcoord_relzero(p):
	'''relcoord : TILDEEMPTY'''
	p[0] = "~"	
	line_numbers.append((p[0], p.lineno(1)))
	
def p_relcoord_relzerotilde(p):
	'''relcoord : TILDE'''
	p[0] = "~"
	line_numbers.append((p[0], p.lineno(1)))

#### Local Coordinates
def p_localcoord_localnumber(p):
	'''localcoord : POWER virtualnumber'''
	p[0] = '^' + p[2]
	line_numbers.append((p[0], p.lineno(1)))
	
def p_localcoord_localzeroempty(p):
	'''localcoord : POWEREMPTY'''
	p[0] = "^"	
	line_numbers.append((p[0], p.lineno(1)))
				
def p_localcoord_localzero(p):
	'''localcoord : POWER'''
	p[0] = "^"
	line_numbers.append((p[0], p.lineno(1)))

	
# Relcoords
def p_relcoords(p):
	'''relcoords : virtualnumber virtualnumber virtualnumber
				 | relcoord relcoord relcoord
				 | localcoord localcoord localcoord'''
	p[0] = (p[1], p[2], p[3])
	line_numbers.append((p[0], p.lineno(1)))

#### Assignment
def p_return_expression(p):
	'''assignment : return expr'''
	p[0] = (('Var', ('Global', 'ReturnValue')), '=', p[2])
	line_numbers.append((p[0], p.lineno(1)))
	
def p_assignment(p):
	'''assignment : variable EQUALS expr
				  | variable PLUSEQUALS expr
				  | variable MINUSEQUALS expr
				  | variable TIMESEQUALS expr
				  | variable DIVIDEEQUALS expr
				  | variable MODEQUALS expr'''
	p[0] = (p[1], p[2], p[3])
	line_numbers.append((p[0], p.lineno(1)))
	
def p_assignment_unary_default(p):
	'''assignment : variable PLUSPLUS
				  | variable MINUSMINUS'''
	op = p[2][0]+'='
	operand = ('NUM', '1')
	p[0] = (p[1], op, operand)
	line_numbers.append((p[0], p.lineno(1)))

def p_assignment_selector_global(p):
	'''assignment : variable EQUALS fullselector'''
	p[0] = (p[1], p[2], ('Selector', p[3]))
	line_numbers.append((p[0], p.lineno(1)))

	
def p_assignment_create(p):
	'''assignment : variable EQUALS create_block'''
	p[0] = (p[1], p[2], p[3])
	line_numbers.append((p[0], p.lineno(1)))
	
#### Vector assignment
def p_vector_assignment_vector(p):
	'''vector_assignment : vector_var EQUALS vector_expr
						 | vector_var PLUSEQUALS vector_expr
						 | vector_var MINUSEQUALS vector_expr'''
	p[0] = (p[1], p[2], p[3])
	line_numbers.append((p[0], p.lineno(1)))
	
def p_vector_assignment_scalar(p):
	'''vector_assignment_scalar : vector_var EQUALS expr
								| vector_var PLUSEQUALS expr
								| vector_var MINUSEQUALS expr
								| vector_var TIMESEQUALS expr
								| vector_var DIVIDEEQUALS expr
								| vector_var MODEQUALS expr'''
	p[0] = (p[1], p[2], p[3])
	line_numbers.append((p[0], p.lineno(1)))
	
#### Vector LHS
def p_vector_var_id(p):
	'''vector_var : LT ID GT'''
	p[0] = ('VAR_ID', p[2])
	line_numbers.append((p[0], p.lineno(1)))

def p_vector_var_sel_id(p):
	'''vector_var : fullselector DOT LT ID GT'''
	p[0] = ('SEL_VAR_ID', (p[1], p[4]))
	line_numbers.append((p[0], p.lineno(1)))
	
def p_vector_var_components(p):	
	'''vector_var : LT variable COMMA variable COMMA variable GT'''
	p[0] = ('VAR_COMPONENTS', [p[2], p[4], p[6]])
	line_numbers.append((p[0], p.lineno(1)))


#### Arithmetic expressions

def p_expr_binary(p):
	'''expr : expr PLUS expr
			| expr MINUS expr
			| expr TIMES expr
			| expr DIVIDE expr
			| expr MOD expr
			| expr POWER INTEGER
			| expr POWER HEX
			| expr POWER BINARY'''

	p[0] = ('BINOP',p[2],p[1],p[3])
	line_numbers.append((p[0], p.lineno(1)))
	
def p_expr_dot(p):
	'''expr : vector_expr TIMES vector_expr'''
	p[0] = ('DOT', p[1], p[3])
	line_numbers.append((p[0], p.lineno(1)))

def p_expr_number(p):
	'''expr : virtualinteger'''
	p[0] = ('NUM',p[1])
	line_numbers.append((p[0], p.lineno(1)))
	
def p_expr_scale(p):
	'''expr : scale'''
	p[0] = ('SCALE', None)
	line_numbers.append((p[0], p.lineno(1)))

def p_expr_variable(p):
	'''expr : ID'''
	p[0] = ('SELVAR', 'Global', p[1])
	line_numbers.append((p[0], p.lineno(1)))
	
def p_expr_array_const(p):
	'''expr : ID LBRACK virtualinteger RBRACK'''
	p[0] = ('ARRAYCONST', p[1], p[3])
	line_numbers.append((p[0], p.lineno(1)))
	
def p_expr_array_expr(p):
	'''expr : ID LBRACK expr RBRACK'''
	p[0] = ('ARRAYEXPR', p[1], p[3])
	line_numbers.append((p[0], p.lineno(1)))
	
def p_expr_selector_variable(p):
	'''expr : fullselector DOT ID'''
	p[0] = ('SELVAR', p[1], p[3])
	line_numbers.append((p[0], p.lineno(1)))

def p_expr_function(p):
	'''expr : function_call'''
	(type, (name, exprlist)) = p[1]
	p[0] = ('FUNC', name, exprlist)
	line_numbers.append((p[0], p.lineno(1)))
	
def p_expr_group(p):
	'''expr : LPAREN expr RPAREN'''
	p[0] = p[2]
	line_numbers.append((p[0], p.lineno(1)))

def p_expr_unary(p):
	'''expr : MINUS expr %prec UMINUS'''
	if p[2][0] == 'NUM':
		p[0] = ('NUM', str(-int(p[2][1])))
	else:	
		p[0] = ('UNARY','-',p[2])
	line_numbers.append((p[0], p.lineno(1)))
	
### Vector expressions
def p_vector_expr_paren(p):
	'''vector_expr : LPAREN vector_expr RPAREN'''
	p[0] = p[2]
	line_numbers.append((p[0], p.lineno(1)))

def p_vector_expr_vector_triplet(p):
	'''vector_expr : LT expr COMMA expr COMMA expr GT'''
	p[0] = ('VECTOR', (p[2], p[4], p[6]))
	line_numbers.append((p[0], p.lineno(1)))
	
def p_vector_expr_vector_unit(p):
	'''vector_expr : LT ID GT'''
	p[0] = ('VECTOR_VAR', p[2])
	line_numbers.append((p[0], p.lineno(1)))
	
def p_vector_expr_selector_vector(p):
	'''vector_expr : fullselector DOT LT ID GT'''
	p[0] = ('SEL_VECTOR_VAR', (p[1], p[4]))
	line_numbers.append((p[0], p.lineno(1)))
	
def p_vector_expr_binop_vector(p):
	'''vector_expr : vector_expr PLUS vector_expr
				   | vector_expr MINUS vector_expr'''
	p[0] = ('VECTOR_BINOP_VECTOR', (p[1], p[2], p[3]))
	line_numbers.append((p[0], p.lineno(1)))
	
def p_vector_expr_binop_scalar(p):
	'''vector_expr : vector_expr PLUS expr
				   | vector_expr MINUS expr
				   | vector_expr TIMES expr
				   | vector_expr DIVIDE expr
				   | vector_expr MOD expr'''
	p[0] = ('VECTOR_BINOP_SCALAR', (p[1], p[2], p[3]))
	line_numbers.append((p[0], p.lineno(1)))
	
def p_vector_expr_binop_reversed(p):
	'''vector_expr : expr PLUS vector_expr
				   | expr TIMES vector_expr'''
	p[0] = ('VECTOR_BINOP_SCALAR', (p[3], p[2], p[1]))
	line_numbers.append((p[0], p.lineno(1)))
	
def p_vector_expr_negative(p):
	'''vector_expr : MINUS vector_expr'''
	p[0] = ('VECTOR_BINOP_SCALAR', (p[2], '*', ('NUM', '-1')))
	line_numbers.append((p[0], p.lineno(1)))
	
def p_vector_expr_here(p):
	'''vector_expr : here'''
	p[0] = ('VECTOR_HERE', None)
	line_numbers.append((p[0], p.lineno(1)))

def p_vector_expr_here_scale(p):
	'''vector_expr : here LPAREN virtualnumber RPAREN'''
	p[0] = ('VECTOR_HERE', p[3])
	line_numbers.append((p[0], p.lineno(1)))
	
#### Function call
def p_function_call(p):
	'''function_call : ID LPAREN exprlist RPAREN'''
	p[0] = ('Call', (p[1], p[3]))
	line_numbers.append((p[0], p.lineno(1)))

def p_method_call(p):
	'''method_call : fullselector DOT ID LPAREN exprlist RPAREN'''
	p[0] = ('MethodCall', (p[1], p[3], p[5]))
	line_numbers.append((p[0], p.lineno(1)))
	
#### Expression list
def p_exprlist_multiple(p):
	'''exprlist : exprlist COMMA expr'''
	p[0] = p[1]
	p[0].append(p[3])
	line_numbers.append((p[0], p.lineno(1)))
	
def p_exprlist_single(p):
	'''exprlist : expr'''
	p[0] = [p[1]]
	line_numbers.append((p[0], p.lineno(1)))

def p_exprlist_empty(p):
	'''exprlist : empty'''
	p[0] = []

#### Template Function Call
def p_template_function_call(p):
	'''template_function_call : ID LT macro_call_params GT LPAREN exprlist RPAREN'''
	p[0] = ('TemplateFunctionCall', (p[1], p[3], p[6]))
	line_numbers.append((p[0], p.lineno(1)))
	
#### Macro call	
def p_macro_call(p):
	'''macro_call : DOLLAR ID macro_call_args'''
	p[0] = ('MacroCall', (p[2], p[3]))
	line_numbers.append((p[0], p.lineno(1)))
	
def p_macro_call_args(p):
	'''macro_call_args : LPAREN macro_call_params RPAREN'''
	p[0] = p[2]
	line_numbers.append((p[0], p.lineno(1)))
	
def p_macro_call_args_empty(p):
	'''macro_call_args : empty'''
	p[0] = []
	line_numbers.append((p[0], p.lineno(1)))
	
def p_macro_call_params(p):
	'''macro_call_params : macro_call_param COMMA macro_call_params'''
	p[0] = [p[1]] + p[3]
	line_numbers.append((p[0], p.lineno(1)))

def p_macro_call_params_one(p):
	'''macro_call_params : macro_call_param'''
	p[0] = [p[1]]
	line_numbers.append((p[0], p.lineno(1)))
	
def p_macro_call_params_empty(p):
	'''macro_call_params : empty'''
	p[0] = []
	
def p_macro_call_param_number(p):
	'''macro_call_param : virtualnumber'''
	p[0] = p[1]
	line_numbers.append((p[0], p.lineno(1)))
	
#### Empty
def p_empty(p):
	'''empty : '''

def p_error(p):
	raise SyntaxError('Syntax error at line {} column {}. Unexpected symbol: "{}"'.format(p.lineno, scriptlex.find_column(bparser.data, p), p.value.replace('\n', '\\n')))
	

bparser = yacc.yacc()

def parse(data,debug=0):
	scriptlex.lexer.lineno = 1
	bparser.error = 0
	bparser.data = data
	p = bparser.parse(data,debug=debug,tracking=True)
	return p

