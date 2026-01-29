# ean13_generator_full_fixed.py
# Program generujący poprawny kod EAN-13 z obliczaniem lub weryfikacją cyfry kontrolnej
# Autor: [Twoje imię]
# Wymaga: Pillow (pip install pillow)

from PIL import Image, ImageDraw, ImageFont

# --- Tablice kodowania EAN-13 ---
ENC_A = {
    '0':'0001101','1':'0011001','2':'0010011','3':'0111101','4':'0100011',
    '5':'0110001','6':'0101111','7':'0111011','8':'0110111','9':'0001011'
}
ENC_B = {
    '0':'0100111','1':'0110011','2':'0011011','3':'0100001','4':'0011101',
    '5':'0111001','6':'0000101','7':'0010001','8':'0001001','9':'0010111'
}
ENC_C = {
    '0':'1110010','1':'1100110','2':'1101100','3':'1000010','4':'1011100',
    '5':'1001110','6':'1010000','7':'1000100','8':'1001000','9':'1110100'
}
FIRST_DIGIT_PATTERN = {
    '0':'AAAAAA','1':'AABABB','2':'AABBAB','3':'AABBBA','4':'ABAABB',
    '5':'ABBAAB','6':'ABBBAA','7':'ABABAB','8':'ABABBA','9':'ABBABA'
}

# --- Obliczanie cyfry kontrolnej ---
def compute_check_digit(digits: str) -> str:
    if not digits.isdigit():
        raise ValueError("Dozwolone są tylko cyfry.")
    if len(digits) != 12:
        raise ValueError("Do obliczenia podaj dokładnie 12 cyfr.")
    s = 0
    for i, d in enumerate(digits):
        n = int(d)
        if (i + 1) % 2 == 0:
            s += n * 3
        else:
            s += n
    check = (10 - (s % 10)) % 10
    return str(check)

# --- Weryfikacja poprawności kodu EAN-13 ---
def validate_ean13(code: str) -> bool:
    return compute_check_digit(code[:12]) == code[-1]

# --- Kodowanie EAN-13 do bitów ---
def encode_ean13(code13: str) -> str:
    first = code13[0]
    left = code13[1:7]
    right = code13[7:]
    pattern = FIRST_DIGIT_PATTERN[first]

    bits = '101'  # start
    for i, ch in enumerate(left):
        bits += ENC_A[ch] if pattern[i] == 'A' else ENC_B[ch]
    bits += '01010'  # separator środkowy
    for ch in right:
        bits += ENC_C[ch]
    bits += '101'  # stop
    return bits

# --- Rysowanie kodu EAN-13 ---
def draw_ean13(code13: str, filename="ean13.png"):
    bits = encode_ean13(code13)
    module = 2  # szerokość kreski
    height = 90  # wysokość normalnych pasków
    long_height = 100  # dłuższe paski dla start/środek/stop
    quiet = 10  # marginesy

    width = (len(bits) + 2 * quiet) * module
    img = Image.new("RGB", (width, long_height + 30), "white")
    draw = ImageDraw.Draw(img)

    x = quiet * module
    for i, bit in enumerate(bits):
        if bit == '1':
            # dłuższe paski dla start/środek/stop
            if (i < 3) or (45 <= i < 50) or (len(bits)-3 <= i):
                h = long_height
            else:
                h = height
            draw.rectangle([x, 0, x + module - 1, h], fill="black")
        x += module

    # Font dla cyfr
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()

    # Pozycje cyfr zgodnie z EAN13
    start_x = quiet * module
    text_y = long_height + 5

    # Pierwsza cyfra (po lewej)
    draw.text((start_x - 12, text_y), code13[0], font=font, fill="black")

    # 6 cyfr po lewej stronie
    for i in range(6):
        offset = start_x + 3*module + i*7*module
        draw.text((offset + 2, text_y), code13[i+1], font=font, fill="black")

    # 6 cyfr po prawej stronie
    for i in range(6):
        offset = start_x + (3 + 42 + 5) * module + i*7*module
        draw.text((offset + 2, text_y), code13[i+7], font=font, fill="black")

    img.save(filename)
    print(f"Zapisano plik: {filename}")

# --- Główna część programu ---
if __name__ == "__main__":
    s = input("Podaj 12 lub 13 cyfr: ").strip()
    if not s.isdigit():
        print("Błąd: dozwolone tylko cyfry.")
    elif len(s) == 12:
        check = compute_check_digit(s)
        full = s + check
        print(f"Cyfra kontrolna: {check}")
        print(f"Pełny kod EAN-13: {full}")
        draw_ean13(full, f"ean13_{full}.png")
    elif len(s) == 13:
        if validate_ean13(s):
            print("Cyfra kontrolna jest poprawna.")
            draw_ean13(s, f"ean13_{s}.png")
        else:
            print("Błędna cyfra kontrolna!")
    else:
        print("Kod powinien mieć 12 lub 13 cyfr.")
