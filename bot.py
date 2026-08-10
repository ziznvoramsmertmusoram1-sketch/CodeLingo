import sqlite3
import datetime
import json
import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
import google.generativeai as genai

# ================= КОНФИГУРАЦИЯ =================
BOT_TOKEN = "8743038849:AAFB8sEkKZ8ilU_m5EAhryP8tQMSxipXfFs"
GEMINI_API_KEY = "AQ.Ab8RN6LIlfOAAokOO_Mu16sY5lXwxjCBKCAv1UCxEtzxdh6kDQ"

# Укажи свой настоящий Telegram ID (узнать в боте @userinfobot)
OWNER_ID = 6341264728  

WEBAPP_URL = "https://ziznvoramsmertmusoram1-sketch.github.io/CodeLingo/"
CHANNEL_AVATAR_URL = "https://i.imgur.com/example.jpg"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ================= БАНК ВОПРОСОВ (ГОТОВЫЙ) =================
LESSON_BANK = {
    "Python": [
        {"q": "Что выведет:\nprint(2 ** 3)", "options": ["6", "8", "9", "ошибка"], "correct": 1},
        {"q": "Как объявить пустой список?", "options": ["list = ()", "list = []", "list = {}", "list = <>"], "correct": 1},
        {"q": "Какой тип данных у 'привет'?", "options": ["int", "str", "char", "text"], "correct": 1},
        {"q": "Сколько раз выполнится:\nfor i in range(5): print(i)", "options": ["4", "5", "6", "бесконечно"], "correct": 1},
        {"q": "Оператор деления с остатком?", "options": ["//", "%", "/", "**"], "correct": 1},
        {"q": "Как объявить функцию в Python?", "options": ["func", "function", "def", "fn"], "correct": 2},
        {"q": "Что выведет:\nprint(len([1, 2, 3]))", "options": ["2", "3", "4", "ошибка"], "correct": 1},
        {"q": "С какого индекса начинается список в Python?", "options": ["0", "1", "-1", "с любого"], "correct": 0},
        {"q": "Как сравнить два значения на равенство?", "options": ["=", "==", "equals()", "is"], "correct": 1},
        {"q": "Что выведет:\nprint('a' + 'b')", "options": ["a b", "ab", "a+b", "ошибка"], "correct": 1},
    ],
    "JavaScript": [
        {"q": "Что выведет:\nconsole.log(typeof [])", "options": ["'array'", "'object'", "'list'", "'undefined'"], "correct": 1},
        {"q": "Как объявить константу?", "options": ["var x = 1", "let x = 1", "const x = 1", "int x = 1"], "correct": 2},
        {"q": "Что выведет:\nconsole.log(1 + '1')", "options": ["2", "'11'", "NaN", "ошибка"], "correct": 1},
        {"q": "Как создать пустой массив?", "options": ["[]", "{}", "()", "new Array"], "correct": 0},
        {"q": "Как объявить функцию?", "options": ["func", "def", "function", "fn"], "correct": 2},
        {"q": "Чем === отличается от ==?", "options": ["ничем", "проверяет и тип, и значение", "проверяет только тип", "работает только с числами"], "correct": 1},
        {"q": "Как узнать длину массива arr?", "options": ["arr.length", "arr.size()", "len(arr)", "arr.count"], "correct": 0},
        {"q": "Что выведет:\nconsole.log(typeof null)", "options": ["'null'", "'undefined'", "'object'", "'boolean'"], "correct": 2},
        {"q": "Как объявить объект?", "options": ["[]", "{}", "()", "<>"], "correct": 1},
        {"q": "Какой метод добавляет элемент в конец массива?", "options": ["arr.add()", "arr.push()", "arr.append()", "arr.insert()"], "correct": 1},
    ],
    "HTML/CSS": [
        {"q": "Какой тег создаёт ссылку?", "options": ["<link>", "<a>", "<href>", "<url>"], "correct": 1},
        {"q": "Какой тег вставляет изображение?", "options": ["<image>", "<img>", "<pic>", "<src>"], "correct": 1},
        {"q": "Какое CSS-свойство меняет цвет текста?", "options": ["text-color", "font-color", "color", "background"], "correct": 2},
        {"q": "Какой тег — заголовок самого высокого уровня?", "options": ["<h6>", "<head>", "<h1>", "<header>"], "correct": 2},
        {"q": "Что делает display: none?", "options": ["делает элемент прозрачным", "скрывает элемент полностью", "уменьшает размер", "ничего"], "correct": 1},
        {"q": "Какой тег создаёт маркированный список?", "options": ["<ol>", "<ul>", "<list>", "<li>"], "correct": 1},
        {"q": "Атрибут alt у <img> нужен для?", "options": ["стилей", "альтернативного текста", "адреса файла", "размера"], "correct": 1},
        {"q": "Какое свойство задаёт внешний отступ?", "options": ["padding", "margin", "border", "gap"], "correct": 1},
        {"q": "Какой тег создаёт таблицу?", "options": ["<table>", "<grid>", "<tab>", "<td>"], "correct": 0},
        {"q": "position: fixed фиксирует элемент относительно?", "options": ["родителя", "окна браузера", "документа", "предыдущего блока"], "correct": 1},
    ],
    "C++": [
        {"q": "Какой оператор выводит текст в консоль?", "options": ["print()", "echo", "cout <<", "console.log"], "correct": 2},
        {"q": "Какой тип для целых чисел?", "options": ["int", "num", "integer", "digit"], "correct": 0},
        {"q": "Как подключить библиотеку?", "options": ["import", "using", "#include", "require"], "correct": 2},
        {"q": "Как объявить указатель на int?", "options": ["int ptr", "int &ptr", "int *ptr", "ptr int"], "correct": 2},
        {"q": "Какой оператор читает ввод пользователя?", "options": ["cin >>", "input()", "read()", "scan()"], "correct": 0},
        {"q": "Оператор new создаёт объект где?", "options": ["в стеке", "в куче (heap)", "в регистре", "нигде"], "correct": 1},
        {"q": "Как выглядит однострочный комментарий?", "options": ["# комментарий", "// комментарий", "-- комментарий", "<!-- -->"], "correct": 1},
        {"q": "Цикл while выполняется пока?", "options": ["условие ложно", "условие истинно", "1 раз", "бесконечно всегда"], "correct": 1},
        {"q": "Какой тип для чисел с плавающей точкой?", "options": ["int", "float", "char", "bool"], "correct": 1},
        {"q": "Какая функция — точка входа программы?", "options": ["start()", "run()", "main()", "init()"], "correct": 2},
    ],
    "Java": [
        {"q": "Как вывести текст в консоль?", "options": ["print()", "System.out.println()", "console.log()", "echo"], "correct": 1},
        {"q": "Как объявляется класс?", "options": ["def", "class", "struct", "type"], "correct": 1},
        {"q": "Какой тип для целых чисел?", "options": ["int", "num", "integer", "digit"], "correct": 0},
        {"q": "Как создать массив из 5 int?", "options": ["int[5]", "new int[5]", "int arr(5)", "array(5)"], "correct": 1},
        {"q": "Какая сигнатура — точка входа программы?", "options": ["void main()", "public static void main(String[] args)", "def main()", "int main()"], "correct": 1},
        {"q": "Ключевое слово для наследования?", "options": ["implements", "extends", "inherits", "super"], "correct": 1},
        {"q": "Как объявить интерфейс?", "options": ["interface", "abstract", "protocol", "trait"], "correct": 0},
        {"q": "Кто освобождает неиспользуемую память?", "options": ["сам программист", "garbage collector", "компилятор", "никто"], "correct": 1},
        {"q": "Строки в Java (String) какие?", "options": ["изменяемые", "неизменяемые (immutable)", "как массив char только", "не объекты"], "correct": 1},
        {"q": "Чем equals() отличается от ==?", "options": ["ничем", "equals() сравнивает значение, == — ссылку", "== сравнивает значение, equals() — ссылку", "equals() работает только с числами"], "correct": 1},
    ],
    "C#": [
        {"q": "Как вывести текст в консоль?", "options": ["print()", "Console.WriteLine()", "echo", "System.print()"], "correct": 1},
        {"q": "Для чего используется var?", "options": ["для констант", "для неявной типизации", "для циклов", "для классов"], "correct": 1},
        {"q": "Как объявить класс?", "options": ["def", "class", "struct", "object"], "correct": 1},
        {"q": "Какой метод — точка входа программы?", "options": ["Start()", "Main()", "Run()", "Init()"], "correct": 1},
        {"q": "Как обозначается наследование от класса Base?", "options": ["class A extends Base", "class A : Base", "class A -> Base", "class A(Base)"], "correct": 1},
        {"q": "Директива using нужна для?", "options": ["циклов", "подключения пространства имён", "удаления объекта", "комментариев"], "correct": 1},
        {"q": "Через что объявляют свойства класса?", "options": ["get/set", "getter/setter()", "@property", "def property"], "correct": 0},
        {"q": "Как объявить массив из int?", "options": ["int[] arr", "array<int> arr", "int arr[]{}", "list int"], "correct": 0},
        {"q": "Что используют для асинхронного кода?", "options": ["thread/join", "async/await", "sync/wait", "go/chan"], "correct": 1},
        {"q": "Какой тип для строк?", "options": ["str", "string", "String[]", "text"], "correct": 1},
    ],
    "Kotlin": [
        {"q": "Как вывести текст в консоль?", "options": ["print/println", "echo", "console.log", "System.out"], "correct": 0},
        {"q": "Чем val отличается от var?", "options": ["ничем", "val — неизменяемая переменная", "var — неизменяемая переменная", "val работает только с числами"], "correct": 1},
        {"q": "Как объявить функцию?", "options": ["func", "def", "fun", "function"], "correct": 2},
        {"q": "Какой символ отмечает nullable-тип?", "options": ["!", "?", "*", "&"], "correct": 1},
        {"q": "Как объявить класс данных?", "options": ["data class", "struct class", "record class", "value class"], "correct": 0},
        {"q": "Какая функция — точка входа программы?", "options": ["fun start()", "fun main()", "fun init()", "fun run()"], "correct": 1},
        {"q": "Как выглядит лямбда в Kotlin?", "options": ["-> {}", "{ }", "() =>", "fn()"], "correct": 1},
        {"q": "Как записать диапазон от 1 до 10?", "options": ["1-10", "1..10", "range(1,10)", "[1,10]"], "correct": 1},
        {"q": "Что заменяет switch в Kotlin?", "options": ["match", "case", "when", "select"], "correct": 2},
        {"q": "Как называют функции, добавленные к существующему классу?", "options": ["extension functions", "mixins", "traits", "partial functions"], "correct": 0},
    ],
    "Swift": [
        {"q": "Как вывести текст в консоль?", "options": ["print()", "console.log()", "echo", "NSLog only"], "correct": 0},
        {"q": "Чем let отличается от var?", "options": ["ничем", "let — константа", "var — константа", "let только для чисел"], "correct": 1},
        {"q": "Какой символ означает опциональный тип?", "options": ["!", "?", "*", "~"], "correct": 1},
        {"q": "Как объявить функцию?", "options": ["def", "func", "fun", "function"], "correct": 1},
        {"q": "Ключевое слово для класса?", "options": ["class", "struct only", "type", "object"], "correct": 0},
        {"q": "Ключевое слово для структуры?", "options": ["class", "struct", "record", "data"], "correct": 1},
        {"q": "Для чего нужен guard?", "options": ["для циклов", "для раннего выхода из функции", "для комментариев", "для импорта"], "correct": 1},
        {"q": "Как называется анонимная функция в Swift?", "options": ["lambda", "closure", "block", "anon"], "correct": 1},
        {"q": "Что в Swift аналог интерфейса?", "options": ["protocol", "interface", "trait", "contract"], "correct": 0},
        {"q": "Оператор ?? используется для?", "options": ["сравнения", "значения по умолчанию при nil", "цикла", "приведения типов"], "correct": 1},
    ],
    "Go": [
        {"q": "Как вывести текст в консоль?", "options": ["print()", "fmt.Println()", "console.log()", "echo"], "correct": 1},
        {"q": "Как объявить переменную коротким способом?", "options": ["var x = 1", "x := 1", "let x = 1", "x = new(1)"], "correct": 1},
        {"q": "Как объявить функцию?", "options": ["def", "func", "fun", "function"], "correct": 1},
        {"q": "Какая функция — точка входа программы?", "options": ["func start()", "func main()", "func init()", "func run()"], "correct": 1},
        {"q": "Как запустить горутину?", "options": ["async fn()", "go fn()", "thread fn()", "spawn fn()"], "correct": 1},
        {"q": "Что используют для общения между горутинами?", "options": ["mutex only", "channel (chan)", "socket", "pipe"], "correct": 1},
        {"q": "Как называется динамический массив в Go?", "options": ["array", "slice", "list", "vector"], "correct": 1},
        {"q": "Что объявляется первой строкой файла?", "options": ["import", "package", "module", "namespace"], "correct": 1},
        {"q": "Как в Go принято обрабатывать ошибки?", "options": ["try/catch", "проверкой err != nil", "исключениями", "panic всегда"], "correct": 1},
        {"q": "Ключевое слово для описания поведения типа?", "options": ["interface", "protocol", "trait", "abstract"], "correct": 0},
    ],
    "Rust": [
        {"q": "Как вывести текст в консоль?", "options": ["print()", "println!()", "console.log()", "echo"], "correct": 1},
        {"q": "Переменные в Rust по умолчанию?", "options": ["изменяемые", "неизменяемые (нужен mut)", "глобальные", "константы всегда"], "correct": 1},
        {"q": "Как объявить функцию?", "options": ["def", "func", "fn", "function"], "correct": 2},
        {"q": "Какая функция — точка входа программы?", "options": ["fn start()", "fn main()", "fn init()", "fn run()"], "correct": 1},
        {"q": "Что управляет памятью в Rust без сборщика мусора?", "options": ["reference counting всегда", "система владения (ownership)", "ручной free()", "malloc/free вручную"], "correct": 1},
        {"q": "Для чего используется Option?", "options": ["для ошибок", "для возможного отсутствия значения", "для циклов", "для строк"], "correct": 1},
        {"q": "Для чего используется Result?", "options": ["для отсутствия значения", "для обработки ошибок", "для циклов", "для типов данных"], "correct": 1},
        {"q": "Что означает символ & перед переменной?", "options": ["умножение", "заимствование (borrow)", "адрес в куче", "макрос"], "correct": 1},
        {"q": "println! — это?", "options": ["функция", "макрос", "переменная", "тип"], "correct": 1},
        {"q": "Cargo в Rust — это?", "options": ["редактор кода", "менеджер пакетов и сборщик", "тип данных", "фреймворк для веба"], "correct": 1},
    ],
    "PHP": [
        {"q": "Как вывести текст?", "options": ["print_r только", "echo", "console.log", "System.out"], "correct": 1},
        {"q": "С какого символа начинается переменная?", "options": ["@", "$", "#", "&"], "correct": 1},
        {"q": "Как открывается PHP-код в файле?", "options": ["<script php>", "<?php", "<php>", "#!/php"], "correct": 1},
        {"q": "Как объявить массив?", "options": ["array() или []", "{}", "list()", "set()"], "correct": 0},
        {"q": "Как объявить функцию?", "options": ["def", "func", "function", "fn"], "correct": 2},
        {"q": "Какой оператор сравнивает и тип, и значение?", "options": ["==", "===", "=", "eq"], "correct": 1},
        {"q": "Как соединить две строки?", "options": ["+", ".", "&", "concat()"], "correct": 1},
        {"q": "Для чего нужны include/require?", "options": ["для циклов", "для подключения файлов", "для баз данных", "для комментариев"], "correct": 1},
        {"q": "Где хранятся данные из HTML-формы (POST)?", "options": ["$_GET", "$_POST", "$_FORM", "$_DATA"], "correct": 1},
        {"q": "PHP-код выполняется где?", "options": ["в браузере пользователя", "на сервере", "нигде, только компилируется", "в базе данных"], "correct": 1},
    ],
    "SQL": [
        {"q": "Какая команда выбирает данные из таблицы?", "options": ["GET", "SELECT", "FETCH", "PULL"], "correct": 1},
        {"q": "Какое ключевое слово задаёт условие выборки?", "options": ["IF", "WHERE", "WHEN", "FILTER"], "correct": 1},
        {"q": "Какое ключевое слово сортирует результат?", "options": ["SORT BY", "ORDER BY", "GROUP BY", "ARRANGE"], "correct": 1},
        {"q": "Какая команда добавляет новую запись?", "options": ["ADD INTO", "INSERT INTO", "CREATE ROW", "NEW INTO"], "correct": 1},
        {"q": "Какая команда изменяет существующую запись?", "options": ["CHANGE", "UPDATE", "MODIFY", "SET"], "correct": 1},
        {"q": "Какая команда удаляет запись?", "options": ["REMOVE", "DELETE", "DROP ROW", "CLEAR"], "correct": 1},
        {"q": "Что используют для объединения двух таблиц?", "options": ["MERGE", "JOIN", "UNION ALL всегда", "LINK"], "correct": 1},
        {"q": "Что группирует строки по значению столбца?", "options": ["ORDER BY", "GROUP BY", "SORT BY", "COMBINE BY"], "correct": 1},
        {"q": "Что возвращает только уникальные значения?", "options": ["UNIQUE", "DISTINCT", "ONLY", "SINGLE"], "correct": 1},
        {"q": "Какая команда создаёт новую таблицу?", "options": ["NEW TABLE", "CREATE TABLE", "MAKE TABLE", "ADD TABLE"], "correct": 1},
    ],
}

# ================= БАЗА ДАННЫХ =================
conn = sqlite3.connect('bot_database.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    role TEXT DEFAULT 'user',
    last_quiz_date TEXT
)
''')
conn.commit()

def get_user_status(user_id: int) -> str:
    if user_id == OWNER_ID:
        return f"👑 СТАТУС: ВЛАДЕЛЕЦ 👑\n\n[⁠]({CHANNEL_AVATAR_URL})"
    
    cursor.execute("SELECT role FROM users WHERE user_id = ?", (user_id,))
    res = cursor.fetchone()
    role = res[0] if res else 'user'
    
    if role == 'premium':
        return "Статус: Premium ⭐️"
    return "Статус: Обычный 👤"

def check_limit(user_id: int) -> bool:
    if user_id == OWNER_ID:
        return True
    
    cursor.execute("SELECT role, last_quiz_date FROM users WHERE user_id = ?", (user_id,))
    res = cursor.fetchone()
    if not res:
        return True
    
    role, last_date = res
    if role == 'premium':
        return True
    
    today = str(datetime.date.today())
    return last_date != today

def update_quiz_date(user_id: int):
    today = str(datetime.date.today())
    cursor.execute("""
        INSERT INTO users (user_id, last_quiz_date) VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET last_quiz_date = excluded.last_quiz_date
    """, (user_id, today))
    conn.commit()

# ================= ИИ ГЕНЕРАЦИЯ =================
async def generate_questions(language: str):
    prompt = f"""
    Сгенерируй 10 уникальных вопросов для проверки знаний по языку: {language}.
    Формат строго JSON array:
    [
      {{
        "q": "Текст вопроса",
        "options": ["A", "B", "C", "D"],
        "correct": 0
      }}
    ]
    """
    try:
        response = await asyncio.to_thread(
            model.generate_content, 
            prompt, 
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Ошибка Gemini: {e}")
        return None

# ================= ХЕНДЛЕРЫ =================
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    role = 'owner' if message.from_user.id == OWNER_ID else 'user'
    cursor.execute("INSERT OR IGNORE INTO users (user_id, role) VALUES (?, ?)", (message.from_user.id, role))
    conn.commit()
    
    status_text = get_user_status(message.from_user.id)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Открыть WebApp", web_app=WebAppInfo(url=WEBAPP_URL))],
        [InlineKeyboardButton(text="🌍 Выбрать язык (В боте)", callback_data="start_quiz")],
        [InlineKeyboardButton(text="⭐ Купить Premium", callback_data="buy_premium")]
    ])
    
    await message.answer(
        f"Привет! Добро пожаловать в бот изучения языков программирования.\n\n{status_text}", 
        reply_markup=kb, 
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "start_quiz")
async def start_quiz_callback(call: types.CallbackQuery):
    if not check_limit(call.from_user.id):
        await call.message.answer("❌ Дневной лимит исчерпан (1 тест в день).\n\nОформите **Premium**, чтобы учиться без ограничений!", parse_mode="Markdown")
        await call.answer()
        return

    languages = list(LESSON_BANK.keys())
    buttons = [[InlineKeyboardButton(text=lang, callback_data=f"lang_{lang}")] for lang in languages]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await call.message.edit_text("Выберите язык программирования:", reply_markup=kb)
    await call.answer()

@dp.callback_query(F.data.startswith("lang_"))
async def process_lang(call: types.CallbackQuery):
    selected_lang = call.data.split("_")[1]
    
    # Попытка получить 10 вопросов через Gemini
    await call.message.edit_text(f"⏳ Gemini генерирует 10 новых вопросов по **{selected_lang}**...", parse_mode="Markdown")
    questions = await generate_questions(selected_lang)
    
    # Резервный вариант из готового банка LESSON_BANK
    if not questions or len(questions) < 10:
        questions = LESSON_BANK.get(selected_lang, [])
        
    if not questions:
        await call.message.answer("Не удалось загрузить вопросы. Попробуйте еще раз.")
        return
        
    update_quiz_date(call.from_user.id)
    await call.message.answer(f"✅ Вопросы готовы! Вы выбрали язык {selected_lang}. Всего вопросов: {len(questions)}")

# Выдача премиума владельцем
@dp.message(Command("grant_premium"))
async def grant_premium(message: types.Message):
    if message.from_user.id != OWNER_ID:
        return
    try:
        target_id = int(message.text.split()[1])
        cursor.execute("UPDATE users SET role = 'premium' WHERE user_id = ?", (target_id,))
        conn.commit()
        await message.answer(f"Пользователю `{target_id}` успешно выдан Premium!", parse_mode="Markdown")
    except Exception:
        await message.answer("Использование: `/grant_premium <user_id>`", parse_mode="Markdown")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
