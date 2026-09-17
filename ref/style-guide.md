# PostgreSQL NLS 简体中文翻译风格指南（nls-v3）

**适用范围**：PostgreSQL 19 `zh_CN` 全部 28 个组件、12,699 条消息（`messages` 仓库中的 `*.po`），以及此后各版本的同类消息：错误、详情、提示、日志、进度、`--help` 帮助文本、`pg_controldata` 一类的标签表、psql 元命令输出。

**目标**：准确 > 一致 > 流畅 > 本土化润色（与 pgdoc 中译风格一致）。消息是运维现场读的东西：一眼看懂出了什么问题、涉及哪个对象、要做什么；能复制到 psql、shell、grep 和 issue 里继续用。

**与文档翻译的关系**：本指南与 pgdoc 中译风格指南（PostgreSQL 文档中译项目，未随本仓库发布） 同源。名词术语以 pgdoc 术语表 pgdoc `glossary.tsv`（术语表）（631 条）及其逐条语境规则 pgdoc `glossary.rules.tsv`（逐条语境规则）、字面保护表 pgdoc `exclude.tsv`（字面保护表）、pgdoc `terms-to-preserve.tsv`（保留原文词表） 为准；理由是读者在消息里看到一个词后会去文档里搜它，两边必须是同一个词。消息特有的高频句式与 NLS 专用补充放在同目录的 [`phrasebook.tsv`](phrasebook.tsv) 与 `glossary.tsv`。文档与消息的差别只在形式：消息没有“首次出现加英文”的引介，有终端对齐、占位符和 gettext 校验。

**优先级**：技术正确（含源码语境） > 本指南条款 > `phrasebook.tsv`（`status=decided`） > pgdoc `glossary.tsv` + `glossary.rules.tsv` > `glossary.tsv` > 同组件既有稳定译法 > 个人偏好。发现术语表有误，核对英文后修正并记录到 pgdoc 的 `change.md`，不在译文里私自绕开。

条款编号 R1–R14 供人和 agent 引用；机器可判定的条款由 `nls_lint.py`（校验器，见下文「机器校验」） 执行（对应表见 R14）。

---

## R1 消息类型决定语气与句末标点

PostgreSQL 的《错误消息风格指南》规定：主消息小写开头、不加句号、尽量一行；详情和提示是完整句子、大写开头、以句号结尾。中文必须保持这套分工，因为客户端（psql、pgAdmin、日志系统）按类型分别排版。

| 类型 | 英文特征 | 中文处理 |
|---|---|---|
| 主消息 `errmsg` / 客户端 `pg_log_error` | 小写开头、无句号、短 | 短句，**不加句号**；不扩写成完整叙述 |
| 详情 / 提示 `errdetail` / `errhint` | 完整句、以 `.` 结尾 | 完整句，以 **`。`** 结尾；一句英文对应一句中文 |
| 上下文 `errcontext` | 片段：`SQL function "%s" statement %d` | 片段，不加句号 |
| 日志 / 进度 | `-ing` / 过去分词 | 进行中“正在…”，已完成“已…”；不用“了”表示状态 |
| 帮助文本 | `Usage:` / `Options:` / 选项行 | R6、R12 |
| 标签表 | `Label:      %s` | R4.2、R6.2 |
| 严重级别标签 | `ERROR:  ` / `WARNING:  ` | R9.2：`错误:  ` / `警告:  `，半角冒号加两个空格 |

- R1.1 英文以 `.` 结尾 ↔ 中文以 `。` 结尾；英文无句号 ↔ 中文无句号；英文以 `:`、`...`、`?` 结尾时中文保留对应标点（`：`、`...`、`？`）。
- R1.2 不把 DETAIL 的事实改写成建议，不给 HINT 增加英文没有的操作步骤，不加“请”“您”除非英文有 `please`/`you`。
- R1.3 语气专业、干练：不用感叹号（英文有才有），不用口语（“太多”→“过多”），不用文学化表达。

## R2 忠实：语义不增不减

- R2.1 保留否定范围、条件、因果、先后顺序、数量、执行主体、参数归属。`cannot X because Y` → “无法 X，因为 Y”。
- R2.2 保留不确定措辞：`may` / `might` / `possibly` / `probably` → “可能” / “也许”；不把猜测写成断言。
- R2.3 `expected X, got/found Y` → “预期为 X，实际为 Y”；多组数量全部保留。
- R2.4 同一消息多个调用点共用时，译文对所有调用点都要成立；不能只按一处源码解释。
- R2.5 拿不准的条目：给最保守、有依据的译文并记录疑问；不用英文原文或“待翻译”充数，不静默改义。

## R3 术语与固定句式

### R3.1 名词术语：以 pgdoc 术语表为准

本轮据 `glossary.tsv` 与 `glossary.rules.tsv` 对消息里高频、此前分歧的名词做出裁决（`phrasebook.tsv` 已按此执行）：

| 英文 | 中文 | 依据与边界 |
|---|---|---|
| database cluster / cluster | **数据库集簇 / 集簇** | pgdoc 规则 121：一个服务实例管理的一组数据库；`pg_upgrade` 的 old/new cluster → 旧集簇 / 新集簇。分布式多节点才译“集群”；`CLUSTER` 命令原样，作为动作是“聚簇”；不单用“簇” |
| standby / hot standby / standby mode | **备库** / 热备 / 备库模式 | pgdoc 规则 522：复制角色；泛指设备待命才用“后备” |
| primary / primary server | **主库** | pgdoc 规则 409：`primary key` 是主键，逐条判断短语 |
| master / secondary / slave | 主库 / 备库 / 从库 | 规则 301、475：仅复制角色；`master key` 主密钥；`secondary index` 二级索引 |
| replica / replication / replica identity | 副本 / 复制 / **复制标识** | `REPLICA IDENTITY` 关键字原样 |
| latch | **锁存器** | 规则 272：`Latch`、`WaitLatch` 等名称保留 |
| buffer / buffer pool / buffer cache / cache | 缓冲区 / 缓冲池 / 缓冲区缓存 / 缓存 | pgdoc |
| token | 词元（SQL 词法） / 令牌（OAuth bearer token） | 规则 562：按语境；代码 `token` 字段名保留 |
| VACUUM / vacuum / autovacuum | `VACUUM` 原样 / 清理 / 自动清理 | 规则 597；`index vacuuming` 索引清理；指代命令的 `full vacuum` 可写 `VACUUM FULL` |
| worker | 后台/并行/应用**工作进程**；zstd 压缩 worker → 工作线程 | 进程与线程按实体区分 |
| archive | 归档 | pgdoc style |
| OID / LSN / TID / TOAST / WAL / XID | 原样 | `terms-to-preserve.tsv`：消息里是标识而非概念解释 |
| relation / table / tuple / row / column / attribute / field | 关系 / 表 / 元组 / 行 / 列 / 属性 / 字段 | 规则 442：relation 不全译成表 |
| locale / collation / encoding | 区域设置 / 排序规则 / 编码 | |
| parser / planner / checkpointer / background writer / startup process | 解析器 / 规划器 / 检查点进程 / 后台写入器 / 启动进程 | `walsender`、`walreceiver` 名称保留 |
| failover / switchover | 故障切换 / 计划内切换 | |
| foreign data wrapper / foreign server / foreign table / user mapping | 外部数据包装器 / 外部服务器 / 外部表 / 用户映射 | `FDW` 缩写保留 |
| deadlock / snapshot / cursor / savepoint / two-phase commit / logical decoding / replication slot / crash recovery / heap | 死锁 / 快照 / 游标 / 保存点 / 两阶段提交 / 逻辑解码 / 复制槽 / 崩溃恢复 / 堆 | |
| connection / socket / file descriptor / shared memory | 连接 / 套接字 / 文件描述符 / 共享内存 | 不用旧译“联接” |
| extension / procedure / privilege / owner / default | 扩展 / 过程 / 权限 / 所有者 / 默认 | `file extension` 是文件扩展名 |

### R3.2 固定句式（动词、情态词、高频短语）

这是语料里分歧最大的部分（附录 A）。统一译法：

| 英文 | 中文 | 说明 |
|---|---|---|
| could not … | 无法… | 尝试后失败 |
| cannot … / unable to … | 无法… | **本轮决定**：不再区分 cannot→“不能”（原 724 条“不能”、315 条“无法”）。语义上“无法”覆盖两者；规范性禁止改由下面两行表达 |
| must not … | 不得… / 不能… | 规范性禁止 |
| … is not allowed / not permitted | …不允许 | |
| not supported / unsupported | 不支持 | |
| out of memory | 内存不足 | 不用“内存溢出” |
| invalid / illegal | 无效 / 非法 | |
| unrecognized / unknown | 无法识别的 / 未知 | |
| unexpected | 意外的 | 不用“非预期”“意料之外” |
| already exists / does not exist | 已存在 / 不存在 | |
| permission denied [to X] | 权限不足[，无法 X] | 原四种译法归一 |
| too many / too few | 过多 / 过少 | |
| missing X / lost | 缺少 X / 丢失 | |
| requires | 需要 | 不用“要求” |
| expected X, got Y | 预期为 X，实际为 Y | |
| terminate / abort / cancel | 终止 / 中止 / 取消 | `abort transaction` 中止事务 |
| skipping / ignoring | 跳过 / 忽略 | |
| deprecated | 已弃用 | |
| retry / try again | 重试 | |
| shut down | 关闭 | |
| exit | 退出 | |

- R3.3 同一英文在相同语境下只有一种译法；同一句式在全部组件用同一模板：`could not open file "%s": %m` → `无法打开文件 "%s"：%m`。
- R3.4 改动一条固定句式必须改全部实例（lint L10、L11）；有意保留的例外要写明语境。
- R3.5 量词：`%d 行`、`%d 条`（记录/条目）、`%d 个`（对象）、`%d 字节`、`%d 块`、`%d 页`、`%d 段`。

### R3.6 相似消息，相似译法（消息簇）

消息先聚类，再按簇翻译。`workbench/nls_cluster.py` 把 12,699 条消息按词法相似度分簇：占位符、带引号的字面量和数字归一化后，词序列**完全相同**的归为一簇（`exact`，含跨组件的同一英文）；与簇的种子模式**只差一两个词**的归入同簇（`near`；≤3 词的短消息须完全一致，4–5 词允许 1 处差异，6 词以上允许 2 处）。每个成员与种子的距离都受此限制，不会因一词一词地传递把无关消息串成一簇。

- R3.6.1 `exact` 簇：所有成员译文完全相同（跨组件亦然），除非 `msgctxt` 或复数形式不同并写明理由。
- R3.6.2 `near` 簇：所有成员共用一个**中文句架**，只有与英文差异位置对应的槽位不同；槽位的译法在簇内一致（`open` → 打开、`read` → 读取、`file` → 文件、`directory` → 目录），并与其他簇复用同一套槽位词。示例：`could not ⟪open⟫ ⟪file⟫ "%s": %m` 这一簇 260 条统一为 `无法⟪打开⟫⟪文件⟫ "%s"：%m`。
- R3.6.3 先定簇模板，再译成员：`workbench/v3/cluster-templates.jsonl` 记录每个多成员簇的英文模板、中文句架、槽位映射和例外；改模板必须回头改全部成员。
- R3.6.4 簇只是词法相近，不等于语义相同。成员在语境里确实是另一种意思（如 `%s: %s` 这类短模板），从簇里拆出并记录理由；不为了“像”而牺牲“对”。
- R3.6.5 工具：`nls_cluster.py --sheet` 生成审阅表（每簇的模板、成员与当前译文），`--translations` 用 agent 产出重新判定簇内一致性；verdict 为 `exact-divergent`（同一英文不同译）和 `review`（中文变体多于英文变体）的簇必须处理。

## R4 标点：标点属于它所在的语言层

### R4.0 原则与理由

一条 PostgreSQL 消息由两层文本叠成：

1. **叙述层**——译者写的中文句子：“无法打开文件”“权限不足，无法创建表空间”。
2. **机器层**——从英文原样嵌入、运行时由程序填入的片段：标识符、值、SQL、命令、选项、路径、`文件:行号`、`host:port`、时间、协议名、程序名前缀，以及 `%s` 这类占位符（运行时填入的几乎总是机器串）。

**规则：叙述层用中文全角标点，机器层保留半角标点，引号一律 ASCII 双引号；技术值清单与诊断字段的逗号边界按 R4.4 保留 ASCII。** 判断时先看标点是不是可复制片段的一部分或消息格式的结构分隔符，再区分技术清单、诊断属性与普通中文叙述。

四条理由：

1. **可复制、可检索。** 消息会被粘贴进 psql、shell、`grep`、日志系统和 issue。机器片段里的标点变了，`pg_catalog.pg_class` 的点、`host:port` 的冒号、`"MyTable"` 的引号就不再是原来的东西，命令会失败、搜索会落空。这一条决定了机器层必须半角。
2. **与文档一致。** pgdoc 中译风格明文规定“正文使用中文全角标点；代码、命令、配置、路径中的半角标点保持原样”。用户在消息里读到一句话，再到手册里读同一概念，标点节奏应当相同。这一条决定了叙述层全角。
3. **字形与节奏。** 全角标点占一个汉字宽，与汉字字形匹配，符合 GB/T 15834《标点符号用法》；半角逗号、冒号夹在汉字之间显得挤，且后面往往还要补一个空格才能看清。终端里这一点尤其明显。
4. **少动。** 12,699 条现有译文已经是这个方向：ASCII 双引号 8,844 处对中文引号 1 处，全角冒号 2,138 处对半角 439 处，全角逗号 1,892 处对半角 482 处，英文句号 → 中文句号 2,151 条对 16 条。规则顺着主流走，改动集中在几百处“少数派”，而不是重排全部。

### R4.1 引号：ASCII 双引号，永远

`关系 "%s" 不存在`、`无法识别的压缩选项："%s"`。不用 “ ” ‘ ’ 「 」。

这是引号的显式约定，理由集中在“引号是值的边界，不是句子的标点”：

- PostgreSQL 用双引号标出**标识符和输入值的精确边界**，让人看见前后空格和空串（`""`）。这个边界属于值，不属于中文句子。
- 与 SQL 标识符引用（`"MyTable"`）形状一致，输出可直接粘回 SQL。
- 日志分析工具、`grep '"%s"'` 一类的匹配规则依赖 ASCII 引号。
- 内容几乎总是 ASCII 标识符，中文引号包着英文标识符视觉失衡；部分终端字体里 “ ” 的宽度还不稳定。
- 20 年来 zh_CN PO 一直如此，现有语料 8,844 : 1。

附带规则：引号数量与英文一致；英文没加引号的词中文也不加；引号外侧按 R5 留空格（`文件 "%s" 的`），内侧不留。

### R4.2 冒号

| 场景 | 用 | 例 |
|---|---|---|
| 叙述句里引出说明、值、原因（含紧跟带引号的值） | **全角 `：`** | `无法打开文件 "%s"：%m`；`预期为 "@"，实际为 "%s"`；`参数 %d：键不能为空` |
| 程序名前缀 `%s: ` | 半角，原样含空格 | `%s: 无法访问目录 "%s"：%m` |
| 严重级别 / 诊断字段标签 | 半角 + 与英文相同的空格数 | `错误:  %s`、`详细信息:  %s`、`第 %d 行:  ` |
| `文件:行号`、`host:port`、`hh:mm:ss`、`%u:%u` | 半角 | `pltcl.c:479` |
| 命令回显 `\pset: …`、`TRAP: …` | 半角 | |
| 标签对齐表（R6.2） | 半角 + 空格对齐 | `最新检查点的 TimeLineID:        %u` |
| 引号内的字面量 | 原样 | `预期为 "://"` |

为什么 `"%s"：%m` 用全角：这个冒号分隔的是中文子句和后面的 errno 文本，属于句子；`"%s"` 只是碰巧站在它前面。写成 `"%s": %m` 会在中文句里塞进一个半角冒号加一个多余的 ASCII 空格，节奏断裂；语料里 `：` 紧跟引号 480 处对 `: ` 167 处，主流也是全角。

为什么程序名前缀和严重级别标签保留半角：`pg_dump: error: …` 的前缀由工具框架统一打印，用户和脚本按 `^prog: ` 过滤；`ERROR:  ` 后的两个空格是服务器日志格式的一部分，psql 与日志解析器按这个形状对齐、切分，zh_CN 沿用 `错误:  ` 已二十年。它们是格式，不是句子。

### R4.3 括号

- 说明性括注属于叙述层，用全角 `（）`，**即使里面是机器值**：`事务 %u（纪元 %u）`、`%s（PID %d）`、`不支持解析器调试（-d）`、`数组大小超过允许的最大值（%zu）`。
- 语法括号属于机器层，保留半角：函数调用 `setlocale()`、`count(*)`、`[OPTION]...`、正则分组、SQL 片段。
- 判定方法：把括号连同内容删掉，句子还成立，就是括注（全角）；删掉就不再是那个 token，就是语法（半角）。
- 全角括号内外都不加空格。

### R4.4 逗号、顿号、分号、句号、省略号

- 普通中文叙述用 `，` `、` `；` `。`。动作、对象类别和概念列举使用顿号，例如 `启用、禁用或验证`、`表、视图和序列`；分句之间用中文逗号。
- 准确的配置值、枚举值、SQL 关键字、选项名、单位等 token 组成的清单，使用 ASCII 逗号加一个空格，例如 `允许的线型是 ascii, old-ascii 和 unicode`、`必须为 "fetch", "stream" 或 "none"`。保留“和”“或”“之一”“最多一个”等逻辑限定，不要求照搬英文牛津逗号。技术名嵌入中文概念说明时按句法处理，例如 `real、double precision 和几何数据类型`。
- 主机、用户、数据库、PID、UID 等诊断属性，保留原文逗号对应的 ASCII 边界，例如 `主机 "%s", 用户 "%s", 数据库 "%s", %s`。这用于模板对照与检索，不意味着正文成为可靠解析协议。
- and、with、上下限与块内位置等关系优先用连词或重组表达：`%d 行和 %d 个字段`、`1 个含 2 个字段的元组`、`至少 %d 个且至多 %d 个`、`块 %u 中偏移量 %u 处`。不把这些关系机械转成顿号或逗号。
- 动态生成的技术清单与静态清单使用相同体例：GUC 可用值列表的独立分隔符 `", "` 保留原样。上游允许本地化此提示，本项目选择 ASCII 以统一边界；不使用带多余空格的 `"、 "`。
- 机器片段内部的 `,` `;` `.` 原样：`-F c|d|t|p`、`pg_catalog.pg_class`、`.pgc`。
- 句末标点严格随 R1.1；不给主消息加句号，不把英文句号漏掉。
- 省略号保留 ASCII `...`：消息里它要么是语法（`[OPTION]...`），要么是与英文输出对齐的进度标记（`正在等待 ...`），脚本可能匹配它；全角“……”是两个字符，还会打乱对齐。
- `%%` 输出百分号，紧贴数字：`%d%%`。尖括号 `<%s>`、方括号、斜杠、连字符原样。

### R4.5 判定流程

1. 这个标点在一个你会整体复制的片段里吗（标识符、值、路径、选项、代码、时间）？→ 半角原样。
2. 它是消息格式的结构分隔符吗（程序名前缀、严重级别标签、`文件:行号`、标签表的冒号）？→ 半角原样。
3. 它分隔准确的技术值清单，或对应原文中的诊断属性边界吗？→ 按 R4.4 使用 ASCII 逗号加一个空格，保留必要的中文连词。
4. 它实际上表达并且、包含、上下限或位置层次吗？→ 明确表达关系，不机械替换标点。
5. 其余中文句子的标点 → 全角；但引号例外，永远 ASCII `"`。

### R4.6 对照示例

| ✗ | ✓ | 条款 |
|---|---|---|
| `无法打开文件 "%s": %m` | `无法打开文件 "%s"：%m` | R4.2 |
| `无法识别的编码：“%s”` | `无法识别的编码："%s"` | R4.1 |
| `%s：无法访问目录 "%s"` | `%s: 无法访问目录 "%s"：%m` | R4.2 前缀 |
| `错误：第 %d 行` | `错误: 第 %d 行`（与英文 `Error: ` 空格数一致） | R4.2 标签 |
| `数组的大小超过了最大允许值(%zu)` | `数组大小超过允许的最大值（%zu）` | R4.3 |
| `由于 setsid（） 失败` | `由于 setsid() 失败` | R4.3 |
| `允许的线型是 ascii、old-ascii 和 unicode` | `允许的线型是 ascii, old-ascii 和 unicode` | R4.4 技术清单 |
| `主机 "%s"、用户 "%s"、%s` | `主机 "%s", 用户 "%s", %s` | R4.4 诊断属性 |
| `1 个元组、每个包含 2 个字段` | `1 个含 2 个字段的元组` | R4.4 包含关系 |
| `启用, 禁用或验证` | `启用、禁用或验证` | R4.4 中文列举 |
| `重置后的首个日志段：      %s` | `重置后的首个日志段:        %s` | R4.2 表 / R6.2 |
| `对于bytea类型的输入语法无效: "%s" ,在第%d行` | `bytea 类型的输入语法无效："%s"，位于第 %d 行` | R4、R5 |

## R5 空格

- R5.1 中文与英文单词、数字、占位符、ASCII 引号之间留**一个**半角空格：`第 %d 行`、`类型 int`、`文件 "%s" 的`、`分配 GSSAPI 缓冲区时内存不足（%d）`。
- R5.2 全角标点两侧不加空格；全角括号内侧不加空格。
- R5.3 占位符与量词之间留空格（`%d 字节`）；百分号紧贴（`%d%%`）。
- R5.4 英文原文作为提示符结尾的空格（`Enter new superuser password: `）必须保留（R8），全角冒号后同样保留该空格。
- 理由：这是中文技术写作的通行排版（pgdoc 亦如此），语料里 17,699 处有空格对 8 处无空格，早已是事实标准。

## R6 终端对齐：按显示宽度

终端里一个汉字占两列。所有对齐按**显示宽度**（East Asian Width 为 W/F 的字符计 2，其余计 1）计算，不按字符数。

### R6.1 帮助选项行
```
  -f, --file=FILENAME          output file or directory name
  -f, --file=FILENAME          输出文件或目录名
```
- 选项列（`  -f, --file=FILENAME`）原样保留，包括元变量 `FILENAME`、`NUM`、`METHOD[:DETAIL]`。
- 说明列从与英文**相同的显示列**开始；选项列没有汉字，所以补的空格数通常与英文相同。
- 说明列续行缩进到同一显示列；整行显示宽度不超过 79 列，超过则在词边界换行续行。
- 用法行的元变量按既有惯例翻译并全组件一致：`%s [OPTION]... [DBNAME]` → `%s [选项]... [数据库名]`；`DATADIR` → 数据目录、`FILENAME` → 文件名、`SECS` → 秒数。

### R6.2 标签对齐表（pg_controldata、pg_resetwal、initdb 摘要等）
```
Latest checkpoint's TimeLineID:       %u
最新检查点的 TimeLineID:                    %u
```
- 标签后半角冒号；用空格把值补到同一显示列；**同一张表内所有行的值列必须齐**。
- 中文标签比英文列宽还长时，整张表一起加宽（pg_controldata 现为 38 → 44 列），不能只加宽一行；在报告里说明。

### R6.3 其他
- `printf` 固定宽度片段（`%-20s`、`%5d`）保留修饰，不改宽度。
- 示例代码、字符画、SQL 片段逐字保留。

## R7 占位符

- R7.1 与英文**完全一致**：类型、长度修饰（`ll`、`z`、`<PRId64>`）、宽度、精度、`*`、标志。数量一个不多一个不少。
- R7.2 需要调换语序时用位置参数 `%1$s`、`%2$d`；一旦使用，所有消耗实参的占位符都要编号（`%m`、`%%` 不消耗实参，不编号）。
- R7.3 `%m` 是 errno 文本，放在全角冒号后：`：%m`。
- R7.4 每条候选都要通过 GNU `msgfmt --check --check-format`（隔离夹具，去掉 fuzzy 后检查），不用正则数占位符代替。

## R8 空白与换行契约

- R8.1 首尾空白、首尾换行、制表符与回车的数量与英文一致；结尾 `\n` 有无必须相同（msgfmt 强制）。
- R8.2 中文不得比英文多换行。
- R8.3 **结构性换行必须保留**：选项行、标签行、列表项、空行分段、示例、字符画，每一行各自对应。
- R8.4 **纯因行宽折行的句子可以合并**：英文说明或段落因超过行宽拆成两行，中文一行放得下（≤ 79 列）时写成一行；选项说明的续行同理可并回上一行。合并后仍要满足 R6。
- R8.5 校验器（pgnls `workbench/importer.py`、站点 `pgweb/nls/validate.py`、`nls_lint.py` L02）按此实现：首尾与制表符严格相等；换行只能减少，且结构行（选项、标签、列表、空行）数量不变。

## R9 不翻译的内容

SQL 关键字与命令、GUC 参数名、选项名（`--jobs`）、函数与调用（`setlocale()`）、类型名（`integer`、`bytea`）、标识符、文件名、路径、环境变量、协议名、SQLSTATE、信号名、`NULL`/`true`/`false`、`pg_*`、`postmaster`、`WAL`/`OID`/`LSN`/`TLI`/`XID`、`TOAST`、`portal`、`nonce`、psql 元命令（`exclude.tsv`）一律原样。

- R9.1 `VACUUM` / `CLUSTER` / `ANALYZE` 作为命令保留；作为动作说明分别是“清理”“聚簇”“分析”。
- R9.2 严重级别标签按既有惯例翻译，半角冒号 + 两个空格：`ERROR:  `→`错误:  `、`WARNING:  `→`警告:  `、`DETAIL:  `→`详细信息:  `、`HINT:  `→`提示:  `、`CONTEXT:  `→`上下文:  `、`LOG:  `→`日志:  `、`NOTICE:  `→`注意:  `、`FATAL:  `→`致命错误:  `、`PANIC:  `→`严重错误:  `、`STATEMENT:  `→`语句:  `。
- R9.3 选项行里的元变量保留；用法行里的元变量按 R6.1 翻译。
- R9.4 psql `\h` 语法模板里的小写占位符（`column_constraint`、`table_name`）按既有惯例译成中文（列约束、表名），大写关键字原样。

## R10 中文表达

- R10.1 短句，主谓宾清楚；一句英文对应一句中文（R8.4 的合并只涉及物理换行）。
- R10.2 少用“被”字句：`could not …` 一律“无法…”；`was terminated by …` 可写“被…终止”，能转主动优先。
- R10.3 “未 / 尚未”表示还没发生，“已”表示完成，“正在”表示进行中；不用“了”表达状态。
- R10.4 数字写法跟随原文（2026-09-12 用户确认）：英文用完整单词表达的数量、序号，中文用汉字数字，例如 `one` → “一”、`first` → “第一”、`fourth` / `number four` → “第四” / “四号”、`zero` → “零”。数量的 `two`、`both`、`twice` 按中文习惯用“两”（“两个”“两次”“两倍”）；序号和数学基数用“二”（“第二”“二的幂”）。`single`、`once`、`zeros`、`nonzero` 等表达同样使用“单个/一个”“一次”“零”“非零”。汉字数字与汉字之间不留空格：“第一个”，不用“第 1 个”或“第 一 个”。
  - 英文本来写成数字的编号、取值、范围、单位和技术片段保持数字，包括 `1`、`4th`、`32-bit`、`LIMIT 1`、`-1`、`%1$s`、`%08X`。同句混用时逐项对应：`hash function 1 must have one argument` → “哈希函数 1 必须有一个参数”；`a power of two between 1 and 1024` → “1 到 1024 之间的二的幂”。`2 billion` → “20 亿”是保留数字系数的单位换算，不属于完整英语单词数字。
  - 原文没有显式数字，而中文因语境补出数量时也用汉字，例如 `Passwords didn't match.` → “两次输入的密码不一致。”。不为冠词 `a/an` 强行补“一”；原有“一维”“两阶段”“双精度”“首个”“多次”“非零”等自然表达保留。`second` 表示时间单位时译为“秒”，不当作序数。不得用全局数字替换；lint L16 只筛候选，需逐条确认原文与译文的数字对应关系。
  - 不译冠词；不加“请”“您”除非英文有。
- R10.5 不做翻译腔的直译：`the name is formed by adding .c to the input file name, after stripping off .pgc if present` → “去掉输入文件名的 .pgc 后缀（如有）再添加 .c 后缀，作为输出文件名”。

## R11 复数

- 中文 `Plural-Forms: nplurals=1; plural=0;`，只有 `msgstr[0]`，须同时覆盖单复数：`%d row(s)` → `%d 行`，不写“一行”。
- 23 条继承的复数头部问题（组件 PO 声明两种形式）不在翻译层修补；按原文件形式数量给译文并在报告中列出。

## R12 帮助文本与共用字串

28 个组件共享 469 条相同英文，译法必须完全相同（lint L11）。固定译法：

| 英文 | 中文 |
|---|---|
| `Usage:` / `Options:` / `Less commonly used options:` | `用法：` / `选项：` / `不常用选项：` |
| `Try "%s --help" for more information.` | `运行 "%s --help" 获取更多信息。` |
| `Report bugs to <%s>.` | `请向 <%s> 报告缺陷。` |
| `%s home page: <%s>` | `%s 主页：<%s>` |
| `-?, --help  show this help, then exit` | `显示此帮助，然后退出` |
| `-V, --version  output version information, then exit` | `输出版本信息，然后退出` |
| `cannot duplicate null pointer (internal error)` | `无法复制空指针（内部错误）` |
| `out of memory` | `内存不足` |

## R13 一致性与变更纪律

- R13.1 **最小改动**：正确且合规的译文不重写；每处修改只解决一个明确的问题，并标注条款编号与一句话理由。
- R13.2 **分类**：`term`（术语/句式）、`punct`、`space`、`align`、`wrap`、`semantic`、`new`、`none`。
- R13.3 **不改写已人工批准的行**（站点 `status = approved`）；异议写入报告的“建议复议”。
- R13.4 **改一处即改全部**：固定句式或术语的变更覆盖所有实例，跨组件相同英文保持相同。
- R13.5 **证据**：语义类改动引用源码位置或语境；没有把握写疑问，不猜。
- R13.6 **验证先于交付**：`nls_lint.py`（含 `--msgfmt`）零 error；warning 逐条处理或说明理由。
- R13.7 不用正则批量替换代替逐条阅读；不因“看起来更顺”改动没有条款依据的译文。

## R14 机器校验与条款对应

| lint | 级别 | 检查 | 条款 |
|---|---|---|---|
| L01 | error | 占位符多重集、位置参数编号完整 | R7 |
| L02 | error | 首尾空白、制表符、换行结构 | R8 |
| L03 | warning | 中英之间空格、全角标点旁空格 | R5 |
| L04 | warning | 中文引号、引号数量 | R4.1 |
| L05 | warning | 叙述冒号全角；前缀 / 标签 / 字面量 / 表半角 | R4.2 |
| L06 | warning | 中文后的半角括号；语法括号被改全角 | R4.3 |
| L07 | warning | 中文间半角逗号 / 分号需辨析（技术清单与诊断字段允许）；句末半角句号 | R4.4 |
| L08 | warning | 句末标点与英文类型不符 | R1.1 |
| L09 | error | 选项说明列、标签值列的显示宽度对齐（表按组件整体判断） | R6 |
| L10 | warning / info | `phrasebook.tsv`（`pending` 项只报告） | R3 |
| L11 | warning | 相同英文跨组件译法不同 | R12、R13.4 |
| L12 | error / warning | 选项、`pg_*`、函数调用未保留（error）；大写词未保留（warning，需人判断是关键字还是普通词） | R9 |
| L13 | error | 改写了已人工批准的行 | R13.3 |
| L14 | error | `msgfmt --check --check-format`（`--msgfmt`） | R7.4 |
| L15 | warning / info | 译文行超过 79 列；标签表整体移位 | R6 |
| L16 | warning | 英语单词数字、中文补出数量与阿拉伯数字的对应候选；屏蔽 printf 参数并扣除原文已有数字后提示，逐条复核 | R10.4 |
| `nls_cluster.py` | 报告 | 消息簇与簇内译法一致性（`exact-divergent` / `review`） | R3.6 |

```bash
review-app/.venv/bin/python workbench/nls_lint.py outputs/nls-bundle-20260911.jsonl.gz --summary
review-app/.venv/bin/python workbench/nls_lint.py BUNDLE --translations workbench/v3/translations/psql.jsonl --component psql --msgfmt --json lint-psql.jsonl
```

---

## 附录 A · 数据依据（2026-09-11，对 nls-v2 推荐译文）

**语料分析**
- 句式分歧：`cannot` 不能 724 / 无法 315；`unexpected` 意外 78 / 非预期 37 / 意料之外 11；`unrecognized` 无法识别 105 / 未识别 13 / 未知 10；`permission denied` 权限不足 55 / 没有权限 12 / 权限不够 7 / 权限被拒绝 2；`too many` 太多 38 / 过多 26；`missing` 缺少 82 / 丢失 14；`requires` 需要 84 / 要求 64；`expected` 预期 89 / 应为 28 / 期望 22；`already exists` 已经存在 48 / 已存在 33；`connection` 连接 159 / 联接 8；`archive` 归档 82 / 存档 6；`standby` 备用 43；`cluster` 集群 135 / 数据库集群 20 / 簇 8。`out of memory` 已 49/50 为“内存不足”。
- 标点：`：` 2,138 / `:` 439；`，` 1,892 / `,` 482；`（` 692 / `(` 167；ASCII 引号 8,844 / 中文引号 1；`"%s"` 2,938 处。英文 `.` → 中文 `。` 2,151 条，`.` 16 条。叙述位置的半角冒号 167 处；标签表里的全角冒号 8 处。
- 空格：中英之间有空格 17,699 处，缺 8 处；全角标点旁空格 43 处（多为合法的提示符尾部空格）。
- 对齐：573 行帮助选项行全部按显示宽度对齐；pg_controldata / pg_resetwal 标签表整体 38 → 44 列，initdb 摘要表 1 行偏差。
- 占位符：推荐译文与英文不一致 2 条（均为误报：非 c-format、合法位置参数），旧译 1,078 条不一致；536 条用位置参数重排。
- 换行：391 条含内部换行，208 条结构性、183 条散文折行；后者 127 条中文一行放得下（R8.4 适用范围）。
- 跨组件：469 条相同英文，3 条译法不同。用法行 `[OPTION]` → `[选项]` 20 条、保留 6 条；`DBNAME` 出现“数据库名 / 数据库名字”两种。

**lint 基线**（`nls_lint.py`，本指南与 `phrasebook.tsv` 定稿后）：1,728 条 finding，其中 error 2（L02 1、L09 1）、warning 1,724、pending 2。L10 共 1,662：P02 cannot→无法 755、P66 集簇 143、P11 意外 74、P01 61、P44 备库 56、P23 需要 54、P13 已存在 49、P24 预期 43、P15 过多 40、P70 主库 36、P14 权限不足 33、P09 无法识别 30、P82 外部数据包装器 27……这就是 agent 要清零 / 逐条处理的工作量，集中在 postgres（1,151）、pg_upgrade（117）、pg_basebackup（62）。

## 附录 B · 决策记录

| 项 | 决定 | 依据 | 如何变更 |
|---|---|---|---|
| database cluster | 数据库集簇 / 集簇 | pgdoc 规则 121；文档与消息同词 | `phrasebook.tsv` P66 |
| standby / primary / master / secondary | 备库 / 主库 / 主库 / 备库 | pgdoc 规则 522、409、301、475 | P44、P70、P94、P95 |
| latch | 锁存器 | pgdoc 规则 272 | P68 |
| token | 词元（词法）/ 令牌（OAuth） | pgdoc 规则 562 | P75 |
| worker | 进程类 → 工作进程；压缩 worker → 工作线程 | 实体区分 | P71 |
| cannot / could not / unable to | 无法 | 用户决定；must not / not allowed 保留“不得 / 不允许” | P01–P05 |
| permission denied to X | 权限不足，无法 X | 语料多数 + 可读 | P14 |
| unexpected / unrecognized / expected | 意外 / 无法识别 / 预期为 | 语料多数 | P11、P09、P24 |
| too many / already exists / requires / missing | 过多 / 已存在 / 需要 / 缺少 | 书面、简洁 | P15、P13、P23、P17 |
| 引号 | ASCII `"` | R4.1 四条理由 | 不可配置 |
| 逗号与顿号 | 技术值清单、诊断字段保留 ASCII 逗号；中文列举用顿号；关系用连词或重组表达 | 2026-09-12 用户确认；138 条全量审计，101 条修订、37 条保留 | R4.4；详见 `outputs/20260912-dunhao-audit/分析报告.md` 与 `outputs/20260912-dunhao-fix/` |
| 叙述冒号（含引号后） | 全角 `：` | R4.2 | 不可配置 |
| 前缀 / 标签 / 表 / `文件:行号` 冒号 | 半角 | R4.2 | 不可配置 |
| 括注（含机器值） | 全角 `（）`；语法括号半角 | R4.3 | 不可配置 |
| 省略号 | ASCII `...` | R4.4 | 不可配置 |
| 纯行宽折行 | 允许合并 | 用户决定；两处校验器已同步 | `layout_problem()` |

## 附录 C · 文件位置

| 用途 | 路径 |
|---|---|
| 本指南 | `~/pgsty/pgnls/workbench/terminology/nls-v3-style.md` |
| 固定句式与术语裁决 | `~/pgsty/pgnls/workbench/terminology/phrasebook.tsv` |
| pgdoc 术语表 / 语境规则 / 字面保护 / 风格 | `~/pgsty/pgdoc/tmp/ref/{glossary.tsv,glossary.rules.tsv,exclude.tsv,terms-to-preserve.tsv,glossary-aliases.tsv,style.md,change.md}` |
| NLS 专有术语补充与决策记录 | `~/pgsty/pgnls/workbench/terminology/{glossary.nls.tsv,glossary.decisions.tsv}` |
| 机器校验 | `~/pgsty/pgnls/workbench/nls_lint.py` |
| 消息聚类 | `~/pgsty/pgnls/workbench/nls_cluster.py` → `workbench/v3/clusters.jsonl`、`cluster-sheet.md`、`cluster-issues.md` |
| agent 提示词 | `~/pgsty/pgnls/NLS-一致性校对-执行提示词.md` |
| 合并与发布 | `~/pgsty/pgnls/workbench/v3_merge.py` → `review-app/manage.py bundle` → 站点 `manage.py nls_import` |
| 上一版规范（历史） | `~/pgsty/pgnls/workbench/terminology/style.md`（nls-v2） |
