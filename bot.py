from telegram import Update
from telegram.ext import (ApplicationBuilder, CallbackQueryHandler,
                          ContextTypes, CommandHandler, MessageHandler, filters)

from gpt import ChatGptService
from util import (load_message, send_text, send_image, show_main_menu,
                  load_prompt, send_text_buttons, Dialog, send_html)

import credentials
import logging

logging.basicConfig(level=logging.INFO)

dialog = Dialog()
dialog.mode = "default"

dialog.score = 0


def reset_quiz():
    dialog.score = 0


topic_prompts = {
    "quiz_prog_btn": "quiz_python",
    "quiz_math_btn": "quiz_math",
    "quiz_biology_btn": "quiz_biology",
}


character_prompts = {
    "cobain_btn": "talk_cobain",
    "hawking_btn": "talk_hawking",
    "nietzsche_btn": "talk_nietzsche",
    "queen_btn": "talk_queen",
    "tolkien_btn": "talk_tolkien"
}


languages = {
    "english": "Англійська",
    "ukrainian": "Українська",
    "french": "Французька",
    "german": "Німецька",
    "spanish": "Іспанська",
}


content_quiz = ""
result_quiz = ""

translate_language = ""

text_education = ""
text_experience = ""
text_skills = ""


async def handle_condition_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if dialog.mode == "gpt":
        await handle_message_chat_gpt(update, context)
    elif dialog.mode in character_prompts:
        await handle_message_talk(update, context)
    elif dialog.mode in topic_prompts:
        await handle_quiz_answer(update, context)
    elif dialog.mode in languages:
        await handle_text_for_translation(update, context)
    elif dialog.mode == "resume_education":
        await handle_resume_education(update, context)
    elif dialog.mode == "resume_experience":
        await handle_resume_experience(update, context)
    elif dialog.mode == "resume_skills":
        await handle_resume_skills(update, context)
    elif dialog.mode == "parrot":
        await parrot_condition(update, context)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Функція start викликана")
    dialog.mode = "default"
    text = load_message("main")
    await send_image(update, context, "main")
    await send_html(update, context, text)
    await show_main_menu(update, context, {
        'start': 'Головне меню',
        'random': 'Дізнатися випадковий цікавий факт 🧠',
        'gpt': 'Задати питання чату GPT 🤖',
        'talk': 'Поговорити з відомою особистістю 👤',
        'quiz': 'Взяти участь у квізі ❓',
        'translate': 'Перекласти текст 🔄',
        'resume_assistance': 'Створити резюме 📄',
        'parrot': 'Повторити повідомлення 🦜'
    })


async def random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Функція random викликана")
    dialog.mode = "random"
    text = load_message("random")
    await send_image(update, context, "random")
    await send_text(update, context, text)
    prompt = load_prompt("random")
    content = await chat_gpt.send_question(prompt, "Дай цікавий факт")
    await send_text_buttons(update, context, content, {
        "more_btn": "Хочу ще факт",
        "back_btn": "Закінчити"
    })


async def handle_button_random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    logging.info(f"Отримано callback: {query.data}")

    await query.answer()

    if query.data == "more_btn":
        await random(update, context)
    elif query.data == "back_btn":
        await start(update, context)
    else:
        logging.warning(f"Невідомий callback: {query.data}")


async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Функція gpt викликана")
    dialog.mode = "gpt"
    text = load_message("gpt")
    await send_image(update, context, "gpt")
    await send_text(update, context, text)
    prompt = load_prompt("gpt")
    chat_gpt.set_prompt(prompt)


async def handle_message_chat_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    logging.info(f"Отримано повідомлення: {text}")

    await chat_gpt.add_message(text)
    logging.info("Повідомлення додано до chat_gpt")

    answer = await chat_gpt.send_message_list()
    logging.info(f"Отримано відповідь від chat_gpt: {answer}")

    await send_text(update, context, answer)
    logging.info("Відповідь відправлено користувачу")


async def talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Функція talk викликана")
    dialog.mode = "talk"
    text = load_message("talk")
    await send_image(update, context, "talk")
    await send_text_buttons(update, context, text, {
        "cobain_btn": "Курт Кобейн",
        "hawking_btn": "Стівен Гокінг",
        "nietzsche_btn": "Фрідріх Ніцше",
        "queen_btn": "Єлизавета II",
        "tolkien_btn": "Джон Толкін",
        "end_btn_talk": "Закінчити"
    })


async def handle_talk_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    logging.info(f"Отримано callback: {query.data}")
    await query.answer()

    if query.data == "end_btn_talk":
        await start(update, context)
        return
    elif query.data in character_prompts:
        character_name = {
            "cobain_btn": "Курт Кобейн",
            "hawking_btn": "Стівен Гокінг",
            "nietzsche_btn": "Фрідріх Ніцше",
            "queen_btn": "Єлизавета II",
            "tolkien_btn": "Джон Толкін"
        }[query.data]

        prompt = load_prompt(character_prompts[query.data])
        chat_gpt.set_prompt(prompt)
        dialog.mode = query.data
        await send_text(update, context, f"Привіт, я {character_name}. Давай поспілкуємося!")
    else:
        logging.warning(f"Невідомий callback: {query.data}")


async def handle_message_talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    logging.info(f"Отримано повідомлення: {text}")

    await chat_gpt.add_message(text)
    logging.info("Повідомлення додано до chat_gpt")

    answer = await chat_gpt.send_message_list()
    logging.info(f"Отримано відповідь від chat_gpt: {answer}")

    await send_text_buttons(update, context, answer, {"end_btn_talk": "Закінчити"})
    logging.info("Відповідь відправлено користувачу")


async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Функція quiz викликана")
    dialog.mode = "quiz"
    reset_quiz()
    text = load_message("quiz")
    await send_image(update, context, "quiz")
    await send_text_buttons(update, context, text, {
        "quiz_prog_btn": "Програмування мовою Python",
        "quiz_math_btn": "Математика",
        "quiz_biology_btn": "Біологія",
        "end_btn_quiz": "Закінчити квіз"
    })


async def handle_quiz_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    logging.info(f"Отримано callback: {query.data}")
    await query.answer()

    if query.data == "end_btn_quiz":
        await start(update, context)
        return

    if query.data in topic_prompts:
        global content_quiz
        dialog.mode = query.data
        prompt = load_prompt(topic_prompts[query.data])
        chat_gpt.set_prompt(prompt)
        content_quiz = await chat_gpt.send_question(prompt, "Дай питання квізу, відповідь має бути словесною, без чисел.")
        await send_text(update, context, f"{content_quiz}\n\nВідповідайте на питання:")
    else:
        logging.warning(f"Невідомий callback: {query.data}")


async def handle_quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    logging.info(f"Отримано повідомлення: {text}")

    global content_quiz
    global result_quiz
    await chat_gpt.add_message(f"Питання таке: {content_quiz}\n Моя відповідь на це питання така: {text.capitalize()}.\n Якщо моя відповідь правильна або близька до правильної відповіді на це питання, то дай напиши: 'true', інакше: напиши правильну відповідь.\n Дай відповідь одним словом у такому форматі, якщо правильно: 'true' або якщо неправильна відповідь: 'правидьна відповідь'.")
    logging.info("Повідомлення додано до chat_gpt")

    result_quiz = await chat_gpt.send_message_list()
    logging.info(f"Отримано відповідь від chat_gpt: {result_quiz}")

    if "true" in result_quiz.lower():
        dialog.score += 1
        await send_text(update, context, "Ваша відповідь - правильна. Вам +1 бал")
    else:
        await send_text(update, context, f"Не правильно! Правильна відповідь: {result_quiz}")

    await send_text_buttons(update, context, f"\n\nПоточний рахунок: {dialog.score}", {
        "quiz_more_btn": "Наступне питання",
        "quiz_change_btn": "Змінити тему",
        "end_btn_quiz": "Закінчити квіз"
    })
    logging.info("Відповідь відправлено користувачу")


async def handle_quiz_navigation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    logging.info(f"Отримано callback: {query.data}")
    await query.answer()

    global result_quiz
    global content_quiz
    if query.data == "quiz_more_btn":
        result_quiz = ""
        content_quiz = ""
        prompt = load_prompt(topic_prompts[dialog.mode])
        content_quiz = await chat_gpt.send_question(prompt, "Дай питання квізу, відповідь має бути словесною, без чисел.")
        await send_text(update, context, f"{content_quiz}\n\nВідповідайте на питання:")

    elif query.data == "quiz_change_btn":
        await send_text(update, context, "Оберіть наступну тему:")
        text = load_message("quiz")
        await send_text_buttons(update, context, text, {
            "quiz_prog_btn": "Програмування мовою Python",
            "quiz_math_btn": "Математика",
            "quiz_biology_btn": "Біологія",
            "end_btn_quiz": "Закінчити квіз"
        })
    elif query.data == "end_btn_quiz":
        await send_text(update, context, f"Дякую за участь! Ваш фінальний рахунок: {dialog.score}")
        await start(update, context)


async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Функція translation викликана")
    dialog.mode = "translation"
    text = "Будь ласка, оберіть мову, на яку потрібно перекласти текст."
    await send_text_buttons(update, context, text, {
        "english": "Англійська",
        "ukrainian": "Українська",
        "french": "Французька",
        "german": "Німецька",
        "spanish": "Іспанська",
        "end_btn_translation": "Закінчити"
    })


async def handle_language_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    logging.info(f"Отримано callback: {query.data}")
    await query.answer()

    if query.data == "end_btn_translation":
        await start(update, context)
        return

    if query.data in languages:
        global translate_language
        translate_language = languages[query.data]
        dialog.mode = query.data
        text = f"Ви обрали {translate_language}.Тепер надішліть текст, який потрібно перекласти."
        await send_text(update, context, text)
        logging.info("Відповідь відправлено користувачу")
    else:
        logging.warning(f"Невідомий callback: {query.data}")


async def handle_text_for_translation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    global translate_language

    text_to_translate = update.message.text
    logging.info(f"Отримано повідомлення: {text_to_translate}")

    await chat_gpt.add_message(f"Переклади даний текст: {text_to_translate} на {translate_language} мову")
    logging.info("Повідомлення додано до chat_gpt")

    translated_text = await chat_gpt.send_message_list()
    logging.info(f"Отримано відповідь від chat_gpt: {translated_text}")

    await send_text_buttons(update, context, f"Переклад:\n{translated_text}", {
        "change_language_btn": "Змінити мову",
        "end_btn_translation": "Закінчити"
    })
    logging.info("Переклад відправлено користувачу")


async def handle_translation_navigation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    logging.info(f"Отримано callback: {query.data}")
    await query.answer()

    if query.data == "change_language_btn":
        await translate(update, context)
    elif query.data == "end_btn_translation":
        await start(update, context)


async def resume_assistance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Функція resume_assistance викликана")
    dialog.mode = "resume"
    text = "Будь ласка, введіть свою інформацію для резюме."
    await send_text_buttons(update, context, text, {
        "resume_start_btn": "Почати",
        "resume_finished_btn": "Закінчити"
    })


async def handle_resume_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    logging.info(f"Отримано callback: {query.data}")
    await query.answer()

    if query.data == "resume_finished_btn":
        await start(update, context)

    if query.data == "resume_start_btn":
        await send_text(update, context, "Вкажіть вашу освіту:")
        logging.info("Відповідь відправлено користувачу")
        dialog.mode = "resume_education"
    else:
        logging.warning(f"Невідомий callback: {query.data}")


async def handle_resume_education(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global text_education
    text_education = update.message.text
    logging.info(f"Отримано повідомлення: {text_education}")
    await send_text(update, context, "Опишіть ваш досвід роботи:")
    dialog.mode = "resume_experience"


async def handle_resume_experience(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global text_experience
    text_experience = update.message.text
    logging.info(f"Отримано повідомлення: {text_experience}")
    await send_text(update, context, "Вкажіть ваші навички:")
    dialog.mode = "resume_skills"


async def handle_resume_skills(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global text_skills
    text_skills = update.message.text
    logging.info(f"Отримано повідомлення: {text_skills}")
    await create_resume_gpt(update, context)


async def create_resume_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global text_education
    global text_experience
    global text_skills

    await chat_gpt.add_message(f"Створи цікаве резюме.\n В тебе є такі дані:\n Освіта:{text_education}\n Досвід роботи:{text_experience}\n Навички:{text_skills}")
    logging.info("Повідомлення додано до chat_gpt")

    resume_text = await chat_gpt.send_message_list()
    logging.info(f"Отримано відповідь від chat_gpt: {resume_text}")

    await send_text_buttons(update, context, f"Ваше резюме:\n {resume_text}", {
        "resume_edit": "Переробити резюме",
        "end_btn_resume": "Закінчити"
    })
    logging.info("Резюме відправлено користувачу")


async def handle_resume_navigation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    logging.info(f"Отримано callback: {query.data}")
    await query.answer()

    if query.data == "resume_edit":
        await resume_assistance(update, context)
    elif query.data == "end_btn_resume":
        await send_text(update, context, "Ваше резюме збережено. Дякуємо!")
        await start(update, context)


async def parrot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Функція, як і папугай повторює за користувачем, поки він не вийде із стану папуги
    """
    print("Функція parrot викликана")
    dialog.mode = "parrot"
    text = "Ви війшли в стан папуги 🦜. Ця функція, як і папугай буде повторювати за вами, поки ви не вийдете із стану папуги."
    await send_text_buttons(update, context, text, {
        "finish_condition_parrot": "Вийти із стану папуги ❌🦜"
    })


async def parrot_condition(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    logging.info(f"Отримано повідомлення: {text}")

    await send_text_buttons(update, context, f"🦜🔊: {text}", {
        "finish_condition_parrot": "Вийти із стану папуги ❌🦜"
    })
    logging.info("Папуга повторив")


async def handle_btn_parrot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    logging.info(f"Отримано callback: {query.data}")
    await query.answer()

    if query.data == "finish_condition_parrot":
        await send_text(update, context, "Ви вийшли із стану папуги ❌🦜")
        await start(update, context)
    else:
        logging.warning(f"Невідомий callback: {query.data}")


chat_gpt = ChatGptService(credentials.ChatGPT_TOKEN)
app = ApplicationBuilder().token(credentials.BOT_TOKEN).build()


app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('random', random))
app.add_handler(CommandHandler("gpt", gpt))
app.add_handler(CommandHandler("talk", talk))
app.add_handler(CommandHandler("quiz", quiz))
app.add_handler(CommandHandler("translate", translate))
app.add_handler(CommandHandler("resume_assistance", resume_assistance))
app.add_handler(CommandHandler("parrot", parrot))

app.add_handler(CallbackQueryHandler(handle_button_random, pattern="^(more_btn|back_btn)$"))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_condition_dialog))

app.add_handler(CallbackQueryHandler(
    handle_talk_choice,
    pattern="^(cobain_btn|hawking_btn|nietzsche_btn|queen_btn|tolkien_btn|end_btn_talk)$"))

app.add_handler(CallbackQueryHandler(handle_quiz_navigation, pattern='^(quiz_more_btn|quiz_change_btn|end_btn_quiz)$'))
app.add_handler(CallbackQueryHandler(handle_quiz_choice, pattern='^quiz_.*'))

app.add_handler(CallbackQueryHandler(handle_translation_navigation,
                                     pattern='^(change_language_btn|end_btn_translation)$'))
app.add_handler(CallbackQueryHandler(handle_language_choice,
                                     pattern='^(english|ukrainian|french|german|spanish|end_btn_translation)$'))

app.add_handler(CallbackQueryHandler(handle_resume_navigation, pattern="^(resume_edit|end_btn_resume)$"))
app.add_handler(CallbackQueryHandler(handle_resume_button, pattern="^(resume_start_btn|resume_finished_btn)$"))

app.add_handler(CallbackQueryHandler(handle_btn_parrot, pattern="^finish_condition_parrot$"))

app.run_polling()
