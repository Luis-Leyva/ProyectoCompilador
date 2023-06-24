import Constants.tokens as tk

MAPA_MEMORIA = {}


def get_mapa_memoria():
    return MAPA_MEMORIA


def check_variable(var):
    try:
        if not MAPA_MEMORIA.keys().__contains__(hash(var)):
            if var == tk.id_:
                raise Exception(
                    "La variable "
                    + var
                    + " no ha sido declarada o no contiene un valor asignado"
                )
            else:
                MAPA_MEMORIA[hash(var)] = var
    except Exception as e:
        print(e)
        exit()


def delete_temp_memoria(var1, var2):
    if var1 == "temp":
        del MAPA_MEMORIA[hash(var1)]
    if var2 == "temp":
        del MAPA_MEMORIA[hash(var2)]


def execute_quad(quadruples):
    open("resultado_ejecucion/resultados.txt", "w")
    length = len(quadruples)
    i = 0
    while i < length:
        line = quadruples[i]
        match line[0]:
            case "+":
                check_variable(line[1])
                check_variable(line[2])

                MAPA_MEMORIA[hash(line[3])] = (
                    MAPA_MEMORIA[hash(line[1])] + MAPA_MEMORIA[hash(line[2])]
                )
                delete_temp_memoria(line[1], line[2])

            case "-":
                check_variable(line[1])
                check_variable(line[2])

                MAPA_MEMORIA[hash(line[3])] = (
                    MAPA_MEMORIA[hash(line[1])] - MAPA_MEMORIA[hash(line[2])]
                )

                delete_temp_memoria(line[1], line[2])
            case "*":
                check_variable(line[1])
                check_variable(line[2])

                MAPA_MEMORIA[hash(line[3])] = (
                    MAPA_MEMORIA[hash(line[1])] * MAPA_MEMORIA[hash(line[2])]
                )

                delete_temp_memoria(line[1], line[2])

            case "/":
                check_variable(line[1])
                check_variable(line[2])

                MAPA_MEMORIA[hash(line[3])] = (
                    MAPA_MEMORIA[hash(line[1])] / MAPA_MEMORIA[hash(line[2])]
                )

                delete_temp_memoria(line[1], line[2])

            case "=":
                if not MAPA_MEMORIA.keys().__contains__(hash(line[1])):
                    MAPA_MEMORIA[hash(line[1])] = line[1]

                MAPA_MEMORIA[hash(line[3])] = MAPA_MEMORIA[hash(line[1])]
                if type(line[1]) == str:
                    if line[1][0:4] == "temp":
                        del MAPA_MEMORIA[hash(line[1])]

            case "cout":
                check_variable(line[3])

                # Escribimos los resultados en un archivo
                with open("resultado_ejecucion/resultados.txt", "a") as file:
                    file.write(str(MAPA_MEMORIA[hash(line[3])]) + "\n")

                if type(line[3]) == str:
                    if line[3][0:4] == "temp":
                        del MAPA_MEMORIA[hash(line[3])]

            case "concat":
                check_variable(line[1])
                check_variable(line[2])

                left = MAPA_MEMORIA[hash(line[1])]
                if type(left) != str:
                    left = str(MAPA_MEMORIA[hash(line[1])])
                else:
                    left = left.lstrip('"').rstrip('"')

                right = MAPA_MEMORIA[hash(line[2])]
                if type(right) != str:
                    right = str(MAPA_MEMORIA[hash(line[2])])
                else:
                    right = right.lstrip('"').rstrip('"')

                MAPA_MEMORIA[hash(line[3])] = left + " " + right

                delete_temp_memoria(line[1], line[2])

            case "!=":
                check_variable(line[1])
                check_variable(line[2])

                MAPA_MEMORIA[hash(line[3])] = (
                    MAPA_MEMORIA[hash(line[1])] != MAPA_MEMORIA[hash(line[2])]
                )

                delete_temp_memoria(line[1], line[2])

            case ">":
                check_variable(line[1])
                check_variable(line[2])

                MAPA_MEMORIA[hash(line[3])] = (
                    MAPA_MEMORIA[hash(line[1])] > MAPA_MEMORIA[hash(line[2])]
                )

                delete_temp_memoria(line[1], line[2])

            case "<":
                check_variable(line[1])
                check_variable(line[2])

                MAPA_MEMORIA[hash(line[3])] = (
                    MAPA_MEMORIA[hash(line[1])] < MAPA_MEMORIA[hash(line[2])]
                )

                delete_temp_memoria(line[1], line[2])

            case "GOTO":
                i = line[3] - 2

                if type(line[3]) == str:
                    if line[3][0:4] == "temp":
                        del MAPA_MEMORIA[hash(line[3])]
                        del [line[3]]

            case "GOTOF":
                if not MAPA_MEMORIA[hash(line[1])]:
                    i = line[3] - 2

                    if type(line[3]) == str:
                        if line[3][0:4] == "temp":
                            del MAPA_MEMORIA[hash(line[3])]
                            del [line[3]]

            case "GOTOV":
                if MAPA_MEMORIA[hash(line[1])]:
                    i = line[3] - 2
                    if type(line[3]) == str:
                        if line[3][0:4] == "temp":
                            del MAPA_MEMORIA[hash(line[3])]
                            del [line[3]]
        i += 1
