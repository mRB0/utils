def unpack_impulse_tracker_date(packed_date):
    '''
    packed_date: 16-bit unsigned int containing a packed date
                 structured like: yyyyyyym mmmddddd

    Return: A tuple of (year, month, day) representing the date.
            month and day are both 1-indexed.
    '''

    # yyyyyyy is the number of years since 1980
    year = ((packed_date >> 9) & 0x7f) + 1980
    month = (packed_date >> 5) & 0xf
    day = packed_date & 0x1f

    return (year, month, day)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('date_hex', help='impulse tracker date value (hex, little-endian, like d928)')

    args = parser.parse_args()

    datevalue_hex = args.date_hex.replace(' ', '')

    datevalue_int_wrong_endianness = int(datevalue_hex, 16)

    datevalue = int.from_bytes(datevalue_int_wrong_endianness.to_bytes(2, byteorder='big'), byteorder='little', signed=False)

    y, m, d = unpack_impulse_tracker_date(datevalue)

    print(f'{y:04d}-{m:02d}-{d:02d}')
