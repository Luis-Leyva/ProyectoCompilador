from pyparsing import Keyword

""" Keywords """
# float
float_ = Keyword("float")
# int
int_ = Keyword("int")
# type
type_ = (float_ | int_)("type")
# program
program = Keyword("program")("program")
# var
var = Keyword("var")
# if
if_ = Keyword("if")("if")
# else
else_ = Keyword("else")("else")
# while
do_while_ = Keyword("while")("do_while")

""" While Regular """
# while
while_ = Keyword("while")("while")

# do
do_ = Keyword("do")("do")
# end
end = Keyword("end")("end")
# print
cout = Keyword("cout")("cout")
