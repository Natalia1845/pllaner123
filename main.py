from flask import Flask, render_template, request, redirect, url_for, session, flash

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:11111111@localhost/pet_app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- МОДЕЛІ ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    calories_per_100g = db.Column(db.Integer, nullable=False)
    preferred_store = db.Column(db.String(100))  # ✅ нове поле


class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('meals', lazy=True))

class MealIngredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meal_id = db.Column(db.Integer, db.ForeignKey('meal.id'), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'), nullable=False)
    amount_in_grams = db.Column(db.Integer, nullable=False)
    meal = db.relationship('Meal', backref=db.backref('ingredients', lazy=True))
    ingredient = db.relationship('Ingredient')

class WeeklyMenu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    meal_id = db.Column(db.Integer, db.ForeignKey('meal.id'), nullable=False)
    day_of_week = db.Column(db.String(10), nullable=False)
    meal_type = db.Column(db.String(20), nullable=False)  # <--- ОБОВ'ЯЗКОВО!

    user = db.relationship('User', backref=db.backref('weekly_menus', lazy=True))
    meal = db.relationship('Meal', backref=db.backref('scheduled_days', lazy=True))


# --- МАРШРУТИ ---
from datetime import datetime

@app.route('/')
def home():
    return render_template('index.html', year=datetime.utcnow().year)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and check_password_hash(user.password, request.form['password']):
            session['user_id'] = user.id
            return redirect(url_for('home'))
        return 'Невірні дані для входу'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))




from collections import defaultdict

@app.route('/weekly_menu')
def weekly_menu():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    menu_items = WeeklyMenu.query.filter_by(user_id=user_id).all()

    days = ['Понеділок', 'Вівторок', 'Середа', 'Четвер', 'Пʼятниця', 'Субота', 'Неділя']
    meal_types = ['Сніданок', 'Обід', 'Вечеря']

    menu_by_day = {day: {mtype: None for mtype in meal_types} for day in days}
    calories_by_day = defaultdict(int)
    total_calories = 0

    for item in menu_items:
        if item.day_of_week in menu_by_day and item.meal_type in meal_types:
            meal_name = item.meal.name if item.meal else 'Невідомо'
            menu_by_day[item.day_of_week][item.meal_type] = meal_name

            # Рахуємо калорії для цієї страви
            meal_calories = 0
            for mi in item.meal.ingredients:
                meal_calories += (mi.amount_in_grams / 100) * mi.ingredient.calories_per_100g

            calories_by_day[item.day_of_week] += meal_calories
            total_calories += meal_calories

    return render_template(
        'weekly_menu.html',
        menu=menu_by_day,
        calories=calories_by_day,
        total_calories=int(total_calories),
        year=datetime.utcnow().year
    )


@app.route('/edit_menu', methods=['GET', 'POST'])
def edit_menu():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    meals = Meal.query.filter_by(user_id=user_id).all()
    days = ['Понеділок', 'Вівторок', 'Середа', 'Четвер', 'Пʼятниця', 'Субота', 'Неділя']
    meal_types = ['Сніданок', 'Обід', 'Вечеря']

    if request.method == 'POST':
        # Очистити старе меню
        WeeklyMenu.query.filter_by(user_id=user_id).delete()

        for day in days:
            for mtype in meal_types:
                meal_id = request.form.get(f"{day}_{mtype}")
                if meal_id:
                    db.session.add(WeeklyMenu(
                        user_id=user_id,
                        meal_id=int(meal_id),
                        day_of_week=day,
                        meal_type=mtype
                    ))
        db.session.commit()
        flash("✅ Меню оновлено вручну!")
        return redirect(url_for('weekly_menu'))

    # Передаємо шаблону всі страви і структуру днів/типів
    return render_template('edit_menu.html', meals=meals, days=days, meal_types=meal_types)





@app.route('/refresh_menu', methods=['POST'])
def refresh_weekly_menu():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    meals = Meal.query.filter_by(user_id=user.id).all()

    if len(meals) < 3:
        flash("❌ Недостатньо страв для формування меню.")
        return redirect(url_for('weekly_menu'))

    WeeklyMenu.query.filter_by(user_id=user.id).delete()

    import random
    days = ['Понеділок', 'Вівторок', 'Середа', 'Четвер', 'Пʼятниця', 'Субота', 'Неділя']
    meal_types = ['Сніданок', 'Обід', 'Вечеря']

    for day in days:
        chosen = random.sample(meals, 3)
        for i, meal in enumerate(chosen):
            db.session.add(WeeklyMenu(
                user_id=user.id,
                meal_id=meal.id,
                day_of_week=day,
                meal_type=meal_types[i]
            ))

    db.session.commit()
    flash("✅ Меню оновлено успішно!")
    return redirect(url_for('weekly_menu'))


@app.route('/shopping_list')
def shopping_list():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    menu_items = WeeklyMenu.query.filter_by(user_id=user_id).all()

    ingredient_totals = {}
    ingredient_stores = {}

    for item in menu_items:
        for mi in item.meal.ingredients:
            name = mi.ingredient.name
            grams = mi.amount_in_grams
            store = mi.ingredient.preferred_store or "🛍 Будь-який"

            ingredient_totals[name] = ingredient_totals.get(name, 0) + grams
            ingredient_stores[name] = store

    return render_template('shopping_list.html', ingredients=ingredient_totals, stores=ingredient_stores)




import pandas as pd
from flask import send_file
from io import BytesIO

@app.route('/export_excel')
def export_excel():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    items = WeeklyMenu.query.filter_by(user_id=user_id).all()

    data = [{
        "День": item.day_of_week,
        "Тип прийому": item.meal_type,
        "Страва": item.meal.name
    } for item in items]

    df = pd.DataFrame(data)
    output = BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)

    return send_file(output, download_name="menu.xlsx", as_attachment=True)




# --- СТАРТ ---
if __name__ == '__main__':
    app.run(debug=True)
