#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ LOST GOD - AUTOMATED FOLDER & MASS GC BOT ADDER ⚡
Automatically joins Telegram Chat Folders (t.me/addlist/...) and
invites all your fleet bots into every group in the folder in seconds!
"""

import sys
import os
import asyncio
from typing import List

try:
    from telethon import TelegramClient, functions, types
    from telethon.tl.functions.chatlists import CheckChatlistInviteRequest, JoinChatlistInviteRequest
    from telethon.tl.functions.channels import InviteToChannelRequest
    from telethon.tl.functions.messages import ImportChatInviteRequest
except ImportError:
    print("\n❌ Telethon not installed! Run: pip install telethon\n")
    sys.exit(1)

# ==================== CONFIGURATION ====================
# Get API_ID and API_HASH from https://my.telegram.org
API_ID = int(os.environ.get("TELEGRAM_API_ID", 0))
API_HASH = os.environ.get("TELEGRAM_API_HASH", "")
SESSION_NAME = "lostgod_folder_adder"

# List of all your fleet bot usernames to add to every GC
DEFAULT_BOT_USERNAMES = [
    # Add your 10 bot usernames here (e.g. '@LostGod1_bot', '@LostGod2_bot')
]

BANNER = """
╔═━─ 𓆩⚡𓆪 ─━═╗
『𓍼ֶָ֢˖ ࣪ꨄ 𝐋𝐎𝐒𝐓 𝐆𝐎𝐃 .་༘࿐』
╚═━─ 𖤐🐉𖤐 ─━═╝
📁 AUTOMATED FOLDER JOIN & MASS BOT ADDER 📁
"""

async def join_folder_and_add_bots(folder_link: str, bot_usernames: List[str]):
    print(BANNER)
    if not API_ID or not API_HASH:
        print("❌ Please set TELEGRAM_API_ID and TELEGRAM_API_HASH in environment or script!")
        print("   Get them free from: https://my.telegram.org")
        return

    print("🔌 Connecting to Telegram Userbot Client...")
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.start()
    me = await client.get_me()
    print(f"✅ Logged in as: {me.first_name} (@{me.username or me.id})\n")

    # Clean the link
    clean_link = folder_link.strip()
    slug = ""
    if "t.me/addlist/" in clean_link:
        slug = clean_link.split("t.me/addlist/")[1].split("?")[0].split("/")[0]
    elif "addlist/" in clean_link:
        slug = clean_link.split("addlist/")[1].split("?")[0].split("/")[0]

    joined_chats = []

    if slug:
        print(f"🔍 Analyzing Chat Folder (Slug: {slug})...")
        try:
            check_res = await client(CheckChatlistInviteRequest(slug=slug))
            folder_title = getattr(check_res, 'title', 'Chat Folder')
            chats_in_folder = check_res.chats
            peers = check_res.peers
            already_peers = getattr(check_res, 'already_peers', [])
            
            print(f"📁 Folder: {folder_title} | Found {len(chats_in_folder)} chats/groups!")
            
            # Join the entire folder
            if peers:
                print(f"🚀 Joining all {len(peers)} chats in folder...")
                await client(JoinChatlistInviteRequest(slug=slug, peers=peers))
                print("✅ Successfully joined all chats in folder!")
            else:
                print("ℹ️ You have already joined the chats in this folder.")

            joined_chats = chats_in_folder
        except Exception as e:
            print(f"❌ Error joining folder: {e}")
    else:
        # Standard invite link t.me/+... or t.me/joinchat/...
        print(f"🔍 Processing invite link: {clean_link}")
        try:
            hash_str = clean_link.split("/")[-1].replace("+", "")
            res = await client(ImportChatInviteRequest(hash=hash_str))
            joined_chats = res.chats
            print("✅ Successfully joined chat via invite link!")
        except Exception as e:
            print(f"⚠️ Note: {e}")

    # Now add all bots to each joined chat
    if not bot_usernames:
        print("\n⚠️ No bot usernames specified to add!")
        return

    print(f"\n🤖 Adding {len(bot_usernames)} bots into {len(joined_chats)} chats...")
    
    # Resolve bot entities
    bot_entities = []
    for uname in bot_usernames:
        uname = uname.strip().lstrip("@")
        if not uname: continue
        try:
            b = await client.get_input_entity(uname)
            bot_entities.append((uname, b))
            print(f"   ✓ Found bot @{uname}")
        except Exception as e:
            print(f"   ✗ Could not find bot @{uname}: {e}")

    if not bot_entities:
        print("❌ No valid bots resolved.")
        await client.disconnect()
        return

    success_count = 0
    for chat in joined_chats:
        chat_title = getattr(chat, 'title', str(chat.id))
        print(f"\n📢 Processing Group: {chat_title}")
        for uname, b_entity in bot_entities:
            try:
                await client(InviteToChannelRequest(
                    channel=chat,
                    users=[b_entity]
                ))
                print(f"   ✅ Added @{uname} to {chat_title}")
                success_count += 1
                await asyncio.sleep(1.5)  # Safe delay to avoid flood
            except Exception as e:
                err = str(e).lower()
                if "already_participant" in err or "user_already_participant" in err:
                    print(f"   ℹ️ @{uname} is already in {chat_title}")
                elif "chat_admin_required" in err or "admin" in err:
                    print(f"   ⚠️ Need admin rights to add bots in {chat_title}")
                else:
                    print(f"   ⚠️ Could not add @{uname}: {e}")

    print(f"\n🎉 Done! Added bots across groups successfully (Total actions: {success_count})")
    await client.disconnect()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 folder_bot_adder.py <folder_link> [@bot1 @bot2 ...]")
        print("Example: python3 folder_bot_adder.py https://t.me/addlist/sOmeSlUg @LostGod1_bot @LostGod2_bot")
        sys.exit(1)

    f_link = sys.argv[1]
    bots = sys.argv[2:] or DEFAULT_BOT_USERNAMES
    asyncio.run(join_folder_and_add_bots(f_link, bots))
