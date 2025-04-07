from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, CallbackContext
import json
import os
import asyncio 
import re
import unicodedata

# bot token is scraped off bc hey, that's my bot
TOKEN = ""

DATA_FILE = "C:\\Users\\Attilio\\Desktop\\alphabetic_bot\\group_trigger_count.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            print("data found and loaded!")
            return json.load(f)
    else: 
        with open(DATA_FILE, "w") as f:
            print("No data found. Creating new data file")
            json.dump({}, f)
        return {}

def save_data(data):
    print("saving data...")
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
        print("YES data is saved")
    except Exception as e:
        print("ERROR saving data: ", e)

# core function: checking for the alphabetical order of the phrase
# after some basic pre-processing of the message
def is_alphabetical(text):
    words = clean_message(text)

    if len(words) < 4:
        return False
    else:
        # making it into a set eliminates duplicate words, then sorting it back into a list to compare
        return words == sorted(list(set(sorted(words, key=str.lower))))

def clean_message(text):
    # regex that filters out anything that's not a letter
    cleaned = re.sub(r'[^a-zA-ZÀ-ÖØ-öø-ÿ\s]', '', text)
    words = cleaned.split()

    # making accent letters into normal letters: è -> e
    # words starting with accent letters are now treated as starting with "base" letters 
    words = [''.join(c for c in unicodedata.normalize('NFKD', w.lower()) if not unicodedata.combining(c)) for w in words]
    return words

# user command handler: checks the longest alphabetical phrase detected in the group it's called 
async def check_longest(update:Update, context:CallbackContext) -> None:
    print("longest...")
    chat_id = str(update.message.chat.id)
    if "longest" in context.bot_data:
        maxlen = context.bot_data["longest"][str(chat_id)]
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Lunghezza massima di una frase riconosciuta in questo gruppo: {maxlen}")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Non sono ancora state trovate frasi in ordine alfabetico in questo gruppo.")
    
    #deletes the command message in the group
    try:
        chat_id = update.message.chat_id
        message_id = update.message.message_id
        await context.bot.delete_message(chat_id, message_id)
    except Exception as e:
        print(f"Errore nell'eliminazione del messaggio: {e}")

# core function: when there's a new text message, it checks for alphabetical order of the words,
# registers the hit and notifies the group
async def check_message(update: Update, context: CallbackContext) -> None:
    if update.message is None:
        return

    chat_id = update.message.chat.id
    if update.message.chat and update.message.chat.type in ["group", "supergroup"]:
        text = update.message.text
        words = clean_message(text)
        if is_alphabetical(text):

            # Ensure the counter dict exists
            if "group_trigger_count" not in context.bot_data:
                context.bot_data["group_trigger_count"] = {}
            
            #increments the hit counter for the group it's been detected
            context.bot_data["group_trigger_count"][str(chat_id)] = (
                context.bot_data["group_trigger_count"].get(str(chat_id), 0) + 1
            )
            flag = False
            # checks for longest and updates if so, initializing if it's not there yet
            if "longest" not in context.bot_data:
                context.bot_data["longest"] = {}
                if str(chat_id) not in context.bot_data["longest"]:
                    context.bot_data["longest"][str(chat_id)] = 3

            if context.bot_data["longest"][str(chat_id)] < len(words):
                context.bot_data["longest"][str(chat_id)] = len(words)
                flag = True
            
            #save_data({"group_trigger_count":context.bot_data["group_trigger_count"]})
            save_data(context.bot_data)
            
            await update.message.reply_text(f"Frase in ordine alfabetico.", parse_mode="Markdown")
            if flag:
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Nuovo record di lunghezza!")
                flag = False

# user command handler: checks the trigger count for the group it's been called
async def check_trigger_count(update: Update, context: CallbackContext) -> None:
    print("counting...")
    chat_id = str(update.message.chat.id)
    
    if "group_trigger_count" in context.bot_data:
        count =context.bot_data["group_trigger_count"].get(str(chat_id), 0)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Totale frasi in ordine alfabetico riconosciute in questo gruppo: {count}")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Non sono ancora state trovate frasi in ordine alfabetico in questo gruppo.")
    
    try:
        chat_id = update.message.chat_id
        message_id = update.message.message_id
        await context.bot.delete_message(chat_id, message_id)
    except Exception as e:
        print(f"Failed to delete message: {e}")

# userc command handler: basically a debug function to print the bot data to terminal, via telegram
async def print_bot(update:Update, context:CallbackContext):
    #bot_data = load_data()
    print(context.bot_data)

# EASTER EGG
async def help(update:Update, context:CallbackContext):
    creuza="Umbre de muri, muri de mainé\nDunde ne vegnì, duve l'è ch'ané\nDa 'n scitu duve a l'ûn-a se mustra nûa\nE a neutte a n'à puntou u cutellu ä gua\nE a muntä l'àse gh'è restou Diu\nU Diàu l'è in çë e u s'è gh'è faetu u nìu\nNe sciurtìmmu da u mä pe sciugà e osse da u Dria\nA funtan-a d'i cumbi 'nta cä de pria\n\nE 'nt'a cä de pria chi ghe saià\nInt'à cä du Dria che u nu l'è mainà\nGente de Lûgan facce da mandillä\nQui che du luassu preferiscian l'ä\nFigge de famiggia udù de bun\nChe ti peu ammiàle senza u gundun\n\nE a 'ste panse veue cose ghe daià\nCose da beive, cose da mangiä\nFrittûa de pigneu giancu de Purtufin\nÇervelle de bae 'nt'u meximu vin\nLasagne da fiddià ai quattru tucchi\nPaciûgu in aegruduse de lévre de cuppi\n\nE 'nt'a barca du vin ghe naveghiemu 'nsc'i scheuggi\nEmigranti du rìe cu'i cioi 'nt'i euggi\nFinch'ou matin crescià da puéilu rechéugge\nFrè di ganeuffeni e d'è figge\nBacan d'a corda marsa d'aegua e de sä\nChe a ne liga e a ne porta 'nte 'na crêuza de mä"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=creuza)

def main():
    print("Bot started. Loading data...")
    bot_data = load_data()
    print(bot_data)

    app = Application.builder().token(TOKEN).build()
    app.bot_data["group_trigger_count"] = bot_data.get("group_trigger_count",{})
    app.bot_data["longest"] = bot_data.get("longest",{})
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_message))
    app.add_handler(CommandHandler("count", check_trigger_count))
    app.add_handler(CommandHandler("print", print_bot))
    app.add_handler(CommandHandler("longest", check_longest))
    app.add_handler(CommandHandler("help", help))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
