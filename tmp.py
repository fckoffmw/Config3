import json
import argparse


class Parser:
    """
    Парсер для учебного конфигурационного языка.
    """

    def __init__(self, lines: list[str]):
        self.lines = lines  # строки входного файла
        self.buffer = {}  # словарь для хранения переменных и констант
        self.operations = {"+", "-", "*", "/"}  # поддерживаемые операции
        self.functions = {"sort"}  # поддерживаемые функции

    @staticmethod
    def _tokenize(line: str) -> list[str]:
        """Разбивает строку на токены."""
        return line.split()

    @staticmethod
    def _is_num(literal: str) -> bool:
        """Проверяет, является ли литерал числом."""
        try:
            float(literal)
            return True
        except ValueError:
            return False

    def _is_arr(self, literal: str) -> bool:
        """Проверяет, является ли литерал массивом."""
        return (
            literal.startswith("array( ")
            and literal.endswith(" )")
            and all(
                self._is_num(token.strip(","))
                for token in literal[6:-2].split()
                if token.strip(",")
            )
        )

    def _evaluate_postfix(self, expression: str) -> float | list:
        """
        Выполняет вычисление выражения в постфиксной записи.
        Пример: ${имя 1 +}.
        """
        stack = []
        tokens = expression.split()

        for token in tokens:
            if self._is_num(token):
                stack.append(float(token))
            elif token in self.buffer:
                stack.append(self.buffer[token])
            elif token in self.operations:
                b = stack.pop()
                a = stack.pop()
                result = {
                    "+": a + b,
                    "-": a - b,
                    "*": a * b,
                    "/": a / b,
                }[token]
                stack.append(result)
            elif token in self.functions:
                if token == "sort" and isinstance(stack[-1], list):
                    stack[-1].sort()
                else:
                    raise SyntaxError(f"Некорректное использование функции: {token}")
            else:
                raise SyntaxError(f"Некорректный токен в выражении: {token}")

        if len(stack) != 1:
            raise SyntaxError(f"Ошибка в постфиксном выражении: {expression}")
        return stack[0]

    def _literal_is_valid(self, literal: str) -> bool:
        """Проверяет корректность записи литерала."""
        if (
            self._is_num(literal)
            or literal.startswith("'") and literal.endswith("'")
            or self._is_arr(literal)
        ):
            return True
        if literal.startswith("${") and literal.endswith("}"):
            return True
        return False

    def _line_is_valid(self, tokens: list[str]) -> bool:
        """Проверяет корректность строки."""
        if len(tokens) == 0:
            return True
        match tokens[0]:
            case "::" | "/+" | "+/":
                return True
            case "let":
                if (
                    len(tokens) >= 4
                    and tokens[2] == "="
                    and tokens[1].isalpha()
                    and self._literal_is_valid(" ".join(tokens[3:]))
                ):
                    return True
        return False

    def _set_value(self, var_name: str, val: str):
        """Устанавливает значение переменной в буфер."""
        if val.startswith("${") and val.endswith("}"):
            expression = val[2:-1]
            typed_val = self._evaluate_postfix(expression)
        elif self._is_num(val):
            typed_val = float(val)
        elif val.startswith("'") and val.endswith("'"):
            typed_val = val[1:-1]
        elif self._is_arr(val):
            typed_val = [float(x.strip(",")) for x in val[6:-2].split()]
        else:
            raise SyntaxError(f"Некорректное значение: {val}")
        self.buffer[var_name] = typed_val

    def _parse(self) -> bool:
        """Парсит строки и записывает данные в буфер."""
        in_comment = False
        for i, line in enumerate(self.lines, 1):
            tokens = self._tokenize(line)
            if len(tokens) == 0:
                continue
            match tokens[0]:
                case "/+":
                    in_comment = True
                    continue
                case "+/":
                    in_comment = False
                    continue
                case "::":
                    continue
            if in_comment:
                continue
            if self._line_is_valid(tokens):
                if tokens[0] == "let":
                    var_name, val = tokens[1], " ".join(tokens[3:])
                    self._set_value(var_name, val)
            else:
                raise SyntaxError(f"Ошибка в строке {i}: {line}")
        if in_comment:
            raise SyntaxError("Открытый многострочный комментарий")

    def get_data(self) -> dict:
        """Возвращает результат анализа."""
        self._parse()
        return self.buffer


def read_file(path: str) -> list[str]:
    """Читает файл и возвращает его строки."""
    if not path.endswith(".kate"):
        raise FileNotFoundError("Файл должен иметь расширение .kate")
    with open(path, "r") as f:
        return f.readlines()


def write_to_json(data: dict, output_path: str):
    """Записывает данные в файл JSON."""
    with open(output_path, "w") as f:
        json.dump(data, f, indent=4)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=str, required=True, help="Путь к .kate файлу")
    parser.add_argument(
        "--output", type=str, required=True, help="Путь для вывода JSON результата"
    )
    args = parser.parse_args()

    lines = read_file(args.file)
    p = Parser(lines)
    data = p.get_data()
    write_to_json(data, args.output)


if __name__ == "__main__":
    main()