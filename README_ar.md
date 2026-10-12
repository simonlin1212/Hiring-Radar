<p align="center"><a href="README.md">简体中文</a> | <a href="README_en.md">English</a> | <a href="README_ko.md">한국어</a> | <a href="README_es.md">Español</a> | <a href="README_fr.md">Français</a> | <a href="README_de.md">Deutsch</a> | <a href="README_pt.md">Português</a> | <a href="README_ru.md">Русский</a> | <b>العربية</b></p>

<h1 align="center">Hiring Radar</h1>

<p align="center">
  <b>رادار لسوق العمل العالمي مدعوم بالذكاء الاصطناعي — يرصد الوظائف المفتوحة حول العالم وفي الصين، للبحث عن عمل وقراءة إشارات القطاعات وأبحاث السوق.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-2.0.0-blue.svg" alt="version 2.0.0">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="MIT">
  <img src="https://img.shields.io/badge/global-24_ATS_+_12_sources-orange.svg" alt="Global">
  <img src="https://img.shields.io/badge/China-170_portals-red.svg" alt="China">
  <img src="https://img.shields.io/badge/MCP-supported-purple.svg" alt="MCP">
  <img src="https://img.shields.io/badge/deps-stdlib_only-lightgrey.svg" alt="stdlib">
</p>

---

## ما هذا

**Hiring Radar أداة بيانات توظيف مصممة للذكاء الاصطناعي — تتيح لمساعدك الذكي (Claude Code / Codex / ChatGPT / أي وكيل) قراءة الوظائف الرسمية المفتوحة لدى الشركات حول العالم وفي الصين.** تقرأ أنظمة تتبع المتقدمين (ATS) التي تستخدمها الشركات ومصادر الوظائف العامة عبر واجهاتها العلنية، وتحوّل الوظائف إلى **بيانات منظمة بحقول موحدة**. تعمل محليًا؛ أمر واحد يستعلم عن شركة أو دولة أو وظيفة، **بلا حساب ولا إعداد**.

ثلاثة استخدامات:

- 🔎 **البحث عن عمل / «من يوظّف الآن؟»**: أي الشركات توظّف في مجال ما الآن، وفي أي المدن، وبأي راتب.
- 📊 **أبحاث السوق / فرص المنتجات**: سحب شرائح كاملة حسب الدولة والوظيفة والفترة لمعرفة ما يدفع السوق المال لتوظيفه (جديد في v2).
- 📈 **إشارة مبكرة للقطاع / الاستثمار**: كثيرًا ما يكشف التوظيف الاستراتيجية قبل النتائج المالية بأشهر. انظر «إشارة القطاع» أدناه.

**العلامات العالمية الكبرى تعمل باسم الشركة فقط**، مثل NVIDIA · OpenAI · Anthropic · Stripe · Databricks · Coinbase · Reddit · Discord · Cloudflare · Notion · Scale AI · Figure · Perplexity · 1X · Cohere · GitLab وغيرها.

**الجديد في v2**: ‏24 نظام ATS ودليل لنحو 90 ألف شركة (اعرف بالاسم أي نظام تستخدمه الشركة) · ‏12 مصدرًا عابرًا للشركات (منها المجمّع freehire وقواعد الوظائف الحكومية في السويد وسنغافورة وألمانيا) · إزالة التكرار بين المصادر ووسم وكالات التوظيف · فئات حسب عمر الإعلان · تشغيل قابل للاستئناف · لقطات محلية لرؤية الوظائف الجديدة والمحذوفة · **خادم MCP** يستدعيه مساعدك الذكي مباشرة.

> ⚠️ تقرأ فقط **الوظائف التي تنشرها الشركات بنفسها** — لا سير ذاتية ولا بيانات شخصية، ولا محتوى يتطلب تسجيل الدخول، وتتوقف عند أي تحقق من الروبوتات. انظر «الاستخدام المسؤول» أدناه.

## الميزات

| الميزة | ما تفعله |
|---|---|
| **حسب الشركة** | يكفي اسم الشركة: تبحث أولًا في الدليل (~90 ألف شركة عبر 24 نظام ATS)، وإلا تخمّن الأنظمة الشائعة؛ أو حدّد بدقة عبر `--ats النظام slug` |
| **عبر الشركات** | `--board` حسب الدولة / الكلمة المفتاحية / آخر N يومًا: freehire، بحث Workable الشامل، قواعد الوظائف الحكومية، لوحات العمل عن بُعد؛ عدة مصادر معًا مع إزالة التكرار |
| **عمر الإعلان** | توسم كل وظيفة 0-3 أشهر / 3-6 أشهر / أكثر من 6 أشهر / بلا تاريخ؛ يعرض `--board` افتراضيًا آخر ستة أشهر |
| **وكالات التوظيف** | توسم الوظائف التي ينشرها صائدو الكفاءات أو وكالات العمالة (الحقل `agency`)؛ ويحذفها `--no-agency` |
| **الاستئناف** | إن قُيّد مصدر أو تعطّل تستمر المصادر الأخرى؛ الأمر نفسه مع `--resume` يكمل الناقص فقط |
| **لقطات محلية** | يحفظ `--save` في ملف SQLite محلي مع تاريخ أول وآخر ظهور؛ ويعرض `--history` الجديد والمحذوف في كل تشغيل |
| **خادم MCP** | يتيح `--mcp` لـ Claude Code / Codex وغيرهما الاستدعاء المباشر (الشركة، البحث عن وظائف، الدليل) |
| **الصين: 170 شركة** | `--local`: ثلاثة محللات عامة (Feishu Hire / Moka / Beisen) + 6 بوابات خاصة لشركات تقنية كبرى |
| **إضافات خاصة** | المصادر التي لا تسمح شروطها بالتوزيع العلني توضع في مجلدك الخاص (`--plugins`) خارج المستودع |
| **المكتبة القياسية فقط** | بلا اعتماديات (محلل Moka وحده يحتاج `pycryptodome`)؛ تعمل على أي `python3` |

## البدء السريع

```bash
git clone https://github.com/simonlin1212/Hiring-Radar.git
cd Hiring-Radar
python3 hiring_radar.py --directory-update   # تنزيل دليل الشركات (~90 ألف شركة، يُحفظ محليًا؛ اختياري لكنه موصى به)
python3 hiring_radar.py --list               # عرض كل المصادر
```

```bash
# 1) حسب الشركة: الاسم يكفي
python3 hiring_radar.py anthropic --keyword research
python3 hiring_radar.py xero                         # وُجدت في الدليل ← يُستخدم النظام الصحيح
python3 hiring_radar.py --find xero                  # إظهار نظام ATS الذي تستخدمه فقط
python3 hiring_radar.py --ats teamtailor <slug>      # تحديد النظام والحساب
python3 hiring_radar.py --workday host,tenant,site

# 2) عبر الشركات: دولة + كلمة مفتاحية + فترة
python3 hiring_radar.py --board freehire --country AU,NZ --keyword receptionist,bookkeeper
python3 hiring_radar.py --board freehire,workable --country AE --max 0 --json > ae.json   # بلا حد أقصى
python3 hiring_radar.py --board jobtech --keyword ekonomiassistent --recent-days 30       # قاعدة الوظائف الحكومية السويدية
python3 hiring_radar.py --board all --keyword "AI engineer"                              # لوحات العمل عن بُعد الأربع

# 3) الاستئناف بعد الانقطاع / اللقطات
python3 hiring_radar.py --board freehire --country AU --max 0 --resume
python3 hiring_radar.py anthropic --save          # التشغيل التالي يعرض الجديد والمحذوف
python3 hiring_radar.py --history

# 4) الشركات الصينية
python3 hiring_radar.py --local agibot --keyword 机器人      # AgiBot (Feishu)
python3 hiring_radar.py --local cambricon --keyword 大模型   # Cambricon (Moka؛ pip install pycryptodome)
python3 hiring_radar.py --local tencent --keyword 算法       # Tencent (بوابة خاصة)
```

**خيارات شائعة**: `--keyword a,b` (أي تطابق) · `--recent-days N` (0 = بلا حد) · `--country AU,NZ` · `--max N` (حد لكل مصدر، الافتراضي 1000، و0 = بلا حد) · `--no-agency` · `--json` · `--limit N` · `--debug`

**متغيرات البيئة**: `HIRING_RADAR_HOME` (الدليل واللقطات وحالة الاستئناف؛ الافتراضي `~/.hiring-radar`) · `HIRING_RADAR_DELAY` (أقل عدد ثوانٍ بين طلبين للموقع نفسه؛ الافتراضي 0.3) · `HIRING_RADAR_PLUGINS` (مجلد الإضافات الخاصة) · `HIRING_RADAR_INSECURE=1` (تعطيل التحقق من الشهادات، خلف وكيل اعتراض فقط)

رموز الخروج: `0` نجاح؛ `3` لم تكتمل بعض المصادر (يُعرض ما جُلب على أي حال؛ استخدم `--resume`).

## لمساعدي الذكاء الاصطناعي (MCP)

```bash
claude mcp add hiring-radar -- python3 /path/to/Hiring-Radar/hiring_radar.py --mcp
```

خمس أدوات: `company_jobs` (شركة واحدة) · `search_jobs` (عبر الشركات) · `find_company` (الدليل) · `list_sources` · `job_history`. يُقتطع وصف الوظيفة إلى 800 حرف في نتائج MCP؛ وللنص الكامل استخدم سطر الأوامر مع `--json`.

## حقول المخرجات

حقول v1 الخمسة عشر كما هي: `title · company · dept · team · location · remote · type · date · date_updated · req_id · comp (الراتب) · jd (كامل) · url · apply_url · id`

تضيف v2 تسعة: `country` (رمز الدولة) · `source` (المصدر) · `age` (الفئة 0-3m/3-6m/6m+/unknown) · `agency` (عبارة الوكالة المكتشفة) · `also` (مصادر أخرى حملت الوظيفة نفسها بعد إزالة التكرار) · `industry` · `size` (حجم الشركة إن وفّره المصدر) · `first_seen` · `last_seen` (مع اللقطات فقط)

غلاف `--json`: ‏`source · total · matched · jobs` (كما في v1) + `version · query · ages · sources · incomplete · candidates · saved`.

## طريقة العمل

```
Company name / country + keyword
        │
        ▼
┌─────────────────────────┐
│ Pick sources             │  By company: directory → public endpoints of 24 ATS
│                         │  Cross-company: freehire / Workable / gov job banks / remote boards / plugins
│                         │  China: Feishu / Moka / Beisen / in-house portals
└──────────┬──────────────┘
           │  Network: honest identity, per-site pacing, back off on 429, stop on 403 or bot checks
┌──────────▼──────────────┐
│ 24 fields + age bucket   │  Keyword / country / last-N-days filters; dedupe; agency flags
└──────────┬──────────────┘
      ┌────┴─────┬──────────────┐
      ▼          ▼              ▼
  Terminal   --json (full)   Snapshots / MCP
```

## المصادر

**حسب الشركة: 24 نظام ATS** (دليل الشركات من [openroles](https://github.com/datascry/openroles)، يُنزَّل إلى جهازك عند التشغيل ولا يُضمَّن في المستودع)

Greenhouse · Ashby · Lever · Workday · SmartRecruiters · Recruitee · Breezy · BambooHR · Personio · Workable · Teamtailor · Pinpoint · Rippling · JazzHR · Manatal · Hireology · Zoho Recruit · UKG/UltiPro · Jobvite · iCIMS · ApplicantPro · isolved Hire · CareerPlug · PageUp

**المصادر العابرة للشركات `--board` (12)**

| المصدر | النطاق | ملاحظات |
|---|---|---|
| `freehire` | العالم (يذكر نحو 3.3 مليون وظيفة مفتوحة) | واجهة [freehire](https://github.com/strelov1/freehire) العامة، تجمع 225 مصدرًا، أوصاف كاملة، تصفية حسب الدولة / الكلمة / آخر N يومًا |
| `workable` | العالم | بحث Workable الشامل، تصفية حسب الدولة / الكلمة |
| `jobtech` | السويد | البيانات المفتوحة لخدمة التوظيف العامة السويدية، أوصاف كاملة |
| `mycareersfuture` | سنغافورة | بوابة الوظائف الحكومية في سنغافورة، مع الراتب، بلا وصف |
| `arbeitsagentur` | ألمانيا | الوكالة الاتحادية الألمانية للتوظيف، بلا وصف |
| `remoteok` · `remotive` · `weworkremotely` · `workingnomads` | العمل عن بُعد | `--board all` = هذه الأربعة |
| `reed` · `adzuna` · `usajobs` | المملكة المتحدة / 19 دولة / الحكومة الاتحادية الأمريكية | تتطلب مفاتيحك المجانية (`REED_API_KEY`، `ADZUNA_APP_ID`+`ADZUNA_APP_KEY`، `USAJOBS_API_KEY`+`USAJOBS_EMAIL`)؛ مكتوبة وفق الوثائق الرسمية ولم يختبرها المشرف على الشبكة الفعلية |

**الصين: 170 شركة (`--local`)**: Feishu Hire (Li Auto / XPeng / NIO / AgiBot / Moonshot AI / MiniMax / Zhipu…) · Moka (Hypergryph / Cambricon / High-Flyer / SHEIN…) · Beisen (Dreame / Chery / Leapmotor / BOE / SANY…) · بوابات خاصة (Tencent / NetEase / JD / Baidu / ByteDance / Unitree). القائمة الكاملة: `--list`.

**غير مدعوم / قيود معروفة**
- **Paycom**: ملف robots.txt الخاص به لا يسمح بقائمة الوظائف، لذلك لا تُقرأ.
- **iCIMS**: قيمة `datePosted` في صفحاته يولّدها النظام (الوقت الحالي ناقص سنتين)، لذا تستخدم الأداة وقت التحديث من خريطة الموقع بدلًا منها. تعامل بحذر مع تواريخ نشر iCIMS التي جمعتها أدوات أخرى.
- في الدليل حسابات غير نشطة كثيرة، فالعثور على شركة بلا وظائف أمر طبيعي؛ وقد تتطابق شركات مختلفة بالاسم نفسه — وعند تعدد النتائج تُعرض كل المرشحات.
- إزالة التكرار حسب الدولة + الشركة + المسمى الوظيفي: المسمى نفسه لشركة واحدة في عدة مدن من دولة واحدة يصبح صفًا واحدًا.

> **عن Moka (توضيح صريح)**: تطبّق واجهات Moka تعتيمًا خفيفًا على الردود في الواجهة الأمامية (AES-128-CBC، والمفتاح وIV يُوزَّعان مع واجهتها الأمامية العلنية). تستخدم الأداة تلك القيم العلنية لاستعادة قائمة الوظائف العامة نفسها التي يعرضها المتصفح تمامًا — دون كسر تسجيل دخول أو تجاوز مصادقة. بدقة، هي «تعيد تنفيذ معالجة الواجهة الأمامية»، وهذا أقل وضوحًا من قراءة JSON عادي؛ للبحث المحلي فقط وعلى مسؤوليتك. للموقف الأنظف احذف كل أسطر `moka` في `parsers/companies.seed` والسطرين المدمجين `yostar`/`tesla-cn` في `radar/local.py`.

## الإضافات الخاصة

للمنصات الكبيرة التي لا تسمح شروطها بنشر شيفرة الجمع، اكتب إضافتك الخاصة واحفظها خارج المستودع:

```bash
python3 hiring_radar.py --plugins ~/my-plugins --board myboard --country AU
```

كل ملف `.py` في مجلد الإضافات لا يبدأ بـ `_` هو مصدر يعرّف `NAME` و`DESC` و`FILTERS` و`pages(q, state=None)` (الواجهة نفسها في `radar/boards/`)؛ ويمكن للملفات التي تبدأ بـ `_` أن تحوي شيفرة مشتركة. تعمل الإضافات بصلاحياتك، وأنت المسؤول عن شروط المواقع التي تزورها.

## إضافة شركة = إضافة سطر (الصين)

قائمة الشركات الصينية هي `parsers/companies.seed` (مفصولة بـ `|`)؛ شركة واحدة = سطر واحد:

```
key | feishu | company name | portal domain (e.g. nio.jobs.feishu.cn)
key | moka   | company name | orgId | siteId
key | beisen | company name | slug
```

لإضافة نظام ATS أو مصدر عابر للشركات، راجع [CONTRIBUTING.md](CONTRIBUTING.md).

## إشارة القطاع

التوظيف **مؤشر مبكر**: أين تتوسع الشركة، وفي أي اتجاه، وفي أي مرحلة — كثيرًا ما يظهر ذلك قبل النتائج المالية بأشهر. توظيف مهندسي خطوط الإنتاج = الخط قيد الإنشاء؛ توظيف الجودة/الصيانة = التحضير لإنتاج مستمر؛ توظيف نوبات ليلية = زيادة الإنتاج وشيكة. استخدم `--save` للقطات دورية و`--history` لرؤية الإيقاع.

> ⚠️ **التوظيف ≠ الإنتاج**: الوظائف مدخلات لا مخرجات؛ و«يوظّف» قد يعني بناء احتياطي أو إشارة معاكسة. تعامل مع الاستنتاجات كإشارات لا كنصيحة استثمارية.

## بنية المشروع

```
Hiring-Radar/
├── hiring_radar.py     # command-line entry (v1 usage unchanged)
├── radar/              # core package
│   ├── http.py         # network: honest identity, pacing, backoff, stop when blocked
│   ├── schema.py       # unified fields, dates, age buckets
│   ├── ats/            # by company: one file per ATS
│   ├── boards/         # cross-company sources
│   ├── directory.py    # company directory (downloaded at runtime)
│   ├── process.py      # dedupe, agency flags
│   ├── sweep.py        # multi-source sweeps, resume
│   ├── store.py        # local snapshots (SQLite)
│   ├── local.py        # China / in-house parser dispatch
│   ├── plugins.py      # private plugin loader
│   └── mcp.py          # MCP server
├── parsers/            # China / in-house parsers + companies.seed
├── tests/              # smoke_test.py · test_offline.py (offline, no network)
└── THIRD_PARTY_NOTICES.md · CHANGELOG.md · CONTRIBUTING.md · LICENSE
```

## التقنية والاعتماديات

- **Python 3.8+**، والنواة بالمكتبة القياسية فقط (urllib / json / re / ssl / argparse / sqlite3 / xml.etree)
- **`pycryptodome`**: لمحللات Moka فقط (`pip install pycryptodome`)
- تحتاج اتصالًا بالإنترنت (قد تتطلب بعض المواقع الدولية وكيلًا)؛ يُتحقق من شهادات SSL افتراضيًا، وخلف وكيل اعتراض اضبط `HIRING_RADAR_INSECURE=1`

## الاستخدام المسؤول / الامتثال

أداة **شخصية / بحثية، محلية ومفتوحة المصدر**. استخدمها بمسؤولية:

- **اقرأ إعلانات الوظائف فقط — لا سير ذاتية ولا أي بيانات شخصية** (البيانات الشخصية تخضع لقانون PIPL الصيني — لا تفعل).
- **واجهات علنية بلا تسجيل دخول فقط**: جدار الدخول / الكابتشا / الحماية النشطة من الروبوتات **لا تُتجاوز**؛ ورمز 403 أو صفحة تحقق يوقف التشغيل؛ لا مجمّعات وكلاء ولا تزييف لبصمة المتصفح.
- **هوية صادقة وتردد منخفض**: يذكر User-Agent اسم HiringRadar ورابط المشروع؛ افتراضيًا 0.3 ثانية بين طلبين للموقع نفسه؛ عند 429 تنتظر كما يُطلب منها، وإن استمر الفشل تتوقف وتنتظر `--resume` منك. يُفحص robots.txt قبل إضافة أي مصدر (ولهذا لا يُدعم Paycom).
- **المفاتيح في متغيرات البيئة فقط**: المصادر التي تحتاج مفتاحًا تقرؤه من البيئة، وتُحجب المفاتيح في رسائل الخطأ.
- **محليًا فقط**: لا استضافة / رفع / خادم؛ تبقى البيانات على جهازك. إن أعدت نشر البيانات فقيّم الامتثال بنفسك؛ ولا إعادة بيع تجارية. دليل الشركات مرخّص بـ CC BY-SA 4.0 — إعادة توزيعه تتطلب الإسناد والترخيص نفسه (راجع [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)).
- «مرئي للعامة» ≠ «حرّ التجميع وإعادة النشر» — الجمع الواسع مع إعادة النشر قد يُعد منافسة غير مشروعة في كثير من الولايات القضائية (بما فيها السوابق القضائية الصينية).

## إخلاء المسؤولية

1. **أنت تتحكم في بياناتك.** تعمل الأداة محليًا؛ لا تجمع شيئًا ولا ترفع شيئًا.
2. **أنت تلتزم بشروط الأطراف الثالثة.** اتبع شروط كل منصة توظيف؛ ولا تستخدمها لإزعاج أصحاب العمل أو إثقال أنظمتهم.
3. **إشارات لا حقائق.** بيانات التوظيف إشارة وليست حقيقة مؤكدة؛ وقرارات القطاع والاستثمار مسؤوليتك.

مقدَّمة بموجب [رخصة MIT](LICENSE) «كما هي» دون أي ضمان. الشيفرة والبيانات الخارجية: راجع [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## License

[MIT](LICENSE)

نرحب بطلبات الدمج لإضافة شركات / مصادر (راجع [CONTRIBUTING.md](CONTRIBUTING.md)).

**Author:** Simon Lin · X [@linsizhen](https://x.com/linsizhen) · Email: [simonlin0423@gmail.com](mailto:simonlin0423@gmail.com)
