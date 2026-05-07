import struct
import typing
import serial
import time
import dataclasses

from common import make_argparser, checksum, field
from common import Serializable, CommonPart
from common import SYNCWORD_BYTES


@dataclasses.dataclass
class BankaPart(Serializable):
    packet_number: int = field("H", default=0)
    """ 2-3, Идентификатор команды """
    lat: float = field("L", default=0)
    """ 4-7, Время """


BANKA_STRUCT = struct.Struct(
    "<H"   # Номер апкета
    "fffB" # широта, долгота, высота, fix
    "H"    # t ds18b20
    "hhh"  # Магнитометр x y z
    "H"    # Фоторезистор
    "B"    # Состояние
)


def main(argv: typing.List[str]) -> int:
    parser = make_argparser()
    args = parser.parse_args(argv)
    #port = serial.Serial(args.serial, baudrate=args.baudrate)
    period = args.period / 1000
    i = 0
    part_struct = CommonPart.struct()
    while True:
        try:
            part = CommonPart()
            part.team_id = 0xBBBB
            packet = SYNCWORD_BYTES + part.pack(part_struct)
            check = checksum(packet)                
            data = packet + bytes([check])
            print(part, "\n", data)
            #port.write(data)
            time.sleep(period)
            i += 1
        except KeyboardInterrupt:
            print("Shutting down...")
            break

    return 0

if __name__ == "__main__":
    import sys
    argv = sys.argv[1:]
    exit(main(argv))