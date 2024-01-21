from inspect import Signature, Parameter
from typing import Callable, List, Any, Union

from sigmatch.errors import SignatureMismatchError


class SignatureMatcher:
    """
    An object of this class contains a "cast" of the expected signature of the called object.
    It can then be applied to the actual called object (by the .match() method) to see if their signatures match the expected one.
    """

    def __init__(self, *args: str) -> None:
        """
        Initializing an object is creating a "cast" of the expected function signature.

        4 types of objects are accepted as arguments (they are all strings):

        1. '.' - corresponds to an ordinary positional argument without a default value.
        2. 'some_argument_name' - corresponds to an argument with a default value. The content of the string is the name of the argument.
        3. '*' - corresponds to packing multiple positional arguments without default values (*args).
        4. '**' - corresponds to packing several named arguments with default values (**kwargs).

        For example, for a function titled like this:

        def func(a, b, c=5, *d, **e):
            ...

        ... such a "cast" will match:

        SignatureMatcher('.', '.', 'c', '*', '**')
        """
        self.expected_signature = args
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
            if raise_exception:
                raise ValueError('It is impossible to determine the signature of an object that is not being callable.')
            return False

        signature = Signature.from_callable(function)
        parameters = list(signature.parameters.values())

        result: Union[bool, int] = True
        result *= self.prove_is_args(parameters)
        result *= self.prove_is_kwargs(parameters)
        result *= self.prove_number_of_position_args(parameters)
        result *= self.prove_number_of_named_args(parameters)
        result *= self.prove_names_of_named_args(parameters)
        result = bool(result)

        if not result and raise_exception:
            raise SignatureMismatchError('The signature of the callable object does not match the expected one.')
        return result

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
