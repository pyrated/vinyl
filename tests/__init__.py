from vinyl import ast, lex

text = '''

    // This is a comment
    let CONSTANT1 Int = 4
    let CONSTANT1 Int = 2

    /*
        This is a familiar stream comment
        With multiple lines....
    */
    def main() {
        let x Int = 42
        if x {
            let y Int = x
        }

        if x {} else {}
    }
'''

stream = lex.StringStream(text)
parser = ast.Parser.from_stream(stream)

try:
    tree = parser.parse()
    print(tree)
except lex.SyntacticalError as e:
    start = e.token.start_location
    print('Syntax Error @ {}:{} => {}'.format(start.line, start.column, e.message))
    print('{}'.format(stream.line_map[start.line]))
    print('{}{}'.format(' ' * max(start.column - 1, 0), '~' * len(e.token.text)))