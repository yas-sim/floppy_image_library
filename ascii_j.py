ascii_table_half = \
    '................' +\
    '................' +\
    ' !"#$%&\'()*+,-./'+\
    '0123456789:;<=>?' +\
    '@ABCDEFGHIJKLMNO' +\
    'PQRSTUVWXYZ[\]^-' +\
    '`abcdefghighlmno' +\
    'pqrstuvwxyz{|}~.' +\
    '■■■■■■■■■■■■■■■■' +\
    '■■■■■■■■■■■■■■■■' +\
    ' ｡｢｣､･ｦｧｨｩｪｫｬｭｮｯ' +\
    'ｰｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿ' +\
    'ﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏ' +\
    'ﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ゛゜' +\
    '■■■■■■■■♠♡♦♧●〇/\\' +\
    '×円年月日時分秒〒市区町村人🏁 '

ascii_table_full = \
    '................' +\
    '................' +\
    '　！”＃＄％＆’（）＊＋，－．／'+\
    '０１２３４５６７８９：；＜＝＞？' +\
    '＠ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯ' +\
    'ＰＱＲＳＴＵＶＷＸＹＺ［￥］＾－' +\
    '‘ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏ' +\
    'ｐｑｒｓｔｕｖｗｘｙｚ｛｜｝～．' +\
    '■■■■■■■■■■■■■■■■' +\
    '■■■■■■■■■■■■■■■■' +\
    ' 。「」、・ヲァィゥェォャュョッ' +\
    'ーアイウエオカキクケコサシスセソ' +\
    'タチツテトナニヌネノハヒフヘホマ' +\
    'ミムメモヤユヨラリルレロワン゛゜' +\
    '■■■■■■■■♠♡♦♧●〇／＼' +\
    '×円年月日時分秒〒市区町村人🏁 '

def asciij_to_utf8(asciij_str:bytearray):
    res = ''
    for ch in asciij_str:
        if ch == ord('\r') or ch == ord('\n'):
            utf8 = chr(ch)
        else:
            utf8 = ascii_table_half[ch]
        res += utf8
    return res

def asciij_string_to_utf8(asciij_str:str):
    res = ''
    for ch in asciij_str:
        ch = ord(ch)
        if ch == ord('\r') or ch == ord('\n'):
            utf8 = chr(ch)
        else:
            utf8 = ascii_table_half[ch]
        res += utf8
    return res
