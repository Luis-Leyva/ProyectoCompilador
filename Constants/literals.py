from pyparsing import Literal

""" Literals """
# semicolon
semicolon = Literal(";").suppress()
# colon
colon = Literal(":").suppress()
# comma
comma = Literal(",").suppress()
# left parenthesis
left_parenthesis = Literal("(")
# right parenthesis
right_parenthesis = Literal(")")
# left curly bracket
left_brace = Literal("{").suppress()
# right curly bracket
right_brace = Literal("}").suppress()
# equal
equal = Literal("=")
# plus
plus = Literal("+")
# minus
minus = Literal("-")
# plus or minus
plus_or_minus = plus | minus
# negative or positive
negative_or_positive = plus | minus
# multiplication or division
mul_or_div = Literal("*") | Literal("/")
# comparision operators
comp_operators = Literal("<") | Literal(">") | Literal("!=")
