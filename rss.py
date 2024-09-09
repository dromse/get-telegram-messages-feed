import os
from dotenv import load_dotenv
from telethon import TelegramClient
from feedgen.feed import FeedGenerator

load_dotenv()

# Your API credentials
api_id = int(os.getenv("api_id") or -1)
api_hash = os.getenv("api_hash") or ""
phone = os.getenv("phone") or ""

# Create a client session
client = TelegramClient("my_telegram_session", api_id, api_hash)

# Atom feed generator
fg = FeedGenerator()
fg.id('https://example.com/telegram-feed')
fg.title('Telegram Unread Messages Feed')
fg.author({'name': 'Telegram Feed Bot', 'email': 'bot@example.com'})
fg.link(href='https://example.com/telegram-feed', rel='self')
fg.language('en')

async def get_all_unread_messages():
    # Iterate over all dialogs (chats, groups, channels)
    async for dialog in client.iter_dialogs(limit=100):
        if not dialog.message.post and not dialog.message.out and dialog.unread_count > 0:
            unread_messages = dialog.unread_count
            print(f"New {unread_messages} {'messages' if unread_messages > 1 else 'message'} from user:", dialog.name)

            async for message in client.iter_messages(dialog.message.peer_id.user_id):
                text = message.text or "No text content"
                if message.media:
                    if message.media_unread:
                        text = "Media message"
                    if message.media.voice:
                        text = "Voice message"

                # Create an entry for the Atom feed
                fe = fg.add_entry()
                fe.id(f'https://example.com/telegram/{message.id}')
                fe.title(f'Message from {dialog.name}')
                fe.link(href=f'https://example.com/telegram/{message.id}')
                fe.description(text)
                fe.published(message.date.strftime("%Y-%m-%dT%H:%M:%SZ"))

                unread_messages -= 1
                if unread_messages <= 0:
                    break

async def main():
    # Connect and start the client
    # client.start(phone)
    await client.connect()

    # Fetch all unread messages from all chats
    await get_all_unread_messages()

    # Output the Atom feed to a file
    with open("/tmp/telegram_unread_feed.xml", "w") as f:
        f.write(fg.atom_str(pretty=True).decode('utf-8'))

# Start the client and execute the function
with client:
    client.loop.run_until_complete(main())
