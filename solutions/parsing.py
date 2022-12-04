from argparse import ArgumentParser
from typing import Callable, Generic, Iterable, TypeVar

from pydantic import BaseModel


class ArgsModel(BaseModel):
    class Meta:
        flags: dict[str, tuple[str, str] | tuple[str] | str]


M_ = TypeVar("M_", bound=ArgsModel)


class Parser(Generic[M_]):
    arg_parser: ArgumentParser
    model: type[M_]

    def __init__(self, model: type[M_], arg_parser: ArgumentParser):
        self.model = model
        self.arg_parser = arg_parser

    def parse(self, args: list[str]) -> M_:
        namespace = self.arg_parser.parse_args(args)
        return self.model(**namespace.__dict__)


def build_parser(model: type[M_]) -> Parser[M_]:
    arg_parser = ArgumentParser()
    for field_name, field in model.__fields__.items():
        flags = model.Meta.flags.get(field_name)
        argnames: Iterable[str]
        if flags is not None:
            if isinstance(flags, str):
                argnames = (f"--{flags}",)
            else:
                if len(flags) == 2:
                    argnames = map("".join, zip(("-", "--"), flags))
                else:
                    argnames = (f"--{flags[0]}",)
        else:
            argnames = (field_name,)
        arg_parser.add_argument(*argnames, type=field.type_, default=field.default)

    parser = Parser(model=model, arg_parser=arg_parser)

    return parser
