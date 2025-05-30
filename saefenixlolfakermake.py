from telethon.sync import TelegramClient
import csv
import asyncio
from telethon.tl.functions.messages import ImportChatInviteRequest
import os
from telethon import types, utils, errors
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.account import UpdateStatusRequest
import base64
import aiohttp
import time

# API ma'lumotlari
api_id = 6810439
api_hash = '66ac3b67cce1771ce129819a42efe02e'

# Bot va referal ID
bot = "@CryptoBot"
refid = "CQoIAMp40qlH"
parol = "Огурец"

# Xevil API kaliti
with open(r"C:\join\xevilkey.csv", 'r') as f:
    reader = csv.reader(f)
    XEVIL_API_KEY = str(next(reader)[0])

# Telefon raqamlar
phonecsv = "phone"
with open(f'{phonecsv}.csv', 'r') as f:
    phlist = [row[0] for row in csv.reader(f)]

print(f'Jami Nomerlar: {len(phlist)}')

channels = ['I9ZGkbu4KE41NDVi']

def image2base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

async def img2txt(body):
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    form_data = {
        "key": XEVIL_API_KEY,
        "body": body,
        "method": "base64"
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
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    params = {
        "key": XEVIL_API_KEY,
        "id": code,
        'action': 'get'
    }
    for _ in range(5):
        async with aiohttp.request(
            method="GET",
            url="https://api.sctg.xyz/res.php",
            params=params,
            headers=headers
        ) as response:
            response_data = await response.text()
            if '|' not in response_data:
                print(response_data)
                await asyncio.sleep(1)
                continue
            status, result = response_data.split('|')
            if status != 'OK':
                return
            return result

async def process_account(phone):
    try:
        print(f"Login {phone}")
        client = TelegramClient(f"sessions/{phone}", api_id, api_hash)
        await client.start(phone)
        print(f"Tizimga kirdi: {phone}")
        await client(UpdateStatusRequest(offline=False))

        try:
            await client(ImportChatInviteRequest("I9ZGkbu4KE41NDVi"))
        except errors.FloodWaitError as e:
            print(f"FloodWaitError: {e.seconds} sekund kuting")

        username = await client.get_entity(bot)
        await client.send_message(username, f"/start {refid}")
        await asyncio.sleep(2)

        messages = await client.get_messages(username, limit=2)
        for message in messages:
            if message.photo:
                path = await message.download_media()
                print(f"{phone} uchun CAPTCHA rasmi: {path}")
                base64_body = image2base64(path)
                result_code = await img2txt(body=base64_body)
                if not result_code:
                    print("| CAPTCHA kodini olishda xatolik")
                    continue
                await asyncio.sleep(2)
                captcha_input = await get_result(code=result_code)
                print("CAPTCHA javobi:", captcha_input)
                if captcha_input:
                    await client.send_message(bot, captcha_input)
                os.remove(path)

        time.sleep(1)
        await client.send_message(username, parol)

        await client.disconnect()
        print(f"{phone} uchun jarayon tugadi")
    except Exception as e:
        print(f"Xato: {phone} -> {e}")

async def main():
    tasks = []
    for i in range(0, len(phlist), 10):  # 10 tadan parallel ishlaydi
        batch = phlist[i:i+10]
        tasks = [process_account(phone) for phone in batch]
        await asyncio.gather(*tasks)
        await asyncio.sleep(5)

asyncio.run(main())
