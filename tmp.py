def macro_parser(string):
    parsed = []
    i=0
    buffer = ""
    while i<len(string):
        char = string[i]
        if i>0 and char=="@" and string[i-1]=="\\":
            buffer = buffer[:-1]+"@"
            i+=1
            continue
        if char=="@" and i+1<len(string):
            if string[i+1]=="<":
                fact = -1
            elif string[i+1]==">":
                fact = 1
            i+=2
            #continue the loop in here
            num_buffer = ""
            while i<len(string):
                if (char:=string[i]).isnumeric():
                    num_buffer += char
                    i+=1
                    continue
                break
            #if no num ignore @ signs
            if not num_buffer:
                continue
            parsed.append(buffer)
            buffer = ""
            num = int(num_buffer)*fact
            parsed.append(num)
            
            continue
        buffer+=char
        i+=1
    if buffer:
        parsed.append(buffer)
    return parsed

if __name__=="__main__":
    tests = [
        "Hello !@<1World",
        "Hello World!@<",
        "Hello World!\@<4",
        "\@Hello World!",
        "@<Hello World!"
    ]

    for test in tests:
        print(parser(test))
