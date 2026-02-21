import typing
import argparse
import dataclasses
import struct
import functools
import string
import itertools

def make_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--serial", nargs="?", type=str, required=True)
    parser.add_argument("--baudrate", nargs="?", type=int, default=115200)
    parser.add_argument("--period", nargs="?", type=int, default=200)
    return parser

SYNCWORD_VALUE = 0xAAAA
SYNCWORD_STRUCT = struct.Struct("<H")
SYNCWORD_BYTES = SYNCWORD_STRUCT.pack(SYNCWORD_VALUE)

COMMON_PART_STRUCT = struct.Struct("<HLHL3h3h")


def field_(fmt: str, **kwargs: typing.Any):
    return dataclasses.field(metadata={"fmt": fmt}, **kwargs)

STRUCT_MASKS = {
    "H": 0xFFFF,
    "L": 0xFFFF_FFFF,
    "h": 0xFFFF,
}

@dataclasses.dataclass
class CommonPart:
    team_id: int = field_("H", default=0)
    """ 2-3, Идентификатор команды """
    time: int = field_("L", default=0)
    """ 4-7, Время """
    temperature: int = field_("H", default=0)
    """ 8-9, Температура """
    pressure: int = field_("L", default=0)
    """ 10-13, Давление """
    acceleration: typing.Tuple[int, int, int] = field_("3H", default=(0,0,0))
    """ 14-19 (2+2+2), Ускорение """
    omega: typing.Tuple[int, int, int] = field_("3H", default=(0,0,0))
    """ 14-19 (2+2+2), Угловые скорости """

    @classmethod
    def struct(cls):
        full_fmt = "<"
        for f in dataclasses.fields(cls):
            fmt = f.metadata["fmt"]
            full_fmt += fmt
        print(full_fmt)
        return struct.Struct(full_fmt)

    def pack(self, self_struct: struct.Struct | None = None) -> bytes:
        self_struct = self_struct or self.__class__.struct()
        values : typing.Tuple[typing.Any] = dataclasses.astuple(self)
        values_flat : typing.List[typing.Any] = []
        for v in values:
            if isinstance(v, tuple):
                values_flat.extend(v)
            else:
                values_flat.append(v)
        values = tuple(values_flat)
        return self_struct.pack(*values)
    
    def fill(self, value: int):
        for f in dataclasses.fields(self):
            fmt = f.metadata["fmt"]
            if fmt[0] in string.digits:
                reps_str = "".join(itertools.takewhile(lambda x: x in string.digits, fmt))
                fmt = fmt[len(reps_str):]
                mask = STRUCT_MASKS[fmt]
                reps = int(reps_str)
                value = value % (mask + 1)
                value_ = (value,) * reps
            else:
                mask = STRUCT_MASKS[fmt]
                value = value % (mask + 1)
                value_ = value

            setattr(self, f.name, value_)

def checksum(data: bytes) -> int:
    return functools.reduce(lambda x, y: x ^ y, data)
