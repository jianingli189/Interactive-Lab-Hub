# Recipe in Motion — Interactive Kitchen

Cornell Tech Developing & Designing Interactive Devices · Fall 2026
Team: Jianing Li (jl4837), Aurora Jiaxin Shen (js3996), Tzu-Yao Chang (tc845)
运行指南更新：2026-11-23（单手降级展示版）

一个可交互鸡蛋饼菜谱：头部动作负责确认、下一步和撤销；手部动作驱动当前步骤的动画反馈；另一个 Pi 上的 proximity sensors 检测厨具拿起与归位。网页内容为英文，终端状态提示为中文。

> 当前版本包含两种模式。展示版检测“明显运动”，由菜谱步骤和厨具状态赋予含义；它不是具体动作分类准确性的证据。实验版保留动作类别规则。实际测试仍有间歇 I²C 故障，自动恢复和单手降级不能证明硬件已长期稳定。

## 1. 系统组成与文件

数据路径：动作 Pi → 本机 Python bridge（HTTP SSE，8765）→ Mac SSH tunnel（18765）→ 网页（5173）。厨具 Pi → 课程 MQTT broker → 动作 Pi 的同一个 bridge → 网页。

| 文件／目录 | 用途 |
|---|---|
| `src/`, `index.html`, `package*.json`, `vite.config.ts`, `tsconfig.json` | React/TypeScript/Vite 网页 |
| `motion_capture.py` | 四个传感器的配置、原始数据读取和采集 |
| `motion_live.py` | 实验版：头动方向与具体手部动作候选识别 |
| `motion_demo.py` | 展示版：复用头动，手部只检测明显运动；允许单手降级 |
| `sensor_recovery.py` | 分传感器健康检查、退避重试和配置恢复 |
| `safe_mux.py` | multiplexer 锁异常清理和等待超时 |
| `bridge/` | 启动动作子程序、接收 MQTT、向网页发送事件、中文终端输出 |
| `pi-utensils/` | 队友 Pi 的厨具识别程序与安装依赖 |
| `tests/`, `examples/`, `bridge/fixtures/` | 自动化测试和历史事件记录；不等于新的实机验证 |
| `docs/2026-11-21-motion-baseline.md`, `INTEGRATION.md` | 历史测试／对接资料；启动方式以本 README 为准 |

不提交虚拟环境、node_modules、运行日志、个人路径备份或密码。旧的逐次补丁安装脚本不需要再运行，本仓库的程序已包含最新修改。

### 动作 Pi 硬件映射

| Mux 通道 | 名称 | 型号 | 地址 |
|---|---|---|---|
| 0 | LH 左手 | LSM6DS3TR-C（照片系列 LSM6DS3） | 0x6A |
| 3 | HF 额头 | LSM6DS3TR-C | 0x6A |
| 4 | RH 右手 | BNO055 | 0x28 |
| 5 | HS 右太阳穴 | MSA311，仅加速度 | 0x62 |

头动实际方向判断来自 HF；HS 参与读取与健康监测。程序识别兼容的原版 LSM6DS3 身份。Mux 地址为 0x70。

厨具 Pi：CH0 筷子、CH1 刀、CH5 铲子、CH6 盐瓶使用 APDS9960；CH7 黑胡椒瓶使用 VCNL4040。阈值在 `pi-utensils/utensil_detection.py` 的 CONFIG 中，是当前装置的参数，改变摆放位置后需要重新验证。

## 2. 先弄清楚四个终端

| 终端 | 实际在哪台设备运行 | 保持运行的程序 |
|---|---|---|
| 1 | 队友 Pi，SSH 登录后 | 厨具识别／MQTT 发布 |
| 2 | Jianing 的 Pi，SSH 登录后 | bridge + 自动启动的动作程序 |
| 3 | Mac | 网页开发服务器 |
| 4 | Mac | SSH 端口转发 |

`pi@jeniejianingli` 是自己的 Pi，`pi@raspberrypi-regina` 是队友的 Pi。`jianing@...` 或 `bash-3.2$` 通常是 Mac。SSH 转发窗口输入密码后没有输出是正常的，不要在该窗口再输入命令。

当前已知 IP：自己的 Pi `10.56.130.63`；队友 Pi `10.56.129.47`。换网络或重启后可能变化；用 Pi 屏幕显示或 `hostname -I` 确认。两个 SSH 登录用户名都是 **pi**。下面所有命令中的 IP 必须与设备当前 IP 一致。

## 3. 首次下载、更新与安装（不是每次开机都做）

### Mac 获取仓库

新电脑需要 Git、Node.js/npm 和 SSH 客户端。下载到固定位置：

```bash
mkdir -p "$HOME/Documents"
cd "$HOME/Documents"
git clone --branch Fall2026 https://github.com/jianingli189/Interactive-Lab-Hub.git
cd "Interactive-Lab-Hub/Final Project"
npm ci
```

已经下载过就进入该仓库执行 `git pull --ff-only`，不要覆盖未提交的个人修改。依赖文件更新后再执行 `npm ci`。

**Jianing 本次更新已经整理在这个本地路径，可以直接用它，不必再次 clone：**

```text
/Users/jianing/Documents/Codex/2026-11-09/referenced-chatgpt-conversation-this-is-an/github-handoff/Final Project
```

下面上传示例以这个现有路径为准；新 clone 的用户改成 `$HOME/Documents/Interactive-Lab-Hub/Final Project`。只使用一个网页目录，避免打开旧版本。

### 更新自己的 Pi

先在 Pi 的桥接窗口按 Ctrl+C。然后在 **Mac 普通终端**执行：

```bash
cd "/Users/jianing/Documents/Codex/2026-11-09/referenced-chatgpt-conversation-this-is-an/github-handoff/Final Project"
ssh pi@10.56.130.63 'mkdir -p /home/pi/kitchen_update/bridge'
scp motion_capture.py motion_live.py motion_demo.py sensor_recovery.py safe_mux.py requirements.txt pi@10.56.130.63:/home/pi/kitchen_update/
scp bridge/sensor_bridge.py bridge/utensil_mqtt.py bridge/requirements.txt pi@10.56.130.63:/home/pi/kitchen_update/bridge/
ssh pi@10.56.130.63
```

进入 **自己的 Pi** 后：

```bash
mkdir -p "/home/pi/Interactive-Lab-Hub/Final Project"
cd "/home/pi/Interactive-Lab-Hub/Final Project"
python3 - <<'PY'
from pathlib import Path
from datetime import datetime
import shutil
source = Path('/home/pi/kitchen_update')
backup = Path('backups') / datetime.now().strftime('before_update_%Y%m%d_%H%M%S')
for incoming in source.rglob('*'):
    if not incoming.is_file():
        continue
    target = Path(incoming.relative_to(source))
    if target.exists():
        saved = backup / target
        saved.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target, saved)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(incoming, target)
print('Installed; previous files saved under', backup)
PY
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt -r bridge/requirements.txt
python -m py_compile motion_capture.py motion_live.py motion_demo.py sensor_recovery.py safe_mux.py bridge/sensor_bridge.py
```

已有 `.venv` 可以继续使用。首次装机通过 `sudo raspi-config` → Interface Options → I2C 启用 I²C，按提示重启。不要在运行识别期间同时扫描总线。

### 更新队友 Pi

先停止队友原来的厨具程序；不要让原版和新版同时发布。**Mac 普通终端**：

```bash
cd "/Users/jianing/Documents/Codex/2026-11-09/referenced-chatgpt-conversation-this-is-an/github-handoff/Final Project"
scp pi-utensils/utensil_detection.py pi@10.56.129.47:/home/pi/utensil_detection_updated.py
scp pi-utensils/requirements.txt pi@10.56.129.47:/home/pi/utensil_requirements.txt
ssh pi@10.56.129.47
```

进入 **队友 Pi** 后：

```bash
mkdir -p "/home/pi/Interactive-Lab-Hub/final_project"
cd "/home/pi/Interactive-Lab-Hub/final_project"
if [ -f utensil_detection_updated.py ]; then
  cp utensil_detection_updated.py "utensil_detection_backup_$(date +%Y%m%d_%H%M%S).py"
fi
mv /home/pi/utensil_detection_updated.py .
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r /home/pi/utensil_requirements.txt
```

保留原来的 `utensil_detection.py`，以后启动的是 **utensil_detection_updated.py**。

## 4. 每次重新开机：按顺序启动四个终端

先给两台 Pi 通电，等待启动并确认网络/IP；Mac 与自己的 Pi 必须能 SSH 通信，两台 Pi 都需要能访问课程 MQTT broker。无需自己启动 Mosquitto broker，也不需要在 Pi 上使用 brew。

MQTT 密码用课程提供的密码。下面会提示输入，输入时不显示字符；密码不会保存在仓库里。它不是 Pi 的 SSH 登录密码。

### 终端 1：启动队友的厨具 Pi

Mac 新开终端：

```bash
ssh pi@10.56.129.47
```

登录后复制：

```bash
cd "/home/pi/Interactive-Lab-Hub/final_project"
source .venv/bin/activate
export PYTHONIOENCODING=utf-8
export KITCHEN_MQTT_HOST='farlab.infosci.cornell.edu'
export KITCHEN_MQTT_PREFIX='IDD/jianing-kitchen/utensil'
export KITCHEN_MQTT_USER='idd'
read -r -s -p 'Course MQTT password: ' KITCHEN_MQTT_PASSWORD
echo
export KITCHEN_MQTT_PASSWORD
python -u utensil_detection_updated.py
```

期望看到 MQTT 已连接和各个传感器连接状态。把五种厨具都放回对应位置，让系统收到初始状态。保持该窗口运行。

### 终端 2：启动自己的动作 Pi 和桥接（展示版）

Mac 新开终端：

```bash
ssh pi@10.56.130.63
```

登录后复制：

```bash
cd "/home/pi/Interactive-Lab-Hub/Final Project"
source .venv/bin/activate
export PYTHONIOENCODING=utf-8
export KITCHEN_MQTT_HOST='farlab.infosci.cornell.edu'
export KITCHEN_MQTT_PREFIX='IDD/jianing-kitchen/utensil'
export KITCHEN_MQTT_USER='idd'
read -r -s -p 'Course MQTT password: ' KITCHEN_MQTT_PASSWORD
echo
export KITCHEN_MQTT_PASSWORD
mkdir -p logs
python -u bridge/sensor_bridge.py \
  --motion-dir "/home/pi/Interactive-Lab-Hub/Final Project" \
  --host 0.0.0.0 \
  --mqtt \
  --demo \
  2>"logs/demo_$(date +%Y%m%d_%H%M%S).log"
```

桥接会自动启动动作程序，**不要再单独运行 motion_demo.py 或 motion_live.py**。期望看到“初始化完成”“手部状态”和厨具拿放信息。保持窗口运行。

### 终端 3：在 Mac 启动网页

Mac 新开终端，不要 SSH：

```bash
cd "/Users/jianing/Documents/Codex/2026-11-09/referenced-chatgpt-conversation-this-is-an/github-handoff/Final Project"
npm ci
npm run dev -- --host 127.0.0.1 --port 5173 --strictPort
```

`npm ci` 只在首次使用或依赖更新时执行，以后省略即可。新 clone 用户用自己的 `.../Interactive-Lab-Hub/Final Project` 路径。看到 `http://localhost:5173/` 后保持运行。端口被占用时，停止旧的网页终端，不要再开第二个网页服务器。

### 终端 4：在 Mac 建立 SSH 转发

Mac 新开终端：

```bash
ssh -N \
  -o ExitOnForwardFailure=yes \
  -o ServerAliveInterval=15 \
  -L 127.0.0.1:18765:127.0.0.1:8765 \
  pi@10.56.130.63
```

输入 Pi 登录密码后停在那里是正常的。保持该窗口运行；按 Ctrl+C 会断开网页到 Pi 的通道。

### 浏览器打开

直接复制到浏览器地址栏：

```text
http://localhost:5173/?sensors=http://127.0.0.1:18765
```

如果只输入 `http://localhost:5173/`，在 Help → Bridge address 填 `http://127.0.0.1:18765`，点击 Connect to sensors。不要填 `0.0.0.0`；不要用浏览器访问 `http://127.0.0.1:8765`（那是 Mac 的端口，不是远端 Pi）。

检查链路可在浏览器打开：

```text
http://127.0.0.1:18765/health
```

出现 JSON 说明 tunnel 和 bridge 可达，不代表每个传感器都健康。首次点击网页开始按钮也用于允许浏览器播放音效。

## 5. 操作与展示前检查

1. 向前点头：完成当前动作，显示完成反馈；不会自动进入下一步。
2. 向右点头：进入下一动作；当前步骤和厨具归位条件必须满足。
3. 向左点头：撤销完成或返回上一步。
4. 切葱、调味、搅拌、翻面步骤先提示拿起刀／盐瓶／黑胡椒瓶／筷子／铲子。proximity 仅检测摆放位置有无物体，不能证明拿的是哪只手、刀口方向或食物熟度。
5. 手部动作反馈不自动证明完成，不测实际盐量、面粉量或熟度。倒油在开火前，使用点头或按钮确认，不要求动作识别。
6. 工具拿起／归位、完成／下一步／撤销和 motion preview 均有手动补救按钮。使用手动工具确认后，该动作以手动状态为准，测试真实工具信号时不要先点手动确认。
7. 未连接队友 Pi 时，运行终端2命令去掉 `--mqtt`，用工具手动按钮继续。不要把手动确认记为 proximity 检测成功。
8. 展示前验证三种头动、五种工具拿放、动画响应；持续运行测试后再展示。不要带电拔线制造故障。

## 6. 展示版、实验版与故障恢复

| | 展示版 `--demo` | 实验版（去掉 `--demo`） |
|---|---|---|
| 手部输出 | 明显运动／静止／未知 | 切、搅拌、拧瓶、翻面等候选规则 |
| 一手故障 | 使用另一只有效手；切换时清空旧窗口 | 保留双手有效条件，暂停手部分类 |
| 网页解释 | 当前步骤 + 已确认工具 → 动画反馈 | 按分类结果匹配步骤 |
| 头部 | 原来的方向检测 | 相同 |
| 统计含义 | 不生成假的翻面／拧瓶计数，不作为分类准确率 | 仍需真实标注验证，已有搅拌误触发拧瓶的历史记录 |

展示阈值：有效手陀螺仪幅值 RMS > 0.35 rad/s 或加速度幅值 SD > 0.5 m/s²；至少20个样本且覆盖0.8秒，窗口上限约2秒；两次分类投票确认运动。目标读取25Hz，每0.5秒分类。左手扶碗静止而右手坏掉时，系统可能看不到右手的实际动作。两手都失效时暂停手部判断，不能凭菜谱伪造动作。

每个传感器独立退避重试：0.5、1、2、5秒，后续最多每5秒重试，不再达到三次就永久停用。恢复后连续5次有效读数才重新启用，失败计数重置。单位是尝试之间的等待，不包含实际 I/O 和重新配置耗时。故障标记 `stage=check_config / restore_config / read_sample` 分别代表检查配置、恢复配置、读取动作数据。

恢复和正常采样共用顺序 I²C 总线，不是互不影响的并行线程：总线超时／BNO重新配置仍可能短暂停顿，数据缺口会清除不完整动作。桥接对子程序无输出设有看门狗并有限次重启；不能修复永久硬件断连，也不是无限重启。

要切换实验版：终端2按 Ctrl+C，使用相同启动命令但删掉 `--demo`，日志文件名前缀可改为 classifier。网页和 tunnel 不变；开始一份新的菜谱会话。不要同时运行两版程序。

## 7. 常见问题

- **sensor connecting**：检查终端2和4仍在运行，先访问 health；确认网页 bridge URL 是 `http://127.0.0.1:18765`。网络/IP变化需重建 tunnel。
- **有厨具消息，没动作**：MQTT 和动作采集是两条路径。看终端2的初始化／故障提示，不要认为 MQTT 正常就等于 IMU 正常。
- **仅左手／仅右手有效**：展示版正在降级，仍使用真实有效数据；实验版不会因此放松分类条件。
- **旧版厨具消息**：没有有效性字段不能用于自动验证，队友应运行本仓库更新版。
- **乱码/latin-1**：确保 Pi 终端设置 `export PYTHONIOENCODING=utf-8`。
- **重复读取**：停止桥接后在 Pi 执行 `pgrep -af 'motion_|sensor_bridge|i2cdetect|screen_boot'`。屏幕脚本本次检查使用 SPI，不直接访问 I²C。
- **BNO055反复I/O错误**：保留日志、错误阶段和当前版本。自动恢复不等于根因已消除；Adafruit 提醒 BNO055 与 I²C multiplexer 可能兼容不佳：[官方 FAQ](https://learn.adafruit.com/adafruit-bno055-absolute-orientation-sensor/faqs)。不要把老款 Pi 的问题直接当作 Pi5 的诊断。

查看最新详细日志（Pi）：

```bash
python - <<'PY'
from pathlib import Path
files = list(Path('logs').glob('*.log'))
if files:
    latest = max(files, key=lambda p: p.stat().st_mtime)
    print(latest)
    print('\n'.join(latest.read_text(encoding='utf-8', errors='replace').splitlines()[-80:]))
else:
    print('No log found')
PY
```

## 8. 结束与安全关闭

1. 终端2（自己的 Pi）：按一次 Ctrl+C，等待程序停止。
2. 终端1（队友 Pi）：按一次 Ctrl+C，等待厨具程序停止。
3. 在两个 Pi 的 SSH 终端分别输入 `sudo poweroff`。SSH 断开正常；等待系统完成关机，约30秒，再断电。不要只凭一颗LED颜色判断关机状态。
4. Mac 终端3、4分别按 Ctrl+C，停止网页服务器和转发；关闭网页。
5. 完成关机断电后再调整传感器接线。

下次通电需按第4节重新启动程序和 tunnel、重新输入 MQTT 密码。程序会配置传感器，不需要手动恢复寄存器。IP、佩戴方向和厨具摆放条件仍需确认。运行不会自动上传日志或自动同步 GitHub。

## 9. 本地验证与已知限制

```bash
npm ci
npm run build
python3 -m unittest discover -s tests -p 'test_*.py'
npx tsc src/sensors/sensorAdapter.ts src/state/recipeState.ts --outDir /tmp/kitchen-tests --module commonjs --target ES2020 --esModuleInterop --skipLibCheck --strict
node tests/test_demo.cjs /tmp/kitchen-tests
node tests/test_adapter.cjs /tmp/kitchen-tests
node tests/test_flow.cjs /tmp/kitchen-tests
```

测试覆盖协议／工具状态传输、恢复退避、mux锁清理、单手展示降级、双手失效停止、网页状态流。它们使用模拟输入，不代表实机长时运行、识别准确率或多人泛化已验证。Python requirements 是依赖范围而非 Pi 的精确环境快照。

网页基础来源于 Aurora 的课程仓库；厨具程序基于 Tzu-Yao 的传感器实现；Jianing 的动作系统与整合版本在此仓库归档。原始来源：[网页](https://github.com/aurorajxshen/Interactive-Lab-Hub/tree/Fall2026/Final%20Project)、[厨具](https://github.com/ctyaaaaao/Interactive-Lab-Hub/tree/Fall2026/final_project/sensors)。个人贡献应按实际开发／测试记录在最终报告进一步确认。
