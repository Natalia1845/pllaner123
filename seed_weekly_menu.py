from main import app, db, WeeklyMenu, Meal, User
import random

with app.app_context():
    user = User.query.first()
    if not user:
        print("❌ Користувача не знайдено.")
        exit()

    meals = Meal.query.filter_by(user_id=user.id).all()
    if len(meals) < 3:
        print("❌ Необхідно щонайменше 3 страви.")
        exit()

    WeeklyMenu.query.filter_by(user_id=user.id).delete()
    db.session.commit()

    days = ['Понеділок', 'Вівторок', 'Середа', 'Четвер', 'Пʼятниця', 'Субота', 'Неділя']
    meal_types = ['Сніданок', 'Обід', 'Вечеря']

    print("ℹ️ Додаємо по 3 страви на день...")

    for day in days:
        selected_meals = random.sample(meals, 3) if len(meals) >= 3 else meals
        for i in range(3):
            db.session.add(WeeklyMenu(
                user_id=user.id,
                meal_id=selected_meals[i % len(selected_meals)].id,
                day_of_week=day,
                meal_type=meal_types[i]
            ))

    db.session.commit()
    print("✅ Тижневе меню оновлено з 3 прийомами їжі щодня.")



