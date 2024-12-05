import unittest
import json
import os

from tmp import Parser, read_file, write_to_json 


class TestParser(unittest.TestCase):

    def setUp(self):
        # Создаем временные файлы для тестирования
        self.valid_kate_file = 'test_valid.kate'
        self.invalid_kate_file = 'test_invalid.kate'
        self.output_json_file = 'output.json'

        # Записываем корректные данные в файл
        with open(self.valid_kate_file, 'w') as f:
            f.write("let a = 1\n")
            f.write("let b = 'hello'\n")
            f.write("let c = array( 1, 2, 3 )\n")
            f.write("/+\n")
            f.write("This is a comment\n")
            f.write("+/\n")

        # Записываем некорректные данные в файл
        with open(self.invalid_kate_file, 'w') as f:
            f.write("let a = 1\n")
            f.write("let b = 'hello'\n")
            f.write("let c = array( 1, 2, 3 )\n")
            f.write("let d = a +\n")  # Ошибка в этой строке

    def tearDown(self):
        # Удаляем временные файлы после тестов
        for file in [self.valid_kate_file, self.invalid_kate_file, self.output_json_file]:
            if os.path.exists(file):
                os.remove(file)

    def test_valid_parsing(self):
        # Тестируем корректный парсинг
        lines = read_file(self.valid_kate_file)
        parser = Parser(lines)
        data = parser.get_data()

        expected_data = {
            'a': 1.0,
            'b': 'hello',
            'c': [1.0, 2.0, 3.0],
        }

        self.assertEqual(data, expected_data)

    def test_invalid_parsing(self):
        # Тестируем некорректный парсинг
        lines = read_file(self.invalid_kate_file)
        parser = Parser(lines)

        with self.assertRaises(SyntaxError):
            parser.get_data()

    def test_write_to_json(self):
        # Тестируем запись в JSON
        lines = read_file(self.valid_kate_file)
        parser = Parser(lines)
        data = parser.get_data()

        write_to_json(data, self.output_json_file)

        with open(self.output_json_file, 'r') as f:
            output_data = json.load(f)

        expected_data = {
            'a': 1.0,
            'b': 'hello',
            'c': [1.0, 2.0, 3.0],
        }

        self.assertEqual(output_data, expected_data)

if __name__ == '__main__':
    unittest.main()