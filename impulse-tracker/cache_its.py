import struct
from collections import namedtuple
import datetime
import shlex

from ittime import unpack_impulse_tracker_time
from itdate import unpack_impulse_tracker_date

CacheEntry = namedtuple('CacheEntry', ('filename', 'sample_name', 'type', 'size', 'datetime'))

ENTRY_TYPE_DIRECTORY = 'directory'
ENTRY_TYPE_LIBRARY = 'library'
ENTRY_TYPE_SAMPLE = 'sample'
ENTRY_TYPE_UNKNOWN = 'unknown'

DIRECTORY_SAMPLE_NAME = b'\x9a' * 8 + b'Directory' + b'\x9a' * 8
LIBRARY_SAMPLE_NAME = b'\x9a' * 9 + b'Library' + b'\x9a' * 9

def load_entries_from_cache_its(path):
    with open(path, 'rb') as cache_file:
        # probably: [ entry count (2 bytes LE) | minor version (1 byte) | major version (1 byte)] ]
        # minor/major typically 0x17 02, or 0x16 02, 0x14 02

        entry_count = struct.unpack('<H', cache_file.read(2))[0]
        cache_file.read(2) # IT version

        entries = []

        for i in range(entry_count):
            is_sample = cache_file.read(4) == b'IMPS'

            filename = cache_file.read(12).split(b'\x00')[0].decode('cp437')

            # 0x0010: 00h, GvL, Flg, Vol
            cache_file.read(4)

            # May be a sample name, or a special value
            sample_name_raw = cache_file.read(26).split(b'\x00')[0]

            if is_sample:
                entry_type = ENTRY_TYPE_SAMPLE
            elif sample_name_raw == DIRECTORY_SAMPLE_NAME:
                entry_type = ENTRY_TYPE_DIRECTORY
            elif sample_name_raw == LIBRARY_SAMPLE_NAME:
                entry_type = ENTRY_TYPE_LIBRARY
            else:
                entry_type = ENTRY_TYPE_UNKNOWN

            if entry_type == ENTRY_TYPE_SAMPLE:
                sample_name = sample_name_raw.decode('cp437')
            else:
                sample_name = None

            # skip details
            cache_file.read(34)

            # fmt follows packed_time, but I see many undocumented values or
            # ones that don't match docs
            (file_size, packed_date, packed_time) = struct.unpack('<IHH8x', cache_file.read(16))

            year, month, day = unpack_impulse_tracker_date(packed_date)
            hour, minute, second = unpack_impulse_tracker_time(packed_time)

            entries.append(CacheEntry(
                filename,
                sample_name,
                entry_type,
                file_size,
                datetime.datetime(year, month, day, hour, minute, second)
            ))

        return entries




if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Load entries from CACHE.ITS file and print them')
    parser.add_argument('cache_its_path', metavar='CACHE.ITS', help='Path to CACHE.ITS')
    parser.add_argument('--for-touch', dest='show_touch_commands', action='store_true', default=False, help='Show touch commands to update file dates/times. Note that the filename may need to be adjusted for case-sensitivity etc.')

    args = parser.parse_args()

    entries = load_entries_from_cache_its(args.cache_its_path)

    if args.show_touch_commands:
        for entry in entries:
            if entry.filename == '\\' or entry.filename == '..':
                continue

            touch_timestamp = entry.datetime.strftime('%Y%m%d%H%M.%S')

            print(shlex.join(['touch', '-c', '-t', touch_timestamp, entry.filename]))


    else:
        for entry in entries:
            if entry.type == ENTRY_TYPE_DIRECTORY:
                size_or_type = f'<DIR>'
            else:
                size_or_type = f'{entry.size}'

            sample_name_description = f' {entry.sample_name}' if entry.sample_name is not None else ''

            print(f'{entry.filename:12s} {size_or_type:8s} {entry.datetime}{sample_name_description}')



