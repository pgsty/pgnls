#!/usr/bin/env python3
"""s2tw — Phase-1 draft converter for the zh_TW campaign (OpenCC bootstrap).

Fills the UNTRANSLATED entries of zh_TW/<branch>/<component>.po from the
zh_CN counterpart (same msgid), converting via the reviewed term engine:

    curated rules (longest-first, span-protected) -> OpenCC s2twp (residual
    spans only) -> artifact postfix

The rules below mirror tmp/build_tw_glossary.py (v5, adversarially reviewed
2026-09-18). Regenerate both together; never apply them as a sequential sed
chain and never as bare single-character string replacements (R0.4).

Touched:   only entries whose msgstr is empty and not fuzzy, not obsolete.
Untouched: the header, translated entries (official zh_TW, R0.5 alignment
           duty) and fuzzy entries (stale official text, phase-2 work).
Marking:   filled entries get "#, fuzzy" — they are machine drafts; the
           review phase removes the flag after checks.

Usage:
    python3 bin/s2tw.py --branch master                 # all components
    python3 bin/s2tw.py --branch master --component psql
    python3 bin/s2tw.py --branch master --dry-run --stats

Requires: opencc-python-reimplemented (pip install opencc-python-reimplemented)
"""
import argparse
import os
import re
import subprocess
import sys
import tempfile

try:
    from opencc import OpenCC
except ImportError:
    sys.exit("pip install opencc-python-reimplemented")

CC = OpenCC("s2twp")

RULES = [
    # --- 官方证据组(in-tree PostgreSQL zh_TW) ---
    ("数据库集簇", "資料庫叢集", "官方", "官方 zh_TW 用 叢集(cluster);CLUSTER 命令動作為 叢集化"),
    ("集簇", "叢集", "官方", ""),
    ("备库模式", "待機模式", "官方", "pg_ctl: server is not in standby mode → 不在待機模式"),
    ("备库查询一致性", "待命查詢一致性", "官方", ""),
    ("备库", "待命伺服器", "官方", "pg_dump: standby servers → 待命伺服器;簡稱 待命"),
    ("热备", "熱備援", "官方", "libpq: hot standby mode → 熱備援模式"),
    ("温备", "溫備援", "裁定", "與 熱備援 同系列"),
    ("冷备", "冷備援", "裁定", "與 熱備援 同系列"),
    ("主库/从库", "主伺服器/從屬伺服器", "裁定", ""),
    ("主库", "主伺服器", "裁定", "與 待命伺服器 對稱;MS 為 主要"),
    ("从库", "從屬伺服器", "裁定", "MS slave = 從屬"),
    ("子事务", "子交易", "官方", ""),
    ("多事务", "多重交易", "MS", "multi- 前綴 TW 作 多重"),
    ("虚拟事务", "虛擬交易", "官方", ""),
    ("事务", "交易", "官方", "官方 zh_TW: commit the current transaction → 提交目前的交易"),
    ("两阶段提交", "兩階段提交", "官方", "官方 zh_TW: Two-phase commit → 兩階段提交(commit 不作 認可)"),
    ("提交日志", "提交日誌", "官方", "CLOG"),
    ("复制相关进程", "複寫相關行程", "官方", ""),
    ("服务器进程", "伺服器行程", "官方", "server process → 伺服器行程"),
    ("工作进程", "工作行程", "官方", "行程系列;zstd 等壓縮 worker 為 執行緒"),
    ("后台进程", "背景行程", "MS", "background = 背景"),
    ("后端进程", "後端行程", "官方", ""),
    ("启动进程", "啟動行程", "官方", ""),
    ("接收进程", "接收行程", "官方", "walreceiver"),
    ("发送进程", "發送行程", "官方", "walsender;官方用 發送"),
    ("守护进程", "常駐程式", "MS", "daemon = 常駐程式"),
    ("进程", "行程", "官方", "官方 zh_TW: child process → 子行程(MS 作 處理序)"),
    ("线程", "執行緒", "MS", ""),
    ("过程语言", "程序語言", "官方", "psql: procedural language → 程序語言"),
    ("用户映射", "使用者映射", "官方", "psql: List of user mappings → 使用者映射清單"),
    ("外部数据包装器", "外部資料包裝器", "官方", "FDW 縮寫保留"),
    ("外部数据", "外部資料", "官方", ""),
    ("外部服务器", "外部伺服器", "官方", ""),
    ("外部表", "外部資料表", "官方", "psql: Foreign table → 外部資料表"),
    ("扩展", "擴充模組", "官方", "psql: installed extensions → 已安裝擴充模組;extended(延伸)義另譯"),
    ("扩展表达式", "延伸運算式", "MS", "extended = 延伸(非 extension 物件)"),
    ("扩展查询协议", "延伸查詢協定", "MS", "extended query protocol = 延伸查詢協定"),
    ("连接字符串", "連接字串", "官方", "libpq: connection string → 連接字串;動詞/一般連線語境為 連線"),
    ("连接", "連線", "官方", "官方 zh_TW: connected → 已連線;disconnect → 中斷連線"),
    ("归并连接", "合併聯結", "MS", "merge join"),
    ("连接条件", "聯結條件", "MS", "join condition;connection 由長詞規則先處理"),
    ("连接方法", "聯結方法", "MS", "join method"),
    ("连接类型", "聯結類型", "MS", "join type"),
    ("断开", "中斷", "官方", "libpq/pg_ctl: 中斷連線"),
    ("发布", "發布", "官方", "psql: publication"),
    ("订阅", "訂閱", "官方", ""),
    ("复制槽", "複寫槽", "MS", "replication slot"),
    ("复制标识", "REPLICA IDENTITY", "官方", "SQL 關鍵字保留原文"),
    ("流复制", "串流複寫", "MS", "streaming = 串流(官方:壓縮串流)"),
    ("流式传输", "串流", "MS", ""),
    ("复制", "複寫", "MS", "replication = 複寫;copy(複製)另譯;官方亦見 複製"),
    ("副本", "複本", "MS", "read replica → 唯讀複本"),
    ("表空间", "表空間", "官方", "psql: List of tablespaces → 表空間清單(固定詞,不隨 資料表)"),
    ("系统目录", "系統目錄", "官方", "catalog = 目錄"),
    ("数据目录", "資料目錄", "官方", ""),
    ("物化", "物化", "裁定", "保留;MS/Oracle 作 具體化,PG 語境少見"),
    ("归档", "封存", "官方", "pg_dump: archive file → 封存檔案"),
    ("恢复", "復原", "官方", "pg_ctl: recovery on restart → 復原;restore 另譯 還原"),
    ("还原", "還原", "官方", "pg_dump/pg_restore: 還原"),
    ("游标", "游標", "官方", "官方 zh_TW: 游標;OpenCC 直轉會誤作 遊標"),
    ("触发器", "觸發器", "官方", "psql: 觸發器"),
    ("列级属性", "欄位層級屬性", "官方", "column-level;column = 欄/欄位,禁 MS 式 資料行"),
    ("索引级属性", "索引層級屬性", "裁定", "index-level"),
    ("行级", "資料列層級", "MS", "row-level security = 資料列層級安全性"),
    ("行安全性", "資料列安全性", "MS", ""),
    ("安全性策略", "安全性原則", "MS", "policy = 原則"),
    ("当前行", "目前資料列", "官方", "current row"),
    ("行缓存", "資料列快取", "MS", "caching rows"),
    ("行指针", "資料列指標", "裁定", "line pointer(與 row 同指)"),
    ("行构造器", "資料列建構器", "MS", "row constructor"),
    ("同等行组", "對等資料列群組", "MS", "peer group"),
    ("元组", "元組", "官方", "官方 zh_TW 保留 元組(tuple)"),
    ("操作符类", "運算子類別", "MS", "operator class;class = 類別"),
    ("操作符族", "運算子家族", "裁定", "operator family"),
    ("操作符", "運算子", "MS", "operator = 運算子"),
    ("排序规则", "定序", "官方", "collation = 定序;禁 s2t 偽影 排序規則"),
    ("区域设置", "區域", "官方", "psql: Locale Provider → 區域提供者;MS 作 地區設定"),
    ("共享", "共用", "MS", "shared = 共用"),
    ("内存", "記憶體", "官方", "libpq: 記憶體"),
    ("文件描述符", "檔案描述符", "裁定", "Linux zh_TW 慣用 描述符;MS 作 描述元"),
    ("文件", "檔案", "官方", "官方 zh_TW: 檔案"),
    ("程序", "程式", "MS", "program = 程式;procedure = 程序;process = 行程,三者分立"),
    ("语句", "敘述", "官方", "statement = 敘述"),
    ("默认", "預設", "官方", "pg_ctl: (default) → (預設)"),
    ("缺省", "預設", "裁定", ""),
    ("设置", "設定", "官方", "set = 設定;config 名詞 = 組態"),
    ("配置", "組態", "官方", "官方 zh_TW: 組態"),
    ("参数", "參數", "官方", "parameter = 參數;OpenCC 直轉會誤作 引數"),
    ("变量", "變數", "官方", "環境變數"),
    ("数组", "陣列", "MS", ""),
    ("对象", "物件", "官方", "psql: 擴充模組中的物件"),
    ("类型", "型別", "官方", "官方 zh_TW: 型別"),
    ("字符串", "字串", "MS", ""),
    ("字符类", "字元類別", "MS", "character class(regex)"),
    ("字符", "字元", "MS", ""),
    ("字节", "位元組", "MS", ""),
    ("提示位", "提示位元", "MS", "hint bits"),
    ("脏位", "髒位元", "MS", "dirty bit"),
    ("有效位", "有效位元", "MS", "valid bit"),
    ("位图", "點陣圖", "MS", "bitmap;社群亦見 位元圖"),
    ("二进制", "二進位", "MS", "十六進位/十進位 同系列,不留 制"),
    ("算法", "演算法", "MS", ""),
    ("布尔", "布林", "MS", ""),
    ("枚举", "列舉", "MS", ""),
    ("绑定", "繫結", "MS", "bind = 繫結"),
    ("递归", "遞迴", "MS", ""),
    ("循环", "迴圈", "MS", "loop = 迴圈"),
    ("嵌套循环连接", "巢狀迴圈聯結", "MS", "nested loop join"),
    ("嵌套循环", "巢狀迴圈", "MS", "nested loop"),
    ("嵌套", "巢狀", "MS", "nested = 巢狀"),
    ("窗口", "視窗", "MS", ""),
    ("哈希", "雜湊", "MS", "hash = 雜湊"),
    ("正则表达式", "正規表示式", "MS", ""),
    ("正则集", "正規集合", "MS", "regular set"),
    ("转义", "逸出", "MS", "escape = 逸出"),
    ("溢出", "溢位", "MS", ""),
    ("令牌", "權杖", "MS", "OAuth token = 權杖"),
    ("词元", "符記", "裁定", "SQL 語法 token;MS 作 語彙基元,不取"),
    ("退出", "結束", "官方", "exit = 結束(exit code = 結束碼);禁 s2t 偽影 退出/離開"),
    ("统计信息", "統計資訊", "MS", "statistics information = 統計資訊"),
    ("信息", "訊息", "官方", "message 語境 = 訊息;information 語境 = 資訊(見 統計資訊)"),
    ("用户", "使用者", "官方", ""),
    ("帮助", "說明", "官方", "help = 說明(Try \\? for help → 顯示說明)"),
    ("获取", "取得", "官方", "get = 取得"),
    ("支持", "支援", "MS", "support = 支援"),
    ("兼容", "相容", "MS", "compatible = 相容"),
    ("创建", "建立", "MS", "create = 建立"),
    ("添加", "新增", "MS", "add = 新增"),
    ("生成列", "產生欄位", "MS", "generated column"),
    ("生成", "產生", "MS", "generate = 產生"),
    ("运行", "執行", "官方", "run/execute = 執行"),
    ("访问", "存取", "MS", "access = 存取"),
    ("认证", "驗證", "MS", "authenticate = 驗證;certification 才是 認證"),
    ("授权", "授權", "MS", ""),
    ("禁用", "停用", "MS", "disable = 停用"),
    ("启用", "啟用", "MS", ""),
    ("空闲空间映射", "可用空間對應", "MS", "FSM;free = 可用"),
    ("空闲空间", "可用空間", "MS", "free space = 可用空間"),
    ("空闲", "閒置", "MS", "idle = 閒置"),
    ("超时", "逾時", "MS", ""),
    ("后台", "背景", "MS", "background = 背景;禁 s2t 偽影 後臺"),
    ("重置", "重設", "MS", "reset = 重設"),
    ("分配", "配置", "MS", "allocate = 配置(記憶體語境);distribute 仍作 分配"),
    ("解析", "解析", "裁定", "parse 保留(TW 通行);MS 作 剖析,不取"),
    ("逆解析", "反解析", "裁定", "deparse"),
    ("死锁", "死結", "MS", "deadlock = 死結;禁 s2t 偽影 死鎖"),
    ("只读", "唯讀", "MS", ""),
    ("队列", "佇列", "MS", "queue = 佇列"),
    ("信号量", "號誌", "MS", "semaphore = 號誌"),
    ("信号", "信號", "官方", "pg_ctl: 升級信號(MS 作 訊號,官方 PG 用 信號)"),
    ("保存点", "儲存點", "MS", "savepoint = 儲存點;禁 s2t 偽影 保存點"),
    ("保存", "儲存", "MS", "save = 儲存"),
    ("注释", "註解", "MS", "comment = 註解(SQL COMMENT)"),
    ("级联", "串聯", "MS", "cascade = 串聯(ON DELETE CASCADE)"),
    ("转储", "備份", "官方", "官方 pg_dump 將 dump 譯 備份;MS 傾印 不取"),
    ("集群", "叢集", "官方", "distributed cluster = 叢集"),
    ("故障切换", "容錯移轉", "MS", "failover = 容錯移轉"),
    ("计划内切换", "計畫性切換", "裁定", "switchover;與容錯移轉區分"),
    ("时间戳", "時間戳記", "MS", ""),
    ("当前", "目前", "官方", "提交目前的交易"),
    ("性能", "效能", "MS", "performance = 效能"),
    ("优化器", "最佳化工具", "MS", "optimizer;planner 是 規劃器,不可混"),
    ("优化", "最佳化", "MS", ""),
    ("硬件", "硬體", "MS", ""),
    ("网络", "網路", "MS", "network = 網路"),
    ("架构", "架構", "MS", "architecture = 架構(schema 保留原文,不再衝突)"),
    ("服务器", "伺服器", "官方", ""),
    ("节点", "節點", "MS", "node = 節點"),
    ("端口", "連接埠", "官方", "libpq: port → 連接埠;簡稱 埠/埠號"),
    ("主机", "主機", "官方", ""),
    ("本地", "本機", "官方", "local socket → 本機 socket"),
    ("打印", "列印", "MS", ""),
    ("全局暂停", "全域停止", "MS", "stop-the-world = 全域停止"),
    ("全局", "全域", "MS", "global = 全域"),
    ("内置", "內建", "MS", "built-in = 內建"),
    ("内联", "內嵌", "MS", "inline = 內嵌"),
    ("嵌入", "內嵌", "MS", "embed = 內嵌"),
    ("智能关闭", "智慧停止", "官方", "pg_ctl shutdown 家族:停止/關停,不作 關機"),
    ("快速关闭", "快速停止", "官方", ""),
    ("立即关闭", "立即停止", "官方", ""),
    ("关闭", "停止", "官方", "shutdown(伺服器語境)= 停止"),
    ("独占", "獨佔", "MS", "exclusive = 獨佔"),
    ("区域", "區域", "官方", ""),
    ("握手", "交握", "MS", "handshake = 交握"),
    ("存储", "儲存", "MS", "storage = 儲存"),
    ("外键", "外來鍵", "裁定", "MS 作 外部索引鍵;官方 psql 見 外鍵;取通行短式"),
    ("主键", "主索引鍵", "MS", "primary key = 主索引鍵"),
    ("分区键", "分割索引鍵", "官方", "psql: Partition key → 分割索引鍵"),
    ("非键", "非鍵", "裁定", "non-key(including columns)"),
    ("约束", "條件約束", "MS", "constraint = 條件約束;官方亦見 限制,待上游對齊"),
    ("访问方法", "存取方法", "MS", "access method = 存取方法"),
    ("访问路径", "存取路徑", "MS", ""),
    ("访问谓词", "存取述詞", "MS", "access predicate"),
    ("谓词", "述詞", "MS", "predicate = 述詞"),
    ("代价", "成本", "MS", "cost = 成本"),
    ("基于代价的", "基於成本的", "MS", "cost-based"),
    ("表达式", "運算式", "MS", "expression = 運算式;regex 語境用 表示式"),
    ("方括号表达式", "方括號表示式", "MS", "regex bracket expression"),
    ("选择率", "選擇率", "裁定", "selectivity;MS 作 選擇性,不取"),
    ("高频值", "最常見值", "裁定", "MCV(most common value)直譯"),
    ("非重复值", "相異值", "MS", "distinct = 相異"),
    ("过滤", "篩選", "MS", "filter = 篩選"),
    ("顺序扫描", "循序掃描", "MS", "sequential = 循序"),
    ("页头", "頁面標頭", "MS", "header = 標頭"),
    ("首部数据", "標頭資料", "MS", "header data"),
    ("标志位", "旗標", "MS", "flag bit = 旗標"),
    ("标志", "旗標", "MS", "flag = 旗標"),
    ("校验和", "檢查碼", "裁定", "checksum;MS 作 總和檢查碼"),
    ("脏页", "髒頁", "裁定", "MS 作 中途分頁,不取"),
    ("脏读", "髒讀", "裁定", "MS 作 中途讀取,不取"),
    ("块号", "區塊編號", "MS", "block number"),
    ("段文件", "區段檔案", "官方", "WAL segment file"),
    ("项指针", "項目指標", "MS", "item = 項目;pointer = 指標"),
    ("偏移号", "位移編號", "MS", "offset number;offset = 位移"),
    ("钉住", "釘選", "MS", "pin = 釘選"),
    ("未钉住", "未釘選", "MS", ""),
    ("未命中", "遺失", "MS", "cache miss = 快取遺失"),
    ("预热", "預熱", "裁定", "cache warming = 快取預熱"),
    ("记忆化", "記憶化", "MS", "memoization"),
    ("映射表", "對應表", "MS", "buffer table(hash 查找表)"),
    ("可见性映射", "可見性對應", "MS", "visibility map"),
    ("构建", "建置", "MS", "build = 建置"),
    ("构造器", "建構器", "MS", "constructor;亦作 建構子"),
    ("调用处理器", "呼叫處理器", "MS", "call handler"),
    ("内联处理器", "內嵌處理器", "MS", "inline handler"),
    ("调用", "呼叫", "MS", "call = 呼叫"),
    ("返回", "傳回", "MS", "return = 傳回"),
    ("编组", "封送處理", "MS", "marshalling"),
    ("变更", "變更", "官方", "官方:變更程序語言的定義"),
    ("更改", "變更", "官方", "change = 變更"),
    ("数据库", "資料庫", "官方", ""),
    ("数据", "資料", "官方", ""),
    ("损坏", "損毀", "MS", "corruption = 損毀"),
    ("迁移", "移轉", "MS", "migration = 移轉"),
    ("页面置换", "頁面取代", "MS", "page replacement = 頁面取代(OS 教科書)"),
    ("页面布局", "頁面配置", "MS", "page layout"),
    ("布局", "配置", "MS", "layout = 配置"),
    ("标识列", "識別欄位", "MS", "identity column"),
    ("标识符", "識別字", "裁定", "identifier;官方亦見 識別碼/識別名稱"),
    ("限定名", "限定名稱", "MS", "qualified name"),
    ("非限定名", "非限定名稱", "MS", ""),
    ("搜索路径", "搜尋路徑", "MS", "search = 搜尋"),
    ("搜索", "搜尋", "MS", ""),
    ("中间表", "中繼資料表", "MS", "intermediate = 中繼"),
    ("临时", "暫存", "MS", "temporary = 暫存"),
    ("参数化", "參數化", "MS", ""),
    ("首选类型", "偏好型別", "MS", "preferred types"),
    ("基础类型", "基底型別", "MS", "base type"),
    ("基础目录", "基底目錄", "MS", ""),
    ("基础备份", "基準備份", "MS", "base backup"),
    ("隐式", "隱含", "MS", "implicit = 隱含"),
    ("赋值", "指派", "MS", "assignment = 指派"),
    ("类型转换", "型別轉換", "MS", "cast"),
    ("强制转换", "強制轉換", "MS", "coercion"),
    ("范围类型", "範圍型別", "MS", ""),
    ("类型化表", "型別化資料表", "裁定", "typed table"),
    ("依赖图", "相依圖", "MS", "dependency = 相依"),
    ("函数依赖", "函式相依", "MS", "functionally dependent"),
    ("功能依赖", "功能相依", "MS", "functional dependency"),
    ("倒排列表", "反向列表", "MS", "postings list(inverted index 家族)"),
    ("后映像", "後映像", "MS", "after-image"),
    ("前映像", "前映像", "MS", ""),
    ("回卷", "回繞", "MS", "wraparound;亦作 環繞"),
    ("视界", "視界", "MS", "horizon"),
    ("幂等", "等冪", "MS", "idempotent = 等冪"),
    ("松耦合", "鬆耦合", "MS", "loose coupling"),
    ("端到端", "端對端", "MS", "end-to-end = 端對端"),
    ("背压", "背壓", "MS", "backpressure"),
    ("可伸缩性", "延展性", "MS", "scalability"),
    ("服务发现", "服務探索", "MS", "service discovery"),
    ("服务级别协议", "服務等級協定", "MS", "SLA"),
    ("协议", "協定", "MS", "protocol = 協定"),
    ("网络分区", "網路分割", "MS", "network partition"),
    ("分区", "資料分割", "MS", "partitioning = 資料分割"),
    ("子分区", "子分割", "裁定", "sub-partitioning"),
    ("剪枝", "修剪", "MS", "pruning = 修剪"),
    ("回放", "重播", "MS", "replay(WAL)"),
    ("再平衡", "重新平衡", "MS", "rebalancing"),
    ("分片", "分片", "MS", "sharding;MS Azure 作 分區,不取"),
    ("脑裂", "腦裂", "MS", "split brain"),
    ("法定人数", "法定人數", "MS", "quorum"),
    ("线性一致性", "線性一致性", "MS", "linearizability"),
    ("单调读", "單調讀取", "MS", "monotonic reads"),
    ("一致前缀读", "一致字首讀取", "MS", "prefix = 字首"),
    ("读偏差", "讀取偏斜", "MS", "skew = 偏斜"),
    ("写偏差", "寫入偏斜", "MS", ""),
    ("倾斜", "偏斜", "MS", "data skew"),
    ("丢失更新", "遺失更新", "MS", "lost update"),
    ("幻读", "幻讀", "裁定", "MS 作 虛設讀取,不取"),
    ("不可重复读", "不可重複讀", "MS", "non-repeatable read"),
    ("读已提交", "讀取認可", "MS", "READ COMMITTED"),
    ("可重复读", "可重複讀", "MS", "REPEATABLE READ"),
    ("可串行性", "可序列化性", "MS", "serializability"),
    ("可串行化", "可序列化", "MS", "SERIALIZABLE"),
    ("串行化异常", "序列化異常", "MS", "serialization anomaly"),
    ("串行化图", "序列化圖", "MS", "serialization graph"),
    ("快照隔离", "快照隔離", "MS", "snapshot isolation"),
    ("并发", "並行", "官方", "官方 pg_dump:parallel dumps → 並行備份;concurrency/parallel 同作 並行"),
    ("乐观并发控制", "樂觀並行控制", "裁定", "MS 作 開放式,不取"),
    ("锁协议", "鎖定協定", "MS", "2PL/S2PL"),
    ("自旋锁", "自旋鎖", "MS", "Linux zh_TW 慣用"),
    ("锁存器", "閂鎖器", "MS", "latch = 閂鎖;禁 s2t 偽影 鎖存器"),
    ("闩锁", "閂鎖器", "MS", "zh_CN 兩種寫法統一為 閂鎖器"),
    ("咨询锁", "諮詢鎖定", "MS", "advisory lock"),
    ("谓词锁", "述詞鎖定", "MS", "predicate lock"),
    ("杂项", "雜項", "MS", ""),
    ("日志序列号", "日誌序列號", "MS", "LSN"),
    ("预写式日志", "預寫式日誌", "裁定", "WAL 縮寫保留"),
    ("写放大", "寫入放大", "MS", "write amplification"),
    ("整页镜像", "整頁映像", "MS", "full-page image;image = 映像"),
    ("增量备份", "增量備份", "裁定", "MS 作 累加,不取"),
    ("时间点恢复", "時間點復原", "MS", "PITR"),
    ("崩溃恢复", "崩潰復原", "裁定", "MS crash = 當機,不取"),
    ("恢复目标", "復原目標", "MS", "recovery target"),
    ("检查点记录", "檢查點記錄", "MS", "checkpoint record"),
    ("检查点", "檢查點", "官方", "pg_ctl: 日誌檢查點"),
    ("检查点进程", "檢查點行程", "官方", "checkpointer"),
    ("重做日志", "重做日誌", "MS", "REDO log"),
    ("撤销日志", "復原日誌", "MS", "UNDO log;TW undo = 復原(與 recovery 同詞,依語境)"),
    ("重做点", "重做點", "MS", "REDO point"),
    ("刷盘", "排清", "MS", "flush = 排清"),
    ("示例", "範例", "MS", "example = 範例"),
    ("级别", "層級", "MS", "level;isolation level 亦可 隔離等級"),
    ("后缀", "字尾", "MS", "suffix = 字尾;prefix = 字首"),
    ("等价类", "等價類別", "MS", "equivalence class"),
    ("三字符组", "三元組", "裁定", "trigram;PG pg_trgm"),
    ("反向引用", "反向參考", "MS", "backreference"),
    ("非贪婪", "非貪婪", "MS", "non-greedy"),
    ("分布式", "分散式", "MS", "distributed = 分散式"),
    ("领导者", "領導者", "MS", "leader"),
    ("追随者", "追隨者", "MS", "follower"),
    ("无主", "無主", "MS", "leaderless"),
    ("推测插入", "推測性插入", "MS", "speculative insertion"),
    ("会话", "工作階段", "官方", "pg_ctl hint: 中斷工作階段"),
    ("阶段", "階段", "MS", "stage"),
    ("单用户模式", "單人模式", "官方", "pg_ctl: single-user server → 單人模式伺服器"),
    ("单用户", "單人", "官方", ""),
    ("发送", "發送", "官方", "pg_ctl: 發送升級信號"),
    ("监控", "監視", "MS", "monitor = 監視"),
    ("交互", "互動", "MS", "interactive = 互動"),
    ("列表", "清單", "MS", "list = 清單"),
    ("选择列表", "選取清單", "MS", "select list"),
    ("目标列表", "目標清單", "MS", "target list"),
    ("输出列表", "輸出清單", "MS", "output list"),
    ("字段", "欄位", "官方", "field = 欄位,與 column 同詞"),
    ("索引列", "索引欄位", "官方", "index column"),
    ("视图", "檢視", "官方", ""),
    ("合并", "合併", "MS", "merge/combine = 合併"),
    ("归并", "合併", "MS", "merge = 合併"),
    ("外连接", "外部聯結", "MS", "outer join"),
    ("反连接", "反聯結", "MS", "anti-join"),
    ("半连接", "半聯結", "MS", "semi-join"),
    ("等值连接", "等值聯結", "MS", "equi-join"),
    ("参数化连接", "參數化聯結", "MS", "parameterized join"),
    ("哈希连接", "雜湊聯結", "MS", "hash join"),
    ("队头阻塞", "佇列頭端阻塞", "MS", "head-of-line blocking"),
    ("笛卡尔积", "笛卡兒積", "MS", "Cartesian product"),
    ("物理结构", "實體結構", "官方", "physical = 實體(官方 zh_TW 高頻)"),
    ("物理", "實體", "官方", "physical = 實體"),
    ("引用完整性", "參照完整性", "MS", "referential integrity;MS 亦作 參考完整性"),
    ("常规", "一般", "MS", "regular = 一般"),
    ("关系扩展锁", "關係延伸鎖定", "MS", "relation extension;extend = 延伸(與 擴充模組 區分)"),
    ("层级锁", "層級鎖定", "MS", "level locks"),
    ("日志压实", "日誌壓實", "裁定", "compaction;避免與 壓縮(compression)相撞"),
    ("提取-转换-加载", "擷取-轉換-載入", "MS", "ETL;extract = 擷取"),
    ("语义", "語意", "MS", "semantics = 語意"),
    ("格式说明符", "格式規範", "MS", "format specifier"),
    ("格式代码", "格式代碼", "MS", "format code;code(編號)= 代碼,原始碼才是 程式碼"),
    ("牺牲", "犧牲", "MS", "victim page"),
    ("吞吐量", "輸送量", "MS", "throughput"),
    ("延迟", "延遲", "MS", "latency"),
    ("响应时间", "回應時間", "MS", "response = 回應"),
    ("层次", "階層", "MS", "hierarchical"),
    ("接口", "介面", "MS", "interface = 介面"),
    ("编程", "程式設計", "MS", "programming"),
    ("调试", "偵錯", "MS", "debug = 偵錯"),
    ("异步", "非同步", "官方", "非同步通知"),
    ("优先级", "優先順序", "MS", "priority"),
    ("缓冲区", "緩衝區", "MS", "buffer"),
    ("缓存", "快取", "MS", "cache = 快取"),
    ("本地缓存", "本機快取", "官方", "local cache"),
    ("描述符", "描述符", "MS", "descriptor"),
    ("管理器", "管理員", "MS", "manager = 管理員"),
    ("写入器", "寫入器", "MS", "writer"),
    ("自动", "自動", "官方", ""),
    ("清理", "清理", "官方", "pg_dump --clean 語境;VACUUM 說明義"),
    ("急切", "積極", "MS", "eager = 積極"),
    ("碎片整理", "碎片整理", "MS", ""),
    ("去重", "去重", "裁定", "MS 作 重複資料刪除,不取"),
    ("空洞", "空洞", "MS", "hole"),
    ("批量", "大量", "MS", "bulk = 大量"),
    ("批次", "批次", "MS", "batch"),
    ("响应", "回應", "MS", ""),
    ("字面", "字面", "MS", "literal"),
    ("截断", "截斷", "MS", "truncation"),
    ("关键字", "關鍵字", "官方", "psql: SQL 關鍵字"),
    ("空值", "空值", "MS", "NULL"),
    ("序号", "序號", "MS", ""),
    ("随机", "隨機", "MS", ""),
    ("直方图", "直方圖", "MS", ""),
    ("边界值", "邊界值", "MS", ""),
    ("百分位点", "百分位數", "MS", "percentile"),
    ("百分位数", "百分位數", "MS", ""),
    ("中位数", "中位數", "MS", "median"),
    ("平均值", "平均數", "MS", "mean"),
    ("采样", "取樣", "MS", "sampling"),
    ("最近邻", "最近鄰居", "MS", "nearest neighbor"),
    ("对等", "對等", "MS", "peer"),
    ("同等", "對等", "MS", ""),
    ("兄弟", "兄弟", "MS", "siblings"),
    ("自引用", "自參考", "MS", "self-referential"),
    ("排他", "排他", "MS", "exclusion"),
    ("组合函数", "合併函式", "MS", "combine function"),
    ("最终函数", "最終函式", "MS", "final function"),
    ("状态转移", "狀態轉換", "MS", "state transition"),
    ("转移函数", "轉換函式", "MS", "transition function"),
    ("过渡", "轉換", "MS", "transition tables/relations"),
    ("逆向", "逆向", "MS", "inverse"),
    ("捕获", "擷取", "MS", "capture(CDC)"),
    ("坐标", "座標", "MS", "coordinate"),
    ("儒略日", "儒略日", "MS", "Julian date"),
    ("时间线", "時間軸", "MS", "timeline;TimeLineID 原樣;社群 時間線 亦見"),
    ("环形", "環形", "MS", "ring"),
    ("堆排序", "堆積排序", "MS", "heapsort"),
    ("分组", "分組", "MS", "GROUP BY = 分組"),
    ("假想集", "假設集", "MS", "hypothetical-set"),
    ("移动聚合", "移動聚合", "MS", "moving-aggregate"),
    ("意外", "非預期", "官方", "官方:unexpected section → 非預期;與 zh_CN 意外 相反"),
    ("无法识别", "無法識別", "官方", "pg_ctl: 無法識別的關停模式"),
    ("已弃用", "已棄用", "裁定", "MS 作 已淘汰,不取"),
    ("权限", "權限", "官方", "官方:權限;OpenCC 直轉會誤作 許可權"),
    ("软件", "軟體", "MS", ""),
    ("主流", "主流", "MS", ""),
    ("日志", "日誌", "官方", ""),
    ("查询", "查詢", "官方", ""),
    ("索引", "索引", "官方", ""),
    ("序列", "序列", "官方", ""),
    ("别名", "別名", "MS", "alias"),
    ("占用", "佔用", "MS", ""),
    ("失败", "失敗", "官方", ""),
    ("磁盘", "磁碟", "MS", "disk"),
    ("验证", "驗證", "官方", ""),
    ("受信任", "受信任", "MS", "trusted"),
    ("状态", "狀態", "官方", ""),
    ("标签", "標籤", "MS", "tag"),
    ("監聽", "監聽", "官方", "listen"),
    ("监听", "監聽", "官方", ""),
    ("独热", "獨熱", "MS", "one-hot"),
    ("预写", "預寫", "MS", ""),
    ("函数", "函式", "官方", ""),
    ("锁定", "鎖定", "MS", "identity 守衛:長於 鎖,避免 鎖定子句 → 鎖定定子句"),
    ("锁", "鎖定", "官方", "lock = 鎖定;鎖存器/自旋鎖/鎖定協定 由長詞規則先處理"),
    ("重量级锁", "重量級鎖定", "MS", "heavyweight locks"),
    ("轻量级锁", "輕量級鎖定", "MS", "lightweight locks"),
    ("行级锁", "資料列層級鎖定", "MS", "row-level locks"),
    ("关系级锁", "關係層級鎖定", "MS", "relation-level locks"),
    ("页锁", "頁面鎖定", "MS", "page locks"),
    ("行类型", "資料列型別", "MS", "row type"),
    ("表别名", "資料表別名", "MS", "table alias"),
    ("表表达式", "資料表運算式", "MS", "table expression"),
    ("堆表", "堆積資料表", "MS", "heap table"),
    ("分区表", "分割資料表", "官方", "psql:Partitioned table → 分割資料表;pg_dump 亦見 分區(官方內部不一致),取 psql 主流 分割"),
    ("分区边界", "分割界限", "MS", "partition bounds"),
    ("分区", "分割", "官方", "官方 psql 主流:declarative table partitioning → 聲明式資料表分割;分割索引鍵;不取 MS 資料分割"),
    ("备份块", "備份區塊", "MS", "backup block"),
    ("事务块", "交易區塊", "MS", "transaction block"),
    ("缓冲池", "緩衝集區", "MS", "buffer pool;MS SQL zh-TW 用語"),
    ("多表索引簇表", "多資料表索引叢集資料表", "MS", "multi-table index cluster tables"),
    ("WAL 段", "WAL 區段", "官方", "segment = 區段"),
    ("版本信息", "版本資訊", "MS", "information 語境 = 資訊;先於 信息→訊息"),
    ("分区表达式", "分割運算式", "MS", "partition expression;守衛:防 分区表 跨詞界誤傷"),
    ("进行类型", "進行型別", "MS", "identity 守衛:進行|類型 跨詞界,防 行类型 誤傷;類型 隨即依 型別 規則"),
    ("详细信息", "詳細資訊", "MS", "DETAIL 標籤 = 詳細資訊;先於 信息→訊息"),
    ("官方", "官方", "MS", "evidence tag"),
]

#
POSTFIX = [
    ("許可權", "權限"),
    ("運運算元", "運算子"),
    ("演演算法", "演算法"),
    ("程式語言", "程序語言"),  # 僅本表:procedure language;programming language 行已由規則覆蓋
    ("引數", "參數"),          # 本表無 argument 列,安全
    ("對映", "映射"),
    ("連線字串", "連接字串"),
    ("主頁", "首頁"),
    ("遊標", "游標"),
    ("專案", "項目"),
]


# ---------------------------------------------------------------- engine ---

def compile_engine(rules):
    ordered = sorted(rules, key=lambda r: len(r[0]), reverse=True)
    pattern = re.compile("(" + "|".join(re.escape(r[0]) for r in ordered) + ")")
    mapping = {r[0]: r for r in ordered}
    return pattern, mapping


PATTERN, MAPPING = compile_engine(RULES)


def convert(text):
    """zh_CN -> zh_TW, single pass, longest-first, rule spans protected."""
    parts = re.split(PATTERN, text)
    out = []
    for i, part in enumerate(parts):
        if i % 2 == 0:
            out.append(CC.convert(part))
        else:
            out.append(MAPPING[part][1])
    s = "".join(out)
    for a, b in POSTFIX:
        s = s.replace(a, b)
    return s


# ------------------------------------------------------------------- po ----

def po_escape(s):
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\t", "\\t")


class Entry:
    __slots__ = ("comments", "lines")

    def __init__(self, lines, comments):
        self.lines = lines          # source lines of the entry body
        self.comments = comments    # source comment lines (#..., including flags)


def parse_po(path):
    """Split a PO file into (header_entry, entries). Obsolete #~ blocks are
    returned as entries too (never modified)."""
    raw = open(path, encoding="utf-8").read().splitlines()
    entries, comments, body, seen_header = [], [], [], False
    for line in raw:
        if not line.strip():
            if body or comments:
                entries.append((seen_header, comments, body))
                if seen_header is False and any(l.startswith("msgstr") for l in body):
                    seen_header = True
                comments, body = [], []
            continue
        if line.startswith("#"):
            if body:  # trailing comment of previous block boundary
                entries.append((seen_header, comments, body))
                if seen_header is False and any(l.startswith("msgstr") for l in body):
                    seen_header = True
                comments, body = [], []
            comments.append(line)
        else:
            body.append(line)
    if body or comments:
        entries.append((seen_header, comments, body))
    return entries


def entry_text(entry, key):
    """Concatenated string of msgid / msgid_plural / msgstr / msgstr[0]..."""
    is_header, comments, body = entry
    grab = False
    parts = []
    for line in body:
        if line.startswith("msgid "):
            grab = (key == "msgid")
            parts = [line[6:].strip().strip('"')] if grab else parts
        elif line.startswith("msgid_plural "):
            grab = (key == "msgid_plural")
            parts = [line[13:].strip().strip('"')] if grab else parts
        elif line.startswith("msgstr"):
            want = (key == "msgstr" and "[" not in line) or \
                   (key.startswith("msgstr[") and line.startswith(key))
            grab = want
            if want:
                parts = [line.split(" ", 1)[1].strip().strip('"') if " " in line else ""]
        elif line.startswith('"'):
            if grab:
                parts.append(line.strip().strip('"'))
    return "".join(parts)


def entry_flags(entry):
    out = []
    for c in entry[1]:
        if c.startswith("#,"):
            out.extend(f.strip() for f in c[2:].split(","))
    return out


def unpoescape(s):
    out, i = [], 0
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s):
            n = s[i + 1]
            out.append({"n": "\n", "t": "\t", '"': '"', "\\": "\\", "r": "\r"}.get(n, n))
            i += 2
        else:
            out.append(c)
            i += 1
    return "".join(out)


def fill_entry(entry, zh_cn_msgstr, plural, cn_plurals):
    """Return new body lines with msgstr filled from converted zh_CN text."""
    is_header, comments, body = entry
    conv = convert(unpoescape(zh_cn_msgstr))
    new = []
    if plural:
        convs = [convert(unpoescape(p)) for p in cn_plurals] or [conv]
        idx = 0
        for line in body:
            if line.startswith("msgstr"):
                if "[" in line:
                    val = convs[idx] if idx < len(convs) else convs[-1]
                    idx += 1
                    new.append('msgstr[%d] "%s"' % (idx - 1, po_escape(val)))
                else:
                    new.append('msgstr "%s"' % po_escape(convs[0] if convs else conv))
            else:
                new.append(line)
        return new
    seen_msgstr = False
    for line in body:
        if line.startswith("msgstr") and not seen_msgstr:
            new.append('msgstr "%s"' % po_escape(conv))
            seen_msgstr = True
        elif line.startswith('"') and seen_msgstr:
            continue  # continuation of the old (empty) msgstr
        else:
            new.append(line)
    return new


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--branch", default="master")
    ap.add_argument("--component", default=None)
    ap.add_argument("--zh-cn", default="zh_CN")
    ap.add_argument("--zh-tw", default="zh_TW")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--stats", action="store_true", help="only print counts")
    ap.add_argument("--verify", action="store_true", help="msgfmt the result with fuzzy stripped")
    args = ap.parse_args()

    tw_dir = os.path.join(args.zh_tw, args.branch)
    cn_dir = os.path.join(args.zh_cn, args.branch)
    names = sorted(os.listdir(tw_dir)) if os.path.isdir(tw_dir) else []
    if args.component:
        names = [n for n in names if n == args.component + ".po"]
    grand = {"files": 0, "filled": 0, "no_cn": 0, "skip": 0}
    for name in names:
        if not name.endswith(".po"):
            continue
        tw_path = os.path.join(tw_dir, name)
        cn_path = os.path.join(cn_dir, name)
        if not os.path.exists(cn_path):
            print("  %s: no zh_CN counterpart, skipped" % name)
            continue
        cn_entries = parse_po(cn_path)
        cn_map = {}
        for e in cn_entries:
            mid = entry_text(e, "msgid")
            if mid and mid != '""' and not any(c.startswith("#~") for c in e[1]):
                cn_map[mid] = e
        out_lines, filled, no_cn, skipped = [], 0, 0, 0
        entries = parse_po(tw_path)
        pending_comment = None
        for idx, entry in enumerate(entries):
            is_header, comments, body = entry
            if not body:
                out_lines.extend(comments)
                out_lines.append("")
                continue
            obsolete = any(c.startswith("#~") for c in comments)
            flags = entry_flags(entry)
            mid = entry_text(entry, "msgid")
            plural = bool(entry_text(entry, "msgid_plural"))
            cur = entry_text(entry, "msgstr") or entry_text(entry, "msgstr[0]")
            if idx == 0 or mid == '""' or obsolete or "fuzzy" in flags or cur:
                skipped += 1
                out_lines.extend(comments + body)
            elif mid in cn_map:
                cn = cn_map[mid]
                cn_str = entry_text(cn, "msgstr")
                cn_plurals = []
                if plural:
                    i = 0
                    while True:
                        t = entry_text(cn, "msgstr[%d]" % i)
                        if t == "" and i > 0:
                            break
                        cn_plurals.append(t)
                        i += 1
                        if i > 4:
                            break
                new_body = fill_entry(entry, cn_str, plural, cn_plurals)
                new_comments = list(comments)
                if new_comments and new_comments[0].startswith("#,"):
                    if "fuzzy" not in new_comments[0]:
                        new_comments[0] += ", fuzzy"
                else:
                    new_comments.insert(0, "#, fuzzy")
                out_lines.extend(new_comments + new_body)
                filled += 1
            else:
                no_cn += 1
                out_lines.extend(comments + body)
            out_lines.append("")
        text = "\n".join(out_lines) + "\n"
        text = re.sub(r"\n{3,}", "\n\n", text)
        if not args.stats and not args.dry_run and filled:
            open(tw_path, "w", encoding="utf-8").write(text)
        if args.verify and filled and not args.dry_run and not args.stats:
            fixture = text.replace("#, fuzzy\n", "")
            with tempfile.NamedTemporaryFile("w", suffix=".po", delete=False, encoding="utf-8") as tf:
                tf.write(fixture)
                tmp_name = tf.name
            r = subprocess.run(["msgfmt", "--check", "--check-format", "-o", "/dev/null", tmp_name],
                               capture_output=True, text=True)
            os.unlink(tmp_name)
            if r.returncode:
                print("  %s: FILLED %d but fixture msgfmt FAILED\n%s" % (name, filled, r.stderr[:400]))
                sys.exit(1)
        if filled or no_cn:
            print("  %s: filled %d, no zh_CN match %d, kept as-is %d%s" %
                  (name, filled, no_cn, skipped, "  [dry-run]" if args.dry_run else ""))
        grand["files"] += 1
        grand["filled"] += filled
        grand["no_cn"] += no_cn
        grand["skip"] += skipped
    print("TOTAL %s/%s: %d files, filled %d entries, no zh_CN match %d" %
          (args.zh_tw, args.branch, grand["files"], grand["filled"], grand["no_cn"]))


if __name__ == "__main__":
    main()
