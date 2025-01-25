from telethon import TelegramClient, events
import sqlite3
import re
import asyncio

# Konfigurasi Telegram API
api_id = 'your_api_id'
api_hash = 'your_api_hash'
phone_number = 'your_phone_number'

db_path = r'C:\Users\Admin\Downloads\Telegram Desktop\kbbi.db'

# Fungsi untuk menghubungkan ke database
def connect_db():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        return conn, cursor
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None, None

# Fungsi untuk mendapatkan dan mengurutkan kata berdasarkan huruf awal dan panjang karakter
def get_sorted_words(cursor, start_letter, length):
    try:
        query = f"""
        SELECT kata
        FROM kbbi
        WHERE kata LIKE '{start_letter}%' AND LENGTH(kata) = {length}
        ORDER BY kata;
        """
        cursor.execute(query)
        results = cursor.fetchall()
        return [result[0] for result in results]
    except sqlite3.Error as e:
        print(f"Error executing query: {e}")
        return []

# Fungsi untuk mendapatkan frasa dua kata yang dimulai dengan huruf tertentu
def get_two_word_phrases(cursor, start_letter):
    try:
        query = f"""
        SELECT kata
        FROM kbbi
        WHERE kata LIKE '{start_letter}%'
        ORDER BY kata;
        """
        cursor.execute(query)
        results = cursor.fetchall()
        return [
            result[0] for result in results
            if len(re.findall(r'\b\w+\b', result[0])) == 2 and re.match(r"^[A-Za-z\s]+$", result[0])
        ]
    except sqlite3.Error as e:
        print(f"Error executing query: {e}")
        return []

# Fungsi untuk mendapatkan kata berdasarkan prefix
def get_words_by_prefix(cursor, prefix):
    try:
        query = f"""
        SELECT kata
        FROM kbbi
        WHERE kata LIKE '{prefix}%'
        ORDER BY kata;
        """
        cursor.execute(query)
        results = cursor.fetchall()
        return [result[0] for result in results]
    except sqlite3.Error as e:
        print(f"Error executing query: {e}")
        return []

# Memulai Telegram Client
client = TelegramClient('session_name', api_id, api_hash)

@client.on(events.NewMessage(pattern='/huruf (.+) (\d+)'))
async def huruf_handler(event):
    parts = event.pattern_match.groups()
    start_letter, length = parts[0], int(parts[1])
    conn, cursor = connect_db()
    if cursor:
        words = get_sorted_words(cursor, start_letter, length)
        if words:
            response = f"Kata-kata yang dimulai dengan huruf '{start_letter}' dan panjang {length} karakter:\n" + "\n".join(words)
        else:
            response = f"Tidak ada kata yang ditemukan dengan huruf awal '{start_letter}' dan panjang {length} karakter."
        await event.respond(response)
        conn.close()

@client.on(events.NewMessage(pattern='/duakata (.+)'))
async def duakata_handler(event):
    start_letter = event.pattern_match.group(1)
    conn, cursor = connect_db()
    if cursor:
        phrases = get_two_word_phrases(cursor, start_letter)
        if phrases:
            response = f"Frasa dua kata yang dimulai dengan huruf '{start_letter}':\n" + "\n".join(phrases)
        else:
            response = f"Tidak ada frasa dua kata yang ditemukan dengan huruf awal '{start_letter}'."
        await event.respond(response)
        conn.close()

@client.on(events.NewMessage(pattern='/cari (.+)'))
async def cari_handler(event):
    prefix = event.pattern_match.group(1)
    conn, cursor = connect_db()
    if cursor:
        words = get_words_by_prefix(cursor, prefix)
        if words:
            response = f"Kata-kata yang diawali dengan prefix '{prefix}':\n" + "\n".join(words)
        else:
            response = f"Tidak ada kata yang ditemukan dengan prefix '{prefix}'."
        await event.respond(response)
        conn.close()

@client.on(events.NewMessage(pattern='/help'))
async def help_handler(event):
    help_message = (
        "Daftar perintah:\n"
        "/huruf <awalan huruf> <jumlah huruf> - Menampilkan kata berdasarkan awalan dan panjang karakter\n"
        "/duakata <huruf> - Menampilkan frasa dua kata yang dimulai dengan huruf tertentu\n"
        "/cari <prefix> - Menampilkan kata-kata berdasarkan prefix\n"
        "/help - Menampilkan pesan bantuan"
    )
    await event.respond(help_message)

client.start(phone_number)
print("Bot is running...")
client.run_until_disconnected()
