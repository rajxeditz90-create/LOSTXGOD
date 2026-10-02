# 🚀 LOST GOD • Easy Setup Guide (आसान तरीका)

Is zip file ko setup karne ke 2 sabse aasan tarike hain:

---

## 🌟 TARIQA 1: 24/7 Free Cloud Me Chalana (Sabse Best & Recommended)
*Isme na laptop on rakhna padega, na PC! Phone se bhi 24/7 saalo tak chalega.*

### Step 1: GitHub Par Upload Karein (Free)
1. [GitHub.com](https://github.com) par login karein (agar account nahi hai to 1 min me bana lein).
2. Upar **"+"** par click karke **"New repository"** par click karein.
3. Repository name likhein (jaise: `lostgod-bot-host`).
4. **"uploading an existing file"** par click karein aur is zip ke saare files drag-and-drop karke **Commit changes** dabayein.

### Step 2: Render.com Par 1-Click Deploy Karein (Free)
1. [Render.com](https://render.com) par free account banayein (GitHub se sign in ho jata hai).
2. Dashboard me **"New +"** dabayein aur **"Web Service"** chunein.
3. Apna GitHub repo `lostgod-bot-host` select karein.
4. Render automatically `Dockerfile` pehchan lega!
5. **Instance Type:** "Free" select karein aur niche **"Deploy Web Service"** dabayein.
6. 2 se 3 minute me aapko ek **Permanent Public Link** mil jayega (jaise: `lostgod-bot-host.onrender.com`).
   - Isme **kabhi 403 error nahi aayega**!
   - Poori duniya se koi bhi apna bot host kar sakega!

### Step 3: Apna Domain Connect Karein (Optional)
- Render Settings me jakar **"Custom Domains"** me apna domain daalein (jaise: `bot.yourdomain.com`).
- Apne domain registrar (GoDaddy, Namecheap, Cloudflare) me CNAME record daalein:
  - **Type:** `CNAME`
  - **Name:** `bot`
  - **Target:** `lostgod-bot-host.onrender.com`

---

## 💻 TARIQA 2: Apne Computer / Laptop / VPS Par Chalana

### Windows PC Par:
1. Is zip file ko Right Click karke **"Extract All"** karein.
2. Folder khol kar **`start.bat`** par double click karein!
3. Yeh automatically dependencies install karega aur browser me `http://localhost:3000` open kar dega!

*(Agar Node.js ya Python nahi hai, to pehle https://nodejs.org aur https://python.org download kar lein)*

### Linux / VPS / Mac Par:
Terminal me folder khol kar sirf yeh commands run karein:
```bash
chmod +x start.sh
./start.sh
```
Ya manual commands:
```bash
pip3 install python-telegram-bot==21.6 httpx aiohttp
npm install
npm start
```
Browser me `http://localhost:3000` kholein!
