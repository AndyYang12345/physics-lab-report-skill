# 原理图绘制指南

## 硬要求

1. **每个实验至少 1 张原理图**，插入「实验原理」小节内对应位置。
2. **必须自己画**（`figstyle.py` + matplotlib）。不许下载网图。
3. **图与正文公式必须自洽**：图里的角度、方向要由公式真算出来，不能"看着差不多"。
   例：画最小偏向角光路图时，先用折射定律解出入射方向，再画线。
4. 图题注格式 `图1  ×××示意图`（图号 + 两个空格 + 名称），宋体五号居中。
5. 插入宽度默认 12.6cm（正文可用宽度约 14.6cm）；横向光路图可用 13.2cm。
   若图与题注被分页拆开，把 `width_cm` 减 0.5 重试。

## figstyle 速查

```text
from figstyle import Fig, pol, DEG

f = Fig(w=16, h=10, xlim=(-5, 5), ylim=(-4, 4))   # 画布尺寸(cm) + 坐标范围

f.line(p1, p2)                    # 直线
f.dashed(p1, p2)                  # 虚线（法线、延长线）
f.arrow(p1, p2)                   # 带箭头（带箭头的整条线）
f.mid_arrow(p1, p2, frac=0.5)     # 光线中段箭头 ← 光学作图用这个
f.poly([p1, p2, p3], fill='#f5f5f5')   # 多边形（棱镜）
f.circle(c, r)                    # 圆
f.dot(p)                          # 实心点
f.arc(c, r, a0, a1)               # 圆弧
f.angle(c, r, a0, a1, label='A')  # 角弧 + 标签（标签在角平分线上）
f.angle_dim(c, r, a0, a1, 'θ')    # 双箭头角度标注
f.right_angle(corner, d1, d2, u)  # 直角符号（d1/d2 为两边方向，度）
f.text(xy, '文字', fs=11)
f.leader(target, text_xy, '标注')  # 引线 + 目标点圆点
f.save('fig1.png', width_cm=16)
```

坐标一律 **y 轴向上**，角度用**度、逆时针为正**，与数学课本一致。

> **画布长宽比要等于数据范围的长宽比**：`h/w = (ylim 跨度)/(xlim 跨度)`。
> 否则 `aspect='equal'` 会在图里留出大片空白边，插进报告后图会显得很小。
> 例：`xlim=(-7,7)`、`ylim=(-1.9,3.3)` → 跨度 14 × 5.2 → `w=16, h=16*5.2/14=5.94`。

---

## 范例 1：分光计结构示意图（俯视）

这是「结构类」图的模板——同心圆 + 刻度 + 管状部件 + 引线标注。

```python
from figstyle import Fig, pol
import math

f = Fig(w=16, h=13.33, xlim=(-6.6, 6.6), ylim=(-4.4, 6.6))   # h/w = Δy/Δx

O = (0, 0)
R_SCALE, R_VERN, R_STAGE = 3.0, 2.5, 1.72
T_ANG, C_ANG = 50, 180          # 望远镜 / 平行光管方位角
TUBE_IN, TUBE_OUT, HW = 1.96, 4.32, 0.25

# 刻度盘 + 刻度线
f.circle(O, R_SCALE, lw=1.4)
for a in range(0, 360, 2):
    long = (a % 10 == 0)
    f.line(pol(O, R_SCALE - (0.20 if long else 0.11), a),
           pol(O, R_SCALE, a), lw=0.8 if long else 0.45)

# 游标盘 + 两个游标（相隔 180°）
f.circle(O, R_VERN, lw=0.7, color='0.45')
for base in (148, 328):
    for k in range(-5, 6):
        a = base + k * 2
        f.line(pol(O, R_VERN, a), pol(O, R_VERN + 0.13, a), lw=0.7)

# 管状部件（望远镜 / 平行光管）
def tube(ang, r_in, r_out, hw, lw=1.4):
    n = (math.cos(math.radians(ang + 90)), math.sin(math.radians(ang + 90)))
    a1, a2 = pol(O, r_in, ang), pol(O, r_out, ang)
    f.poly([(a1[0] + n[0]*hw, a1[1] + n[1]*hw), (a2[0] + n[0]*hw, a2[1] + n[1]*hw),
            (a2[0] - n[0]*hw, a2[1] - n[1]*hw), (a1[0] - n[0]*hw, a1[1] - n[1]*hw)], lw=lw)
    return n

tube(C_ANG, TUBE_IN, TUBE_OUT, HW - 0.02)
nT = tube(T_ANG, TUBE_IN, TUBE_OUT, HW)

# 狭缝（平行光管外端）+ 光源
sx, sy = pol(O, TUBE_OUT + 0.06, C_ANG)
f.line((sx, sy - 0.19), (sx, sy + 0.19), lw=2.4)
f.line((sx - 0.09, sy - 0.19), (sx - 0.09, sy + 0.19), lw=1.1)
f.line((sx + 0.09, sy - 0.19), (sx + 0.09, sy + 0.19), lw=1.1)
L = pol(O, TUBE_OUT + 0.62, C_ANG)
f.circle(L, 0.15, lw=1.3)
for a in range(0, 360, 45):
    f.line(pol(L, 0.20, a), pol(L, 0.30, a), lw=1.0)

# 望远镜目镜端封口 + 调焦手轮
ex, ey = pol(O, TUBE_OUT, T_ANG)
ux, uy = math.cos(math.radians(T_ANG)), math.sin(math.radians(T_ANG))
f.line((ex + nT[0]*HW, ey + nT[1]*HW), (ex + ux*0.26 + nT[0]*HW, ey + uy*0.26 + nT[1]*HW), lw=1.4)
f.line((ex - nT[0]*HW, ey - nT[1]*HW), (ex + ux*0.26 - nT[0]*HW, ey + uy*0.26 - nT[1]*HW), lw=1.4)
f.line((ex + ux*0.26 + nT[0]*HW, ey + uy*0.26 + nT[1]*HW),
       (ex + ux*0.26 - nT[0]*HW, ey + uy*0.26 - nT[1]*HW), lw=1.4)
knob = pol(O, 2.5, T_ANG)
f.circle((knob[0] + nT[0]*HW, knob[1] + nT[1]*HW), 0.13, lw=1.2)

# 载物台 + 调平螺钉 + 三棱镜
f.circle(O, R_STAGE, lw=1.4)
for a in (90, 210, 330):
    f.circle(pol(O, R_STAGE, a), 0.10, lw=1.1, fill='white')
f.poly([pol(O, 0.96, a) for a in (90, 210, 330)], lw=1.4, fill='#f0f0f0')
f.dot(O, r=0.045)

# 引线标注
f.leader(pol(O, TUBE_OUT - 0.4, T_ANG), (5.4, 5.0), '望远镜', ha='left')
f.leader(pol(O, R_SCALE, -28), (3.0, -3.6), '刻度盘')
f.leader(pol(O, R_VERN, 148), (-5.6, 3.2), '游标')
f.leader(pol(O, R_STAGE, 205), (-4.3, -3.3), '载物台')
f.leader(pol(O, 0.96, 315), (4.6, -2.6), '三棱镜', ha='left')
f.line((-5.2, -1.9), (O[0], O[1] - 0.14), lw=0.8)
f.text((-5.2, -1.6), '中心轴')
f.leader(pol(O, TUBE_OUT + 0.3, C_ANG), (-5.9, -0.6), '光源')
f.leader((sx, sy), (-6.0, 1.2), '狭缝')
f.leader(pol(O, TUBE_IN + 1.2, C_ANG), (-4.4, 2.4), '平行光管')

f.save('fig1.png', width_cm=16)
```

要点：
- 部件位置全部用 `pol(O, r, 角度)` 极坐标算，同心结构不会画歪；
- 引线 `f.leader(目标点, 文字位置, '文字')` 会自动加目标圆点；
- **管件的方位角就是它的轴线方向**，后面画光路图时直接复用这个角度。

---

## 范例 2：最小偏向角光路图（几何自洽）

这是「光路类」图的模板。**关键：射线方向由折射定律解出来，不是估的。**

```python
from figstyle import Fig, pol
import math

A = 60.0          # 棱镜顶角
N_GLASS = 1.6     # 玻璃折射率（用来定入射角）

# —— 先算，再画 ——
r = A / 2.0                                   # 最小偏向角时内部光线平行底边
i = math.degrees(math.asin(N_GLASS * math.sin(math.radians(r))))
dmin = 2 * i - A
print('i=%.2f°  r=%.2f°  δmin=%.2f°' % (i, r, dmin))

f = Fig(w=16, h=5.94, xlim=(-7.0, 7.0), ylim=(-1.9, 3.3))   # h/w = Δy/Δx

apex = (0.0, 3.0)
L = 4.3
Lv = pol(apex, L, 240)          # 左下顶点
Rv = pol(apex, L, 300)          # 右下顶点
f.poly([apex, Lv, Rv], lw=1.5, fill='#fafafa')

# 内部光线（平行底边，水平）
h = 0.42 * L
I = (apex[0] - h / math.sqrt(3), apex[1] - h)   # 入射点
E = (apex[0] + h / math.sqrt(3), apex[1] - h)   # 出射点

d_in  = (math.cos(math.radians(i - 30)),  math.sin(math.radians(i - 30)))
d_out = (math.cos(math.radians(-(i - 30))), math.sin(math.radians(-(i - 30))))
S = (I[0] - d_in[0]*3.7,  I[1] - d_in[1]*3.7)
T = (E[0] + d_out[0]*3.7, E[1] + d_out[1]*3.7)

f.line(S, I, lw=1.6); f.mid_arrow(S, I, 0.60, lw=1.6)
f.line(I, E, lw=1.3); f.mid_arrow(I, E, 0.50, lw=1.3)
f.line(E, T, lw=1.6); f.mid_arrow(E, T, 0.62, lw=1.6)

# 法线（过入射点，垂直左面）
nrm = (math.cos(math.radians(150)), math.sin(math.radians(150)))
f.dashed((I[0] + nrm[0]*1.5, I[1] + nrm[1]*1.5),
         (I[0] - nrm[0]*1.4, I[1] - nrm[1]*1.4))

# 偏向角顶点 P：入射延长线与出射反向延长线的交点
k = 0.3164 * L
P = (apex[0], apex[1] - k)
d_b = (math.cos(math.radians(180 - (i - 30))), math.sin(math.radians(180 - (i - 30))))
f.dashed(I, (P[0] + d_in[0]*0.72, P[1] + d_in[1]*0.72))
f.dashed(E, (P[0] + d_b[0]*0.72,  P[1] + d_b[1]*0.72))
f.dot(P, r=0.04)

# 角度标注
f.angle(I, 0.62, 150, 180 + (i - 30), label='i', lr=1.5, fs=13)
f.angle(I, 0.40, 330, 360, label='r', lr=1.65, fs=13)
f.angle(apex, 0.66, 240, 300, label='A', lr=1.55, fs=13)
f.angle(P, 0.74, -(i - 30), (i - 30), label='δ', lr=1.6, fs=13)

# 文字标注
f.text((-5.3, -1.35), '入射光')
f.text((5.3, -1.35), '出射光')
f.text((-3.05, 2.28), '法线')

f.save('fig3.png', width_cm=16)
```

要点：
- **先算 `i`、`r`、`dmin` 并打印出来**，确认和正文公式一致，再画；
- 内部光线「平行底边」是最小偏向角的判据，画成水平线即可；
- 偏向角顶点 P 是两条延长线的交点，位置也用几何算（`apex[1] - 0.3164*L` 是
  60° 棱镜在最小偏向角下的固定比例）；
- 用 `mid_arrow` 让箭头落在线段中段，避免在 I、E 两个顶点处堆成一团。

---

## 常见图型清单

| 实验类型 | 该画什么 |
| --- | --- |
| 分光计 / 光谱类 | 仪器俯视结构图、光路图、角度几何图 |
| 干涉 / 衍射 | 光路图、光程差几何图、条纹分布示意 |
| 电学类 | 电路原理图（可用 matplotlib 画，或用 `schemdraw`） |
| 力学 / 振动 | 受力图、装置示意图、坐标选取图 |
| 示波器 / 信号 | 波形示意图、测量接线图 |

电学类若想用 `schemdraw` 画电路图，自行安装（`pip install schemdraw`）后即可，
但原则不变：**自己画，不许贴网图**。
