from database.database import * 

dict_user_reser_cat = {}

async def on_startup():
    print("Бот запускается...")
    users = get_users()
    for user in users:
        cats = [(i[1], i[5]) for i in get_all_reserve_budget(user)]
        dict_user_reser_cat[str(user)] = cats

