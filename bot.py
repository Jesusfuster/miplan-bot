import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

# ─── TAREAS (edita esto desde Claude) ───────────────────────────────────────
TASKS = [
    {"id": 1, "text": "Levantarte a las 9:15", "tag": "RUTINA", "done": False},
    {"id": 2, "text": "Apuntarte al gym con tu amigo", "tag": "MAÑANA", "done": False},
    {"id": 3, "text": "Lavar el coche (exterior)", "tag": "MAÑANA", "done": False},
    {"id": 4, "text": "Tocar a tu compi de trabajo", "tag": "ESTA SEMANA", "done": False},
    {"id": 5, "text": "Responder a la jefa", "tag": "HECHO ✅", "done": True},
    {"id": 6, "text": "Recoger Avesitrán", "tag": "HECHO ✅", "done": True},
    {"id": 7, "text": "Lavar el coche (interior)", "tag": "HECHO ✅", "done": True},
]

PENDIENTES = [
    "Apuntarse al gym con amigo",
    "Tocar a compi de trabajo",
    "Limpiar casa del padre antes de que llegue (fecha TBD)",
    "Colgar ventilador en el cuarto",
]

RUTINA = [
    ("9:15", "Levantarse. Sin snooze."),
    ("—", "Mañana: por definir"),
    ("—", "Tarde: por definir"),
    ("~2:00", "Cama. Máximo las 2."),
]

# ─── HELPERS ────────────────────────────────────────────────────────────────

def is_admin(update: Update) -> bool:
    return update.effective_user.id == ADMIN_ID

def tasks_keyboard():
    keyboard = []
    for t in TASKS:
        check = "✅" if t["done"] else "⬜"
        keyboard.append([InlineKeyboardButton(f"{check} {t['text']}", callback_data=f"task_{t['id']}")])
    return InlineKeyboardMarkup(keyboard)

# ─── COMMANDS ───────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    h = datetime.now().hour
    if h < 14:
        greeting = "Buenos días"
    elif h < 21:
        greeting = "Buenas tardes"
    else:
        greeting = "Buenas noches"

    text = (
        f"*{greeting}, Jesús* 👋\n\n"
        "El primer movimiento es el más importante.\n\n"
        "Comandos disponibles:\n"
        "📋 /hoy — Tareas del día\n"
        "🔄 /rutina — Tu rutina objetivo\n"
        "📌 /pendientes — Todos los pendientes\n"
        "💬 /claude — Abrir sesión de coaching\n"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def hoy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pending = [t for t in TASKS if not t["done"]]
    done = [t for t in TASKS if t["done"]]
    text = f"*Tareas de hoy* — {len(done)}/{len(TASKS)} completadas\n\n"
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=tasks_keyboard())

async def rutina(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "*Tu rutina objetivo* 🔄\n\n"
    for time, desc in RUTINA:
        text += f"`{time}` — {desc}\n"
    text += "\n_Regla de oro: no pienses, actúa. El cerebro negocia, el cuerpo ejecuta._"
    await update.message.reply_text(text, parse_mode="Markdown")

async def pendientes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "*Pendientes generales* 📌\n\n"
    for p in PENDIENTES:
        text += f"• {p}\n"
    await update.message.reply_text(text, parse_mode="Markdown")

async def claude(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("💬 Abrir Claude", url="https://claude.ai")]]
    await update.message.reply_text(
        "*Sesión de coaching* 💬\n\nAbre Claude para continuar con tu plan de vida.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("task_"):
        task_id = int(data.split("_")[1])
        for t in TASKS:
            if t["id"] == task_id:
                t["done"] = not t["done"]
                break
        done = sum(1 for t in TASKS if t["done"])
        await query.edit_message_text(
            f"*Tareas de hoy* — {done}/{len(TASKS)} completadas\n",
            parse_mode="Markdown",
            reply_markup=tasks_keyboard()
        )

# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("hoy", hoy))
    app.add_handler(CommandHandler("rutina", rutina))
    app.add_handler(CommandHandler("pendientes", pendientes))
    app.add_handler(CommandHandler("claude", claude))
    app.add_handler(CallbackQueryHandler(button_handler))
    logger.info("Bot iniciado...")
    app.run_polling()

if __name__ == "__main__":
    main()
