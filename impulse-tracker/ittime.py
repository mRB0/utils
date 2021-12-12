# nb. seconds are integer divided by 2 to fit the structure

def unpack_impulse_tracker_time(packed_time):
    '''
    packed_time: 16-bit unsigned int containing a packed time
                 structured like: hhhhhmmm mmmsssss

    Return: A tuple of (hour, minute, second) representing the time

    NB. The packed time stores seconds at 2-second resolution using
    integer division, so eg. hh:mm:32 and hh:mm:33 are both represented
    as hh:mm:32
    '''
    hour = (packed_time >> 11) & 0x1f
    minute = (packed_time >> 5) & 0x3f
    second = (packed_time & 0x1f) * 2

    return (hour, minute, second)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('time_hex', help='impulse tracker time value (hex, little-endian, like 55ba)')

    args = parser.parse_args()

    timevalue_hex = args.time_hex.replace(' ', '')

    timevalue_int_wrong_endianness = int(timevalue_hex, 16)

    timevalue = int.from_bytes(timevalue_int_wrong_endianness.to_bytes(2, byteorder='big'), byteorder='little', signed=False)

    h, m, s = unpack_impulse_tracker_time(timevalue)

    print(f'{h:d}:{m:02d}:{s:02d}')
