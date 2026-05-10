# 反应釜数据分析与报警系统

对间歇反应釜（Batch Reactor）的运行数据进行自动处理、安全监控与统计分析。

## 功能

- **缺失值检查与填补** — 识别缺失数据并用相邻有效值的均值或边界值填补
- **安全状态判断** — 根据温度、压力、流量、杂质含量的安全范围判定运行状态
- **描述性统计** — 手动计算均值、中位数、极差、方差、标准差等指标（不依赖统计库）
- **异常值检测** — 使用 IQR（四分位距）方法检测统计异常值
- **相关性分析** — 计算变量间的 Pearson 相关系数并给出定性判断
- **报警等级系统** — 4 级报警（正常/注意/警告/危险），区分轻微超限与严重超限
- **可视化** — 生成温度-压力趋势图、转化率散点图、杂质变化图、异常次数柱状图（加分项）

## 技术栈

- **Python 3.14**
- **matplotlib** — 数据可视化
- **NumPy** — 趋势线拟合（仅可视化模块使用）

核心统计计算（均值、中位数、方差、标准差、Pearson 相关系数、IQR）全部手动实现，不依赖 `numpy` / `pandas` / `scipy` 等现成统计库。

## 快速开始

```bash
# 克隆仓库
git clone https://github.com/hunyzhao-cmyk/reactor_analysis.git
cd reactor-analysis

# 安装依赖
pip install matplotlib numpy

# 运行程序
python reactor_analysis.py
```

程序启动后显示交互菜单：

```
==========  反应釜数据分析系统  ==========
1.  查看原始数据
2.  检查缺失值
3.  填补缺失值
4.  判断安全状态
5.  计算描述性统计指标
6.  检测异常值
7.  计算相关系数
8.  查看报警等级统计
9.  可视化分析
0.  退出系统
请输入功能编号：
```

输入对应数字回车即可执行相应功能。

## 项目结构

```
reactor_analysis.py   — 主程序（所有函数 + 菜单）
reactor_analysis.png  — 可视化输出图片
```

## 函数清单

| 函数 | 作用 |
|------|------|
| `task_basic_check(records)` | 输出采样时间点，统计有效/缺失值 |
| `fill_missing(records, var)` | 对指定变量填补缺失值，不破坏原始数据 |
| `judge_status(record)` | 判断单条记录的安全状态 |
| `calculate_statistics(values)` | 手动计算描述性统计指标 |
| `detect_outliers_iqr(values)` | IQR 方法检测异常值 |
| `pearson_corr(x, y)` | 手动计算 Pearson 相关系数 |
| `alarm_level(record)` | 判断单条记录的报警等级 |
| `plot_visualizations(records)` | matplotlib 可视化 |
| `main()` | 循环菜单主入口 |
