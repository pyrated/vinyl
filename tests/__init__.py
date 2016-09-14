from vinyl import ast, lex

text = '''

    def fooBar(y: Int, x: Int): 2214342345324234 {

    }

'''

stream = lex.StringStream(text)
parser = ast.Parser.from_stream(stream)

try:
    print(parser.parse())
except lex.SyntacticalError as e:
    start = e.token.start_location
    print('Syntax Error @ {}:{} => {}'.format(start.line, start.column, e.message))
    print('{}'.format(stream.line_map[start.line]))
    print('{}{}'.format(' ' * max(start.column - 1, 0), '~' * len(e.token.text)))