def parse_col(col):
    """
    Берет сырое название ID#90 и возвращает нормальное ID
    """
    return col.split("#", 1)[0].upper()

def remove_commas(s):
    """
    Берет стринг s, удаляет в ней все запятые внутри скобок
    """
    ans, stack = "", 0
    for char in s:
        if char == "(":
            stack += 1
        if char == ")":
            stack -= 1
        if char == "," and stack > 0:
            ans += " " 
        else:
            ans += char
    return ans