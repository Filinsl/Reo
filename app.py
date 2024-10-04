from flask import Flask, render_template, request, redirect, session
import os
import time
import random
import requests
import json

app = Flask(__name__)
app.secret_key = 'R3EdyG8VCe'

# Укажите ваш ключ API JSONBin
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')  # Получение токена GitHub из переменных окружения
REPO_NAME = 'ваш_репозиторий'  # Укажите имя вашего репозитория
FILE_PATH = 'results.json'  # Путь к вашему JSON файлу в репозитории

# Загрузка результатов из GitHub
def load_results():
    url = f'https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}'
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}'
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        content = response.json()['content']
        results = json.loads(content)
        return sorted(results, key=lambda x: x['time_spent'])  # Сортировка по времени
    return []

# Сохранение результата в GitHub
def save_result(username, time_spent):
    url = f'https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}'
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Content-Type': 'application/json'
    }

    # Загрузка текущих результатов
    results = load_results()
    # Добавление нового результата
    results.append({'username': username, 'time_spent': time_spent})

    # Кодирование результатов в JSON
    json_data = json.dumps(results)
    sha = requests.get(url, headers=headers).json()['sha']  # Получаем SHA для обновления файла
    data = {
        "message": "Update results",
        "content": json_data,
        "sha": sha
    }

    response = requests.put(url, headers=headers, json=data)
    return response.status_code == 200

# Главная страница с игрой
@app.route('/')
def index():
    if 'username' not in session:
        return redirect('/login')
    return render_template('index.html', username=session['username'])

# Страница входа/регистрации
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        # Ограничение на длину ника
        if len(username) > 15:
            return render_template('login.html', error="Username must be 15 characters or less.")
        session['username'] = username
        return redirect('/')
    return render_template('login.html')

# Обработка завершения игры и сохранение результатов
@app.route('/submit_result', methods=['POST'])
def submit_result():
    if 'username' not in session:
        return redirect('/login')
    
    time_spent = float(request.form['time_spent'])
    username = session['username']
    
    # Сохранение нового результата в GitHub
    save_result(username, time_spent)
    
    return redirect('/results')

# Страница с результатами
@app.route('/results')
def results():
    results = load_results()
    return render_template('results.html', results=results)

# Выход из сессии
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
