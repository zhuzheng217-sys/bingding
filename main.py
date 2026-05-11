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

# =====================================
# 中国时区
# =====================================
tz = pytz.timezone('Asia/Shanghai')

# 明天
tomorrow = datetime.now(tz) + timedelta(days=1)

# =====================================
# 农历对象
# =====================================
day = sxtwl.fromSolar(
    tomorrow.year,
    tomorrow.month,
    tomorrow.day
)

# =====================================
# 天干地支
# =====================================
tg = "甲乙丙丁戊己庚辛壬癸"
dz = "子丑寅卯辰巳午未申酉戌亥"

# =====================================
# 农历中文月份/日期
# =====================================
cn_month = [
    "正月", "二月", "三月", "四月", "五月", "六月",
    "七月", "八月", "九月", "十月", "冬月", "腊月"
]

cn_day = [
    "初一", "初二", "初三", "初四", "初五",
    "初六", "初七", "初八", "初九", "初十",
    "十一", "十二", "十三", "十四", "十五",
    "十六", "十七", "十八", "十九", "二十",
    "廿一", "廿二", "廿三", "廿四", "廿五",
    "廿六", "廿七", "廿八", "廿九", "三十"
]

# =====================================
# 农历日期
# =====================================
lunar_month = cn_month[day.getLunarMonth() - 1]
lunar_day = cn_day[day.getLunarDay() - 1]

lunar_text = f"{lunar_month}{lunar_day}"

# =====================================
# 月柱
# =====================================
month_gan = tg[day.getMonthGZ().tg]
month_zhi = dz[day.getMonthGZ().dz]
month_gz = month_gan + month_zhi

# =====================================
# 日柱
# =====================================
day_gan = tg[day.getDayGZ().tg]
day_zhi = dz[day.getDayGZ().dz]
day_gz = day_gan + day_zhi

# =====================================
# 触发条件
#
# 月天干有：
#   丙 或 丁
#
# 日天干有：
#   丙 或 丁
# =====================================
matched = (
    month_gan in ["丙", "丁"]
    and
    day_gan in ["丙", "丁"]
)

# =====================================
# 钉钉机器人加签
# =====================================
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

# =====================================
# 消息内容
# =====================================
if matched:

    title = "🔴⚠️ 黄历提醒：丙丁触发"

    markdown_text = f"""
# 🔴⚠️ 黄历提醒

## 明天符合条件！

---

### 📅 日期信息

- 公历：{tomorrow.strftime('%Y-%m-%d')}
- 农历：{lunar_text}

---

### ☯ 干支信息

- 月柱：{month_gz}
- 日柱：{day_gz}

---

# ⚠️ 满足条件 ⚠️

## 丙丁月 + 丙丁日

请注意安排事项。
"""

else:

    title = "🟢 明日黄历正常"

    markdown_text = f"""
# 🟢 明日黄历正常

---

### 📅 日期信息

- 公历：{tomorrow.strftime('%Y-%m-%d')}
- 农历：{lunar_text}

---

### ☯ 干支信息

- 月柱：{month_gz}
- 日柱：{day_gz}

---

✅ 未触发提醒条件
"""

# =====================================
# 发送钉钉消息
# =====================================
data = {
    "msgtype": "markdown",
    "markdown": {
        "title": title,
        "text": markdown_text
    }
}

response = requests.post(url, json=data)

# =====================================
# 输出日志
# =====================================
print("========== 黄历提醒 ==========")
print("公历:", tomorrow.strftime('%Y-%m-%d'))
print("农历:", lunar_text)
print("月柱:", month_gz)
print("日柱:", day_gz)
print("是否触发:", matched)
print("状态码:", response.status_code)
print("返回:", response.text)
