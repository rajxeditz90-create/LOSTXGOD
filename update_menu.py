import re

menu_content = """╔═━─ 𓆩⚡𓆪 ─━═╗
『𓍼ֶָ֢˖ ࣪ꨄ 𝐋𝐎𝐒𝐓 𝐆𝐎𝐃 .་༘࿐』
╚═━─ 𖤐🐉𖤐 ─━═╝

╭━━━𓆩 🐉 𝐍𝐄𝐗𝐔𝐒 𝐂𝐎𝐑𝐄 𓆪━━━╮
│ ✦ 🤖 𝐁ᴏᴛ: 𝐀ᴍʀɪᴛ 𝐗 𝐌ᴇɴᴛᴀʟ ꨄ
│ 𖤐 👑 𝐎ᴡɴᴇʀ: 𝐏ʀɪᴍᴀʀʏ 𝐀ᴅᴍɪɴ ✧
│ ✦ ⚙️ 𝐏ʀᴇꜰɪx: [ + / 💦 / / ] ꨄ
│ 𖤐 🟢 𝐌ᴏᴅᴇ: 𝐔ʟᴛʀᴀ 𝐎ᴘᴇʀᴀᴛɪ𝐎ɴ ✧
│ ✦ 🤖 𝐅ʟᴇᴇᴛ: 𝐌ᴜʟᴛɪ-𝐁ᴏᴛ 𝐌ᴏᴅᴇ ꨄ
╰━━━༺❀༻━━━╯

╭━━━𓆩 🚀 𝐐𝐔𝐈𝐂𝐊 𝐒𝐓𝐀𝐑𝐓 𓆪━━━╮
│ ✦ 𝟏  𝐌ᴇɴᴜ     →  /help
│ 𖤐 𝟐  𝐓ʀʏ      →  +rnc hello
│ ✦ 𝟑  𝐇ᴀʟᴛ     →  /stop
│ 𖤐 𝟒  𝐒ᴛᴀᴛᴜꜱ   →  /bots
╰━━━༺❀༻━━━╯

╭━━━𓆩 🌀 𝐀𝐋𝐋 𝐍𝐂 𝐂𝐎𝐌𝐌𝐀𝐍𝐃𝐒 𓆪━━━╮
│ ✦ 🌐 +allgcnc <text>   ɢʟᴏʙᴀʟ ᴀʟʟ-ɢᴄ ɴᴄ
│ 𖤐 🛑 /stopglobalnc    ꜱᴛᴏᴘ ɢʟᴏʙᴀʟ ɴᴄ
│ ✦ 🎲 +rnc <text>       ʀᴀɴᴅᴏᴍ ɴᴀᴍᴇ ᴄʏᴄʟᴇ
│ 𖤐 🔥 +flamenc <text>   ғʟᴀᴍᴇ ɴᴀᴍᴇ ᴍᴏᴅᴇ
│ ✦ 🌙 +lunanc <text>     ʟᴜɴᴀ ɴᴀᴍᴇ ᴍᴏᴅᴇ
│ 𖤐 🌊 +ohyesnc <text>   ᴡᴀᴠᴇ ʀᴇʟᴀʏ ᴍᴏᴅᴇ
│ ✦ 💥 +aahnc <text>      ᴀᴅᴀᴘᴛɪᴠᴇ ʙᴜʀꜱᴛ
│ 𖤐 🌊 +horneync <text>  ᴡᴀᴛᴇʀ ʜʏᴘᴇʀғɪʀᴇ
│ ✦ 💎 +purenc <text>     ᴘᴜʀᴇ ɴᴀᴍᴇ ᴍᴏᴅᴇ
│ 𖤐 🥷 +stealthnc <text> ᴍɪᴄʀᴏ-ᴊɪᴛᴛᴇʀ ᴍᴏᴅᴇ
│ ✦ ⚡ +bhosdanc <text>   ᴇᴍᴏᴊɪ ʙᴜʀꜱᴛ ᴍᴏᴅᴇ
│ 𖤐 🔱 +areync <text>    ᴘᴇʀꜱᴏɴᴀʟ ɴᴀᴍᴇ ᴍᴏᴅᴇ
│ ✦ 🎩 +hatnc <text>      ʜᴀᴛ ꜱᴛʏʟᴇ ᴍᴏᴅᴇ
│ 𖤐 😭 +crync <text>     ᴄʀʏ ᴇᴍᴏᴊɪ ᴍᴏᴅᴇ
│ ✦ ☠️ +zalgonc <text>   ᴢᴀʟɢᴏ ɢʟɪᴛᴄʜ ᴍᴏᴅᴇ
│ 𖤐 🌈 +gradientnc <text> ɢʀᴀᴅɪᴇɴᴛ ᴄᴏʟᴏʀ ᴍᴏᴅᴇ
│ ✦ 🧠 +godnc <text>   𝐀ᴍʀɪᴛ ᴘᴇʀꜱᴏɴᴀʟ ᴍᴏᴅᴇ
│ 𖤐 🧠 +lostgodnc <text>   𝐀ᴍʀɪᴛ ɢʜᴏꜱᴛ ᴍᴏᴅᴇ
│ ✦ ⚡ +lostgodxnc <text>   𝐀ᴍʀɪᴛ ʟɪɢʜᴛ ᴍᴏᴅᴇ
│ 𖤐 🔄 +tripnc  +ultranc  +pairnc
│ ✦ 🔥 +infernc  +voidnc  +stormnc
│ 𖤐 🩸 +bloodnc  +divinenc  ʙʟɪᴛᴢ ᴘʀᴇꜱᴇᴛꜱ
│ ✦ 🔤 +boldnc  +italicnc  +cursivenc
│ 𖤐 ✍️ +bubblenc  +smallcapsnc  +flipnc
│ ✦ 🧠 +god1 +god2 +god3 +god4 +god5
│ 𖤐 +god6 +god7 +god8 +god9 +god10
│ 𖤐 ⛔ /stop  ꜱᴛᴏᴘ ᴀᴄᴛɪᴠᴇ ɴᴄ ᴄʏᴄʟᴇꜱ
╰━━━༺❀༻━━━╯

╭━━━𓆩 🎭 𝐀𝐍𝐈𝐌𝐀𝐓𝐈𝐎𝐍 𓆪━━━╮
│ ✦ +loading       ᴀɴɪᴍᴀᴛᴇᴅ ʟᴏᴀᴅɪɴɢ ʙᴀʀ
│ 𖤐 +spinner       ꜱᴘɪɴɴᴇʀ ᴡɪᴛʜ ʙʀᴀɴᴅ ʟᴀʙᴇʟꜱ
│ ✦ +countdown [N]  ᴄᴏᴜɴᴛᴅᴏᴡɴ ᴀɴɪᴍᴀᴛɪᴏɴ
│ 𖤐 +typewrite <text>  ʟᴇᴛᴛᴇʀ-ʙʏ-ʟᴇᴛᴛᴇʀ ᴛʏᴘᴇ
│ ✦ +glitch <text>  ɢʟɪᴛᴄʜ ᴛᴇxᴛ ᴀɴɪᴍᴀᴛɪᴏɴ
╰━━━༺❀༻━━━╯

╭━━━𓆩 😈 𝐅𝐀𝐊𝐄 𝐓𝐑𝐎𝐋𝐋 𓆪━━━╮
│ ✦ /fakeban @user   ғᴀᴋᴇ ʙᴀɴ ᴀɴɪᴍᴀᴛɪᴏɴ
│ 𖤐 /fakekick @user  ғᴀᴋᴇ ᴋɪᴄᴋ ᴀɴɪᴍᴀᴛɪᴏɴ
│ ✦ /fakewarn @user  ғᴀᴋᴇ ᴡᴀʀɴɪɴɢ ᴄᴏᴜɴᴛ
│ 𖤐 /fakedm @user    ғᴀᴋᴇ ᴀᴅᴍɪɴ ᴅᴍ ᴀʟᴇʀᴛ
│ ✦ +matrix @user    ᴍᴀᴛʀɪx-ꜱᴛʏʟᴇ ᴛʀᴏʟʟ
╰━━━༺❀༻━━━╯

╭━━━𓆩 💬 𝐌𝐄𝐒𝐒𝐀𝐆𝐄 & 𝐑𝐄𝐏𝐋𝐘 𓆪━━━╮
│ ✦ +spam <text>       ᴛᴇxᴛ ʟᴏᴏᴘ
│ 𖤐 /stopspam          ꜱᴛᴏᴘ ᴛᴇxᴛ ʟᴏᴏᴘ
│ ✦ +slide <text>      ʀᴇᴘʟʏ ᴍᴏᴅᴇ
│ 𖤐 +slidereply        ᴀᴜᴛᴏ ʀᴇᴘʟʏ ᴍᴏᴅᴇ
│ ✦ /stopslidereply    ꜱᴛᴏᴘ ꜱʟɪᴅᴇ ʀᴇᴘʟʏ
│ 𖤐 +autoreply         ᴀᴜᴛᴏ ʀᴇᴘʟʏ ᴛᴇxᴛ
│ ✦ /stopautoreply     ꜱᴛᴏᴘ ᴀᴜᴛᴏ ʀᴇᴘʟʏ
│ 𖤐 +targetreply       ᴛᴀʀɢᴇᴛ ʀᴇᴘʟʏ ᴍᴏᴅᴇ
│ ✦ /stoptargetreply   ꜱᴛᴏᴘ ᴛᴀʀɢᴇᴛ ʀᴇᴘʟʏ
╰━━━༺❀༻━━━╯

╭━━━𓆩 ❤️ 𝐑𝐄𝐀𝐂𝐓𝐈𝐎𝐍 𝐌𝐎𝐃𝐄𝐒 𓆪━━━╮
│ ✦ +autoreact  +heartreact  +boomreact
│ 𖤐 +customreact <emoji>  ᴄᴜꜱᴛᴏᴍ ʀᴇᴀᴄᴛɪᴏɴ
│ ✦ /stopreact            ᴇɴᴅ ᴀᴜᴛᴏ ʀᴇᴀᴄᴛ
╰━━━༺❀༻━━━╯

╭━━━𓆩 🖼️ 𝐌𝐄𝐃𝐈𝐀 𝐌𝐎𝐃𝐔𝐋𝐄𝐒 𓆪━━━╮
│ ✦ +aiimg <prompt>  ᴀɪ ɪᴍᴀɢᴇ ɢᴇɴᴇʀᴀᴛᴏʀ
│ 𖤐 +song <name>     ꜱᴏɴɢ ꜱᴇᴀʀᴄʜ + ᴀᴜᴅɪᴏ
│ ✦ /gcpfp [delay]   ɢʀᴏᴜᴘ ᴘʀᴏꜰɪʟᴇ ᴘɪᴄᴛᴜʀᴇ
│ 𖤐 /gcpfpadd  /gcpfpset  ᴘɪᴄ ᴍᴀɴᴀɢᴇʀ
│ ✦ /gcpfpstatus  /stopgcpfp  /gcpfpclear
│ 𖤐 /setmenuphoto  /setmenuvideo  /clearmenu
╰━━━༺❀༻━━━╯

╭━━━𓆩 🛡️ 𝐆𝐑𝐎𝐔𝐏 𝐂𝐎𝐍𝐓𝐑𝐎𝐋 𓆪━━━╮
│ ✦ /mute  /purge [count]  /leave
│ 𖤐 /restrict  /unrestrict  /gclist
│ ✦ /ncdel  /ncwar  /stopncwar
│ 𖤐 /globalstop  /globalmute  /globalunmute
│ ✦ /globalannounce <message>
╰━━━༺❀༻━━━╯

╭━━━𓆩 🔐 𝐀𝐃𝐌𝐈𝐍 & 𝐓𝐎𝐎𝐋𝐒 𓆪━━━╮
│ ✦ /ping  /status    𝟗𝟎-ᴅᴀʏ ᴜᴘᴛɪᴍᴇ & ʟᴀᴛᴇɴᴄʏ
│ 𖤐 /addsudo  /removesudo  /sudolist
│ ✦ /bots  /botname <name>
│ 𖤐 /panel  ɪɴᴛᴇʀᴀᴄᴛɪᴠᴇ ᴄᴏɴᴛʀᴏʟ ᴘᴀɴᴇʟ
│ ✦ /floodbypass on|off|status
│ 𖤐 /start  /help  ᴏᴘᴇɴ ᴛʜɪꜱ ᴅᴇᴄᴋ
╰━━━༺❀༻━━━╯

┈┉┅━❀꧁ 𓆩♡𓆪 ꧂❀━┅┉┈
𖤐 𝐍𝐂: 𝐀ᴍʀɪᴛ 𝐌ᴏᴅᴇ  •  𝐁ʀᴀɴᴅ: 𝐀ᴍʀɪᴛ 𝐗 𝐌ᴇɴᴛᴀʟ 𖤐
⋆｡°✩ ❝ 𝐃ᴇꜱɪɢɴᴇᴅ ꜰᴏʀ 𝐀ᴍʀɪᴛ 𝐗 𝐌ᴇɴᴛᴀʟ ❞ ✩°｡⋆"""

with open("public/lost_god_upgraded.py", "r", encoding="utf-8") as f:
    text = f.read()

# Build python literal representation
lines = menu_content.splitlines()
code_lines = ["_MENU_TEXT = (\n"]
for line in lines:
    escaped = line.replace('\\', '\\\\').replace('"', '\\"')
    code_lines.append(f'    "{escaped}\\n"\n')
code_lines.append(")\n")
new_menu_block = "".join(code_lines)

# Find start and end of _MENU_TEXT in text
start_idx = text.find("_MENU_TEXT = (")
if start_idx != -1:
    end_idx = text.find("\n\n\ndef ", start_idx)
    if end_idx != -1:
        text = text[:start_idx] + new_menu_block + "\n\n" + text[end_idx+3:]
        with open("public/lost_god_upgraded.py", "w", encoding="utf-8") as f:
            f.write(text)
        print("Successfully replaced _MENU_TEXT with requested design!")
    else:
        print("Could not find end of _MENU_TEXT block")
else:
    print("Could not find _MENU_TEXT = (")
