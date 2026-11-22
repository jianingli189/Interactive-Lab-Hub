# Final Project — Kitchen Motion Interface

课程项目的传感器/网页对接基线。头动与手动独立检测，共享单线程顺序 I²C 读取；标准输出为逐行 JSON，硬件诊断发往标准错误。

## 当前验证范围

2026-11-21（纽约时间）用户完成一次向前、向右、向左点头测试，记录恰好包含：

| t（程序启动后秒） | 动作 | action |
|---|---|---|
| 13.684 | 向前点头 | confirm |
| 15.607 | 向右点头 | next |
| 17.084 | 向左点头 | undo |

该次日志未出现额外头部事件、传感器读取错误、重试或跳过时隙。约 24.6 秒运行只能支持这次功能检查，不能代表总体准确率或长期稳定性。手部分类和计数仍是候选规则，尚未完成实时准确性验证。

## 文件

- `motion_live.py`：实时识别及 JSON 输出。
- `motion_capture.py`：硬件初始化、读取、健康检查、带动作提示的原始采集；必须与 live 文件同目录。
- `requirements.txt`：未锁版本的安装依赖，不是 Pi 环境的精确快照。
- `INTEGRATION.md`：网页对接协议、进程管理和错误处理。
- `replay_events.py`、`examples/head_session.jsonl`：无硬件回放本次真实头动日志。
- `test_offline.py`：无需硬件库的离线检查。

## 硬件映射

Raspberry Pi 5 Model B Rev 1.1；I²C 100 kHz；multiplexer 地址 0x70。

| 标识 | 通道 | 型号 | 地址 | 用途 |
|---|---|---|---|---|
| LH | 0 | LSM6DS3TR-C | 0x6A | 左手 |
| HF | 3 | LSM6DS3TR-C | 0x6A | 额头，头动主判定 |
| RH | 4 | BNO055 | 0x28 | 右手 |
| HS | 5 | MSA311 | 0x62 | 太阳穴，只读取和健康监测 |

规则依赖原有安装朝向，换朝向/佩戴方式后须重新验证。MSA311 没有陀螺仪。BNO055 为 IMUPLUS 0x08，明确设置单位；加速度 m/s²（含重力），角速度 rad/s。

## Pi 上运行

已有可工作的 `.venv` 时直接复用，不必升级依赖。新环境先在 `sudo raspi-config` 中启用 I²C，再执行：

```bash
cd "/home/pi/Interactive-Lab-Hub/Final Project"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -c "import board, adafruit_msa3xx; print('imports OK')"
python -m py_compile motion_live.py motion_capture.py
python motion_live.py --step auto
```

MSA 的 Python 导入名是 `adafruit_msa3xx`，发行包名使用 `adafruit-circuitpython-msa301`。参考 https://docs.circuitpython.org/projects/msa301/en/latest/ 。本交接未进行新环境硬件安装测试。

`--step` 可选 auto/chop/stir/flip/twist；这是启动参数，不是运行中的网页指令。启动后先静止约两秒，手部窗口还需积累约两秒；此时 unknown/features=null 正常。Ctrl+C 停止。

```bash
python motion_capture.py --task health --seconds 60
python motion_capture.py --task stir --trials 3 --note "P01 chopsticks stirring"
```

不要同时运行 capture 与 live 或多个 live 进程访问同一总线。

## 无硬件对接

```bash
python3 replay_events.py
python3 replay_events.py --fast
python3 test_offline.py
```

## 识别限制与故障处理

目标读取率 25 Hz；每秒发布状态，头/手事件在检测完成时发布。固定长度窗口和有超时的事件缓存，不保存实时原始数据到磁盘。

- 所有动作事件均带 candidate=true，表示实验性候选，不是置信概率。
- 拧瓶回转也出料：twist_stroke 是单向候选扭转，twist_cycle 是相邻反向候选的配对；不能将两种计数相加。动作计数不代表克数。
- 翻面可能与拿放铲子混淆；切菜和搅拌规则仍需负样本与独立测试。当前程序不会判断食物已熟。
- 右手读取 Errno 121 最多重试两次；不填零或复制旧帧。长间隔清空识别窗口。
- 单个传感器故障使相关检测失效；HF 故障清头部，LH/RH 故障清手部；HS 不参与头动硬判决。累计计数保留，未完成动作丢弃。
- 配置丢失时不会在 live 中自动重新初始化，需停止并重启。主线程底层 I/O 阻塞仍可能影响所有传感器，尚未做长期压力测试。
- health/capture 的重试计数为进程累计值；status=OK 不能单独证明采样均匀。

## 代码来源

`motion_live.py` 来自本次对话提供、用户报告已运行的代码。`motion_capture.py` 根据用户贴出的完整源码及之后两次 preflight/burst 补丁还原。尚未与 Pi 文件做字节级校验（SSH 需要用户认证）；没有修改阈值。真实示例日志来自用户本次提交，只保留 JSON 消息。
