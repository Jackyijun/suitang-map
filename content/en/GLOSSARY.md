# 英文版译名与体例（GLOSSARY）

中文是源文本，英文按同一套键写在本目录的 `*.json` 里（结构见 `src/i18n.py` 开头）。本文件记录译名体例，新增或修改英文时照此执行；同一个名称在全图各处必须写法一致（地图注记、悬停说明、索引、对照表、年表、节点说明）。总原则与《宋辽夏金元形势图》（songyuan-map）的 GLOSSARY 相同，这里只写隋唐图用到的部分和新增的通名。

## 一、总原则

1. **说真话**：英文只翻译中文已有的内容，不增不减；中文本身有误时先改中文，再改英文（并运行 `python tools/i18n.py lock`）。
2. **通俗写法，全图统一**：采用英文读者最常见的写法（Samarkand、Bukhara、Kashgar、Khotan、Goguryeo），不用学术转写。
3. **地名用当时当地的名称**：中国及汉字文化圈的地名用汉语拼音转写中文古名；汉字圈以外的地名用当地当时名称的通行英文写法，而不是把中文译音再转回拼音（碎叶 → Suyab，怛逻斯 → Talas，曲女城 → Kanyakubja，飞鸟 → Asuka）。
4. **今地 / 今名**用今天的通行英文名和行政区（Xi'an, Shaanxi；Gongju, South Chungcheong, South Korea）；方位写成 “northwest of Changwu”，“一带” 写成 “around …”。行政区划变了中英文一起改（越南 2025 年 7 月并省：广南并入岘港、广平并入广治、平定并入嘉莱、永福并入富寿）。
5. **地图注记不加中文里没有的消歧义**：同音的不同地名照写（弋阳郡、义阳郡都作 Yiyang Commandery；奚、霫的地图短名都作 Xi），靠位置和悬停里的汉字区分；政权全称可括注（霫 Xi (Bai Xi)）。
6. 英文界面里，地图注记只显示英文；悬停说明、索引、对照表、年表在英文名后附注汉字原名。
7. 拼音撇号一律用直撇 '（Chang'an、Xi'an、Wu'an）；引号也用直双引号。
8. 美式拼写（labor、honor、center、armor、traveled），与宋元图一致。

## 二、拼音与通名

| 类别 | 写法 | 例 |
|---|---|---|
| 拼音 | 不标声调；音节界限有歧义时加撇号；ü 保留 | Chang'an、Yan'an、Lüzhou、Lüliang |
| 多音字 | 按地名旧读 | 信都 Xindu、会稽 Kuaiji、琅邪 Langya、枹罕 Fuhan、越巂 Yuexi、番州 Panzhou、泷州 Shuangzhou、浚县 Xun County、歙州 Shezhou、冯翊 Pingyi、牟平 Muping（牟州 Muzhou） |
| 州（单音节专名） | 连写 | 雍州 Yongzhou、并州 Bingzhou |
| 州（多音节专名） | 分写 Zhou | 西会州 Xihui Zhou、北燕州 Beiyan Zhou |
| 郡（隋大业） | X Commandery | 京兆郡 Jingzhao Commandery、涿郡 Zhuo Commandery |
| 郡下县 | Y County, X Commandery | 京兆郡郑县 Zheng County, Jingzhao Commandery |
| 县 | X County | 魏县 Wei County |
| 镇 | X Garrison | 恒安镇 Heng'an Garrison、龟兹镇 Kucha Garrison |
| 城（城名的一部分） | City；朝鲜半岛的山城作 Fortress | 统万城 Tongwan City、伏俟城 Fuqi City；安市城 Ansi Fortress |
| 关 / 口 / 岭 | Pass；已成专名者照拼 | 蒲津关 Pujin Pass、飞狐口 Feihu Pass、古北口 Gubeikou |
| 水 / 河 / 江 | X River；外域河流用当地通行名，不把中文译音转回拼音 | 汾水 Fen River；乌浒水 Oxus、药杀水 Jaxartes、曳咥河 Irtysh、嗢昆水 Orkhon、娑陵水 Selenga、剑河 Kem、胪朐河 Kherlen、臧河 Tsangpo、雷翥海 Aral Sea；朝鲜半岛按韩语读音：萨水 Salsu River、浿水 Paesu River、蛇水 Sasu River、黄山江 Hwangsan River；越南的沱江 Đà River |
| 山 | 山脉 X Mountains；单峰 Mount X | 燕然山 Yanran Mountains、邙山 Mount Mang |
| 仓 | Granary | 洛口仓 Luokou Granary、兴洛仓 Xingluo Granary |
| 牙帐 | royal camp | 契丹牙帐 Khitan royal camp |
| 羁縻 | loose-rein | 羁縻州 loose-rein prefectures |
| 蛮 / 诸蛮 | tribes（不用 barbarian） | 牂柯诸蛮 Zangke tribes、五溪蛮 Five Streams tribes |

## 三、唐初的边疆机构与名号

| 中文 | 英文 | 说明 |
|---|---|---|
| 都护府 | X Protectorate | 安西都护府 Anxi Protectorate |
| 大都护府 | X Grand Protectorate | 单于大都护府 Chanyu Grand Protectorate |
| 都督府（羁縻） | X Area Command | 松漠都督府 Songmo Area Command、熊津都督府 Ungjin Area Command |
| 行台 | Branch Department | 东南道行台 Southeast Branch Department |
| 可汗 | Qaghan；汗国 Qaghanate | 颉利可汗 Illig Qaghan；“天可汗” Heavenly Qaghan；东突厥 Eastern Turkic Qaghanate |
| 某公 / 某王（封爵） | Duke of X / Prince of X | 唐公李渊 Li Yuan, Duke of Tang；秦王 Prince of Qin |
| 称帝 | proclaimed emperor | 吴（李子通称帝）Wu (Li Zitong proclaimed emperor) |
| 臣隋 / 臣唐 | Sui vassal / Tang vassal | |
| 奉（奉立的傀儡皇帝） | in the name of | 唐王李渊（奉恭帝）Li Yuan, Prince of Tang (in the name of Emperor Gong) |
| 受禅 | accepts the abdication | 李渊受禅 Li Yuan accepts the abdication |
| 东都 | Eastern Capital | |
| 行在 | temporary capital | 江都（行在）Jiangdu (temporary capital) |

## 四、人名、政权

- 汉人名：姓在前、拼音（Li Shimin、Dou Jiande、Wang Shichong）；复姓连写（Yuwen Huaji、Zhangsun Wuji、Yuchi Jingde、Qutu Tong、Heruo Bi）；帝王用 “Emperor + 庙号/谥号 + of + 朝”（Emperor Yang of Sui、Emperor Taizong of Tang）。
- 突厥可汗用英文通行写法：沙钵略 Ishbara、达头 Tardu、启民 Qimin、始毕 Shibi、处罗 Chuluo、颉利 Illig、突利 Tuli、统叶护 Tong Yabghu、射匮 Shekui、乙毗咄陆 Yipi Duolu；阿史那 Ashina；“设” Shad（大度设 Dadu Shad）。
- 朝鲜半岛用新罗马字：Goguryeo、Baekje、Silla、Eulji Mundeok、Yeon Gaesomun、Kim Yu-sin、Gyebaek、King Uija、Buyeo Pung、Ungjin、Sabi；泉男生、泉男建即渊氏，作 Yeon Namsaeng、Yeon Namgeon。
- 日本用平文式：Asuka、Naniwa、Tsukushi、Ōmi-Ōtsu。越南保留声调符号：Lý Phật Tử、Trà Kiệu、Quảng Nam；但隋唐在今越南设的州郡是中国建置，用拼音（交州 Jiaozhou、爱州 Aizhou、驩州 Huanzhou、日南郡 Rinan Commandery），今地才写越南名。
- 高句丽的城用新罗马字加 Fortress（辽东城 Yodong Fortress、建安城 Geonan Fortress、安市城 Ansi Fortress），隋唐所设州郡仍用拼音。
- 吐蕃：Songtsen Gampo、Gar Tongtsen（禄东赞）、Pugyal（悉补野）、Yarlung、Rasa（逻些）；象雄 Zhangzhung、苏毗 Sumpa。
- 西域与葱岭以西：焉耆 Karasahr、龟兹 Kucha、于阗 Khotan、疏勒 Kashgar、康国 Samarkand、安国 Bukhara、石国 Chach、史国 Kesh、拔汗那 Ferghana、吐火罗 Tokharistan、缚喝 Balkh、帆延 Bamiyan、迦毕试 Kapisa、木鹿 Merv、疾陵城 Zaranj。
- 政权名见 `units.json`：地图上用短名（s），说明里用全称（n）。隋末群雄写作 “国号 (人名)”：Xia (Dou Jiande)、Zheng (Wang Shichong)。

## 五、年代

- 一律照写农历月序，不换算公历：618 年五月 → 5th month, 618；闰二月 → intercalary 2nd month；615 年八至九月 → 8th–9th month, 615；跨年 → 11th month, 619 – 4th month, 620。
- 年号：Wude 1、Zhenguan 23（年号拼音 + 序数，不写 “1st year of”）；按月的节点写 Wude 1, 5th month。
- 年份区间用 en dash：581–583；“一说” 写作 “629 (or 627)”。

## 六、战役

- 名称：Battle of X / Siege of X / Fall of X / Conquest of X；中文写成句子的照译（刘方平交州 Liu Fang takes Jiaozhou）。
- 交战结果：“A defeated B”，城破加注 “(city fell)”；中文另有说明时照译括注（Goguryeo held (Tang withdrew)）。
- 主将：“A and B vs. C”。

## 七、维护

- `python tools/i18n.py status`：缺译、过期、未登记指纹的条数。
- `python tools/i18n.py todo [文件]`：逐条列出缺译与过期的中文。
- 改完英文：`python tools/i18n.py lock` 记下中文指纹；以后中文一改，对应英文就会报“过期”。
- `python run.py --html` 默认严格：有缺译或过期就停下；`--draft` 允许先出草稿（缺译处显示中文）。
- `python tools/i18n.py table` 导出中英对照表 `build/i18n-review.tsv` 供审校。
