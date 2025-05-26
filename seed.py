from main import app, db
from models import Ingredient, User, Meal, MealIngredient

# --- Інгредієнти ---
ingredients_data = [
    {"name": "Картопля", "calories_per_100g": 77},
    {"name": "Куряче філе", "calories_per_100g": 165},
    {"name": "Помідор", "calories_per_100g": 18},
    {"name": "Огірок", "calories_per_100g": 16},
    {"name": "Рис", "calories_per_100g": 130},
    {"name": "Яйце", "calories_per_100g": 155},
    {"name": "Сир твердий", "calories_per_100g": 330},
    {"name": "Морква", "calories_per_100g": 41},
    {"name": "Яловичина", "calories_per_100g": 250},
    {"name": "Олія оливкова", "calories_per_100g": 884}
]

# --- Страви з інгредієнтами ---
meals_data = [
    {
        "name": "Курка з рисом",
        "ingredients": [("Куряче філе", 150), ("Рис", 100), ("Олія оливкова", 10)]
    },
    {
        "name": "Салат овочевий",
        "ingredients": [("Помідор", 100), ("Огірок", 100), ("Морква", 50), ("Олія оливкова", 5)]
    },
    {
        "name": "Яєчня з сиром",
        "ingredients": [("Яйце", 120), ("Сир твердий", 30), ("Олія оливкова", 5)]
    }
]

# --- Запис у базу ---
with app.app_context():
    # Додавання інгредієнтів
    for item in ingredients_data:
        existing = Ingredient.query.filter_by(name=item["name"]).first()
        if not existing:
            ingredient = Ingredient(
                name=item["name"],
                calories_per_100g=item["calories_per_100g"]
            )
            db.session.add(ingredient)
    db.session.commit()
    print("✅ Інгредієнти додано до бази даних.")

    # Отримуємо першого користувача
    user = User.query.first()
    if not user:
        print("❌ У базі немає жодного користувача. Спочатку зареєструйся через сайт.")
        exit()
    print(f"✅ Дані будуть додані для користувача: {user.email}")

    # Додавання страв
    for meal_data in meals_data:
        existing = Meal.query.filter_by(name=meal_data["name"], user_id=user.id).first()
        if not existing:
            meal = Meal(name=meal_data["name"], user_id=user.id)
            db.session.add(meal)
            db.session.commit()

            for ing_name, grams in meal_data["ingredients"]:
                ing = Ingredient.query.filter_by(name=ing_name).first()
                if ing:
                    mi = MealIngredient(
                        meal_id=meal.id,
                        ingredient_id=ing.id,
                        amount_in_grams=grams
                    )
                    db.session.add(mi)
            db.session.commit()
    print("✅ Страви з інгредієнтами додано до бази.")
