#randombeast
import sys
import json
import base64
import asyncio
from urllib.parse import unquote
from telethon.tl.functions.account import UpdateStatusRequest
from wand.image import Image
from wand.color import Color
from telethon.tl.functions.messages import ImportChatInviteRequest
import aiohttp
import fake_useragent
from loguru import logger
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import InputUser, InputBotAppShortName
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import RequestAppWebViewRequest
import csv
logger.remove()
logger.add(
    sink=sys.stdout,
    format="<white>{time:YYYY-MM-DD HH:mm:ss}</white> | <level>{level: <8}</level> | <cyan><b>{line}</b></cyan> - <white><b>{message}</b></white>"
)
logger = logger.opt(colors=True)

with open(r"C:\join\xevilkey.csv", 'r') as f:
    reader = csv.reader(f)
    XEVIL_API_KEY = str(next(reader)[0])

with open(r"C:\join\beastid.csv", 'r') as f:
    reader = csv.reader(f)
    ID = str(next(reader)[0])
print(f"QATNASHILAYOTAN GIVEAWAY - {ID}")

with open(r"C:\join\beasbatchsize.csv", 'r') as f:
    reader = csv.reader(f)
    beastbatchsize = int(next(reader)[0])
print(f"Bir vaqtda bajariladian raqamlar - {beastbatchsize}")

with open(r"C:\join\beastidochiqkanal.csv", 'r') as f: 
    CHANNELS = [row[0] for row in csv.reader(f)]

with open(r"C:\join\beastyopiqkanal.csv", 'r') as f: 
    YOPIQCHANNELS = [row[0] for row in csv.reader(f)]


# not used
async def get_challenge_token(start_param: str, http_client: aiohttp.ClientSession):
    sitekey = "ysc1_aEfRqT3rn5Ky2KdQjZWZNdy8cscKDTi9xTIz4qLPa7b6d980"
    captcha_url = f"https://randombeast.win/user/draws/drawjoin/{start_param}&sitekey={sitekey}"

    response = await http_client.get(f"http://localhost:5000/captcha?url={captcha_url}")
    if not response.ok:
        return

    data = await response.json()
    task_id = data['task_id']

    logger.info(f"Generating challenge token")
    attempt = 0
    while attempt <= 30:
        response = await http_client.get(f"http://localhost:5000/result?id={task_id}")
        if not response.ok:
            return

        data_text = await response.text()
        print(data_text)
        if data_text != "CAPTCHA_NOT_READY":
            data = json.loads(data_text)
            challenge_token = data['value']
            elapsed_time = data['elapsed_time']

            if challenge_token == "CAPTCHA_FAIL":
                return

            logger.success(f"Token was generated in <le>{elapsed_time}</le> seconds")
            return challenge_token

        await asyncio.sleep(1.5)

        attempt += 1


###


def svg2base64(svg_data):
    with Image(blob=svg_data.encode('utf-8'), format='svg', background=Color("transparent")) as img:
        img.format = 'png'
        png_blob = img.make_blob()
        png_base64 = base64.b64encode(png_blob).decode('utf-8')
        data_url = f"data:image/png;base64,{png_base64}"
        return data_url


async def img2txt(body):
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    form_data = {
        "key": XEVIL_API_KEY,
        "body": body,
        "method": base64
    }
    async with aiohttp.request(
            method="POST",
            url="https://api.sctg.xyz/in.php",
            data=form_data,
            headers=headers
    ) as response:
        response_data = await response.text()
        if '|' not in response_data:
            print(response_data)
            return

        status, code = response_data.split('|')
        if status != 'OK':
            return

        return code


async def get_result(code):
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    params = {
        "key": XEVIL_API_KEY,
        "id": code,
        'action': 'get'
    }

    timeout = 20  # sekund
    elapsed = 0
    while elapsed < timeout:
        async with aiohttp.request(
                method="GET",
                url="https://api.sctg.xyz/res.php",
                params=params,
                headers=headers
        ) as response:
            response_data = await response.text()
            if '|' not in response_data:
                await asyncio.sleep(1)
                elapsed += 1
                continue

            status, result = response_data.split('|')
            if status == 'OK':
                return result

        await asyncio.sleep(1)
        elapsed += 1

    logger.warning("CAPTCHA 20 soniyada yechilmadi, davom etilyapti...")
    return None

import random

def divide_batches(accounts_list, batch_size):
    """
    Divide accounts into batches based on custom invite strategy:
    - First batch_size accounts run without inviteCode
    - As soon as an inviteCode is obtained, use it for the next 4 * batch_size accounts
    - Then again skip one batch (without inviteCode), then use same/new code for next 4 batches, and so on
    """
    batches = []
    n = len(accounts_list)
    i = 0
    invite_period = 4
    use_invite = False
    invite_code = None

    while i < n:
        current_batch = accounts_list[i:i + batch_size]
        batches.append({
            "accounts": current_batch,
            "use_invite": use_invite,
            "invite_code": invite_code,
        })

        if use_invite:
            invite_period -= 1
            if invite_period == 0:
                # after 4 batches, reset
                use_invite = False
                invite_period = 4
        else:
            if invite_code is None:
                # this is first batch (no invite)
                pass
            else:
                use_invite = True

        i += batch_size

    return batches




async def participate(tg_client: TelegramClient, name, invite_code=None):
    async with tg_client:
        bot_entity = await tg_client.get_entity("randombeast_bot")
        bot = InputUser(user_id=bot_entity.id, access_hash=bot_entity.access_hash)
        app = InputBotAppShortName(bot_id=bot, short_name="devapp")

        web_view = await tg_client(
            RequestAppWebViewRequest(
                peer=bot,
                app=app,
                platform="android",
                start_param=ID,
                write_allowed=True
            )
        )

        init_data = unquote(web_view.url.split('tgWebAppData=', maxsplit=1)[1].split('&tgWebAppVersion', maxsplit=1)[0])
        await tg_client.start()
        await tg_client(UpdateStatusRequest(offline=False))
        for channel in CHANNELS:
            try:
                await tg_client(JoinChannelRequest(channel))
                await asyncio.sleep(1)
                logger.success(f"<lm>{name}</lm> | Kanalga muvaffaqiyatli qo'shildi <lc>{channel}</lc>")
            except Exception as e:
                logger.error(
                    f"<lm>{name}</lm> | "
                    f"Error while joining <lc>{channel}</lc>: <lr>{e}</lr>"
                )
        for yopiq_link in YOPIQCHANNELS:
            try:
                await tg_client(ImportChatInviteRequest(yopiq_link)) 
                logger.success(f"<lm>{name}</lm> | Kanalga muvaffaqiyatli qo'shildi <lc>{yopiq_link}</lc>")
            except Exception as e:
                logger.error(
                    f"<lm>{name}</lm> | "
                    f"Error while joining <lc>{yopiq_link}</lc>: <lr>{e}</lr>"
                )

        

    headers = {
        'accept': 'application/json',
        'accept-language': 'ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'origin': 'https://randombeast.win',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'sec-ch-ua': '"Microsoft Edge";v="134", "Chromium";v="134", "Not:A-Brand";v="24", "Microsoft Edge WebView2";v="134"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': fake_useragent.UserAgent(platforms=["mobile"]).random,
    }

    async with aiohttp.ClientSession(headers=headers) as http_client:
        response = await http_client.get(F"https://randombeast.win/api/draw/getTracking?trackingCode={ID}")
        if response.ok:
            data = await response.json()
            draw_id = data.get("drawId")
            if draw_id:
                headers["referer"] = f"https://randombeast.win/user/draws/drawjoin/{draw_id}"
            
        else:
            logger.warning(f"<lm>{name}</lm> | Tekshirish holati: <lg>{response.status}</lg>")
        json_data = {
            "initData": init_data
        }
        for _ in range(2): response = await http_client.post("https://randombeast.win/api/auth/verify", json=json_data)
        
        attempt = 0
        max_attempts = 3
        success = False

        while attempt < max_attempts and not success:
            attempt += 1
            logger.info(f"<lm>{name}</lm> | Givga qatnashish {attempt}-urinish")

            # Har safar yangi captcha olish
            json_data = {
                "drawId": draw_id,
                "initData": init_data
            }
            response = await http_client.post("https://randombeast.win/api/draw/getdraw", json=json_data)
            if not response.ok:
                logger.error(f"<lm>{name}</lm> | Yangi CAPTCHA olishda xatolik")
                continue

            data = await response.json()
            checkin_token = data.get('checkinToken')
            captcha = data.get('captcha', {})

            captcha_svg = captcha.get('svg')
            captcha_token = captcha.get('token')

            if not captcha_svg or not captcha_token:
                logger.error(f"<lm>{name}</lm> | CAPTCHA ma'lumotlari yetarli emas")
                continue

            base64_body = svg2base64(svg_data=captcha_svg)
            result_code = await img2txt(body=base64_body)
            await asyncio.sleep(delay=1)
            captcha_input = await get_result(code=result_code)
            if not captcha_input:
                logger.warning(f"<lm>{name}</lm> | CAPTCHA yechilmadi, keyingi urinish...")
                continue
            
            if invite_code:
                #invite_codelik
                json_data = {
                    'drawId': draw_id,
                    'initData': init_data,
                    'inviteCode': invite_code,
                    'captchaToken': captcha_token,
                    'captchaInput': captcha_input,
                    'challengeToken': None,
                    'checkinToken': checkin_token,
                    'livenessCheckHash': None,
                    'trackingCode': None
                }
            else:
                # invite_codesiz
                json_data = {
                    'drawId': draw_id,
                    'initData': init_data,
                    'captchaToken': captcha_token,
                    'captchaInput': captcha_input,
                    'challengeToken': None,
                    'checkinToken': checkin_token,
                }

            response = await http_client.post("https://randombeast.win/api/draw/checkin", json=json_data)
            logger.info(f"<lm>{name}</lm> | Givga qatnashish holati: <lg>{response.status}</lg>")

            if not response.ok:
                continue

            data = await response.json()
            success = data.get('success', False)
            message = data.get('message', '')

            if success:
                logger.success(f"<lm>{name}</lm> | <lc>{ID}</lc> Muvaffaqiyatli qatnashdi")
                with open(f"{ID}.csv", 'a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow([name])
                    
                json_data = {
                    "action": "generateInviteLink",
                    "drawId": draw_id,
                    "initData": init_data
                }
                    
                response = await http_client.post("https://randombeast.win/api/draw/invitelink", json=json_data)
                if response.ok:
                    result = await response.json()
                    import re
                    link = result["link"]
                    match = re.search(r'invite_([A-Za-z0-9]+)', link)
                    if match:
                        code = match.group(1)
                        invite_code = code
                        return invite_code 
                    return True
                return None

            logger.error(f"<lm>{name}</lm> | Xabar: <lr>{message}</lr>")

        return False

async def main():
    import random

    with open("accounts.json", encoding="utf-8") as f:
        accounts_data = json.load(f)

    accounts_list = list(accounts_data.items())
    batch_size = beastbatchsize
    import csv
    def load_used_names(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return set(line.strip() for line in f if line.strip())
        except FileNotFoundError:
            return set()

    used_names = load_used_names(f"{ID}.csv")

    batches = divide_batches(accounts_list, batch_size)
    total_results = []
    global_invite_code = None

    for idx, batch in enumerate(batches):
        tasks = []

        logger.info(f"🧩 {idx+1}-batch ishlayapti | InviteCode: {batch['invite_code'] or 'Yo‘q'}")

        for name, session_string in batch["accounts"]:
            if name in used_names:
                logger.success(f"<lr>{name}</lr> allaqachon qatnashgan, o'tkazildi")
                continue

            tg_client = TelegramClient(
                StringSession(session_string),
                api_id=6810439,
                api_hash="66ac3b67cce1771ce129819a42efe02e"
            )
            await tg_client.start()
            await tg_client(UpdateStatusRequest(offline=False))

            # participate() endi invite_code qabul qiladi
            tasks.append(participate(tg_client, name, batch.get("invite_code")))

        results = await asyncio.gather(*tasks)
        total_results.extend(results)

        # Yangi invite_code olish (agar qatnashgan bo‘lsa)
        successful_codes = [r for r in results if r]
        if successful_codes:
            global_invite_code = random.choice(successful_codes)
            for b in batches:
                if b["invite_code"] is None:
                    b["invite_code"] = global_invite_code

    muvaffaqiyatli = sum(bool(r) for r in total_results)
    logger.info(f"<le>{muvaffaqiyatli}</le>/<ly>{len(total_results)}</ly> ta akkaunt muvaffaqiyatli qatnashdi")

if __name__ == '__main__':
    asyncio.run(main())
