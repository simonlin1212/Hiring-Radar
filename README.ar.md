# Hiring Radar

[中文](README.md) · [English](README.en.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Português](README.pt.md) · [Русский](README.ru.md) · **العربية**

<p align="center">
  <b>رادار مدعوم بالذكاء الاصطناعي لسوق العمل العالمي — يمسح الوظائف حول العالم وفي الصين، للبحث عن عمل ورصد إشارات القطاع.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-1.1.0-blue.svg" alt="version 1.1.0">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="MIT">
  <img src="https://img.shields.io/badge/global-9_ATS_+_4_boards-orange.svg" alt="Global">
  <img src="https://img.shields.io/badge/China-170_portals-red.svg" alt="China">
  <img src="https://img.shields.io/badge/deps-stdlib_only-lightgrey.svg" alt="stdlib">
</p>

---

## ما هذا

**Hiring Radar أداة بيانات توظيف أصلية للذكاء الاصطناعي — تمنح ذكاءك الاصطناعي (Claude Code / ChatGPT / أي وكيل) القدرة على قراءة الوظائف الرسمية المفتوحة من شركات حول العالم + الصين.** تقرأ مباشرةً نقاط النهاية العامة لأنظمة تتبّع المتقدمين (ATS) التي تستخدمها الشركات، وتجمع الوظائف في **بيانات منظَّمة** لتغذية ذكائك الاصطناعي. ليست موقع توظيف آخر يطلب التسجيل: تعمل محليًا، وأمر واحد يستعلم عن أي شركة في العالم، أو مجال كامل، أو يمسح عدة شركات — **بلا حساب وبلا إعداد**.

أنظمة ATS التي تستخدمها الشركات (Greenhouse / Ashby / Lever / Feishu Hire / Moka / Beisen…) تكشف **نفس نقاط نهاية JSON العامة التي تستدعيها واجهاتها الأمامية**، وتحمل الوصف الكامل للوظيفة والقسم والموقع وتاريخ النشر والراتب. يقرأ Hiring Radar تلك النقاط العامة بالضبط: سريع ونظيف وجاهز لتغذية الذكاء الاصطناعي.

استخدامان:

- 🔎 **البحث عن عمل / «أين يجري التوظيف» (الأساسي)**: أي الشركات توظّف الآن في مجال ما، وفي أي مدن، وبأي راتب.
- 📈 **إشارة مبكرة للقطاع / الاستثمار (ثانوي)**: غالبًا ما يكشف التوظيف الاستراتيجية قبل النتائج المالية بأشهر.

التغطية: **٩ أنظمة ATS دولية كبرى + ٤ منصّات عالمية للعمل عن بُعد + ١٧٠ بوابة رسمية لشركات صينية**. تغطية الصين (محلّلات عامة لـ Feishu Hire / Moka / Beisen + بوابات خاصة لـ Tencent/NetEase/JD/Baidu/ByteDance/Unitree) هي الفجوة التي تتركها معظم الأدوات الحالية.

**العلامات العالمية الكبرى تعمل باسم الشركة فقط**، مثل NVIDIA · OpenAI · Anthropic · Stripe · Databricks · Coinbase · Reddit · Discord · Cloudflare · Notion · Scale AI · Figure · Perplexity · 1X · Cohere · GitLab وغيرها.

> ⚠️ يقرأ **إعلانات الوظائف التي تنشرها الشركات بنفسها** — لا سِيَر ذاتية/بيانات شخصية أبدًا، ولا محتوى خلف تسجيل الدخول. استخدام شخصي، تردد منخفض، زائر مهذّب.

## ✨ المزايا

| الميزة | الوصف |
|---|---|
| **حسب الشركة (دوليًا)** | اسم الشركة وحده يكفي لفحص ٨ أنظمة ATS تلقائيًا (Greenhouse/Ashby/Lever/SmartRecruiters/Recruitee/Breezy/BambooHR/Personio)؛ عند الإصابة: وصف كامل + قسم + موقع + تاريخ + راتب |
| **لوحات العمل عن بُعد العالمية** | `--board` يمسح عدة شركات: RemoteOK / Remotive / WeWorkRemotely / WorkingNomads |
| **١٧٠ شركة صينية** | `--local`: محلّلات **عامة** لـ Feishu Hire / Moka / Beisen (إضافة شركة = إضافة سطر) + ٦ بوابات خاصة. ذكاء مُجسَّد / نماذج كبيرة / أشباه موصلات / سيارات / طاقة / كَمّي / متعددة الجنسيات / ألعاب |
| **مرشّح بالكلمات/الحداثة** | `--keyword a,b,c` (الفاصلة = أو؛ يبحث في العنوان/القسم/الموقع/الوصف/الراتب) · `--recent-days N` |
| **مخرجات منظَّمة موحّدة** | مخطط من ١٥ حقلًا؛ `--json` يُخرج كل شيء (بما فيه الوصف الكامل) لتغذية الذكاء الاصطناعي |
| **ملخّص في الطرفية** | افتراضيًا أعلى الشركات / الأقسام / المواقع + قائمة الوظائف |
| **مُوجَّه بالبيانات** | قائمة الشركات الصينية جدول بذور `companies.seed` — **إضافة شركة = سطر واحد بلا كود** |
| **مكتبة قياسية فقط** | سكربت بنقطة دخول واحدة، بلا تبعيات (Moka فقط يحتاج `pycryptodome`)، يعمل على أي `python3` |

## 🚀 البدء السريع

```bash
git clone https://github.com/simonlin1212/Hiring-Radar.git
cd Hiring-Radar
pip install pycryptodome      # اختياري، فقط للشركات الصينية على Moka

python3 hiring_radar.py --list             # سرد كل الشركات / اللوحات القابلة للاستعلام
```

```bash
# 1) دوليًا: اسم الشركة وحده يكفي (figure/1x/anthropic/openai/scale/nvidia مدمجة) أو افحص أي اسم تلقائيًا
python3 hiring_radar.py figure
python3 hiring_radar.py anthropic --keyword research
python3 hiring_radar.py --greenhouse <slug>          # تحديد ATS صراحةً
python3 hiring_radar.py --workday host,tenant,site

# 2) الصين: --local <key> (المفاتيح عبر --list)
python3 hiring_radar.py --local agibot --keyword robot      # AgiBot (Feishu)
python3 hiring_radar.py --local cambricon --keyword LLM     # Cambricon (Moka)
python3 hiring_radar.py --local dreame                      # Dreame (Beisen)
python3 hiring_radar.py --local tencent --keyword algorithm # Tencent (خاص)

# 3) اللوحات: «أين يجري التوظيف» عبر الشركات
python3 hiring_radar.py --board all --keyword "AI engineer"

# 4) مخرجات منظَّمة كاملة (مع الوصف الكامل) للتحليل
python3 hiring_radar.py --local zhipu --keyword LLM --json > out.json
```

**خيارات عامة**: `--keyword` · `--recent-days N` · `--limit N` · `--json` · `--list` · `--debug` · `--script <path>`

## 📋 حقول المخرجات

`title · company · dept · team · location · remote · type · date · date_updated · req_id · comp(الراتب) · jd(كامل) · url · apply_url · id` (١٥ حقلًا)

عادةً تتضمن GH / Ashby / Lever / Feishu / Moka / Beisen / Tencent / NetEase / JD / Baidu الوصف الكامل؛ أما Workday وبعض مستأجري Moka فعلى مستوى القائمة فقط (العنوان/القسم/الموقع/التاريخ). `--json` يُخرج كل شيء.

## 🌐 المصادر

**أنظمة ATS الدولية (فحص تلقائي بالاسم — ٩ أنظمة)**
Greenhouse · Ashby · Lever · Workday · SmartRecruiters · Recruitee · Breezy · BambooHR · Personio

العلامات الكبرى تعمل باسم الشركة فقط (كلها مُتحقَّق منها)، مثل:
**NVIDIA · OpenAI · Anthropic · Stripe · Databricks · Coinbase · Reddit · Discord · Cloudflare · Notion** · Scale AI · Figure · Perplexity · 1X · Cohere · GitLab …

**لوحات العمل عن بُعد العالمية (`--board`)**
RemoteOK · Remotive · WeWorkRemotely · WorkingNomads · `all`

**الصين — ١٧٠ شركة (`--local`، بوابات رسمية، جدول بذور)**
- **Feishu Hire**: Li Auto, XPeng, NIO, AgiBot, Galbot, RobotEra, Moonshot, MiniMax, Zhipu, Pony.ai, Hesai …
- **Moka**: Hypergryph, Perfect World, Biren, Cambricon, High-Flyer, Ubiquant, SHEIN, Bosch …
- **Beisen** (صناعات كبرى / سيارات / أجهزة منزلية / معدات ثقيلة): Dreame, Chery, Leapmotor, BOE, SANY …
- **خاصة**: Tencent, NetEase, JD, Baidu, ByteDance, Unitree

> القائمة الكاملة: `python3 hiring_radar.py --list`

## ➕ إضافة شركة = إضافة سطر (بلا كود)

قائمة الشركات الصينية في `parsers/companies.seed` (مفصولة بـ `|`)، تُحمَّل عند البدء. أضف سطرًا:

```
key | feishu | الشركة | نطاق-البوابة (مثل nio.jobs.feishu.cn)
key | moka   | الشركة | orgId | siteId   # كلاهما في رابط app.mokahr.com/social-recruitment/{orgId}/{siteId}
key | beisen | الشركة | slug             # البوابة {slug}.zhiye.com، مثل dreame
```

لإضافة مصدر جديد كليًا (كتابة محلّل) راجع [CONTRIBUTING.md](CONTRIBUTING.md).

## 📈 إشارة القطاع (ثانوي)

التوظيف **مؤشر مبكر**. مثلًا:

- توظيف مهندسي خطوط = الخط لا يزال يُبنى؛ ضمان الجودة/الصيانة = استعداد للإنتاج المستمر؛ ورديات ليلية = اقتراب رفع الإنتاج؛ فحص الوارد/جودة الموردين = إدماج موردين خارجيين.
- استخدم `--local <الشركة> --keyword factory,production,assembly` للجانب التصنيعي؛ و`--recent-days` للأحدث؛ وخذ **لقطات شهرية** للأسماء المهمة لتتبع الاتجاه.

> ⚠️ **التوظيف ≠ الإنتاج.** الوظائف «مدخلات» لا «مخرجات»؛ بينهما العائد والتوسّع وسلسلة التوريد. تعامل معها كإشارة لا كنصيحة استثمارية.

## ⚖️ الاستخدام المسؤول / الامتثال

أداة **شخصية / بحثية، محلية + مفتوحة المصدر**. استخدمها بمسؤولية:

- **إعلانات الوظائف فقط — لا سِيَر ذاتية / بيانات شخصية أبدًا.**
- **نقاط النهاية العامة بلا تسجيل دخول فقط**: عند جدار تسجيل / كابتشا / مكافحة روبوتات نشطة، **لا تتجاوزها**.
- **محليًا فقط**: بلا استضافة / رفع / خادم. عند إعادة نشر البيانات، قيّم الامتثال بنفسك.
- **تردد منخفض، زائر مهذّب**؛ بلا إعادة بيع تجاري. «مرئي علنًا» ≠ «حر في التجميع وإعادة النشر».

## ⚠️ إخلاء المسؤولية

1. **أنت تتحكم في بياناتك.** يعمل محليًا؛ لا يجمع ولا يرفع شيئًا.
2. **أنت تلتزم بشروط الأطراف الثالثة.** التزم بشروط كل منصة؛ بلا إزعاج أو إثقال لأنظمتها.
3. **إشارات لا حقائق.** بيانات التوظيف إشارة؛ وأحكام القطاع/الاستثمار على مسؤوليتك.

مُقدَّمة بموجب [رخصة MIT](LICENSE) «كما هي» دون أي ضمان.

## 🙋 المؤلف

**Simon Lin** · Douyin: Simon林 · WeChat: 硅基世纪

أداة محلية تجمع الوظائف الرسمية المفتوحة من شركات حول العالم وفي الصين. مرحبًا بطلبات الدمج لإضافة شركات / مصادر (راجع [CONTRIBUTING.md](CONTRIBUTING.md)).

## 📄 License

[MIT](LICENSE)
