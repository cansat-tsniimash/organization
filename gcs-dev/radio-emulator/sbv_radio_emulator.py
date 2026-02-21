import typing
import serial
import time

from common import make_argparser, checksum, CommonPart, SYNCWORD_BYTES


def main(argv: typing.List[str]) -> int:
    parser = make_argparser()
    args = parser.parse_args(argv)
    port = serial.Serial(args.serial, baudrate=args.baudrate)
    period = args.period / 1000
    i = 0
    part_struct = CommonPart.struct()
    while True:
        try:
            part = CommonPart()
            part.fill(i)
            part.team_id = 0xBBBB
            packet = SYNCWORD_BYTES + part.pack(part_struct)
            check = checksum(packet)
            data = packet + bytes([check])
            if i % 2:
                data = data[:len(data)//2]
            print(part, data)
            port.write(data)
            time.sleep(period)
            i += 1
        except KeyboardInterrupt as e:
            print("Shutting down...")
            break

    return 0

if __name__ == "__main__":
    import sys
    argv = sys.argv[1:]
    exit(main(argv))