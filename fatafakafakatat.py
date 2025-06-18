import requests
from licensing.methods import Helpers
def color(text, color_code):
    color_map = {
        "red": "91",
        "green": "92",
        "yellow": "93",
        "blue": "94",
        "magenta": "95",
        "cyan": "96",
        "white": "97",
        "bold_white": "1;97"
    }
    code = color_map.get(color_code, "97")
    return f"\033[{code}m{text}\033[0m"
url = "https://raw.githubusercontent.com/Enshteyn40/crdevice/refs/heads/main/randomize_3.csv"
response = requests.get(url)
lines = response.text.splitlines()
hash_values_list = [line.strip() for line in lines]

def GetMachineCode():
    return Helpers.GetMachineCode(v=2)

machine_code = GetMachineCode()
print(color(machine_code, "white"))

if machine_code in hash_values_list:
    import base64
    import asyncio
    import csv
    import ssl
    import time
    import subprocess
    from urllib.parse import unquote
    from termcolor import colored
    from telethon import TelegramClient
    from telethon.sessions import StringSession
    from telethon.tl.types import InputUser, InputBotAppShortName
    from telethon.tl.functions.messages import RequestAppWebViewRequest, ImportChatInviteRequest
    from telethon.tl.functions.channels import JoinChannelRequest
    import aiohttp
    import aiohttp_proxy

    # 📁 Fayllarni o'qish
    with open(r"C:\join\proxy.csv", 'r') as f:
        reader = csv.reader(f)
        ROTATED_PROXY = next(reader)[0]

    givs = []
    bot_mapping = {}
    with open(r"C:\join\randogiv.csv", 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) > 1:
                start_param = row[0].strip()
                bot_username = row[1].strip()
                givs.append(start_param)
                bot_mapping[start_param] = bot_username

    with open(r"C:\join\randolimit.csv", 'r') as f:
        reader = csv.reader(f)
        limituzz = int(next(reader)[0])

    with open(r"C:\join\ranochiqkanal.csv", 'r') as f:
        premium_channels = [row[0].strip() for row in csv.reader(f)]

    with open(r"C:\join\ranyopiqkanal.csv", 'r') as f:
        yopiq_channels = [row[0].strip() for row in csv.reader(f)]

    channels = premium_channels + yopiq_channels

    # 🔧 Asosiy ish funksiyasi
    async def run(phone, start_param, channels, token):
        api_id = 22962676
        api_hash = '543e9a4d695fe8c6aa4075c9525f7c57'
        tg_client = TelegramClient(f"../sessions/{phone}", api_id, api_hash)
        await tg_client.connect()
        if not await tg_client.is_user_authorized():
            print(colored(f"{phone} | ❌ Sessiya mavjud emas", "red"))
            return

        async with tg_client:
            me = await tg_client.get_me()
            name = phone

            for yopiq_link in yopiq_channels:
                try:
                    await tg_client(ImportChatInviteRequest(yopiq_link))
                    time.sleep(limituzz)
                    print(colored(f"{name} | Kanalga a'zo bo‘ldi {yopiq_link}", "green"))
                except Exception as e:
                    print(colored(f"{name} | ❌ Yopiq kanal xatolik: {e}", "red"))

            for ochiq_link in premium_channels:
                try:
                    await tg_client(JoinChannelRequest(ochiq_link))
                    time.sleep(limituzz)
                    print(colored(f"{name} | Kanalga a'zo bo‘ldi {ochiq_link}", "green"))
                except Exception as e:
                    print(colored(f"{name} | ❌ Ochiq kanal xatolik: {e}", "red"))

            bot_username = bot_mapping.get(start_param)
            if not bot_username:
                print(colored(f"❌ Giv uchun bot topilmadi: {start_param}", "yellow"))
                return

            try:
                bot_entity = await tg_client.get_entity(bot_username)
                bot = InputUser(user_id=bot_entity.id, access_hash=bot_entity.access_hash)
                bot_app = InputBotAppShortName(bot_id=bot, short_name="JoinLot")

                web_view = await tg_client(
                    RequestAppWebViewRequest(
                        peer=await tg_client.get_input_entity('me'),
                        app=bot_app,
                        platform="android",
                        write_allowed=True,
                        start_param=start_param
                    )
                )

                init_data = unquote(web_view.url.split('tgWebAppData=', 1)[1].split('&tgWebAppVersion')[0])

                headers = {
                        'Host': 'randomgodbot.com',
                        'Accept': '*/*',
                        'Accept-Language': 'ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7',
                        'Cache-Control': 'no-cache',
                        'Connection': 'keep-alive',
                        'Pragma': 'no-cache',
                        'Referer': f'https://randomgodbot.com/join/?tgWebAppStartParam={start_param}',
                        'Sec-Fetch-Dest': 'empty',
                        'Sec-Fetch-Mode': 'cors',
                        'Sec-Fetch-Site': 'same-origin',
                        "User-Agent": "Mozilla/5.0 (Linux; Android 13; SAMSUNG SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/21.0 Chrome/114.0.5735.131 Mobile Safari/537.36"
                    }

                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                proxy_conn = aiohttp_proxy.ProxyConnector(ssl_context=ssl_context).from_url(ROTATED_PROXY) if ROTATED_PROXY else None
                async with aiohttp.ClientSession(headers=headers, connector=proxy_conn) as http_client:
                    try:
                        http_client.headers.add('Host', 'randomgodbot.com')
                        encoded_init_data = base64.b64encode(init_data.encode()).decode()
                        url = f"https://randomgodbot.com/lot_join?userId={me.id}&startParam={start_param}&id={encoded_init_data}&token={token}"
                        response = await http_client.get(url=url, ssl=False)
                        response.raise_for_status()
                        response_json = await response.json()
                        description = response_json.get("description", "")
                        result = response_json.get("result", "")
                        ok = response_json.get("ok", False)
                        if description == "ALREADY_JOINED":
                            print(colored(f"{name} | ❕ Allaqachon qatnashgan", "blue"))
                            with open("danludanvodka.csv", "a", newline='', encoding='utf-8') as f:
                                csv.writer(f).writerow([phone])
                        elif ok and result == "success":
                            print(colored(f"{name} | ✅ Givga muvaffaqiyatli qo‘shildi", "green")) 
                            with open("danludanvodka.csv", "a", newline='', encoding='utf-8') as f:
                                csv.writer(f).writerow([phone])
                        else:
                            print(colored(f"{name} | ⚠️ Giv javobi: {response_json}", "yellow"))
                    except Exception as err:
                            print(colored(f"{name} | Giv uchun aynan so'rovda xatolik: {err}", "yellow"))
            except Exception as err:
                print(colored(f"{name} | ❌ Giv so‘rov xatoligi: {err}", "red"))

    # 🔄 Batch ishlovchi
    async def process_batch(batch_phones, batch_givs, batch_tokens):
        if not (len(batch_phones) == len(batch_givs) == len(batch_tokens)):
            print(colored("❌ Batch uzunliklari teng emas!", "red"))
            return
        tasks = []
        for phone, giv, token in zip(batch_phones, batch_givs, batch_tokens):
            tasks.append(run(phone, giv, channels, token))
        await asyncio.gather(*tasks)

    # ▶️ Asosiy boshqaruvchi
    async def main():
        global givs
        batch_size = 4
        phonecsv = "../phone"
        skipcsv = "captcthcarandomise.csv"

        with open(f"{phonecsv}.csv", 'r') as f:
            phones = [line.strip() for line in f if line.strip()]

        try:
            with open(skipcsv, 'r') as f:
                skipped_phones = set(line.strip() for line in f if line.strip())
        except FileNotFoundError:
            skipped_phones = set()

        filtered_phones = [phone for phone in phones if phone not in skipped_phones]

        # givs ni barcha telefonlarga moslashtirish
        if len(givs) == 1:
            givs = givs * len(filtered_phones)
        elif len(givs) < len(filtered_phones):
            while len(givs) < len(filtered_phones):
                givs += givs
            givs = givs[:len(filtered_phones)]

        for i in range(0, len(filtered_phones), batch_size):
            batch_phones = filtered_phones[i:i + batch_size]
            batch_givs = givs[i:i + batch_size]

            if len(batch_phones) == 0 or len(batch_givs) == 0:
                print(colored("❌ Batchda raqam yoki giv yo‘q — o‘tkazib yuborildi", "red"))
                continue

            needed_tokens = len(batch_phones)
            tokens = []

            while len(tokens) < needed_tokens:
                print(colored(f"🔄 Token yetarli emas ({len(tokens)}/{needed_tokens}) — generator ishga tushyapti...", "yellow"))
                subprocess.run(["uv", "run", "generatorrandom.py", "--count", str(needed_tokens), "--part", str(needed_tokens)], check=True)
                with open("tokens.txt", "r", encoding="utf-8") as f:
                    tokens = [line.strip() for line in f if line.strip()]

            batch_tokens = tokens[:needed_tokens]
            tokens = tokens[needed_tokens:]

            with open("tokens.txt", "w", encoding="utf-8") as f:
                f.writelines(t + "\n" for t in tokens)

            print(colored(f"▶️ Batch: {len(batch_phones)} ta raqam uchun ishga tushdi", "cyan"))
            await process_batch(batch_phones, batch_givs, batch_tokens)

    if __name__ == '__main__':
        asyncio.run(main())
else:
    print(color("Kodni aktivlashtirish uchun @Enshteyn40 ga murojat qiling", "magenta"))
