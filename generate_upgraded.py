import os
import sys

# Script that generates public/lost_god_upgraded.py
# with all requested features cleanly integrated

upgraded_code = '''import logging
import asyncio
import os
import json
import random
import time
import io
import urllib.request
import urllib.parse
from typing import Set, Dict, List, Any, Optional
from telegram import (
    Update,
    Chat,
    ChatPermissions,
    ReactionTypeEmoji,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.error import RetryAfter, TimedOut, NetworkError, BadRequest, Forbidden
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.CRITICAL
)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.CRITICAL)
logging.getLogger("telegram").setLevel(logging.CRITICAL)
logging.getLogger("http.server").setLevel(logging.CRITICAL)

# ══════════════════════════════════════════════════════════════════
#  90-DAYS BASE UPTIME ENGINE
# ══════════════════════════════════════════════════════════════════
# Aaj 90 days se shuru hoga, kal 91 days, parso 92 days etc.
_UPTIME_BASE_OFFSET = 90 * 86400
_BOT_START_TIMESTAMP = time.time() - _UPTIME_BASE_OFFSET

def get_uptime() -> str:
    elapsed = int(time.time() - _BOT_START_TIMESTAMP)
    days = elapsed // 86400
    hours = (elapsed % 86400) // 3600
    minutes = (elapsed % 3600) // 60
    seconds = elapsed % 60
    return f"{days}d {hours}h {minutes}m {seconds}s"

TOKENS_FILE = "tokens.json"
GROUPS_FILE = "groups.json"
SUDO_FILE   = "sudo_users.json"
MEDIA_FILE  = "menu_media.json"

# Default Owner ID (Replit secret ya env OWNER_ID se override ho sakta hai)
OWNER_ID = int(os.environ.get("OWNER_ID", "7878403531"))
_OWNER_IDS_RAW = os.environ.get("OWNER_IDS", "")
OWNER_IDS: Set[int] = {OWNER_ID} | {
    int(value.strip())
    for value in (_OWNER_IDS_RAW.split(",") if _OWNER_IDS_RAW else [str(OWNER_ID)])
    if value.strip()
}

def _is_owner(user_id: Optional[int]) -> bool:
    return user_id is not None and user_id in OWNER_IDS

def get_base_tokens() -> List[str]:
    raw = os.environ.get("BOT_TOKENS", """
8627586769:AAH8PYGWOZmv_JkmCAySy5z5G7oot556qL4,
8761699443:AAEpZ4zDZ2PdWhd8QChxq7-pFibsRQMhPPs,
8713895336:AAEViwMyRC9_kaVclGofdeTi3YIMmJvGhz4,
8873576482:AAFtswU_xQusPj0vrictYAbH_515DrI9z_s,
8821731664:AAGSzXtRCWM5jN3j821Lnra88H5B7CKm7lg,
8801100592:AAHUX21a10z4R0R-sk773D75vkcPcd7meaU,
8871557055:AAEuDWDmPTzjv1JC4kaK7Z9uGKmwhVVMXoM,
7956054766:AAFsDxg4ky7UILHNuUGqAGyY1HbWW6DsEFE,
8586613886:AAFQfhb5d4nP2vjCAQz-qQZxf9Yctynu8C8,
8720119028:AAF6asBQcagz6dwXQEqvAW24rQoNxwWT5MY
""")
    tokens = [t.strip() for t in raw.replace("\\n", ",").split(",") if t.strip()]
    for i in range(1, 11):
        ov = os.environ.get(f"BOT_TOKEN_{i}", "").strip()
        if ov and i <= len(tokens):
            tokens[i-1] = ov
    return tokens

def load_groups() -> Set[int]:
    try:
        if os.path.exists(GROUPS_FILE):
            with open(GROUPS_FILE, "r") as f:
                return set(json.load(f))
    except Exception:
        pass
    return set()

def save_groups(groups: Set[int]):
    try:
        with open(GROUPS_FILE, "w") as f:
            json.dump(list(groups), f)
    except Exception:
        pass

def load_sudo() -> Set[int]:
    try:
        if os.path.exists(SUDO_FILE):
            with open(SUDO_FILE, "r") as f:
                return set(int(x) for x in json.load(f))
    except Exception:
        pass
    return set()

def save_sudo() -> None:
    try:
        with open(SUDO_FILE, "w") as f:
            json.dump(list(SUDO_USERS - OWNER_IDS), f)
    except Exception:
        pass

def load_extra_tokens() -> List[str]:
    try:
        if os.path.exists(TOKENS_FILE):
            with open(TOKENS_FILE, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return []

def load_menu_media() -> Dict[str, str]:
    try:
        if os.path.exists(MEDIA_FILE):
            with open(MEDIA_FILE, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def save_menu_media(data: Dict[str, str]):
    try:
        with open(MEDIA_FILE, "w") as f:
            json.dump(data, f)
    except Exception:
        pass

known_chats:       Set[int]  = load_groups()
SUDO_USERS:        Set[int]  = load_sudo() | OWNER_IDS
all_bot_instances: List[Any] = []
all_apps:          List[Any] = []
extra_tokens:      List[str] = load_extra_tokens()

mute_chats:          Set[int]       = set()
ncdel_chats:         Set[int]       = set()
ncwar_targets:       Dict[int, str] = {}
autoreact_chats:     Dict[int, str] = {}
custom_react_emojis: Dict[int, str] = {}
slide_reply_targets: Dict[int, int] = {}
autoreply_chats:     Dict[int, str] = {}
targetreply_chats:   Dict[int, dict]= {}
_menu_media:         Dict[str, str] = load_menu_media()
_seen_updates:       Set[int]       = set()

SUFFIX_EMOJIS = [
    "🌸", "🌺", "🌻", "🌹", "🪷", "🌷", "💮", "🏵️",
    "✨", "💫", "⭐", "🌟", "💥", "🔥", "⚡", "❄️",
    "🌊", "🫧", "💧", "🌀", "🌈", "🌙", "☄️", "🌟",
    "💎", "🔮", "🧿", "🪬", "👑", "💀", "🦋", "🐉",
]

_SUFFIX = " ִֶָ𓂃 ࣪˖ ִֶָ{emoji}་༘࿐"

def make_suffix() -> str:
    return _SUFFIX.format(emoji=random.choice(SUFFIX_EMOJIS))

WRAP_LEFT = [
    "🌊", "✨", "💎", "👑", "🔥", "꧁", "⭅╡", "♛", "𖤍", "❦", "⚡", "☄️", "💀", "🌟", "🔱",
]
WRAP_RIGHT = [
    "🌊", "⚡", "💀", "🔥", "✨", "꧂", "╞⭆", "♛", "𖤍", "❦", "🌙", "💎", "👑", "☄️", "🔱",
]

def _build_name(text: str, last: list) -> str:
    for _ in range(20):
        wl = random.choice(WRAP_LEFT)
        wr = random.choice(WRAP_RIGHT)
        suf = make_suffix()
        candidate = f"{wl}{text}{wr}{suf}"[:255]
        if candidate != last[0]:
            last[0] = candidate
            return candidate
    return f"{text}{make_suffix()}{random.randint(0,99)}"[:255]

BURN_SYMS = ["🔥","💥","⚡","☄️","🌋","🔴","🟠","🌩️","🌪️","💣"]
WAVE_SYMBOLS = [
    "🌊","💧","🫧","🌀","🌧️","⛲","🚿","🐚","🌬️","🫗",
    "🧊","🌈","⛵","🏄","🤽","🐬","🐟","🦈","🫙","💎",
]
WATER_SYMS = [
    "🌊","💧","🚿","🛁","🫧","🐚","🌀","🌧️","⛲","🌬️",
    "🌊🌧️","💧🌊","🫧🌊","🌀🌊","🌊💧","🌧️🌊","⛲🌊","🐚🌊",
]

def is_admin(user_id: int) -> bool:
    return _is_owner(user_id) or user_id in SUDO_USERS

def _is_primary_bot(context) -> bool:
    if not all_bot_instances:
        return True
    return context.bot.id == all_bot_instances[0].id

_OWNER_GATE_MSG = (
    "┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅\\n"
    "⚡️ 𝐋𝐎𝐒𝐓 𝐆𝐎𝐃 𝐂𝐎𝐍𝐓𝐑𝐎𝐋 ⚡️\\n"
    "𝑰𝒔 𝒃𝒐𝒕 𝒌𝒂 𝒂𝒄𝒄𝒆𝒔𝒔 𝒔𝒊𝒓𝒇 𝒂𝒅𝒎𝒊𝒏 𝒌𝒆 𝒍𝒊𝒚𝒆 𝒉𝒂𝒊.\\n"
    "┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅"
)

def _dedup(handler):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        uid = (context.bot.id, update.update_id)
        if uid in _seen_updates:
            return
        _seen_updates.add(uid)
        if len(_seen_updates) > 10000:
            for u in sorted(_seen_updates)[:5000]:
                _seen_updates.discard(u)

        msg = update.message or update.edited_message
        if msg and msg.text and msg.text.startswith("/"):
            user = update.effective_user
            if not user or not is_admin(user.id):
                try:
                    await msg.reply_text(_OWNER_GATE_MSG)
                except Exception:
                    pass
                return
        await handler(update, context)
    return wrapper

class BotFloodTracker:
    def __init__(self):
        self._flood_until: Dict[int, float] = {}

    def is_flooded(self, bot_id: int) -> bool:
        exp = self._flood_until.get(bot_id, 0.0)
        if time.monotonic() < exp:
            return True
        self._flood_until.pop(bot_id, None)
        return False

    FLOOD_CAP  = 3.0

    def mark_flooded(self, bot_id: int, seconds: float) -> None:
        capped = min(float(seconds), self.FLOOD_CAP)
        self._flood_until[bot_id] = time.monotonic() + max(capped, 0.05)

    def remaining(self, bot_id: int) -> float:
        return max(0.0, self._flood_until.get(bot_id, 0.0) - time.monotonic())

_flood_tracker = BotFloodTracker()

class TaskController:
    def __init__(self):
        self.tasks:  Dict[str, asyncio.Task]  = {}
        self.events: Dict[str, asyncio.Event] = {}

    def _key(self, chat_id: int, task_type: str) -> str:
        return f"{chat_id}_{task_type}"

    async def start_task(self, chat_id: int, task_type: str, coro_factory) -> None:
        await self.stop_task(chat_id, task_type)
        key = self._key(chat_id, task_type)
        stop_event = asyncio.Event()
        self.events[key] = stop_event

        async def wrapped():
            try:
                await coro_factory(stop_event)
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.error(f"Task {key} error: {e}")
            finally:
                self.tasks.pop(key, None)
                self.events.pop(key, None)

        self.tasks[key] = asyncio.create_task(wrapped())

    async def stop_task(self, chat_id: int, task_type: str) -> bool:
        key = self._key(chat_id, task_type)
        stopped = False
        if key in self.events:
            self.events[key].set()
            stopped = True
        if key in self.tasks:
            task = self.tasks.pop(key)
            if not task.done():
                task.cancel()
                try:
                    await asyncio.wait_for(task, timeout=2.0)
                except Exception:
                    pass
            stopped = True
        self.events.pop(key, None)
        return stopped

    async def stop_all_for_chat(self, chat_id: int) -> int:
        prefix = f"{chat_id}_"
        keys = [k for k in list(self.tasks.keys()) + list(self.events.keys())
                if k.startswith(prefix)]
        task_types = set(k.split("_", 1)[1] for k in keys)
        count = 0
        for t in task_types:
            if await self.stop_task(chat_id, t):
                count += 1
        return count

task_controller = TaskController()

async def _hyperfire_engine(chat_id: int, bots: List[Any], stop_event: asyncio.Event, name_factory):
    CONCURRENCY = 2
    if not bots:
        return

    async def _safe_rename(bot, name: str, bot_id: int, sem: asyncio.Semaphore):
        try:
            await bot.set_chat_title(chat_id, name)
        except RetryAfter as e:
            _flood_tracker.mark_flooded(bot_id, e.retry_after)
        except Exception:
            pass
        finally:
            sem.release()

    async def _bot_worker(bot):
        bot_id = getattr(bot, "id", id(bot))
        sem = asyncio.Semaphore(CONCURRENCY)
        fire_tasks = set()
        try:
            while not stop_event.is_set():
                if _flood_tracker.is_flooded(bot_id):
                    wait = _flood_tracker.remaining(bot_id)
                    if wait > 0:
                        try:
                            await asyncio.wait_for(stop_event.wait(), timeout=min(wait, 0.25))
                        except asyncio.TimeoutError:
                            pass
                    continue
                try:
                    await asyncio.wait_for(sem.acquire(), timeout=0.1)
                except asyncio.TimeoutError:
                    continue
                if stop_event.is_set():
                    sem.release()
                    break
                name = name_factory()[:255]
                t = asyncio.create_task(_safe_rename(bot, name, bot_id, sem))
                fire_tasks.add(t)
                t.add_done_callback(fire_tasks.discard)
        finally:
            for t in list(fire_tasks):
                if not t.done():
                    t.cancel()

    workers = [asyncio.create_task(_bot_worker(bot)) for bot in bots]
    try:
        await asyncio.gather(*workers, return_exceptions=True)
    finally:
        for w in workers:
            if not w.done():
                w.cancel()

# ══════════════════════════════════════════════════════════════════
#  DECORATED GOD-TIER VIP MENU
# ══════════════════════════════════════════════════════════════════
_MENU_TEXT = (
    "╔═══════════════════════════════════╗\\n"
    "║  ⚡ 𝕬𝕸𝕽𝕴𝕿 𝖃 𝕸𝕰𝕹𝕿𝕬𝕷 𝖁𝟏𝟎 ⚡  ║\\n"
    "║     『 𝐆𝐎𝐃-𝐓𝐈𝐄𝐑 𝐍𝐄𝐗𝐔𝐒 𝐂𝐎𝐑𝐄 』      ║\\n"
    "╚═══════════════════════════════════╝\\n\\n"
    "╭━━━✦❘༻ 👑 𝐒𝐔𝐏𝐑𝐄𝐌𝐄 𝐈𝐍𝐅𝐎 ༺❘✦━━━╮\\n"
    "│ ✦ 🤖 𝐅ʟᴇᴇᴛ 𝐂ᴏᴅᴇ    : 𝐀ᴍʀɪᴛ 𝐗 𝐌ᴇɴᴛᴀʟ ꨄ\\n"
    "│ 𖤐 👑 𝐂ᴏᴍᴍᴀɴᴅᴇʀ    : 𝐒ᴜᴘʀᴇᴍᴇ 𝐀ᴅᴍɪɴ ✧\\n"
    "│ ✦ ⚡ 𝐄ɴɢɪɴᴇ        : 𝐔ʟᴛʀᴀ-𝐇ʏᴘᴇʀʙʟɪᴛᴢ\\n"
    "│ 𖤐 🛡️ 𝐅ʟᴏᴏᴅ 𝐆ᴜᴀʀᴅ   : 𝐆ʜᴏꜱᴛ 𝐁ʏᴘᴀꜱꜱ [𝐎𝐍]\\n"
    "│ ✦ ⚙️ 𝐏ʀᴇғɪx        : [  +  |  /  |  💦  ]\\n"
    "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯\\n\\n"
    "╭━━━✦❘༻ 🌀 𝐍𝐂 𝐖𝐀𝐑 𝐀𝐑𝐒𝐄𝐍𝐀𝐋 ༺❘✦━━━╮\\n"
    "│ 🌐 +allgcnc <txt>   ⌁ 𝐆ʟᴏʙᴀʟ 𝐀ʟʟ-𝐆𝐂 𝐍𝐂 ⚡\\n"
    "│ 🎲 +rnc <text>      ⌁ 𝐑ᴀɴᴅᴏᴍ 𝐂ʏᴄʟᴇ 𝐄ɴɢɪɴᴇ\\n"
    "│ 🔥 +flamenc <text>  ⌁ 𝐆ʜᴏꜱᴛ-𝐅ʟᴀᴍᴇ 𝐌ᴏᴅᴇ\\n"
    "│ 🌊 +horneync <text> ⌁ 𝐇ʏᴘᴇʀғɪʀᴇ 𝐖ᴀᴠᴇ 𝐌ᴏᴅᴇ\\n"
    "│ 🥷 +stealthnc <txt> ⌁ 𝐌ɪᴄʀᴏ-𝐉ɪᴛᴛᴇʀ 𝐒ᴛᴇᴀʟᴛʜ\\n"
    "│ 💎 +purenc <text>   ⌁ 𝐙ᴇʀᴏ-𝐃ᴇʟᴀʏ 𝐌ᴀ𝐱 𝐒ᴘᴇᴇᴅ\\n"
    "│ ☠️ +zalgonc <text>   ⌁ 𝐙ᴀʟɢᴏ 𝐆ʟɪᴛᴄʜ 𝐌ᴏᴅᴇ\\n"
    "│ 🌈 +gradientnc <txt>⌁ 𝐂ᴏʟᴏʀ 𝐒ʜɪғᴛ 𝐆ʀᴀᴅɪᴇɴᴛ\\n"
    "│ ⛔ /stop            ⌁ 𝐇ᴀʟᴛ 𝐀ʟʟ 𝐀ᴄᴛɪᴠᴇ 𝐂ʏᴄʟᴇꜱ\\n"
    "│ 🛑 /stopglobalnc    ⌁ 𝐒ᴛᴏᴘ 𝐆ʟᴏʙᴀʟ 𝐀ʟʟ-𝐆𝐂 𝐍𝐂\\n"
    "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯\\n\\n"
    "╭━━━✦❘༻ 🧠 𝐆𝐎𝐃 𝐆𝐎𝐃 𝐌𝐎𝐃𝐄𝐒 ༺❘✦━━━╮\\n"
    "│ ✦ +god1  🔥 𝐈ɴғᴇʀɴᴏ   │ ✦ +god6  🐉 𝐃ʀᴀɢᴏɴ\\n"
    "│ 𖤐 +god2  ⚡ 𝐋ɪɢʜᴛɴɪɴɢ │ 𖤐 +god7  🩸 𝐁ʟᴏᴏᴅ\\n"
    "│ ✦ +god3  💀 𝐕ᴏɪᴅ      │ ✦ +god8  💎 𝐃ɪᴀᴍᴏɴᴅ\\n"
    "│ 𖤐 +god4  🌊 𝐎ᴄᴇᴀɴ     │ 𖤐 +god9  🌑 𝐄ᴄʟɪᴘꜱᴇ\\n"
    "│ ✦ +god5  👑 𝐃ɪᴠɪɴᴇ    │ ✦ +god10 🔱 𝐓ʀɪᴅᴇɴᴛ\\n"
    "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯\\n\\n"
    "╭━━━✦❘༻ 💬 𝐒𝐏𝐀𝐌 & 𝐑𝐄𝐏𝐋𝐘 ༺❘✦━━━╮\\n"
    "│ 📢 +spam <text>      ⌁ 𝐀ʟʟ-𝐁ᴏᴛꜱ 𝐓ᴇxᴛ 𝐅ʟᴏᴏᴅ\\n"
    "│ 🛑 /stopspam         ⌁ 𝐈ɴꜱᴛᴀɴᴛ 𝐒ᴘᴀᴍ 𝐇ᴀʟᴛ\\n"
    "│ ↩️ +slide <text>     ⌁ 𝐒ʏᴍʙᴏʟ 𝐑ᴇᴘʟʏ 𝐁ᴏᴍʙ\\n"
    "│ 🎯 +slidereply       ⌁ 𝐓ᴀʀɢᴇᴛ 𝐁ᴜʀꜱᴛ 𝐑ᴇᴘʟɪᴇꜱ\\n"
    "│ 🤖 +autoreply <txt>  ⌁ 𝐄ᴠᴇʀʏ 𝐌ꜱɢ 𝐀ᴜᴛᴏ-𝐑ᴇᴘʟʏ\\n"
    "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯\\n\\n"
    "╭━━━✦❘༻ 🛡️ 𝐆𝐑𝐎𝐔𝐏 𝐂𝐎𝐍𝐓𝐑𝐎𝐋 ༺❘✦━━━╮\\n"
    "│ 🔇 /mute             ⌁ 𝐒ɪʟᴇɴᴄᴇ 𝐍ᴏɴ-𝐀ᴅᴍɪɴꜱ\\n"
    "│ 🗑️ /purge [N]        ⌁ 𝐌ᴀꜱꜱ 𝐌ᴇꜱꜱᴀɢᴇ 𝐃ᴇʟᴇᴛᴇ\\n"
    "│ ⚔️ /ncwar <text>     ⌁ 𝐀ɴᴛɪ-𝐄ɴᴇᴍʏ 𝐍𝐂 𝐖ᴀʀ\\n"
    "│ 🚯 /ncdel            ⌁ 𝐃ᴇʟᴇᴛᴇ 𝐄ɴᴇᴍʏ 𝐍𝐂 𝐌ꜱɢꜱ\\n"
    "│ 🚪 /leave            ⌁ 𝐀ʟʟ 𝐁ᴏᴛꜱ 𝐄xɪᴛ 𝐆𝐂\\n"
    "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯\\n\\n"
    "╭━━━✦❘༻ 🔐 𝐒𝐔𝐏𝐑𝐄𝐌𝐄 𝐀𝐃𝐌𝐈𝐍 ༺❘✦━━━╮\\n"
    "│ ⚡ /ping  •  /status ⌁ 𝟗𝟎-𝐃ᴀʏ 𝐔ᴘᴛɪᴍᴇ & 𝐋ᴀᴛᴇɴᴄʏ\\n"
    "│ 👑 /addsudo <id>     ⌁ 𝐆ʀᴀɴᴛ 𝐀ᴅᴍɪɴ 𝐑ᴀɴᴋ\\n"
    "│ ⛔ /removesudo <id>  ⌁ 𝐑ᴇᴠᴏᴋᴇ 𝐀ᴅᴍɪɴ 𝐑ᴀɴᴋ\\n"
    "│ 🤖 /bots             ⌁ 𝐂ʜᴇᴄᴋ 𝐅ʟᴇᴇᴛ 𝐇ᴇᴀʟᴛʜ\\n"
    "│ 📛 /botname <name>   ⌁ 𝐌ᴀꜱꜱ 𝐑ᴇɴᴀᴍᴇ 𝐁ᴏᴛꜱ\\n"
    "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯\\n\\n"
    "┈┉┅━❀꧁ 𓆩⚡ 𝐋𝐎𝐒𝐓 𝐆𝐎𝐃 ⚡𓆪 ꧂❀━┅┉┈"
)

def _extract_base(raw: str, prefixes: tuple, context) -> str:
    for prefix in prefixes:
        if raw.lower().startswith(prefix.lower()):
            return raw[len(prefix):].strip()
    return " ".join(context.args) if context.args else ""

# ══════════════════════════════════════════════════════════════════
#  COMMANDS IMPLEMENTATION
# ══════════════════════════════════════════════════════════════════

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or not update.message: return
    known_chats.add(update.effective_chat.id)
    save_groups(known_chats)
    await update.message.reply_text(_MENU_TEXT)

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    await update.message.reply_text(_MENU_TEXT)

async def ping_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.message: return
    start_t = time.monotonic()
    msg = await update.message.reply_text("⚡ Calculating Ping…")
    latency_ms = round((time.monotonic() - start_t) * 1000, 2)
    bots_count = len([b for b in all_bot_instances if b is not None])
    uptime_str = get_uptime()

    status_card = (
        "╔════════════════════════════════╗\\n"
        "║   ⚡ 𝐋𝐎𝐒𝐓 𝐆𝐎𝐃 𝐒𝐓𝐀𝐓𝐔𝐒 ⚡   ║\\n"
        "╚════════════════════════════════╝\\n\\n"
        f"🚀 𝐋𝐚𝐭𝐞𝐧𝐜𝐲     :  `{latency_ms} ms` [Ultra Fast]\\n"
        f"⏱️ 𝐔𝐩𝐭𝐢𝐦𝐞      :  `{uptime_str}`\\n"
        f"🤖 𝐅𝐥𝐞𝐞𝐭 𝐁𝐨𝐭𝐬   :  `{bots_count} Online`\\n"
        f"🌐 𝐊𝐧𝐨𝐰𝐧 𝐆𝐂𝐬   :  `{len(known_chats)} Groups`\\n"
        f"🛡️ 𝐅𝐥𝐨𝐨𝐝 𝐆𝐮𝐚𝐫𝐝  :  `Active (Ghost Bypass)`\\n"
        f"👑 𝐎𝐰𝐧𝐞𝐫 𝐈𝐃     :  `{OWNER_ID}`\\n\\n"
        "┈┉┅━❀꧁ 𓆩 𝐃𝐎𝐌𝐈𝐍𝐀𝐍𝐂𝐄 𓆪 ꧂❀━┅┉┈"
    )
    await msg.edit_text(status_card, parse_mode="Markdown")

async def stop_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.effective_chat or not update.message: return
    count = await task_controller.stop_all_for_chat(update.effective_chat.id)
    if count > 0:
        await update.message.reply_text("🛑 𝐒𝐓𝐎𝐏𝐏𝐄𝐃 — All tasks cancelled in this chat.")
    else:
        await update.message.reply_text("Nothing running here.")

# ══════════════════════════════════════════════════════════════════
#  GLOBAL ALL-GC NC COMMAND (/globalnc & /stopglobalnc)
# ══════════════════════════════════════════════════════════════════
async def globalnc_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.message or not _is_primary_bot(context): return

    raw = (update.message.text or "").strip()
    base = _extract_base(raw, ("/globalnc", "+allgcnc", "💦allgcnc", "+globalnc"), context)
    if not base:
        return await update.message.reply_text("Usage: `+allgcnc <text>` ya `/globalnc <text>`", parse_mode="Markdown")

    if not known_chats:
        return await update.message.reply_text("❌ No known groups found. Add bots to groups first.")

    bots = [b for b in all_bot_instances if b is not None] or [context.bot]
    target_gcs = list(known_chats)
    started_count = 0

    msg = await update.message.reply_text(f"🚀 Starting Global NC in {len(target_gcs)} groups with '{base}'…")

    for chat_id in target_gcs:
        _last = [""]
        def make_name_for_chat():
            return _build_name(base, _last)
        def _create_gc_coro(cid):
            async def _gc_nc_loop(stop_event: asyncio.Event):
                await _hyperfire_engine(cid, bots, stop_event, make_name_for_chat)
            return _gc_nc_loop
        try:
            await task_controller.start_task(chat_id, "globalnc", _create_gc_coro(chat_id))
            started_count += 1
        except Exception:
            pass

    await msg.edit_text(
        f"⚡ 💦 𝐀𝐋𝐋 𝐆𝐂 𝐍𝐂 𝐀𝐂𝐓𝐈𝐕𝐄! ⚡\\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\\n"
        f"🌐 Active in `{started_count}/{len(target_gcs)}` Groups\\n"
        f"🛑 Stop all with: `/stopglobalnc`",
        parse_mode="Markdown"
    )

async def stopglobalnc_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.message or not _is_primary_bot(context): return
    stopped_count = 0
    for chat_id in list(known_chats):
        if await task_controller.stop_task(chat_id, "globalnc"):
            stopped_count += 1
    await update.message.reply_text(f"🛑 𝐆𝐋𝐎𝐁𝐀𝐋 𝐍𝐂 𝐒𝐓𝐎𝐏𝐏𝐄𝐃 in `{stopped_count}` Groups.", parse_mode="Markdown")

# ══════════════════════════════════════════════════════════════════
#  ZALGO & GRADIENT NC HANDLERS
# ══════════════════════════════════════════════════════════════════
_ZALGO_UP = ["̍","̎","̄","̅","̿","̑","̆","̐","͒","͗","͑","̇","̈","̊","͂"]
_ZALGO_DOWN = ["̖","̗","̘","̙","̜","̝","̞","̟","̠","̤","̥","̦","̩","̪","̫"]
_GRADIENT_SETS = [
    ["🔴","🟠","🟡","🟢","🔵","🟣"],
    ["🟣","🟪","🔷","💠","💎","✨"],
    ["🖤","🩶","🤍","💀","☠️","⚡"],
    ["🔥","💥","⚡","☄️","🌋","🩸"]
]

def _make_zalgo(text: str) -> str:
    res = []
    for char in text:
        res.append(char)
        if char != ' ':
            res.append(random.choice(_ZALGO_UP))
            res.append(random.choice(_ZALGO_DOWN))
    return "".join(res)

async def zalgonc_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.effective_chat or not update.message or not _is_primary_bot(context): return
    raw = (update.message.text or "").strip()
    base = _extract_base(raw, ("+zalgonc", "💦zalgonc", "/zalgonc"), context)
    if not base: return await update.message.reply_text("Usage: +zalgonc <text>")

    chat_id = update.effective_chat.id
    bots = [b for b in all_bot_instances if b is not None] or [context.bot]
    def make_name():
        g = _make_zalgo(base)
        sym = random.choice(["☠️","💀","👁️","⚡","🖤"])
        return f"{sym} {g} {sym}"[:255]
    async def nc_loop(stop_event: asyncio.Event):
        await _hyperfire_engine(chat_id, bots, stop_event, make_name)
    await task_controller.start_task(chat_id, "nc", nc_loop)
    await update.message.reply_text(f"☠️ 𝐙𝐀𝐋𝐆𝐎 𝐆𝐋𝐈𝐓𝐂𝐇 𝐍𝐂 𝐀𝐂𝐓𝐈𝐕𝐄 ({len(bots)} bots)\\nStop: /stop")

async def gradientnc_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.effective_chat or not update.message or not _is_primary_bot(context): return
    raw = (update.message.text or "").strip()
    base = _extract_base(raw, ("+gradientnc", "💦gradientnc", "/gradientnc"), context)
    if not base: return await update.message.reply_text("Usage: +gradientnc <text>")

    chat_id = update.effective_chat.id
    bots = [b for b in all_bot_instances if b is not None] or [context.bot]
    def make_name():
        grad = random.choice(_GRADIENT_SETS)
        s1, s2 = grad[0], grad[-1]
        return f"{s1}{s2} {base} {s2}{s1}{make_suffix()}"[:255]
    async def nc_loop(stop_event: asyncio.Event):
        await _hyperfire_engine(chat_id, bots, stop_event, make_name)
    await task_controller.start_task(chat_id, "nc", nc_loop)
    await update.message.reply_text(f"🌈 𝐆𝐑𝐀𝐃𝐈𝐄𝐍𝐓 𝐍𝐂 𝐀𝐂𝐓𝐈𝐕𝐄 ({len(bots)} bots)\\nStop: /stop")

async def randnc_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.effective_chat or not update.message or not _is_primary_bot(context): return
    raw = (update.message.text or "").strip()
    base = _extract_base(raw, ("+rnc", "💦rnc", "/rnc"), context)
    if not base: return await update.message.reply_text("Usage: +rnc <text>")
    chat_id = update.effective_chat.id
    bots = [b for b in all_bot_instances if b is not None] or [context.bot]
    _last = [""]
    def make_name(): return _build_name(base, _last)
    async def nc_loop(stop_event: asyncio.Event):
        await _hyperfire_engine(chat_id, bots, stop_event, make_name)
    await task_controller.start_task(chat_id, "nc", nc_loop)
    await update.message.reply_text(f"🎲 𝐑𝐍𝐂 𝐀𝐂𝐓𝐈𝐕𝐄 ({len(bots)} bots)\\nStop: /stop")

async def flamenc_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.effective_chat or not update.message or not _is_primary_bot(context): return
    raw = (update.message.text or "").strip()
    base = _extract_base(raw, ("+flamenc", "💦flamenc", "/flamenc"), context)
    if not base: return await update.message.reply_text("Usage: +flamenc <text>")
    chat_id = update.effective_chat.id
    bots = [b for b in all_bot_instances if b is not None] or [context.bot]
    def make_name():
        sym = random.choice(BURN_SYMS)
        return f"{sym}{base}{sym}{make_suffix()}"[:255]
    async def nc_loop(stop_event: asyncio.Event):
        await _hyperfire_engine(chat_id, bots, stop_event, make_name)
    await task_controller.start_task(chat_id, "nc", nc_loop)
    await update.message.reply_text(f"🔥 𝐅𝐋𝐀𝐌𝐄𝐍𝐂 𝐀𝐂𝐓𝐈𝐕𝐄 ({len(bots)} bots)\\nStop: /stop")

async def spam_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.effective_chat or not update.message or not _is_primary_bot(context): return
    raw = (update.message.text or "").strip()
    base = _extract_base(raw, ("+spam", "💦spam", "/spam"), context)
    if not base: return await update.message.reply_text("Usage: +spam <text>")
    chat_id = update.effective_chat.id
    bots = [b for b in all_bot_instances if b is not None] or [context.bot]
    async def _bot_spam_worker(bot, stop_event: asyncio.Event):
        while not stop_event.is_set():
            try: await bot.send_message(chat_id=chat_id, text=base)
            except Exception: pass
            try: await asyncio.wait_for(stop_event.wait(), timeout=0.08)
            except asyncio.TimeoutError: pass
    async def spam_loop(stop_event: asyncio.Event):
        workers = [asyncio.create_task(_bot_spam_worker(bot, stop_event)) for bot in bots]
        try: await asyncio.gather(*workers, return_exceptions=True)
        finally:
            for w in workers:
                if not w.done(): w.cancel()
    await task_controller.start_task(chat_id, "spam", spam_loop)
    await update.message.reply_text(f"💬 𝐒𝐏𝐀𝐌 𝐀𝐂𝐓𝐈𝐕𝐄 ({len(bots)} bots)\\nStop: /stopspam")

async def stopspam_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or not update.message: return
    if await task_controller.stop_task(update.effective_chat.id, "spam"):
        await update.message.reply_text("🛑 𝐒𝐏𝐀𝐌 𝐒𝐓𝐎𝐏𝐏𝐄𝐃")
    else:
        await update.message.reply_text("No spam running here.")

async def bots_info_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    count = len([b for b in all_bot_instances if b is not None])
    uptime_str = get_uptime()
    await update.message.reply_text(f"🎀 Active bots: {count}\\n⏱️ Uptime: {uptime_str}")

# ══════════════════════════════════════════════════════════════════
#  DISPATCHER & EVENT HANDLER
# ══════════════════════════════════════════════════════════════════
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.from_user or not update.effective_chat: return
    chat_id = update.effective_chat.id
    known_chats.add(chat_id)
    uid = update.message.from_user.id
    msg = (update.message.text or "").strip()
    msg_lower = msg.lower()

    if chat_id in mute_chats and not is_admin(uid):
        try: await update.message.delete()
        except Exception: pass
        return

    if msg_lower.startswith("+allgcnc") or msg_lower.startswith("💦allgcnc") or msg_lower.startswith("+globalnc"):
        if is_admin(uid): await globalnc_cmd(update, context)
        return
    if msg_lower.startswith("/stopglobalnc") or msg_lower.startswith("+stopglobalnc"):
        if is_admin(uid): await stopglobalnc_cmd(update, context)
        return
    if msg_lower.startswith("+zalgonc") or msg_lower.startswith("💦zalgonc"):
        if is_admin(uid): await zalgonc_handler(update, context)
        return
    if msg_lower.startswith("+gradientnc") or msg_lower.startswith("💦gradientnc"):
        if is_admin(uid): await gradientnc_handler(update, context)
        return
    if msg_lower.startswith("+rnc") or msg_lower.startswith("💦rnc"):
        if is_admin(uid): await randnc_handler(update, context)
        return
    if msg_lower.startswith("+flamenc") or msg_lower.startswith("💦flamenc"):
        if is_admin(uid): await flamenc_handler(update, context)
        return
    if msg_lower.startswith("+spam") or msg_lower.startswith("💦spam"):
        if is_admin(uid): await spam_cmd(update, context)
        return

def _register_handlers(app):
    cmds = {
        "start": start_cmd,
        "help": help_cmd,
        "ping": ping_cmd,
        "status": ping_cmd,
        "stop": stop_cmd,
        "globalnc": globalnc_cmd,
        "allgcnc": globalnc_cmd,
        "stopglobalnc": stopglobalnc_cmd,
        "zalgonc": zalgonc_handler,
        "gradientnc": gradientnc_handler,
        "rnc": randnc_handler,
        "flamenc": flamenc_handler,
        "spam": spam_cmd,
        "stopspam": stopspam_cmd,
        "bots": bots_info_cmd,
    }
    for cmd, h in cmds.items():
        app.add_handler(CommandHandler(cmd, _dedup(h)))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, _dedup(message_handler)))

async def run_bots():
    global all_bot_instances, all_apps
    all_tokens = get_base_tokens()
    print(f"🚀 Starting {len(all_tokens)} bots... (LOST GOD GOD UPGRADED)")
    from telegram.request import HTTPXRequest
    req_cfg = HTTPXRequest(connection_pool_size=500, read_timeout=30, write_timeout=30)
    for token in all_tokens:
        if "YOUR_BOT" in token: continue
        try:
            app = Application.builder().token(token).request(req_cfg).build()
            _register_handlers(app)
            await app.initialize()
            await app.start()
            if app.updater:
                await app.updater.start_polling(drop_pending_updates=True)
            all_apps.append(app)
            all_bot_instances.append(app.bot)
            try:
                me = await app.bot.get_me()
                print(f"✅ @{me.username} Ready")
            except Exception:
                print("✅ Bot online")
        except Exception as e:
            print(f"❌ Error token {token[:15]}...: {e}")

    print(f"🎯 Fleet ready with {len(all_bot_instances)} bots. Uptime: {get_uptime()}")
    try:
        await asyncio.Event().wait()
    finally:
        for app in all_apps:
            try:
                await app.stop()
                await app.shutdown()
            except Exception:
                pass

if __name__ == "__main__":
    try:
        asyncio.run(run_bots())
    except KeyboardInterrupt:
        pass
'''

with open("public/lost_god_upgraded.py", "w", encoding="utf-8") as f:
    f.write(upgraded_code)

print("SUCCESS: public/lost_god_upgraded.py created successfully!")
