from inspect import Signature, Parameter
from typing import Callable, Tuple, List, Any, Union

from sigmatch.errors import SignatureMismatchError, IncorrectArgumentsOrderError


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
        self.check_expected_signature(args)
        self.expected_signature = args
        self.is_args = '*' in args
        self.is_kwargs = '**' in args
        self.number_of_position_args = len([x for x in args if x == '.'])
        self.number_of_named_args = len([x for x in args if x.isidentifier()])
        self.names_of_named_args = list(set([x for x in args if x.isidentifier()]))

    def match(self, function: Callable[..., Any], raise_exception: bool = False) -> bool:
        """We check that the signature of the function passed as an argument corresponds to the "cast" obtained during initialization of the SignatureMatcher object."""
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

    def check_expected_signature(self, expected_signature: Tuple[str, ...]) -> None:
        met_name = False
        met_star = False
        met_double_star = False
        all_met_names = set()

        for item in expected_signature:
            if not isinstance(item, str):
                raise TypeError(f'Only strings can be used as symbolic representation of function parameters. You used "{item}" ({type(item).__name__}).')
            if not item.isidentifier() and item not in ('.', '*', '**'):
                raise ValueError(f'Only strings of a certain format can be used as symbols for function arguments: arbitrary variable names, and ".", "*", "**" strings. You used "{item}".')

            if item == '.':
                if met_name or met_star or met_double_star:
                    raise IncorrectArgumentsOrderError('Positional arguments must be specified first.')

            elif item.isidentifier():
                met_name = True
                if met_star or met_double_star:
                    raise IncorrectArgumentsOrderError('Keyword arguments can be specified after positional ones, but before unpacking.')
                if item in all_met_names:
                    raise IncorrectArgumentsOrderError(f'The same argument name cannot occur twice. You have a repeat of "{item}".')
                all_met_names.add(item)

            elif item == '*':
                if met_star:
                    raise IncorrectArgumentsOrderError('Unpacking of the same type (*args in this case) can be specified no more than once.')
                met_star = True
                if met_double_star:
                    raise IncorrectArgumentsOrderError('Unpacking positional arguments should go before unpacking keyword arguments.')

            elif item == '**':
                if met_double_star:
                    raise IncorrectArgumentsOrderError('Unpacking of the same type (**kwargs in this case) can be specified no more than once.')
                met_double_star = True

    def prove_is_args(self, parameters: List[Parameter]) -> bool:
        """Checking for unpacking of positional arguments."""
        return self.is_args == bool(len([parameter for parameter in parameters if parameter.kind == parameter.VAR_POSITIONAL]))

    def prove_is_kwargs(self, parameters: List[Parameter]) -> bool:
        """Checking for unpacking of named arguments."""
        return self.is_kwargs == bool(len([parameter for parameter in parameters if parameter.kind == parameter.VAR_KEYWORD]))

    def prove_number_of_position_args(self, parameters: List[Parameter]) -> bool:
        """Checking that the number of positional arguments matches the expected one."""
        return self.number_of_position_args == len([parameter for parameter in parameters if (parameter.kind == parameter.POSITIONAL_ONLY or parameter.kind == parameter.POSITIONAL_OR_KEYWORD) and parameter.default == parameter.empty])

    def prove_number_of_named_args(self, parameters: List[Parameter]) -> bool:
        """Checking the number of named arguments."""
        return self.number_of_named_args == len([parameter for parameter in parameters if (parameter.kind == parameter.KEYWORD_ONLY or parameter.kind == parameter.POSITIONAL_OR_KEYWORD) and parameter.default != parameter.empty])

    def prove_names_of_named_args(self, parameters: List[Parameter]) -> bool:
        """Checking that the names of the named arguments match the expected ones."""
        names_of_parameters = [parameter.name for parameter in parameters if (parameter.kind == parameter.KEYWORD_ONLY or parameter.kind == parameter.POSITIONAL_OR_KEYWORD) and parameter.default != parameter.empty]

        result: Union[bool, int] = True
        for name in self.names_of_named_args:
            result *= (name in names_of_parameters)

        return bool(result)
