# Upgrade script for lost_god_upgraded.py
import re

with open("public/lost_god_upgraded.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update Telethon imports at the top
old_imp = """try:
    from telethon import TelegramClient, functions, types
    from telethon.sessions import StringSession
    from telethon.tl.functions.channels import InviteToChannelRequest
    from telethon.tl.functions.chatlists import CheckChatlistInviteRequest, JoinChatlistInviteRequest
    from telethon.tl.functions.messages import ImportChatInviteRequest
    HAS_TELETHON = True
except ImportError:
    HAS_TELETHON = False"""

new_imp = """try:
    from telethon import TelegramClient, functions, types
    from telethon.sessions import StringSession
    from telethon.tl.functions.channels import InviteToChannelRequest, EditAdminRequest
    from telethon.tl.functions.chatlists import CheckChatlistInviteRequest, JoinChatlistInviteRequest
    from telethon.tl.functions.messages import ImportChatInviteRequest, EditChatAdminRequest
    from telethon.tl.types import ChatAdminRights
    HAS_TELETHON = True
except ImportError:
    HAS_TELETHON = False"""

if old_imp in code:
    code = code.replace(old_imp, new_imp, 1)

print("Imports updated:", "EditAdminRequest" in code)
