def next_f(number_f):
    lst = list(number_f)

    if number_f.isdigit():
        return str(int(number_f) + 1)
    else:
        for index in range(len(lst))[::-1]:
            num = lst.pop(index)
            if num.isdigit():
                num = str(int(num) + 1)
                if len(num) < 2:
                    lst.insert(index, num)
                    break
                else:
                    lst.insert(index, '0')
            else:
                num = chr(ord(num) + 1)
                lst.insert(index, num)
                break
        return ''.join(lst)
