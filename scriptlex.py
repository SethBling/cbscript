from ply import *

keywords = (
    'for', 'dir', 'desc', 'scale', 'in', 'end', 'not', 'and', 'or', 'to', 'by', 'import',
    'at', 'as', 'facing', 'rotated', 'align', 'here', 'the_end', 'the_nether', 'overworld',
    'move', 'create', 'tell', 'title', 'subtitle', 'actionbar',
    'reset', 'clock', 'function', 'if', 'unless', 'then', 'do', 'else', 'switch', 'case',
    'return', 'while', 'macro', 'block', 'define', 'array', 'remove', 'success', 'result',
)

tokens = keywords + (
     'COMMAND',
     'LEQ','GEQ','GT','LT','EQUALEQUAL','DOLLAR','DOT','COLON',
     'PLUSEQUALS','MINUSEQUALS','TIMESEQUALS','DIVIDEEQUALS','MODEQUALS','PLUSPLUS','MINUSMINUS',
     'EQUALS','PLUS','MINUS','TIMES','DIVIDE','MOD','REF',
	 #'POWEREMPTY',
	 'POWER',
     'LPAREN','RPAREN','COMMA','DECIMAL','FLOAT','HEX','BINARY','FUNCTIONID','ID','NEWLINE','LBRACK','RBRACK','LCURLY','RCURLY',
     'ATID', 'NOT', 'TILDEEMPTY', 'TILDE',
     'NORMSTRING', 'COMMENT', 'PRINT'
)

def t_None(t):
    r'None'
    t.value = "0"
    t.type = "DECIMAL"
        
    return t

def t_False(t):
    r'False'
    t.value = "0"
    t.type = "DECIMAL"
        
    return t

def t_True(t):
    r'True'
    t.value = "1"
    t.type = "DECIMAL"
        
    return t

def t_FUNCTIONID(t):
	r'[A-Za-z_][A-Za-z0-9_]*\('
	t.value = t.value[:-1]
	return t
	
def t_ID(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    if t.value in keywords:
        t.type = t.value
    return t
    
def t_COMMAND(t):
    r'(?m)^\s*/.+'
    t.lexer.lineno += t.value.count('\n')
    t.value = t.value.strip()
    return t

def t_WHITESPACE(t):
    r'[ \t]'

def t_ATID(t):
    r'@[A-Za-z_][A-Za-z0-9_]*'
    t.value = t.value[1:]
    return t

t_PRINT			= r'\$print\('	
t_EQUALEQUAL	= r'=='
t_LEQ			= r'<='
t_GEQ			= r'>='
t_LT			= r'<'
t_GT			= r'>'
t_DOLLAR		= r'\$'
t_COMMA			= r'\,'
t_PLUSEQUALS    = r'\+='
t_MINUSEQUALS   = r'-='
t_TIMESEQUALS   = r'\*='
t_MODEQUALS		= r'\%='
t_EQUALS		= r'='
t_PLUS			= r'\+'
t_MINUS			= r'-'
t_TIMES			= r'\*'
t_PLUSPLUS		= r'\+\+'
t_MINUSMINUS	= r'--'
t_DOT			= r'\.'
t_COLON			= r'\:'
t_NOT			= r'!'
t_REF			= r'&'

#def t_POWEREMPTY(t):
#    r'\^[ \t]'
#    t.value = "^"
#    return t
t_POWER   = r'\^'

def t_TILDEEMPTY(t):
    r'~[ \t]'
    t.value = "~"
    return t
t_TILDE = r'~'
t_FLOAT = r'\d+\.\d+'
t_DECIMAL = r'\d+'

def t_HEX(t):
	r'0x[0-9A-Fa-f]+'
	t.value = str(int(t.value, 16))
	return t
	
def t_BINARY(t):
	r'0b[01]+'
	t.value = str(int(t.value, 2))
	return t

def t_DIVIDEEQUALS(t):
    r'/='
    return t

def t_DIVIDE(t):
    r'/'
    return t
    
t_MOD  = r'\%'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_LBRACK  = r'\['
t_RBRACK  = r'\]'
t_LCURLY  = r'\{'
t_RCURLY  = r'\}'

t_ignore = '\r'

def t_NEWLINE(t):
    r'\n'
    t.lexer.lineno += 1
    return t
	
def t_NORMSTRING(t):
	 r'("((\\.)|[^"\n])*")|(\'((\\.)|[^\'\n])*\')'
	 return t

def t_COMMENT(t):
    r'\#.+'
    return t

def t_error(t):
    print('Illegal character "{}" was skipped at line {}'.format(t.value[0], t.lexer.lineno))
    t.lexer.skip(1)
    
# Compute column.
#     input is the input text string
#     token is a token instance
def find_column(input, token):
    line_start = input.rfind('\n', 0, token.lexpos) + 1
    return (token.lexpos - line_start) + 1

lexer = lex.lex(debug=0)