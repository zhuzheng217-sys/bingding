from datetime import datetime, timedelta
import requests
import sxtwl
import os
import pytz

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

# 月干
month_gan = tg[day.getMonthGZ().tg]

# 日干
day_gan = tg[day.getDayGZ().tg]

# 完整干支
month_gz = tg[day.getMonthGZ().tg]
month_gz += "子丑寅卯辰巳午未申酉戌亥"[day.getMonthGZ().dz]

day_gz = tg[day.getDayGZ().tg]
day_gz += "子丑寅卯辰巳午未申酉戌亥"[day.getDayGZ().dz]

print("月干:", month_gan)
print("日干:", day_gan)

# 条件判断
if month_gan in ["丙", "丁"] and day_gan in ["丙", "丁"]:

    webhook = os.environ["DINGTALK_WEBHOOK"]

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

    r = requests.post(webhook, json=data)

    print(r.text)

else:
    print("不符合条件")