"""
反应釜数据分析与报警系统
"""

import copy
import math
import numpy as np

# ============================================================
# 基础数据
# ============================================================
records = [
    {"time": 0,   "T": 72,   "P": 1.05, "F": 9.8,  "conv": 0.10, "imp": 0.76},
    {"time": 10,  "T": 78,   "P": 1.12, "F": 10.1, "conv": 0.18, "imp": 0.70},
    {"time": 20,  "T": 86,   "P": 1.25, "F": 10.4, "conv": 0.31, "imp": 0.63},
    {"time": 30,  "T": 95,   "P": 1.38, "F": 10.8, "conv": 0.46, "imp": 0.58},
    {"time": 40,  "T": 108,  "P": 1.60, "F": 11.1, "conv": 0.60, "imp": 0.51},
    {"time": 50,  "T": 122,  "P": 1.88, "F": 11.3, "conv": 0.70, "imp": 0.49},
    {"time": 60,  "T": 118,  "P": 2.12, "F": 11.6, "conv": 0.77, "imp": 0.92},
    {"time": 70,  "T": 115,  "P": 1.90, "F": 10.9, "conv": 0.81, "imp": 0.46},
    {"time": 80,  "T": None, "P": 1.72, "F": 10.5, "conv": 0.84, "imp": 0.44},
    {"time": 90,  "T": 126,  "P": 1.55, "F": None, "conv": 0.85, "imp": 0.43},
    {"time": 100, "T": 119,  "P": None, "F": 9.9,  "conv": 0.86, "imp": 0.42},
    {"time": 110, "T": 114,  "P": 1.32, "F": 9.5,  "conv": 0.87, "imp": 0.41}
]

VARIABLES = ["T", "P", "F", "conv", "imp"]

# 安全范围
SAFE_RANGES = {
    "T": (70, 120),
    "P": (1.0, 2.0),
    "F": (8.0, 12.0),
    "imp": (None, 0.80)  # 仅上限
}

# 严重超限界限
SEVERE_LIMITS = {
    "T": (60, 130),
    "P": (0.8, 2.3),
    "F": (7.0, 13.0),
    "imp": (None, 1.0)
}


# ============================================================
# 任务一：数据读取、组织与基本检查
# ============================================================
def task_basic_check(records):
    """输出所有采样时间点，统计有效/缺失值，输出缺失详情"""
    print("=== 采样时间点 ===")
    times = [r["time"] for r in records]
    print(times)

    print("\n=== 各变量有效数据与缺失值统计 ===")
    for var in VARIABLES:
        valid = sum(1 for r in records if r[var] is not None)
        missing = len(records) - valid
        print(f"变量 {var}：有效数据 {valid} 个，缺失值 {missing} 个")

    print("\n=== 缺失值详情 ===")
    for var in VARIABLES:
        missing_times = [r["time"] for r in records if r[var] is None]
        for t in missing_times:
            print(f"变量 {var} 存在 1 个缺失值，缺失时间点为：{t} min")


# ============================================================
# 任务二：缺失值处理函数
# ============================================================
def fill_missing(records, variable):
    """对指定变量填补缺失值，返回新数据不破坏原数据"""
    new_records = copy.deepcopy(records)
    n = len(new_records)

    for i in range(n):
        if new_records[i][variable] is not None:
            continue
        time = new_records[i]["time"]

        # 向前找有效值
        prev_val = None
        for j in range(i - 1, -1, -1):
            if new_records[j][variable] is not None:
                prev_val = new_records[j][variable]
                break

        # 向后找有效值
        next_val = None
        for j in range(i + 1, n):
            if new_records[j][variable] is not None:
                next_val = new_records[j][variable]
                break

        if prev_val is not None and next_val is not None:
            fill_val = round((prev_val + next_val) / 2, 2)
            print(f"{variable} 在 {time} min 处缺失，已用 {prev_val} 和 {next_val} 的平均值 {fill_val} 填补")
        elif prev_val is not None:
            fill_val = prev_val
            print(f"{variable} 在 {time} min 处缺失，已是边界，用前值 {fill_val} 填补")
        elif next_val is not None:
            fill_val = next_val
            print(f"{variable} 在 {time} min 处缺失，已是边界，用后值 {fill_val} 填补")
        else:
            fill_val = 0
            print(f"{variable} 在 {time} min 处缺失，无有效数据，用 0 填补")

        new_records[i][variable] = fill_val

    return new_records


# ============================================================
# 任务三：安全状态判断
# ============================================================
def judge_status(record):
    """根据单条记录判断反应釜运行状态"""
    # 检查缺失
    for var in ["T", "P", "F", "imp"]:
        if record[var] is None:
            return "数据缺失，无法判断"

    abnormal = []

    # 判断各变量是否超限
    if record["T"] < SAFE_RANGES["T"][0] or record["T"] > SAFE_RANGES["T"][1]:
        abnormal.append("温度")
    if record["P"] < SAFE_RANGES["P"][0] or record["P"] > SAFE_RANGES["P"][1]:
        abnormal.append("压力")
    if record["F"] < SAFE_RANGES["F"][0] or record["F"] > SAFE_RANGES["F"][1]:
        abnormal.append("流量")
    if record["imp"] > SAFE_RANGES["imp"][1]:
        abnormal.append("杂质")

    if len(abnormal) == 0:
        return "运行正常"
    elif len(abnormal) == 1:
        return abnormal[0] + "异常"
    else:
        return "多变量异常"


def task_status_all(records):
    """遍历所有记录输出安全状态"""
    print("\n=== 反应釜安全状态 ===")
    for r in records:
        status = judge_status(r)
        print(f"time = {r['time']} min，状态：{status}")


# ============================================================
# 任务四：描述性统计分析
# ============================================================
def calculate_statistics(values):
    """输入数值列表，返回统计指标字典，自动忽略 None"""
    clean = [v for v in values if v is not None]
    n = len(clean)

    if n == 0:
        return {"mean": 0, "median": 0, "min": 0, "max": 0,
                "range": 0, "variance": 0, "std": 0}

    total = sum(clean)
    mean = total / n

    # 排序
    sorted_vals = sorted(clean)
    if n % 2 == 1:
        median = sorted_vals[n // 2]
    else:
        median = (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2

    min_val = sorted_vals[0]
    max_val = sorted_vals[-1]
    range_val = max_val - min_val

    # 方差 (总体方差)
    variance = sum((x - mean) ** 2 for x in clean) / n
    std = math.sqrt(variance)

    return {
        "mean": round(mean, 3),
        "median": round(median, 3),
        "min": round(min_val, 3),
        "max": round(max_val, 3),
        "range": round(range_val, 3),
        "variance": round(variance, 3),
        "std": round(std, 3)
    }


def task_statistics_all(records):
    """计算所有变量统计指标并打印"""
    print("\n=== 描述性统计结果 ===")
    for var in VARIABLES:
        vals = [r[var] for r in records]
        stats = calculate_statistics(vals)
        print(f"\n变量 {var}：")
        print(f"  mean = {stats['mean']}")
        print(f"  median = {stats['median']}")
        print(f"  min = {stats['min']}")
        print(f"  max = {stats['max']}")
        print(f"  range = {stats['range']}")
        print(f"  variance = {stats['variance']}")
        print(f"  std = {stats['std']}")


# ============================================================
# 任务五：IQR 异常值检测
# ============================================================
def detect_outliers_iqr(values):
    """IQR 方法检测异常值"""
    clean = [v for v in values if v is not None]
    sorted_vals = sorted(clean)
    n = len(sorted_vals)

    # Q1、Q3
    def percentile_25(data):
        idx = 0.25 * (len(data) - 1)
        lo = int(idx)
        hi = lo + 1
        frac = idx - lo
        return data[lo] * (1 - frac) + data[hi] * frac

    def percentile_75(data):
        idx = 0.75 * (len(data) - 1)
        lo = int(idx)
        hi = lo + 1
        frac = idx - lo
        return data[lo] * (1 - frac) + data[hi] * frac

    q1 = percentile_25(sorted_vals)
    q3 = percentile_75(sorted_vals)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    outliers = [v for v in clean if v < lower or v > upper]

    return q1, q3, iqr, lower, upper, outliers


def task_outliers_all(records):
    """检测所有变量的 IQR 异常值并输出"""
    print("\n=== IQR 异常值检测 ===")
    for var in ["T", "P", "F", "imp"]:
        vals = [r[var] for r in records]
        q1, q3, iqr, lower, upper, outliers = detect_outliers_iqr(vals)
        print(f"\n变量 {var}：")
        print(f"  Q1 = {q1:.3f}, Q3 = {q3:.3f}, IQR = {iqr:.3f}")
        print(f"  下限 = {lower:.3f}, 上限 = {upper:.3f}")
        if outliers:
            outlier_times = []
            for r in records:
                if r[var] is not None and (r[var] < lower or r[var] > upper):
                    outlier_times.append((r["time"], r[var]))
            for t, v in outlier_times:
                print(f"  异常值：time = {t} min，值 = {v}")
        else:
            print("  无异常值")


# ============================================================
# 任务六：Pearson 相关系数
# ============================================================
def pearson_corr(x, y):
    """计算 Pearson 相关系数，自动跳过含 None 的数据点"""
    pairs = [(a, b) for a, b in zip(x, y) if a is not None and b is not None]
    n = len(pairs)
    if n < 2:
        return None

    sum_x = sum(p[0] for p in pairs)
    sum_y = sum(p[1] for p in pairs)
    sum_xy = sum(p[0] * p[1] for p in pairs)
    sum_x2 = sum(p[0] ** 2 for p in pairs)
    sum_y2 = sum(p[1] ** 2 for p in pairs)

    numerator = n * sum_xy - sum_x * sum_y
    denominator = math.sqrt((n * sum_x2 - sum_x ** 2) * (n * sum_y2 - sum_y ** 2))

    if denominator == 0:
        return None
    return numerator / denominator


def interpret_correlation(r):
    """根据 r 值给出相关性判断"""
    if r is None:
        return "无法计算"
    if r >= 0.8:
        return "强正相关"
    elif r >= 0.4:
        return "中等正相关"
    elif r > -0.4:
        return "弱相关"
    elif r > -0.8:
        return "中等负相关"
    else:
        return "强负相关"


def task_correlation_all(records):
    """计算多组变量间的相关系数"""
    print("\n=== Pearson 相关系数分析 ===")

    pairs = [("T", "conv"), ("T", "P"), ("conv", "imp"), ("F", "conv")]
    for var1, var2 in pairs:
        x = [r[var1] for r in records]
        y = [r[var2] for r in records]
        r = pearson_corr(x, y)
        if r is not None:
            print(f"  {var1} 与 {var2}：r = {r:.4f}，{interpret_correlation(r)}")
        else:
            print(f"  {var1} 与 {var2}：无法计算")


# ============================================================
# 任务七：报警等级系统
# ============================================================
def alarm_level(record):
    """判断单条记录的报警等级"""
    for var in ["T", "P", "F", "imp"]:
        if record[var] is None:
            return -1  # 数据缺失

    level = 0  # 0: 正常, 1: 注意, 2: 警告, 3: 危险

    severe_count = 0

    for var in ["T", "P", "F", "imp"]:
        val = record[var]

        # 检查是否超限（轻微）
        if var == "imp":
            slight = val > SAFE_RANGES["imp"][1]
        else:
            slight = val < SAFE_RANGES[var][0] or val > SAFE_RANGES[var][1]

        # 检查是否严重超限
        if var == "imp":
            severe = val > SEVERE_LIMITS["imp"][1] if SEVERE_LIMITS["imp"][1] else False
        else:
            severe = val < SEVERE_LIMITS[var][0] or val > SEVERE_LIMITS[var][1]

        if severe:
            severe_count += 1
        elif slight:
            if level < 1:
                level = 1

    if severe_count >= 2:
        level = 3
    elif severe_count == 1:
        level = 2

    return level


def task_alarm_all(records):
    """输出每个时间点的报警等级并统计"""
    print("\n=== 报警等级统计 ===")
    level_counts = {0: 0, 1: 0, 2: 0, 3: 0}

    for r in records:
        level = alarm_level(r)
        if level == -1:
            print(f"time = {r['time']} min，数据缺失，无法判断等级")
        else:
            level_names = ["正常", "注意", "警告", "危险"]
            print(f"time = {r['time']} min，等级 {level}（{level_names[level]}）")
            level_counts[level] += 1

    print("\n各等级出现次数：")
    for level in range(4):
        print(f"{level} 级（{['正常','注意','警告','危险'][level]}）：{level_counts[level]} 次")


# ============================================================
# 可视化
# ============================================================
def plot_visualizations(records):
    """绘制四类图形"""
    try:
        import matplotlib.pyplot as plt

        # 提取数据（用填补后的完整数据）
        filled = copy.deepcopy(records)
        for var in ["T", "P", "F", "imp"]:
            filled = fill_missing(filled, var)

        times = [r["time"] for r in filled]
        temps = [r["T"] for r in filled]
        pressures = [r["P"] for r in filled]
        flows = [r["F"] for r in filled]
        imp = [r["imp"] for r in filled]
        conv = [r["conv"] for r in filled]

        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False

        fig, axes = plt.subplots(2, 2, figsize=(12, 8))

        # 1. 温度、压力随时间变化
        ax1 = axes[0, 0]
        ax1.plot(times, temps, 'o-', color='tab:red', label='T (°C)')
        ax1.set_xlabel('时间 (min)')
        ax1.set_ylabel('温度 (°C)', color='tab:red')
        ax1.tick_params(axis='y', labelcolor='tab:red')

        ax1b = ax1.twinx()
        ax1b.plot(times, pressures, 's--', color='tab:blue', label='P (MPa)')
        ax1b.set_ylabel('压力 (MPa)', color='tab:blue')
        ax1b.tick_params(axis='y', labelcolor='tab:blue')
        ax1.set_title('温度与压力随时间变化')
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines1b, labels1b = ax1b.get_legend_handles_labels()
        ax1.legend(lines1 + lines1b, labels1 + labels1b)

        # 2. 转化率与温度散点图
        ax2 = axes[0, 1]
        ax2.scatter(temps, conv, c='tab:green', s=50)
        ax2.set_xlabel('温度 (°C)')
        ax2.set_ylabel('转化率')
        ax2.set_title('转化率与温度关系')
        # 趋势线
        z = np.polyfit(temps, conv, 1)
        p = np.poly1d(z)
        ax2.plot(temps, p(temps), 'r--', alpha=0.6)

        # 3. 杂质含量随时间变化
        ax3 = axes[1, 0]
        ax3.plot(times, imp, 'o-', color='tab:purple')
        ax3.axhline(y=0.80, color='r', linestyle='--', alpha=0.5, label='安全上限')
        ax3.set_xlabel('时间 (min)')
        ax3.set_ylabel('杂质含量')
        ax3.set_title('杂质含量随时间变化')
        ax3.legend()

        # 4. 各变量异常次数柱状图
        ax4 = axes[1, 1]
        var_names = ['T', 'P', 'F', 'imp']
        abnormal_counts = []
        for var in var_names:
            if var == "imp":
                cnt = sum(1 for r in records if r[var] is not None and r[var] > SAFE_RANGES[var][1])
            else:
                cnt = sum(1 for r in records if r[var] is not None and
                          (r[var] < SAFE_RANGES[var][0] or r[var] > SAFE_RANGES[var][1]))
            abnormal_counts.append(cnt)

        ax4.bar(var_names, abnormal_counts, color=['tab:red', 'tab:blue', 'tab:orange', 'tab:purple'])
        ax4.set_xlabel('变量')
        ax4.set_ylabel('异常次数')
        ax4.set_title('各变量异常次数')

        plt.tight_layout()
        plt.savefig('reactor_analysis.png', dpi=150)
        plt.show()
        print("\n可视化图片已保存为 reactor_analysis.png")

    except ImportError:
        print("\n未安装 matplotlib，跳过可视化")
    except Exception as e:
        print(f"\n可视化出错: {e}")


# ============================================================
# 任务八：菜单系统
# ============================================================
def show_menu():
    """显示主菜单"""
    print("\n" + "=" * 40)
    print("     反应釜数据分析系统")
    print("=" * 40)
    print("1.  查看原始数据")
    print("2.  检查缺失值")
    print("3.  填补缺失值")
    print("4.  判断安全状态")
    print("5.  计算描述性统计指标")
    print("6.  检测异常值")
    print("7.  计算相关系数")
    print("8.  查看报警等级统计")
    print("9.  可视化分析（加分项）")
    print("0.  退出系统")
    print("=" * 40)


def main():
    while True:
        show_menu()
        choice = input("请输入功能编号：").strip()

        if choice == "1":
            print("\n=== 原始数据 ===")
            print(f"{'time':>5} {'T':>6} {'P':>6} {'F':>6} {'conv':>6} {'imp':>6}")
            for r in records:
                t = r["T"] if r["T"] is not None else "None"
                p = r["P"] if r["P"] is not None else "None"
                f = r["F"] if r["F"] is not None else "None"
                c = r["conv"] if r["conv"] is not None else "None"
                imp = r["imp"] if r["imp"] is not None else "None"
                print(f"{r['time']:>5} {str(t):>6} {str(p):>6} {str(f):>6} {str(c):>6} {str(imp):>6}")

        elif choice == "2":
            task_basic_check(records)

        elif choice == "3":
            print("\n=== 填补缺失值 ===")
            filled_records = copy.deepcopy(records)
            for var in ["T", "P", "F", "imp"]:
                filled_records = fill_missing(filled_records, var)
            print("\n填补后的数据：")
            print(f"{'time':>5} {'T':>8} {'P':>8} {'F':>8} {'conv':>8} {'imp':>8}")
            for r in filled_records:
                print(f"{r['time']:>5} {r['T']:>8} {r['P']:>8} {r['F']:>8} {r['conv']:>8} {r['imp']:>8}")

        elif choice == "4":
            task_status_all(records)

        elif choice == "5":
            task_statistics_all(records)

        elif choice == "6":
            task_outliers_all(records)

        elif choice == "7":
            task_correlation_all(records)

        elif choice == "8":
            task_alarm_all(records)

        elif choice == "9":
            plot_visualizations(records)

        elif choice == "0":
            print("感谢使用反应釜数据分析系统，再见！")
            break

        else:
            print("输入有误，请重新输入")

        input("\n按 Enter 键继续...")


if __name__ == "__main__":
    main()
