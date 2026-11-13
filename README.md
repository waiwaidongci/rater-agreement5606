# 杉序岩芯标记一致性簿

杉序岩芯图谱研究组有17位标记分析员，由固定三位标记者对独立匿名岩芯图像分类。上游输入 `sx-core-panel-1-202611.json` 等逐人标签，本系统替代表格里的逐票计数与随意重采样，下游是负责人批准的类别边界复核说明。三个具体痛点是只报一致百分比、类别失衡的机会基线被忽略、按单票重采样破坏同一试样结构。

固定种子生成3项研究×120试样×3票=1080标签、四种岩相，分别覆盖多类评议、类别失衡、全单类未定义边界。数据为合成匿名图像编号，不含现场地质结论。Fleiss κ是相对类别基率的一致性，不是与金标准对照的准确率。

## 启动、环境和角色

```sh
cp .env.example .env
docker compose up --build -d --wait
docker compose exec -T backend python -m scripts.seed_demo
```

|入口|地址|
|---|---|
|浏览器|http://localhost:18235|
|API / Swagger|http://localhost:19235/docs|
|MySQL|127.0.0.1:17735|

|账号 / 密码|权限与主要页面|典型动作|
|---|---|---|
|admin@shanxu.demo / Shanxu2026!|六页、写入与审阅|批准或退回分类口径复核|
|analyst@shanxu.demo / Shanxu2026!|六页、导入/改票/运行/说明|修订逐票、排队；审批403|
|viewer@shanxu.demo / Shanxu2026!|六页只读、批准CSV|阅读逐票与结果、下载快照；写入403|

首次启动自动seed，手动独立执行也幂等，不覆盖用户改票、试样说明和复核意见。`.env.example`含三个端口、MYSQL_DATABASE/USER/PASSWORD/ROOT_PASSWORD、JWT_SECRET、SEED_DEMO、RATE_LIMIT_WRITES默认60。演示密码和JWT secret仅用于本地，部署须设置自己的值。

Compose恰好frontend/backend/worker/db/redis五服务，均有健康检查。Nginx `/api/`移除前缀后转发FastAPI，前端探针127.0.0.1；backend等待DB/Redis，worker再等待backend。Celery真队列保存运行JSON和数据库结果，共享artifacts卷。停止清除本题演示数据：`docker compose down -v --remove-orphans`。

## 标记分析员的一天

1. 09:00，秦砚登录“评议总览”，先看逐票格和类别基率，区分一致性与准确率。
2. 09:10，在“试样与逐票”选择 `SX-31A 多类图谱评议`，核对文件 `sx-core-panel-1-202611.json`，如 `SX1-IMG-001` 的固定三票。
3. 核对原面板“标记者甲 / 标记者乙 / 标记者丙”，以及声明类别顺序“砂岩 / 粉砂岩 / 泥岩 / 碳酸盐岩”。每人每试样恰一票；缺票、重复人、未知类会拒绝。试样补注和改票均留痕。
4. 在“固定面板配置”预先设B=400、seed=231。A研究带岩芯编号（40个岩芯、组大小2或4，不等组），队列按岩芯成组重采样；无岩芯字段的旧研究仍逐试样。
5. A研究实际N120/360票，Pbar=0.7083333333、Pe=0.2511265432、κ=0.6105260989。类别总票97/95/84/84，一起解释机会基线。
6. 读400有效/0退化重复和经验percentile区间[0.5227401669,0.6846227401]，可展开每组试样归属、每次抽中岩芯×倍数→试样总数、κ与失败理由。区间按岩芯成组解释，不再假设同芯试样iid。
7. 对照“单类边界评议”：全部票同类时Pe=1、κ未定义，worker会失败，不把它标成κ1。全一致但有多类时κ可以1。
8. 在“口径复核”写争议试样的类别边界与独立复核行动，保持原三位标记者。说明冻结整份统计与bootstrap快照。
9. 负责人纪岚批准/退回；观察员陶野下载批准CSV（κ、Pbar、Pe、重采样单位、岩芯组数/组大小、前8次抽中岩芯×倍数→试样总数、有效/退化数、区间、逐试样P、岩芯与计数）。重复审批409，后续改票不改写已有快照；过程留痕核对全部动作。

## Fleiss κ与成组bootstrap口径

设N个试样、r=3个固定标记者、C个预先声明的名义类别，nᵢⱼ是试样i被分到类别j的票数。每行总数必须3：

`Pᵢ = Σⱼ nᵢⱼ(nᵢⱼ−1) / [r(r−1)]`

`Pbar = mean(Pᵢ)`，`pⱼ = Σᵢ nᵢⱼ/(Nr)`，`Pe = Σⱼ pⱼ²`，`κ = (Pbar−Pe)/(1−Pe)`。

后端用整数计数和Fraction计算核心比值，先判断Pe恰等于1再转JSON浮点。Pe=1未定义；全一致多类别κ1；未出现类别保留在声明顺序中，计数0。κ可为负，不裁成0，也不解读为识别准确率。试样级P和类别基率与κ同时保存。

Bootstrap固定seed，B400–1000次。若有岩芯编号（`specimens.core`）：以岩芯为抽样单位，每次有放回抽原数量K个岩芯，抽中岩芯携带其全部试样进入该次重复，重复抽中保留倍数（同芯出现m次即整组重复m份）；保存抽中岩芯列表、倍数、试样总数和行索引。每行原三票绑定，不能按单票抽，也不能把标记者当新抽样单位。点估计始终用原逐票全部试样行等权计算，与组大小无关；不等组不改变κ。缺组（部分试样有岩芯、部分为空）或不足两组拒绝，提示补齐或全部留空。无岩芯字段的旧数据（`core=''`）沿用逐试样iid重采样，不推断分组。每次重新计算κ；Pe=1的重复保存null κ、抽取记录和失败原因，未补抽替换。

有效数/B≥90%才报告有效重复κ的2.5%和97.5%线性percentile经验区间（NumPy quantile method=linear）；不足90%保留全部重复并明确“暂不报告”，门槛不因成组而改变。这是预先设定的可报告门槛，不是有限样本精确覆盖保证。有岩芯时条件为岩芯可交换、面板固定；无岩芯时才是试样iid。两者都不含抽取新标记者的不确定性；空间相关、共享图像或类别定义改变会影响解释。

手算例四试样二类计数[3,0]/[2,1]/[1,2]/[0,3]：Pbar=2/3、Pe=.5、κ=1/3。B400/seed231得到397有效、3退化，经验区间约[-.3714285714,1]。两试样[3,0]/[0,3]虽κ1，但同参数只有205有效/195退化，不报告区间。真实API与浏览器都验证了这些边界。

成组手算例四试样二类、岩芯分组C1={[3,0],[2,1]}与C2={[0,3]}（组大小2/1，不等组）：点估计仍为全四行κ=1/3，不因C1样本多而加权。B400/seed231按2个岩芯有放回抽取，每次携带整组，抽中C1两次时该重复为4行（C1整组重复两份），抽中C1/C2各一次时为3行；重复抽中的倍数不合并也不补抽。区间仅在有效比例≥90%时报告。旧数据`core=''`与改造前逐试样结果一致（同seed逐次抽取完全相同）。

MySQL的κ/Pbar/Pe列均用DOUBLE(asdecimal=False)，保持Python float，避免默认Decimal十位小数转换损失；API逐项与JSON结果比到1e-15并查询实际列类型。

## 结构与校验

79个有职责的Python/TS/Vue/CSS源文件（不计空包、依赖和dist）。五实体AgreementStudy → Specimen（含core分组）→ RaterVote → AgreementRun → ReviewMemo贯穿ORM/schema/service/routes、前端API/store和六页：评议总览、试样与逐票、固定面板配置、κ与重采样、口径复核、过程留痕。

前端 `src/{api,stores,types,components/common,hooks,pages,router,utils,constants}`；后端 `src/{routes,controllers,services,models,schemas,middlewares,utils,constants,config}`，另scripts/seed_demo.py与migrations/。VoteMatrix、AgreementSummary、CategoryMargins、RunList多页复用，BootstrapStrip展示后端实际频数和经验区间；useTask/useRoute和format工具处理交互。

角色Role、运行RunStatus、审阅MemoStatus位于 `backend/src/constants/enums.py`，前端对应 `frontend/src/constants/enums.ts`。JWT授权、审计、RequestID/Error/Redis写限流三个中间件形成横切链路。配额按令牌摘要或无令牌IP与分钟计数，默认60写请求、超限429含Retry-After；计数服务不可用503，健康GET不计。审批行锁限制draft只能审一次，批准导出取result_snapshot。

2–240试样、声明2–6唯一类别、固定3位唯一标记者；每试样同一面板各一票。岩芯编号可全部留空（逐试样）或全部填写且至少两组，缺组/单组拒绝；CFG页与复核页显示组数、组大小和不等组标记。重复试样、重复人、缺票、未知类别和非法B/seed拒绝；安全422不回显NaN等非法input。全单类数据可存底稿，但κ计算明确失败，不伪造结果。指纹按试样编号/票键排序，行序稳定，对票、试样说明、类别/面板顺序和参数敏感。

|层|技术|
|---|---|
|前端|Vue3 / TypeScript / Vite6.4.6；Public Sans+Noto Serif SC；炭灰逐票图谱|
|后端|Python3.11 / FastAPI / SQLAlchemy / MySQL8|
|队列|Celery5.4 / Kombu5.4.2 / Redis7，worker并发1|
|数值|整数/Fraction Fleiss κ、按岩芯成组或逐试样bootstrap、真实频数SVG|

本地前端 `cd frontend && npm ci && npm run dev`；`npm run build`执行vue-tsc与Vite。后端安装requirements并设置DATABASE_URL/REDIS_URL/JWT_SECRET后运行uvicorn。当前用ORM create_all建表，migrations提供初始结构说明，不声称生产版本迁移链。许可证MIT，见LICENSE。

实际验收见批次 `test-artifacts/gb-0031/TESTING.md`，测试脚本、关键JSON、CSV、PNG、原始.log与源码分离。未做外部真实岩相准确率验证、生产压力或完整无障碍审计。令牌/IP分钟限流不是生产抗滥用全链路，重新登录可获得新令牌计数。Google字体断网时回退本地字体。任何复核方案仍需试验员结合图谱定义执行，不提供地质因果或现场风险保证。
