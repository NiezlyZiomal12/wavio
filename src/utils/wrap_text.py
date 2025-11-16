def wrap_text(text, font, max_width):
    words = text.split(" ")
    lines = []
    current = ""

    for w in words:
        test = current + w + " "
        if font.size(test)[0] <= max_width:
            current = test
        else:
            lines.append(current)
            current = w + " "

    if current:
        lines.append(current)

    return lines
