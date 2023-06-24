from prettytable import PrettyTable
from queue import LifoQueue, Queue
import json
import Constants.keywords as kw
import Constants.literals as lt
import Constants.tokens as tk
import vm.maquina_virtual as mv
from Constants import cubo_semantico
from pyparsing import (
    Group,
    Optional,
    delimited_list,
    Forward,
    ParseException,
    ZeroOrMore,
)


""" Tablas """
# Tabla de varibles
tabla_variables = {}
# Cubo semantico
cubo_s = cubo_semantico.cubo_semantico

""" Pilas """
# Pila de operandos
pila_operandos = LifoQueue()
# Pila de operadores
pila_operadores = LifoQueue()
# Pila de tipos
pila_tipos = LifoQueue()
# Pila de saltos
pila_saltos = LifoQueue()

""" FILA """
# Fila de cuadruplos
fila_cuadruplos = Queue()

fila_temporales = Queue()
for i in range(0, 100):
    fila_temporales.put("temp" + str(i))

fila_bool = Queue()
fila_bool.put(False)

""" Cuadruplos """


# Generador de cuadruplos
def generar_cuadruplo(operador, operando_izq, operando_der, resultado):
    fila_cuadruplos.put([operador, operando_izq, operando_der, resultado])


""" Puntos Neuralgicos Generales """


def put_operators(token):
    pila_operadores.put(token[0])


def exp_precedence():
    right_op = pila_operandos.get()
    right_type = pila_tipos.get()
    operator = pila_operadores.get()
    left_op = pila_operandos.get()
    left_type = pila_tipos.get()

    try:
        result_type = cubo_s[left_type][right_type][operator]
        if result_type == "error":
            raise ValueError(
                "Error: tipo "
                + left_type
                + " no puede ser operado con tipo"
                + right_type
            )
    except ValueError as error:
        print(error)
        exit()

    temp = fila_temporales.get()
    generar_cuadruplo(operator, left_op, right_op, temp)
    pila_operandos.put(temp)
    pila_tipos.put(result_type)
    tabla_variables[temp] = result_type
    if type(left_op) == str:
        if left_op[0:4] == "temp":
            fila_temporales.put(left_op)
    if type(right_op) == str:
        if right_op[0:4] == "temp":
            fila_temporales.put(right_op)


def check_precedence(token):
    if pila_operadores.queue.__len__() > 0:
        top_operadores = pila_operadores.queue[-1]
        if top_operadores == "negative" or top_operadores == "positive":
            right_op = pila_operandos.get()
            operator = pila_operadores.get()
            temp = fila_temporales.get()
            if operator == "negative":
                generar_cuadruplo("*", right_op, -1, temp)
                tabla_variables[temp] = pila_tipos.queue[-1]
            pila_operandos.put(temp)
        elif top_operadores == "+" or top_operadores == "-":
            exp_precedence()
        elif top_operadores == "*" or top_operadores == "/":
            exp_precedence()
        elif (
            top_operadores == "<"
            or top_operadores == ">"
            or top_operadores == "!="
        ):
            if fila_bool.get():
                exp_precedence()
                fila_bool.put(False)
            else:
                fila_bool.put(True)


""" Grammar y Puntos Neuralgicos """
# Forwards for recursive definitions
vars_ = Forward()
body = Forward()
expresion = Forward()
statement = Forward()
assign = Forward()
condition = Forward()
cycle = Forward()
cycle_w = Forward()
print_ = Forward()
exp = Forward()
termino = Forward()
factor = Forward()


""" PROGRAMA """
programa = kw.program + tk.id_ + lt.semicolon + Optional(vars_) + body + kw.end

""" VARS """


# Creacion de tabla de variables
def agregar_variables(var_list):
    len_list = len(var_list)

    for i in range(0, len_list):
        len_list_i = len(var_list[i])
        var_type = var_list[i][len_list_i - 1]

        for j in range(0, len_list_i - 1):
            var_id = var_list[i][j]

            # Si la variable ya esta declarada
            try:
                if tabla_variables.keys().__contains__(var_id):
                    raise ValueError(
                        "Error: La variable '{}' ya esta declarada".format(
                            var_list[i][j]
                        )
                    )
                    exit()
                else:
                    tabla_variables[var_id] = var_type
            except ValueError as error:
                print(error)
                exit()


vars_ <<= (
    kw.var
    + Group(
        delimited_list(
            Group(delimited_list(tk.id_) + lt.colon + kw.type_),
            delim=lt.semicolon,
        ).setParseAction(agregar_variables)
    )
    + lt.semicolon
)

""" Body """
body <<= (
    lt.left_brace
    + delimited_list(statement, delim=lt.semicolon)
    + lt.semicolon
    + lt.right_brace
)


""" Print """


def cuadruplo_print(token):
    # Creamos cuadruplo de print con multiples operandos
    if pila_operadores.queue[-1] == "cout":
        if len(token) == 1:
            pila_tipos.get()
            generar_cuadruplo(
                pila_operadores.get(), None, None, pila_operandos.get()
            )
        else:
            for i in range(len(token) - 1):
                pila_operadores.put("concat")

            # Realizamos una suma de strings
            for i in range(len(token) - 1):
                pila_tipos.get()
                right_op = str(pila_operandos.get())
                pila_tipos.get()
                left_op = str(pila_operandos.get())
                operator = pila_operadores.get()
                result = fila_temporales.get()
                generar_cuadruplo(operator, left_op, right_op, result)
                if left_op[0:4] != "temp" and right_op[0:4] == "temp":
                    fila_temporales.put(right_op)
                pila_operandos.put(result)
                pila_tipos.put("string")
                tabla_variables[result] = "string"

            result = pila_operandos.get()
            generar_cuadruplo(pila_operadores.get(), None, None, result)
            fila_temporales.put(result)
            pila_tipos.get()


def put_string(token):
    pila_operandos.put(token[0])
    pila_tipos.put("string")
    tabla_variables[token[0]] = "string"


print_ <<= Group(
    kw.cout.set_parse_action(put_operators)
    + lt.left_parenthesis.suppress()
    + delimited_list(
        tk.cte_string.set_parse_action(put_string) | Group(expresion),
        delim=lt.comma,
    ).set_parse_action(cuadruplo_print)
    + lt.right_parenthesis.suppress()
)


""" ASSIGN """


def id_equal(token):
    # Checar que la variable exista
    try:
        if not tabla_variables.keys().__contains__(token[0]):
            raise ValueError(
                "Error: La variable '{}' no esta declarada".format(token[0])
            )
    except ValueError as error:
        print(error)
        exit()

    # Utilizamos las correspondientes
    pila_operandos.put(token[0])
    pila_tipos.put(tabla_variables[token[0]])
    pila_operadores.put("=")


def cuadruplo_assign(token):
    # Verificamos que el tipo de resultado sea = al tipo de la variable
    tipo_resultado = pila_tipos.get()
    try:
        # Utilizamos el cubo semantico
        if tipo_resultado != pila_tipos.get():
            raise ValueError(
                "Error: tipo "
                + tipo_resultado
                + " no puede ser asignado a tipo "
                + tabla_variables[token[0]]
            )
    except ValueError as error:
        print(error)
        exit()

    # Generamos el cuadruplo de asignacion
    temp = pila_operandos.get()
    tabla_variables[temp] = tipo_resultado
    generar_cuadruplo(pila_operadores.get(), temp, None, pila_operandos.get())

    # Regreamos el temporal a su fila si es que es temporal
    if type(temp) == str:
        if temp[0:4] == "temp":
            fila_temporales.put(temp)


assign <<= Group(
    (tk.id_ + lt.equal).set_parse_action(id_equal) + Group(expresion)
)

""" STATEMENT """
statement <<= (
    assign.set_parse_action(cuadruplo_assign)
    | condition
    | print_
    | cycle
    | cycle_w
)


""" DO WHILE """


def put_do_jump():
    pila_saltos.put(len(fila_cuadruplos.queue))


def do_while_cuadruplo():
    tipo_esp = pila_tipos.get()
    try:
        if tipo_esp != "bool":
            raise ValueError("Error: La expresion no es booleana")
        else:
            result = pila_operandos.get()
            generar_cuadruplo("GOTOV", result, None, pila_saltos.get() + 1)
    except ValueError as err:
        print(err)
        exit()


cycle <<= Group(
    kw.do_.set_parse_action(put_do_jump)
    + body
    + kw.do_while_
    + lt.left_parenthesis.suppress()
    + Group(expresion)
    + lt.right_parenthesis.suppress()
).set_parse_action(do_while_cuadruplo)


""" WHILE """


def while_jumps():
    pila_saltos.put(len(fila_cuadruplos.queue))


def while_cuadruplo():
    tipo_esp = pila_tipos.get()
    try:
        if tipo_esp != "bool":
            raise ValueError("Error: La expresion no es booleana")
        else:
            result = pila_operandos.get()
            generar_cuadruplo(
                "GOTOF",
                result,
                None,
                None,
            )
            pila_saltos.put(len(fila_cuadruplos.queue) - 1)
    except ValueError as err:
        print(err)
        exit()


def while_end():
    end = pila_saltos.get()
    generar_cuadruplo("GOTO", None, None, end)

    fila_cuadruplos.queue[end][3] = len(fila_cuadruplos.queue) + 1


cycle_w <<= Group(
    (
        kw.while_.set_parse_action(while_jumps)
        + lt.left_parenthesis.suppress()
        + Group(expresion)
        + lt.right_parenthesis.suppress()
    ).set_parse_action(while_cuadruplo)
    + body
).set_parse_action(while_end)

""" IF ELESE """


def if_jumps():
    tipo_esp = pila_tipos.get()
    try:
        if tipo_esp != "bool":
            raise ValueError("Error: La expresion no es booleana")
        else:
            result = pila_operandos.get()
            generar_cuadruplo("GOTOF", result, None, None)
            pila_saltos.put(len(fila_cuadruplos.queue) - 1)
    except ValueError as error:
        print(error)
        exit()


def if_end():
    end = pila_saltos.get()
    fila_cuadruplos.queue[end][3] = len(fila_cuadruplos.queue) + 1


def else_jumps():
    generar_cuadruplo("GOTO", None, None, None)
    end = pila_saltos.get()
    pila_saltos.put(len(fila_cuadruplos.queue) - 1)
    fila_cuadruplos.queue[end][3] = len(fila_cuadruplos.queue) + 1


condition <<= Group(
    kw.if_
    + lt.left_parenthesis.suppress()
    + Group(expresion)
    + Group(lt.right_parenthesis.suppress()).set_parse_action(if_jumps)
    + body
    + Optional(kw.else_.set_parse_action(else_jumps) + body)
).set_parse_action(if_end)

# expresion
expresion <<= exp + Optional(
    lt.comp_operators.set_parse_action(put_operators) + exp
).set_parse_action(check_precedence)
# exp
exp <<= (
    termino
    + ZeroOrMore(lt.plus_or_minus.set_parse_action(put_operators) + termino)
).set_parse_action(check_precedence)

# termino
termino <<= (
    factor + ZeroOrMore(lt.mul_or_div.set_parse_action(put_operators) + factor)
).set_parse_action(check_precedence)

"""	FACTOR """


def put_parenthesis(token):
    if token[0][0] == "(":
        pila_operadores.put("(")
    elif token[0][0] == ")":
        pila_operadores.get()


def negative_positive(token):
    if token[0] == "-":
        pila_operadores.put("negative")
    elif token[0] == "+":
        pila_operadores.put("positive")


def id_constant(token):
    if token[0] == tk.id_:
        try:
            if not tabla_variables.keys().__contains__(token[0]):
                raise ValueError(
                    "Error: La variable " + token[0] + " no esta declarada"
                )
        except ValueError as error:
            print(error)
            exit()
        pila_operandos.put(token[0])
        pila_tipos.put(tabla_variables[token[0]])
    else:
        if token[0] == tk.cte_int:
            pila_tipos.put("int")
            pila_operandos.put(int(token[0]))
        elif token[0] == tk.cte_float:
            pila_tipos.put("float")
            pila_operandos.put(float(token[0]))


factor <<= Group(lt.left_parenthesis).set_parse_action(
    put_parenthesis
) + expresion + Group(lt.right_parenthesis).set_parse_action(
    put_parenthesis
) | Optional(
    lt.negative_or_positive.set_parse_action(negative_positive)
) + (
    tk.id_ | tk.cte
).set_parse_action(
    id_constant
)


""" Archivos de prueba: """
fibonacci = "test_cases/fibonacci.txt"
factorial = "test_cases/factorial.txt"
test1 = "test_cases/test1.txt"
n_while = "test_cases/while.txt"

try:
    scan_result = programa.parse_file(fibonacci, parseAll=True)
except ParseException as e:
    print(e)
    exit()


""" Imprimir el resultado del parseo """
with open("tablas_y_filas/parse_result.txt", "w") as f:
    f.write("Resultado del parseo\n")
    for line in scan_result:
        f.write(str(line) + "\n")


""" Imprimir la tabla de variables """
tabla_variables = json.dumps(tabla_variables, indent=4)
with open("tablas_y_filas/tabla_variables.txt", "w") as f:
    f.write("Tabla de variables\n")
    for line in tabla_variables.split("\n"):
        f.write(line + "\n")


""" Imprimir la fila de cuadruplos """
table = PrettyTable()
table.title = "Fila de cuadruplos"
table.field_names = [
    "No.",
    "Operando 1",
    "Operando 2",
    "Operador",
    "Resultado",
    "",
]
for i, cuadruplo in enumerate(fila_cuadruplos.queue):
    table.add_row(
        [i + 1, cuadruplo[0], cuadruplo[1], cuadruplo[2], cuadruplo[3], ""]
    )

with open("tablas_y_filas/fila_cuadruplos.txt", "w") as f:
    f.write("Fila de cuadruplos\n")
    f.write(str(table))


""" Ejecutar la fila de cuadruplos """
mv.execute_quad(fila_cuadruplos.queue)


""" Imprimir la tabla de memoria """
table = PrettyTable()
table.title = "Tabla de memoria"
table.field_names = ["Direccion", "Valor"]
for key, value in mv.get_mapa_memoria().items():
    table.add_row([key, value])

with open("tablas_y_filas/tabla_memoria.txt", "w") as f:
    f.write("Tabla de memoria\n")
    f.write(str(table))
