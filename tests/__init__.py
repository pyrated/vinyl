import vinyl.lex as lex

for t in lex.Lexer(lex.StringStream('// This makes no sense\ndef x = (23i32)')):
    print(t)