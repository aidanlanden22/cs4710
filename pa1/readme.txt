Programing Assignment 1 - Theorem Prover
CS4710 Artificial Intelligence
Leiqing Cai (Lc9ac)


The program can be run by:  python pa1.py
To redirect input:          python pa1.py < input_file


Why Command:
    Each rule is stored as a postfix expresssion.
    When "Why" is called on an posfix expresssion:
        1. a stack of operands and a list of string representing the reasoning is maintained:
        2. Scan through the postfix expresssion:
            a. If it is an operator: &, |, !
                - Pop the top two elements off the stack, perform the operation, and push it back to the stacks
                - A "BECAUSE" statement is appended to the reasoning.
            b. If it is a operand:
                - Search for all the rules that implies this variable
                    i. If such rule exists:
                        - Recusively call why on the postfix expression that implies the variable
                        - If one rules implies this variable is true, stop searching and concatenate the reasoning of the implication to the current reasoning, and then append a "I THUS KNOW THAT" statment to the reasoning.
                        - If none of the rules implies that the variable is true. concatenate reasonings of all the implication, and then append a "Thus I CANNOT PROVE" statement.
                    ii. If no such rule exists:
                        - Check the knowledge base to determine the truth of the variable.
                        - Append a "I KNOW" statement to the reasoning.
        3. Return the top element on the stack, along with the reasoning.

                        
    