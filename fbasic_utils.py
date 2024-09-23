import math
import struct

from fbasic_ir_table import ir_table, ir_table_ff
from ascii_j import *

def decode_float(data:bytearray):
    exponent = data[0]
    mantissa_MSB = 1 if exponent & 0x80 else 0
    exponent = exponent & 0x7f
    if exponent & 0x40:
        exponent = (exponent ^ 0x7f) - 1        # complement of 2
    tmpbuf = data.copy()
    tmpbuf[0] = 0
    tmpbuf[1] |= 0x80 if mantissa_MSB == 1 else 0x00
    mantissa = struct.unpack_from('>I', tmpbuf, 0)[0]
    mantissa /= 0x1000000
    value = mantissa * (2**exponent)
    return value

def decode_double(data:bytearray):
    exponent = data[0]
    mantissa_MSB = 1 if exponent & 0x80 else 0
    exponent = exponent & 0x7f
    if exponent & 0x40:
        exponent = (exponent ^ 0x7f) - 1        # complement of 2
    tmpbuf = data.copy()
    tmpbuf[0] = 0
    tmpbuf[1] |= 0x80 if mantissa_MSB == 1 else 0x00
    mantissa = struct.unpack_from('>Q', tmpbuf, 0)[0]
    mantissa /= 0x100000000000000
    value = mantissa * (2**exponent)
    return value


class Decode_State:
    skip_link = 'Skipping link pointer',
    line_num = 'Line number on the top of the line',
    ir_dec = 'IR decoding',
    ir_dec_ff = 'Extended IR decoding (with prefix $ff)',
    string = 'String decoding',
    remark = 'Remark',
    literal = 'Leteral value'

class Prev_Type:
    keyword = 'keyword',
    literal = 'literal',
    new_line = 'new_line',
    string = 'string',
    remark = 'remark',
    line_number = 'line_number'

def F_BASIC_IR_decode(ir_data):
    ir_codes = list(ir_table.keys())
    ir_min = min(ir_codes)
    ir_max = max(ir_codes)
    ir_codes = list(ir_table_ff.keys())
    ir_min_ff = min(ir_codes)
    ir_max_ff = max(ir_codes)
    prev_type = Prev_Type.new_line
    res = ''
    # Link pointer (XX,XX), Line Number (XX, XX), IR/Literal, Line separator (0x00)
    # Line number: 0xfe 0xf2 0xXX 0xXX
    # Line separator: 0x00
    state = Decode_State.skip_link
    count = 0
    line_num = 0
    literal_type = 0
    literal_val = 0
    decode_buf = bytearray()
    special_chars = ' =+-*/\^()%#$!&@,.\';:?<>"_'
    for ir in ir_data:
        match state:
            case Decode_State.skip_link:
                count += 1
                if count < 2:
                    continue
                count = 0
                decode_buf = bytearray()
                state = Decode_State.line_num
            case Decode_State.line_num:
                count += 1
                decode_buf.extend([ir])
                if count < 2:
                    continue
                line_num = struct.unpack_from('>H', decode_buf, 0)[0]
                count = 0
                res += str(line_num)
                prev_type = Prev_Type.line_number
                state = Decode_State.ir_dec
            case Decode_State.ir_dec:               # BASIC keyword
                if ir == 0x00:                      # Line separator
                    res += '\n'
                    count = 0
                    state = Decode_State.skip_link
                    continue
                if ir == 0xfe:                      # Constant/Literal value
                    count = 1
                    decode_buf = bytearray([ir])
                    state = Decode_State.literal
                    continue
                if ir == 0xff:
                    state = Decode_State.ir_dec_ff
                    continue
                if ir >= ir_min and ir <= ir_max:
                    keyword = ir_table[ir]
                    if prev_type != Prev_Type.keyword and prev_type != Prev_Type.string:
                        if keyword not in special_chars:
                            res += ' '
                    res += keyword
                    prev_type = Prev_Type.keyword
                    if keyword == '\'' or keyword == 'REM':
                        state = Decode_State.remark
                    continue
                if prev_type != Prev_Type.keyword and prev_type != Prev_Type.string:
                    if chr(ir) not in special_chars:
                        res += ' '
                res += chr(ir)
                if ir == ord('"'):
                    state = Decode_State.string
                else:
                    prev_type = Prev_Type.keyword
            case Decode_State.ir_dec_ff:                        # BASIC keyword with $FF prefix
                if ir >= ir_min_ff and ir <= ir_max_ff:
                    keyword = ir_table_ff[ir]
                    if prev_type != Prev_Type.keyword and prev_type != Prev_Type.string:
                        res += ' '
                    res += keyword
                prev_type = Prev_Type.keyword
                state = Decode_State.ir_dec
            case Decode_State.literal:
                decode_buf.extend([ir])
                count += 1
                if count == 2:
                    literal_type = ir   # keep the literal type ID
                    continue
                match literal_type:
                    case 0x01:      # 1 byte, signed integer
                        literal_val = int(ir)
                        literal_str = str(literal_val)
                    case 0x02:      # 2 byte, signed integer
                        if count < 2+2:
                            continue
                        literal_val = struct.unpack_from('>H', decode_buf, 2)[0]
                        literal_str = str(literal_val)
                    case 0x04:      # 4 byte, sigle precision floating point [EXP]+[3MAN]
                        if count < 2+4:
                            continue
                        literal_val = decode_float(decode_buf[2:])
                        if int(literal_val) == literal_val:     # no fractional digits
                            literal_str = str(int(literal_val)) + '!'
                        else:
                            literal_str = str(literal_val)
                    case 0x08:      # 8 byte, double precision floating point [EXP]+[7MAN]
                        if count < 2+8:
                            continue
                        literal_val = decode_double(decode_buf[2:])
                        if int(literal_val) == literal_val:     # no fractional digits
                            literal_str = str(int(literal_val)) + '#'
                        else:
                            literal_str = str(literal_val)
                    case 0xf2:      # 2 byte, unsigned integer, dedicatd for line number
                        if count < 2+2:
                            continue
                        literal_val = struct.unpack_from('>H', decode_buf, 2)[0]
                        literal_str = str(literal_val)
                res += literal_str
                prev_type = Prev_Type.literal
                state = Decode_State.ir_dec
            case Decode_State.string:
                res += ascii_table_half[ir]
                prev_type = Prev_Type.string
                if ir == ord('"'):
                    state = Decode_State.ir_dec
                if ir == 0x00:
                    res += '\n'
                    count = 0
                    state = Decode_State.skip_link
                    continue
            case Decode_State.remark:
                if ir == 0x00:                      # Line separator
                    res += '\n'
                    count = 0
                    state = Decode_State.skip_link
                    prev_type = Prev_Type.remark
                    continue
                res += ascii_table_half[ir]
    return res
