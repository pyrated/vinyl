import vinyl.cs as cs
import vinyl.lex as lex

for t in lex.Lexer(cs.StringStream('// This makes no sense\ndef x = (23i32)')):
    print(t)