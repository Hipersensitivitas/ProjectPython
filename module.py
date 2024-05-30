import asyncio
import random
from telethon import TelegramClient, events, functions

api_id = 8818391
api_hash = '7c53af69fba665f36e83fdc76b8631f1'
phone_number = '+628174716011'

client = TelegramClient('new_session_name', api_id, api_hash)

stop_spamming = False
auto_reply = False
fake_typing_tasks = []
fake_playing_tasks = []
original_profile = {}
fake_typing_running = False
fake_playing_running = False

indonesian_words = [
    "saya", "kamu", "dia", "mereka", "kita", "ingin", "makan", "minum",
    "bermain", "belajar", "bekerja", "berjalan", "tidur", "bangun",
    "rumah", "sekolah", "kantor", "taman", "makan", "minuman",
    "senang", "sedih", "marah", "lelah", "bahagia"
]

def generate_random_sentence(word_count=5):
    words = random.choices(indonesian_words, k=word_count)
    return ' '.join(words).capitalize() + '.'

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
        async with client.action(event.chat_id, 'playing'):
            await asyncio.sleep(2)

@client.on(events.NewMessage(pattern='.help'))
async def help(event):
    help_message = (
        "**Daftar Perintah:**\n\n"
        "**.help**\n"
        "Menampilkan pesan bantuan\n\n"
        "**.delayspam <text> <jumlah> <delay>**\n"
        "Mengirimkan kalimat random dengan delay spam\n"
        "Contoh penggunaan: `.delayspam Hello 5 1.5`\n\n"
        "**.pshspam <text> <jumlah> <delay>**\n"
        "Mengirimkan pesan delayspam sesuai request\n"
        "Contoh penggunaan: `.pshspam Hello 5 1.5`\n\n"
        "**.stopspam**\n"
        "Menghentikan proses spam\n"
        "Contoh penggunaan: `.stopspam`\n\n"
        "**.autoreply on**\n"
        "Mengaktifkan auto-reply\n"
        "Contoh penggunaan: `.autoreply on`\n\n"
        "**.autoreply off**\n"
        "Menonaktifkan auto-reply\n"
        "Contoh penggunaan: `.autoreply off`\n\n"
        "**.joinvc**\n"
        "Bergabung ke obrolan suara (userbot)\n"
        "Contoh penggunaan: `.joinvc`\n\n"
        "**.faketyping**\n"
        "Mengetik palsu secara terus-menerus\n"
        "Contoh penggunaan: `.faketyping`\n\n"
        "**.stopfaketyping**\n"
        "Menghentikan mengetik palsu\n"
        "Contoh penggunaan: `.stopfaketyping`\n\n"
        "**.fakeplaying**\n"
        "Menampilkan status bermain palsu secara terus-menerus\n"
        "Contoh penggunaan: `.fakeplaying`\n\n"
        "**.stopfakeplaying**\n"
        "Menghentikan status bermain palsu\n"
        "Contoh penggunaan: `.stopfakeplaying`\n\n"
        "**.purge**\n"
        "Menghapus seluruh chat Anda di grup\n"
        "Contoh penggunaan: `.purge`\n\n"
        "**.clone**\n"
        "Mengkloning akun yang di-reply\n"
        "Contoh penggunaan: `.clone`\n\n"
        "**.unclone**\n"
        "Kembali ke akun asli\n"
        "Contoh penggunaan: `.unclone`\n\n"
        "**.intip @username**\n"
        "Melihat riwayat nama dan username\n"
        "Contoh penggunaan: `.intip @username`\n\n"
        "**.join <username grup/link grup>**\n"
        "Bergabung ke grup berdasarkan username atau tautan\n"
        "Contoh penggunaan: `.join @nama_grup` atau `.join https://t.me/nama_grup`"
        "**.purgeall**\n"
        "Menghapus seluruh chat di grup\n"
        "Contoh penggunaan: `.purgeall`"
    )
    await event.respond(help_message)

@client.on(events.NewMessage(pattern='.delayspam'))
async def delayspam(event):
    global stop_spamming
    stop_spamming = False

    args = event.message.text.split()[1:]
    if len(args) != 3:
        await event.respond('Usage: .delayspam <text> <jumlah> <delay>')
        return
    text, count, delay = args
    try:
        count = int(count)
        delay = float(delay)
    except ValueError:
        await event.respond('Invalid count or delay value')
        return
    for _ in range(count):
        if stop_spamming:
            await event.respond('Spamming stopped.')
            break
        random_text = generate_random_sentence()
        await event.respond(random_text)
        await asyncio.sleep(delay)

@client.on(events.NewMessage(pattern='.pshspam'))
async def pshspam(event):
    global stop_spamming
    stop_spamming = False

    args = event.message.text.split()[1:]
    if len(args) != 3:
        await event.respond('Usage: .pshspam <text> <jumlah> <delay>')
        return
    text, count, delay = args
    try:
        count = int(count)
        delay = float(delay)
    except ValueError:
        await event.respond('Invalid count or delay value')
        return
    for _ in range(count):
        if stop_spamming:
            await event.respond('Spamming stopped.')
            break
        await event.respond(text)
        await asyncio.sleep(delay)

@client.on(events.NewMessage(pattern='.stopspam'))
async def stop_spam(event):
    global stop_spamming
    stop_spamming = True
    await event.respond('Spamming will stop shortly.')

@client.on(events.NewMessage(pattern='.autoreply'))
async def toggle_autoreply(event):
    global auto_reply
    args = event.message.text.split()[1:]
    if len(args) != 1 or args[0] not in ('on', 'off'):
        await event.respond('Usage: .autoreply on|off')
        return
    auto_reply = args[0] == 'on'
    await event.respond(f'Auto-reply {"enabled" if auto_reply else "disabled"}.')

@client.on(events.NewMessage(pattern='.joinvc'))
async def join_vc(event):
    try:
        await client.edit_permissions(event.chat_id, client.get_me(), view_messages=True, send_messages=True,
                                      send_media=True, send_stickers=True, send_gifs=True, send_games=True,
                                      send_inline=True, embed_links=True, send_polls=True, change_info=True,
                                      invite_users=True, pin_messages=True, add_admins=True, manage_call=True)
        await event.respond('Joined voice chat.')
    except Exception as e:
        await event.respond(f'Error: {str(e)}')

@client.on(events.NewMessage(pattern='.faketyping'))
async def faketyping(event):
    global fake_typing_running
    if fake_typing_running:
        await event.respond('Fake typing is already running.')
        return
    await event.respond('Starting fake typing...')
    task = asyncio.create_task(fake_typing(event))
    fake_typing_tasks.append(task)

@client.on(events.NewMessage(pattern='.stopfaketyping'))
async def stopfaketyping(event):
    global fake_typing_running
    fake_typing_running = False
    for task in fake_typing_tasks:
        task.cancel()
    fake_typing_tasks.clear()
    await event.respond('Stopped fake typing.')

@client.on(events.NewMessage(pattern='.fakeplaying'))
async def fakeplaying(event):
    global fake_playing_running
    if fake_playing_running:
        await event.respond('Fake playing is already running.')
        return
    await event.respond('Starting fake playing...')
    task = asyncio.create_task(fake_playing(event))
    fake_playing_tasks.append(task)

@client.on(events.NewMessage(pattern='.stopfakeplaying'))
async def stopfakeplaying(event):
    global fake_playing_running
    fake_playing_running = False
    for task in fake_playing_tasks:
        task.cancel()
    fake_playing_tasks.clear()
    await event.respond('Stopped fake playing.')

@client.on(events.NewMessage(pattern='.purge'))
async def purge(event):
    async for message in client.iter_messages(event.chat_id, from_user='me'):
        await message.delete()
    await event.respond('Purged all messages.')

@client.on(events.NewMessage(pattern='.clone'))
async def clone(event):
    if event.is_reply:
        reply_message = await event.get_reply_message()
        user = await client.get_entity(reply_message.from_id)
    else:
        await event.respond('Reply to a user to clone.')
        return
    me = await client.get_me()
    original_profile['first_name'] = me.first_name
    original_profile['last_name'] = me.last_name
    original_profile['about'] = (await client(functions.users.GetFullUserRequest(id=me.id))).about
    await event.respond('Cloning...')
    await client(functions.account.UpdateProfileRequest(first_name=user.first_name, last_name=user.last_name))
    await client(functions.account.UpdateUsernameRequest(username=''))
    await event.respond('Clone successful.')

@client.on(events.NewMessage(pattern='.unclone'))
async def unclone(event):
    me = await client.get_me()
    await client(functions.account.UpdateProfileRequest(first_name=original_profile['first_name'],
                                                        last_name=original_profile['last_name']))
    await client(functions.account.UpdateUsernameRequest(username=me.username))
    await event.respond('Profile restored to original.')

@client.on(events.NewMessage(pattern='.intip'))
async def intip(event):
    if event.is_reply:
        reply_message = await event.get_reply_message()
        user_id = reply_message.from_id
    else:
        args = event.message.text.split()
        if len(args) != 2:
            await event.respond('Reply to a user or use: .intip @username')
            return
        username = args[1]
        user = await client.get_entity(username)
        user_id = user.id

    animation_text = "Mencari riwayat pengguna..."
    message = await event.respond(animation_text)

    for i in range(len(animation_text)):
        new_text = animation_text[:i + 1]
        if new_text != message.text:
            try:
                await message.edit(new_text)
            except MessageNotModifiedError:
                pass
        await asyncio.sleep(0.1)

    full_user = await client(functions.users.GetFullUserRequest(id=user_id))

    if full_user.users:
        user = full_user.users[0]
        history_message = "👤 History for {}\n\nNames:\n".format(user_id)
        for name in user.first_name_history:
            history_message += f"{name.date.strftime('%d/%m/%y %H:%M:%S')} {name.first_name}\n"

        history_message += "\nUsernames:\n"
        for username in user.usernames:
            history_message += f"{username.date.strftime('%d/%m/%y %H:%M:%S')} @{username.username}\n"

        await message.edit(history_message)
    else:
        await message.edit('User not found.')

@client.on(events.NewMessage(pattern='.join'))
async def join(event):
    args = event.message.text.split()[1:]
    if len(args) != 1:
        await event.respond('Usage: .join <username grup/link grup>')
        return
    link_or_username = args[0]
    try:
        if "t.me" in link_or_username:
            link = link_or_username.split('/')[-1]
            await client(functions.messages.ImportChatInviteRequest(link))
        else:
            username = link_or_username.strip('@')
            await client(functions.messages.AddChatUserRequest(
                chat_id=username,
                user_id=await client.get_me(),
                fwd_limit=0
            ))
        await event.respond(f'Successfully joined {link_or_username}')
    except Exception as e:
        await event.respond(f'Error joining {link_or_username}: {str(e)}')

@client.on(events.NewMessage(pattern='.purgeall'))
async def purge_all(event):
    async for message in client.iter_messages(event.chat_id):
        await message.delete()
    await event.respond('Purged all messages.')

client.start()
client.run_until_disconnected()
