from datetime import datetime, timedelta
import requests
import sxtwl
import os
import pytz
import time
import hmac
import hashlib
import base64
import urllib.parse

# 中国时区
tz = pytz.timezone('Asia/Shanghai')

# 明天
tomorrow = datetime.now(tz) + timedelta(days=1)

# 农历
day = sxtwl.fromSolar(
    tomorrow.year,
    tomorrow.month,
    tomorrow.day
)

tg = "甲乙丙丁戊己庚辛壬癸"
dz = "子丑寅卯辰巳午未申酉戌亥"

# 月干
month_gan = tg[day.getMonthGZ().tg]

# 日干
day_gan = tg[day.getDayGZ().tg]

# 月柱
month_gz = tg[day.getMonthGZ().tg] + dz[day.getMonthGZ().dz]

# 日柱
day_gz = tg[day.getDayGZ().tg] + dz[day.getDayGZ().dz]

print("月干:", month_gan)
print("日干:", day_gan)

# 判断条件
if month_gan in ["丙", "丁"] and day_gan in ["丙", "丁"]:

    webhook = os.environ["DINGTALK_WEBHOOK"]
    secret = os.environ["DINGTALK_SECRET"]

    # ===== 加签 =====
    timestamp = str(round(time.time() * 1000))

    string_to_sign = f'{timestamp}\n{secret}'

    hmac_code = hmac.new(
        secret.encode('utf-8'),
        string_to_sign.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()

    sign = urllib.parse.quote_plus(
        base64.b64encode(hmac_code)
    )

    url = f"{webhook}&timestamp={timestamp}&sign={sign}"

    # ===== 消息 =====
    text = f"""
黄历提醒

明天符合条件：

日期：{tomorrow.strftime('%Y-%m-%d')}

月柱：{month_gz}
日柱：{day_gz}

满足：
丙丁月 + 丙丁日
"""

    data = {
        "msgtype": "text",
        "text": {
            "content": text
        }
    }

    r = requests.post(url, json=data)

    print(r.text)

else:
    print("不符合条件")
