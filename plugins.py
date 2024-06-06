import asyncio
import logging
import time
import sqlite3
from datetime import datetime, timedelta
from telethon import TelegramClient, events
from telethon.tl import functions, types
from PIL import Image
import pytesseract
import io
import random
from collections import defaultdict  # Tambahkan ini

api_id = 8818391
api_hash = '7c53af69fba665f36e83fdc76b8631f1'
phone_number = '+628174716011'

# Konfigurasi logging untuk memantau proses
logging.basicConfig(level=logging.INFO)

# Nama session yang akan digunakan untuk menyimpan sesi login
session_name = 'bottele'

client = TelegramClient(session_name, api_id, api_hash)

# Global variables
stop_spamming = False
auto_reply = False
fake_typing_running = False
fake_playing_running = False
fake_typing_tasks = []
fake_playing_tasks = []
fer_active = False
monitor_active = False
autopr_active = False
reset_mode = False
message_count = {}
character_names = []
allowed_groups = []
original_profile = {}
afk_status = {
    'is_afk': False,
    'reason': None,
    'start_time': None
}

# Membaca daftar kata dari file
word_dict = defaultdict(list)
with open('words.txt', 'r') as file:
    for line in file:
        word = line.strip().lower()
        if word:
            word_dict[word[0]].append(word)

async def fake_typing(event):
    global fake_typing_running
    fake_typing_running = True
    while fake_typing_running:
        async with client.action(event.chat_id, 'typing'):
            await asyncio.sleep(2)

async def fake_playing(event):
    global fake_playing_running
    fake_playing_running = True
    while fake_playing_running:
        async with client.action(event.chat_id, 'game'):
            await asyncio.sleep(2)

# Function to fetch words from kbbi.db
def get_filtered_words():
    conn = sqlite3.connect('kbbi.db')
    cursor = conn.cursor()
    cursor.execute("SELECT kata FROM kbbi")  # Adjust table and column names as necessary
    all_words = cursor.fetchall()
    conn.close()

    # Filter words containing only alphabetic characters
    filtered_words = [word[0] for word in all_words if word[0].isalpha()]
    return filtered_words

# Generate random sentence
def generate_random_sentence(words):
    return " ".join(random.choices(words, k=5))

@client.on(events.NewMessage(pattern='%reset'))
async def reset(event):
    global reset_mode
    args = event.message.text.split()[1:]
    if len(args) != 1 or args[0] not in ('on', 'off'):
        await event.respond('Penggunaan: .reset on|off')
        return
    reset_mode = args[0] == 'on'
    await event.respond(f'Mode reset {"diaktifkan" if reset_mode else "dinonaktifkan"}.')

@client.on(events.NewMessage)
async def delete_message(event):
    global reset_mode
    if reset_mode:
        try:
            await client.delete_messages(event.chat_id, event.message.id)
        except Exception as e:
            print(f'Error deleting message: {e}')

@client.on(events.NewMessage(pattern='%delay'))
async def delayspam(event):
    args = event.message.text.split()[1:]
    if len(args) != 3:
        await event.respond('Penggunaan: %delay <text> <jumlah> <delay>')
        return
    text = args[0]
    jumlah = int(args[1])
    delay = float(args[2])

    words = get_filtered_words()
    if not words:
        await event.respond('Tidak ada kata yang valid dalam database.')
        return

    global stop_spamming
    stop_spamming = False
    for i in range(jumlah):
        if stop_spamming:
            break
        await event.respond(generate_random_sentence(words))
        await asyncio.sleep(delay)

@client.on(events.NewMessage(pattern='%psh'))
async def pshspam(event):
    global stop_spamming
    args = event.message.text.split()[1:]
    if len(args) < 2:
        await event.respond('Penggunaan: %psh <text> <delay>')
        return
    text = ' '.join(args[:-1])
    delay = float(args[-1])
    stop_spamming = False

    while not stop_spamming:
        await event.respond(text)
        await asyncio.sleep(delay)


@client.on(events.NewMessage(pattern='%diem'))
async def stopspam(event):
    global stop_spamming
    stop_spamming = True
    await event.respond('Spam dihentikan.')

@client.on(events.NewMessage(pattern='%autoreply'))
async def autoreply(event):
    global auto_reply
    args = event.message.text.split()[1:]
    if len(args) != 1 or args[0] not in ('on', 'off'):
        await event.respond('Penggunaan: .autoreply on|off')
        return
    auto_reply = args[0] == 'on'
    await event.respond(f'Auto-reply {"diaktifkan" if auto_reply else "dinonaktifkan"}.')

@client.on(events.NewMessage)
async def reply(event):
    if auto_reply and event.chat_id in allowed_groups:
        await event.respond("Saya sedang sibuk sekarang. Nanti saya akan balas pesan Anda.")

@client.on(events.NewMessage(pattern='%joinvc'))
async def joinvc(event):
    try:
        await client(functions.phone.JoinGroupCallRequest(
            call=event.chat_id,
            join_as=await client.get_me(),
        ))
        await event.respond('Bergabung ke obrolan suara.')
    except Exception as e:
        await event.respond(f'Gagal bergabung ke obrolan suara: {str(e)}')

@client.on(events.NewMessage(pattern='%ngetik'))
async def ngetik(event):
    fake_typing_tasks.append(asyncio.create_task(fake_typing(event)))
    await event.respond('avv')

@client.on(events.NewMessage(pattern='%berhenti'))
async def berhenti(event):
    global fake_typing_running
    fake_typing_running = False
    for task in fake_typing_tasks:
        task.cancel()
    fake_typing_tasks.clear()
    await event.respond('Avv')

@client.on(events.NewMessage(pattern='%main'))
async def main(event):
    fake_playing_tasks.append(asyncio.create_task(fake_playing(event)))
    await event.respond('avv')

@client.on(events.NewMessage(pattern='%fesd'))
async def f(event):
    global fake_playing_running
    fake_playing_running = False
    for task in fake_playing_tasks:
        task.cancel()
    fake_playing_tasks.clear()
    await event.respond('Avv')


@client.on(events.NewMessage(pattern='%purgeme'))
async def purgeme(event):
    me = await client.get_me()  # Mengambil informasi pengguna saat ini
    deleted_count = 0  # Menghitung jumlah pesan yang dihapus

    async for message in client.iter_messages(event.chat_id, from_user=me.id):  # Mengiterasi semua pesan dari pengguna saat ini
        await message.delete()  # Menghapus pesan
        deleted_count += 1  # Menambah jumlah pesan yang dihapus

    await event.respond(
        f'Semua pesan Anda di grup ini telah dihapus. Total pesan yang dihapus: {deleted_count}.')  # Memberi tahu bahwa semua pesan telah dihapus


@client.on(events.NewMessage(pattern='%clone'))
async def clone(event):
    if event.is_reply:
        reply_message = await event.get_reply_message()
        original_profile['first_name'] = (await client.get_me()).first_name
        original_profile['last_name'] = (await client.get_me()).last_name
        original_profile['about'] = (await client(functions.account.GetFullUserRequest(
            id='me'
        ))).about
        original_profile['photo'] = (await client.get_profile_photos('me'))[0]

        await client(functions.account.UpdateProfileRequest(
            first_name=reply_message.sender.first_name,
            last_name=reply_message.sender.last_name
        ))

        await client(functions.photos.UploadProfilePhotoRequest(
            file=await client.upload_file(reply_message.sender.photo)
        ))

        await client(functions.account.UpdateProfileRequest(
            about=await client(functions.account.GetFullUserRequest(
                id=reply_message.sender_id
            )).about
        ))

        await event.respond('Profil berhasil dikloning.')

@client.on(events.NewMessage(pattern='%restore'))
async def restore(event):
    if original_profile:
        await client(functions.account.UpdateProfileRequest(
            first_name=original_profile['first_name'],
            last_name=original_profile['last_name'],
            about=original_profile['about']
        ))
        await client(functions.photos.UploadProfilePhotoRequest(
            file=await client.upload_file(original_profile['photo'])
        ))
        await event.respond('Profil berhasil dikembalikan.')
    else:
        await event.respond('Tidak ada profil untuk dikembalikan.')

@client.on(events.NewMessage(pattern='%detect'))
async def detect_text(event):
    if event.is_reply and event.media:
        reply_message = await event.get_reply_message()
        image = await client.download_media(reply_message.media)
        image = Image.open(io.BytesIO(image))
        text = pytesseract.image_to_string(image)
        await event.respond(f'Teks terdeteksi: {text}')
    else:
        await event.respond('Balas pesan yang berisi gambar untuk mendeteksi teks.')

@client.on(events.NewMessage(pattern='%afk'))
async def afk(event):
    global afk_status
    args = event.message.text.split(maxsplit=1)
    reason = args[1] if len(args) > 1 else 'AFK'
    afk_status = {
        'is_afk': True,
        'reason': reason,
        'start_time': datetime.now()
    }
    await event.respond(f'Sekarang dalam mode AFK: {reason}')

@client.on(events.NewMessage(pattern='%back'))
async def back(event):
    global afk_status
    afk_status = {
        'is_afk': False,
        'reason': None,
        'start_time': None
    }
    await event.respond('Kembali dari mode AFK.')

@client.on(events.NewMessage)
async def handle_afk(event):
    global afk_status
    if afk_status['is_afk'] and event.is_private and not event.out:
        delta = datetime.now() - afk_status['start_time']
        minutes = delta.total_seconds() // 60
        await event.respond(f'Saya sedang AFK selama {minutes} menit.\nAlasan: {afk_status["reason"]}')

@client.on(events.NewMessage(pattern='%fer'))
async def activate_fer(event):
    global fer_active
    fer_active = not fer_active
    status = 'diaktifkan' if fer_active else 'dinonaktifkan'
    await event.respond(f'Fitur Fer {status}.')

@client.on(events.NewMessage(pattern='%purgeall'))
async def purgeall(event):
    async for message in client.iter_messages(event.chat_id):
        try:
            await client.delete_messages(event.chat_id, message.id)
        except Exception as e:
            print(f'Error deleting message: {e}')

@client.on(events.NewMessage)
async def fer_auto_reply(event):
    global fer_active
    if fer_active and event.is_private and not event.out:
        await event.respond('Pesan otomatis: Saya sedang sibuk sekarang.')

@client.on(events.NewMessage(pattern='%maxtor'))
async def maxtor(event):
    if event.is_reply:
        reply_message = await event.get_reply_message()
        if reply_message.sticker or reply_message.photo or reply_message.document.mime_type.startswith('image/'):
            await event.respond(reply_message)
        elif reply_message.text and any(char in reply_message.text for char in ('😀', '😁', '😂', '🤣', '😃', '😄', '😅', '😆', '😉', '😊', '😋', '😎', '😍', '😘', '😗', '😙', '😚', '🙂', '🤗', '🤩', '🤔', '🤨', '😐', '😑', '😶', '🙄', '😏', '😣', '😥', '😮', '🤐', '😯', '😪', '😫', '😴', '😌', '😛', '😜', '😝', '🤤', '😒', '😓', '😔', '😕', '🙃', '🤑', '😲', '☹️', '🙁', '😖', '😞', '😟', '😤', '😢', '😭', '😦', '😧', '😨', '😩', '🤯', '😬', '😰', '😱', '😳', '🤪', '😵', '😡', '😠', '🤬', '😷', '🤒', '🤕', '🤢', '🤮', '🤧', '😇', '🤠', '🤡', '🤥', '🤫', '🤭', '🧐', '🤓', '😈', '👿', '👹', '👺', '💀', '☠️', '👻', '👽', '👾', '🤖', '💩', '😺', '😸', '😹', '😻', '😼', '😽', '🙀', '😿', '😾')):
            await event.respond(reply_message.text)
        else:
            await event.respond('Balas pesan dengan stiker, foto, atau emoji.')
    else:
        await event.respond('Balas pesan dengan stiker, foto, atau emoji.')

@client.on(events.NewMessage(pattern='%help'))
async def help_command(event):
    help_text = """
**Berikut adalah daftar perintah yang tersedia:**

Berikut adalah daftar perintah yang tersedia:

1. `%reset on|off`: Mengaktifkan atau menonaktifkan mode reset untuk menghapus pesan yang masuk secara otomatis.
   *Contoh*: `%reset on`

2. `%delay <text> <jumlah> <delay>`: Mengirim kalimat random bahasa indonesia dengan waktu delay tertentu.
   *Contoh*: `%delay halo 5 2`

3. `%psh <text> <jumlah> <delay>`: Mengirim pesan berulang kali dengan delay tertentu.
   *Contoh*: `%psh halo 5 2`

4. `%diem`: Menghentikan semua spam yang sedang berjalan.
   *Contoh*: `%diem`

5. `%autoreply on|off`: Mengaktifkan atau menonaktifkan fitur auto-reply.
   *Contoh*: `%autoreply on` & `%autoreply off`

6. `%joinvc`: Bergabung ke obrolan suara dalam grup.
   *Contoh*: `%joinvc`

7. `%ngetik`: Memulai aksi mengetik palsu.
   *Contoh*: `%ngetik`

8. `%berhenti`: Menghentikan aksi mengetik palsu.
   *Contoh*: `%berhenti`

9. `%main`: Memulai aksi bermain game palsu.
   *Contoh*: `%main`

10. `%fesd`: Menghentikan aksi bermain game palsu.
    *Contoh*: `%fesd`

11. `%purgeme`: Menghapus semua pesan Anda dalam chat.
    *Contoh*: `%purgeme`

12. `%clone`: Mengkloning profil pengguna yang dibalas.
    *Contoh*: `%clone`

13. `%restore`: Mengembalikan profil asli.
    *Contoh*: `%restore`

14. `%detect`: Mendeteksi teks dari gambar yang dibalas.
    *Contoh*: `%detect`

15. `%afk <reason>`: Mengaktifkan mode AFK dengan alasan.
    *Contoh*: `%afk Sibuk`

16. `%back`: Menonaktifkan mode AFK.
    *Contoh*: `%back`

17. `%fer`: Mengaktifkan atau menonaktifkan fitur Fer.
    *Contoh*: `%fer`

18. `%maxtor`: Membalas pesan dengan stiker, foto, atau emoji.
    *Contoh*: `%maxtor`

19. `%purgeall`: Untuk menghapus seluruh pesan tanpa terkecuali.
    *Contoh*: `%purgeall`
    """
    await event.respond(help_text)

# async def main():
#     await client.start(phone_number)
#     print("Client Created")
#     await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(client.send_message(-1002188347981, '`Bot Sudah Aktif🔥🔥`'))
    client.run_until_disconnected()
