from services import check_date_in_str


while True:
    text = input("Введите вашу строку: ")
    if check_date_in_str(text):
        print("В вашей строке есть дата")
    else:
        print("В вашей строке нет даты")

    print("\n")
    