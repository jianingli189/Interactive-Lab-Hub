# Web integration / 网页对接

## 数据流

浏览器不能直接运行 Python 或读 GPIO。由 Pi 后端启动一个 `motion_live.py` 子进程，将 stdout 按行解码 JSON，再通过已有 WebSocket/SSE 转发到浏览器。本交接提供协议与回放工具，不包含已部署的 HTTP/WebSocket 服务。

stderr 只用于诊断，不要与 stdout 合并。网络数据块不等于一行，必须用逐行解析器。Python 使用 flush=True。

Node.js 后端最小读取示例（替换 Python 路径，接入自己的广播函数）：

```js
import { spawn } from 'node:child_process';
import { createInterface } from 'node:readline';
import { randomUUID } from 'node:crypto';

const sessionId = randomUUID();
const child = spawn('/home/pi/Interactive-Lab-Hub/Final Project/.venv/bin/python',
  ['-u', 'motion_live.py', '--step', 'auto'],
  { cwd: '/home/pi/Interactive-Lab-Hub/Final Project',
    stdio: ['ignore', 'pipe', 'pipe'] });
createInterface({ input: child.stdout }).on('line', line => {
  try {
    const event = JSON.parse(line);
    if (event.schema !== 'kitchen-motion.v1') return;
    const envelope = { sessionId, event };
    console.log(envelope); // 在这里转发给自己的 WebSocket/SSE 客户端
  } catch (error) { console.error('Invalid event:', error.message); }
});
child.stderr.on('data', data => process.stderr.write(data));
child.on('error', error => console.error('Process failed:', error));
child.on('exit', (code, signal) => console.error('Sensor offline', code, signal));
process.on('SIGINT', () => child.kill('SIGINT'));
process.on('SIGTERM', () => child.kill('SIGTERM'));
```

这是后端示例，不是浏览器代码。生产后端还须管理退出、重连和事件队列；只允许一个进程控制总线，不要按浏览器连接数启动进程。

## 消息约定

公共字段：schema=kitchen-motion.v1；seq 为当前进程单调序号；t 为启动以来单调时钟秒数；type 为消息类别。每次重启 seq 和计数归零，后端使用 `(sessionId, seq)` 去重；不要仅用 seq 跨重启去重。

| type | 主要字段 | 建议处理 |
|---|---|---|
| ready | channels, target_hz, step, utc | 已初始化，不代表窗口已积累 |
| head_event | action, duration, candidate | confirm/next/undo |
| hand_event | action, count, candidate | flip/twist_stroke/twist_cycle |
| state | hand_state, sensors, counts, features, timing | 状态显示，不要每秒重复完成步骤 |
| sensor_fault | sensor, message | 显示失效；阻止依赖该传感器的动作 |
| sensor_recovered | sensor | 已恢复读取，识别窗口仍需积累 |
| stopped | reason | 程序主动停止 |
| fatal | message | 启动或外层运行失败 |

head_event：confirm = 确认当前步骤完成；next = 请求进入下一步；undo = 请求撤销。网页自己维护可撤销的菜谱状态和动作历史。confirm 不等于 next；不要让一次点头触发两个跳转。只在当前 UI 状态允许时接受事件，先显示识别反馈便于测试。

hand_state 可为 unknown/idle/chop/stir/twist。flip 是完成后发出的事件，不是持续状态。unknown 是拒绝强行分类，不是错误。features=null 为数据不足或窗口无效；features 单位和算法见代码。

hand_event count 是该进程累计值。twist_stroke 附 direction=+1/-1（传感器轴方向，不是固定顺/逆时针）和 duration；twist_cycle 是配对计数。不要把累计 count 当成每次增量相加。网页步骤可记录起始计数来计算本步骤增量，或按唯一事件维护自己的历史；撤销网页步骤不会减少硬件进程计数。

step 当前只在启动时设定。初步接入建议运行 auto，网页按当前菜谱步骤过滤；这不等价于动态改变检测器。若以后实现实时 step 输入，应增加独立控制接口、切换时清空未完成事件、返回确认；本版没有实现该接口。

## 健康与时序

sensors 表示最近读取/配置检查结果，不是实时硬件保证。loop_hz 是循环频率；配合 sensor_read_failures、skipped_slots 和 rh_retries 看，不能解释为每颗传感器有效率。max_cycle_ms 是最近报告区间最大值，其余 timing 计数累计。配置检查约每秒一次；故障后立即重查。

后端检测进程退出并设置心跳超时（例如连续 3 秒没有 state 则显示暂不可用）；重连不要重放过期动作控制网页。当前实现尚未包含应用层确认/重发机制。

## 验证边界

本次真实日志仅验证向前、右、左各一次对应 confirm/next/undo；不是头动准确率测试。手部事件尚未与实际动作计数逐一核对。阈值依赖佩戴方向、用户和工具；不将 candidate 解释为概率。不要根据现有候选事件自动控制加热设备。

## 已知问题更新（2026-11-21）

[混合动作测试记录](tests/2026-11-21-mixed-actions.md)确认：持续搅拌可误触发 twist_stroke/twist_cycle，且 hand_state 会在 stir/twist/unknown 间变化。搅拌步骤不要消费拧瓶计数；所有候选仍需按步骤与用户确认处理。本次按用户要求未改代码。
