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

# 农历对象
day = sxtwl.fromSolar(
    tomorrow.year,
    tomorrow.month,
    tomorrow.day
)

# 天干地支
tg = "甲乙丙丁戊己庚辛壬癸"
dz = "子丑寅卯辰巳午未申酉戌亥"

# 农历月份/日期
cn_month = [
    "正月","二月","三月","四月","五月","六月",
    "七月","八月","九月","十月","冬月","腊月"
]

cn_day = [
    "初一","初二","初三","初四","初五","初六","初七","初八","初九","初十",
    "十一","十二","十三","十四","十五","十六","十七","十八","十九","二十",
    "廿一","廿二","廿三","廿四","廿五","廿六","廿七","廿八","廿九","三十"
]

lunar_month = cn_month[day.getLunarMonth() - 1]
lunar_day = cn_day[day.getLunarDay() - 1]

lunar_text = f"{lunar_month}{lunar_day}"

# 月柱
month_gan = tg[day.getMonthGZ().tg]
month_zhi = dz[day.getMonthGZ().dz]
month_gz = month_gan + month_zhi

# 日柱
day_gan = tg[day.getDayGZ().tg]
day_zhi = dz[day.getDayGZ().dz]
day_gz = day_gan + day_zhi

# 判断条件
matched = (
    month_gan in ["丙", "丁"]
    and
    day_gan in ["丙", "丁"]
)

# ===== 钉钉加签 =====

webhook = os.environ["DINGTALK_WEBHOOK"]
secret = os.environ["DINGTALK_SECRET"]

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

if matched:

    markdown_text = f"""
# ⚠️ 黄历提醒 ⚠️

<font color="#FF0000">

## 明天符合条件！

- 公历：{tomorrow.strftime('%Y-%m-%d')}
- 农历：{lunar_text}

---

- 月柱：{month_gz}
- 日柱：{day_gz}

---

### 满足：

# 丙丁月 + 丙丁日

⚠️⚠️⚠️ 请注意 ⚠️⚠️⚠️

</font>
"""

else:

    markdown_text = f"""
# 明日黄历信息

- 公历：{tomorrow.strftime('%Y-%m-%d')}
- 农历：{lunar_text}

---

- 月柱：{month_gz}
- 日柱：{day_gz}

---

✅ 未触发提醒条件
"""

data = {
    "msgtype": "markdown",
    "markdown": {
        "title": "黄历提醒",
        "text": markdown_text
    }
}

# ===== 发送 =====

r = requests.post(url, json=data)

print(r.text)
