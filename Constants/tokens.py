from pyparsing import Word, Regex, alphanums, alphas

""" Tokens """
# id
id_ = Word(alphas, alphanums + "_")
# cte.string
cte_string = Regex(r"\".*\"")
# cte_int
cte_int = Regex(r"\d+")
# cte_float
cte_float = Regex(r"\d+\.\d+([eE][-+]?\d+)?")
# cte
cte = cte_float | cte_int
