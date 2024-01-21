from inspect import Signature, Parameter
from typing import Callable, List, Any, Union


class SignatureMatcher:
    """
    Объект данного класса содержит в себе "слепок" ожидаемой сигнатуры вызываемого объекта.
    Его затем можно "прикладывать" к реальным вызываемым объектам (см. метод .match()), чтобы понять, соответствуют ли их сигнатуры ожидаемой.
    """

    def __init__(self, *args: str) -> None:
        """
        Инициализация объекта - это создание "слепка" ожидаемой сигнатуры функций.

        В качестве аргументов принимаются 4 типа объектов (они все являются строками):
        1. '.' - соответствует обыкновенному позиционному аргументу без дефолтного значения.
        2. 'some_argument_name' - соответствует аргументу с дефолтным значением. Содержание строки - имя аргумента.
        3. '*' - соответствует запаковке нескольких позиционных аргументов без дефолтных значений (*args).
        4. '**' - соответствует запаковке нескольких именованных аргументов с дефолтными значениями (**kwargs).

        К примеру, функции, озаглавленной вот так:
        def func(a, b, c=5, *d, **e):
            ...

        ... будет соответствовать такой "слепок":
        SignatureMatcher('.', '.', 'c', '*', '**')
        """
        self.is_args = '*' in args
        self.is_kwargs = '**' in args
        self.number_of_position_args = len([x for x in args if x == '.'])
        self.number_of_named_args = len([x for x in args if x.isidentifier()])
        self.names_of_named_args = list(set([x for x in args if x.isidentifier()]))

    def match(self, function: Callable[..., Any], raise_exception: bool = False) -> bool:
        """
        Проверяем, что сигнатура функции, переданной в качестве аргумента, соответствует "слепку", полученному при инициализации объекта SignatureMatcher.
        """
        if not callable(function):
            raise ValueError('It is impossible to determine the signature of an object that is not being callable.')

        signature = Signature.from_callable(function)
        parameters = list(signature.parameters.values())

        result: Union[bool, int] = True
        result *= self.prove_is_args(parameters)
        result *= self.prove_is_kwargs(parameters)
        result *= self.prove_number_of_position_args(parameters)
        result *= self.prove_number_of_named_args(parameters)
        result *= self.prove_names_of_named_args(parameters)

        return bool(result)

    def prove_is_args(self, parameters: List[Parameter]) -> bool:
        """
        Проверка наличия распаковки позиционных аргументов.
        """
        return self.is_args == bool(len([parameter for parameter in parameters if parameter.kind == parameter.VAR_POSITIONAL]))

    def prove_is_kwargs(self, parameters: List[Parameter]) -> bool:
        """
        Проверка наличия распаковки именованных аргументов.
        """
        return self.is_kwargs == bool(len([parameter for parameter in parameters if parameter.kind == parameter.VAR_KEYWORD]))

    def prove_number_of_position_args(self, parameters: List[Parameter]) -> bool:
        """
        Проверка, что количество позиционных аргументов совпадает с ожидаемым.
        """
        return self.number_of_position_args == len([parameter for parameter in parameters if (parameter.kind == parameter.POSITIONAL_ONLY or parameter.kind == parameter.POSITIONAL_OR_KEYWORD) and parameter.default == parameter.empty])

    def prove_number_of_named_args(self, parameters: List[Parameter]) -> bool:
        """
        Проверка количества именованных аргументов.
        """
        return self.number_of_named_args == len([parameter for parameter in parameters if (parameter.kind == parameter.KEYWORD_ONLY or parameter.kind == parameter.POSITIONAL_OR_KEYWORD) and parameter.default != parameter.empty])

    def prove_names_of_named_args(self, parameters: List[Parameter]) -> bool:
        """
        Проверка, что имена именованных аргументов совпадают с ожидаемыми.
        """
        names_of_parameters = [parameter.name for parameter in parameters if (parameter.kind == parameter.KEYWORD_ONLY or parameter.kind == parameter.POSITIONAL_OR_KEYWORD) and parameter.default != parameter.empty]

        result: Union[bool, int] = True
        for name in self.names_of_named_args:
            result *= (name in names_of_parameters)

        return bool(result)
