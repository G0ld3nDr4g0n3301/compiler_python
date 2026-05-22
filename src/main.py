import sys
from lexer import Lexer
from parser import Parser, ParseError
from analyzer import SemanticAnalyzer
from optimizer import DeadCodeEliminator
from interpreter import Interpreter
from ast_printer import AstPrinter

def main():
    examples = [
        """
        var width : number = 5;
        var height : number = 10;
        var area : number = width * height;
        print area;
        """,
        """
        var greeting : string = "Hello, ";
        var name : string = "World!";
        var lang : number = 1;
        if (lang == 1) {
            print greeting + name;
        } else {
            print "Unknown language";
        }
        """,
        """
        var i : number = 0;
        var is_valid : bool = i < 3;
        while (is_valid) {
            print "Counter: ";
            print i;
            i = i + 1;
            is_valid = i < 3;
        }
        """,
        """
        var unused_var : number = 42;
        var x : number = 10;
        x = "now im a string";
        """,
        """
        func fibonacci(n : number) : number {
            if (n <= 1) {
                return n;
            }
            if (0) {
                print "lol";
            }
            return fibonacci(n - 1) + fibonacci(n - 2);
            print "test";
        }
        print "Fibonacci of 9 is:";
        print fibonacci(9);
        """,
        """
        print 1 + 5 - 8;
        print "hello " + "world";
        """,
        """
        var arr : number[] = [10, 20, 30];
        print arr;
        print "Element at index 1 is:";
        print arr[1];
        
        arr[1] = 99;
        print "Modified array:";
        print arr;
        """,
        """
        var names : string[] = [];
        print names;
        """,
        """
        var bad_arr : number[] = [1, "two", 3];
        """,
        """
        var test_arr : number[] = [1, 2];
        print test_arr[5];
        """
    ]

    for i, code in enumerate(examples):
        print(f"========== EXAMPLE {i + 1} ==========")
        
        try:
            lexer = Lexer(code)
            tokens = lexer.tokenize()

            parser = Parser(tokens)
            ast = parser.parse()

            analyzer = SemanticAnalyzer()
            analyzer.analyze(ast)
            
            has_errors = False
            for msg in analyzer.warnings:
                print(msg)
                if "[Error]" in msg:
                    has_errors = True

            if not has_errors:
                dce = DeadCodeEliminator()
                ast = dce.optimize(ast)
                
                print("--- EXECUTION OUTPUT ---")
                interpreter = Interpreter()
                interpreter.interpret(ast)
                print("------------------------")
                
                print("--- AST AFTER OPTIMIZATION ---")
                printer = AstPrinter()
                printer.print_ast(ast)
                print("------------------------")
            else:
                print("--- EXECUTION SKIPPED (Due to semantic errors) ---")

        except Exception as e:
            print(f"Fatal Exception: {e}", file=sys.stderr)
            
        print("\n")

if __name__ == "__main__":
    main()