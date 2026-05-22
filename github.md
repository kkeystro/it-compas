# GitHub — как залить проект

## 📦 Подготовка

Убедись, что у тебя установлен `git` и `gh` (GitHub CLI):

```bash
git --version
gh --version
```

Войди в GitHub CLI (если ещё не):

```bash
gh auth login
# Выбери: GitHub.com → HTTPS → Login with a web browser
```

Или настрой git вручную:

```bash
git config --global user.name "Твоё имя"
git config --global user.email "твой@email.com"
```

---

## 🚀 Заливка на GitHub (с нуля)

### 1. Создай репозиторий на GitHub

**Вариант A — через gh CLI (быстро):**

```bash
cd /home/kkeystro/centerinvest

# Создать репозиторий и запушить
gh repo create centerinvest --public --source=. --push
```

**Вариант B — через web-интерфейс:**

1. Зайди на https://github.com/new
2. Название: `centerinvest`
3. **Не** создавай README, .gitignore и лицензию (они уже есть)
4. Нажми "Create repository"
5. Выполни команды:

```bash
cd /home/kkeystro/centerinvest

git remote add origin https://github.com/<твой-username>/centerinvest.git
git push -u origin master
```

---

### 2. Проверь, что всё закоммичено

```bash
git status
# → nothing to commit, working tree clean
```

Если есть незакоммиченные изменения:

```bash
git add -A
git commit -m "Prepare for GitHub: cleanup, docs, README"
```

---

### 3. Отправь на GitHub

```bash
git push -u origin master
```

---

## 🔄 Обновление изменений

Если ты уже залил проект и хочешь обновить его:

```bash
# 1. Проверить статус
git status

# 2. Добавить изменения
git add -A

# 3. Создать коммит
git commit -m "Описание изменений"

# 4. Отправить
git push
```

---

## 🌿 Работа с ветками (рекомендуется)

```bash
# Создать новую ветку для фичи
git checkout -b feature/awesome-feature

# ... сделать изменения ...
git add -A
git commit -m "Add awesome feature"
git push -u origin feature/awesome-feature

# Создать PR на GitHub и смержить
# Или смержить локально:
git checkout master
git merge feature/awesome-feature
git push
```

---

## ❌ Что НЕ должно попасть в репозиторий

Файлы и папки, которые игнорируются `.gitignore`:

- `node_modules/` — зависимости фронтенда
- `__pycache__/`, `*.pyc` — байткод Python
- `.env` — секреты и пароли (используй `.env.example`)
- `*.db`, `*.sqlite3` — базы данных
- `.vscode/`, `.idea/` — настройки IDE
- `dist/`, `build/` — артефакты сборки

Перед коммитом проверь:

```bash
git status
```

⚠️ Если видишь `backend/test_changes.py` — удали его (это временный файл):

```bash
git rm backend/test_changes.py
```

---

## 🔍 Полезные команды

```bash
# Посмотреть, что будет в коммите
git diff --stat

# Отменить добавление файла
git reset HEAD file.txt

# Посмотреть историю
git log --oneline --graph --all

# Откатить незакоммиченные изменения
git checkout -- file.txt
```

---

## 📚 Полезные ссылки

- [GitHub Docs — создание репозитория](https://docs.github.com/en/get-started/quickstart/create-a-repo)
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)
- [gh CLI manual](https://cli.github.com/manual/)
