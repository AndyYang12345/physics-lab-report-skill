#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
物理实验报告 · 原理图绘制库（matplotlib）

为什么不用网图：版权不明、分辨率不可控、符号系统常和正文对不上。
自己画能保证「图里的角度/方向与正文公式严格自洽」。

用法（见 reference/figures.md 的两个完整范例）：

    from figstyle import Fig, DEG
    f = Fig(w=16, h=10, xlim=(-5, 5), ylim=(-4, 4))
    f.line((-3, 0), (3, 0))
    f.angle((0, 0), 1.2, 0, 60, label='A')
    f.save('fig1.png')

坐标一律「y 轴向上」的数学坐标系，角度用度、逆时针为正。
"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# --------------------------------------------------------------------------
# 中文字体
# --------------------------------------------------------------------------
_CJK_CANDIDATES = ['Noto Sans CJK SC', 'Noto Sans CJK JP', 'Droid Sans Fallback',
                   'WenQuanYi Zen Hei', 'Source Han Sans SC', 'SimHei']


def setup_font():
    """挑一个系统里真实存在的中文字体并设为默认，返回字体名"""
    from matplotlib import font_manager as fm
    have = {f.name for f in fm.fontManager.ttflist}
    for name in _CJK_CANDIDATES:
        if name in have:
            plt.rcParams['font.sans-serif'] = [name] + _CJK_CANDIDATES
            plt.rcParams['axes.unicode_minus'] = False
            return name
    raise RuntimeError('系统里找不到中文字体，检查 fonts-noto-cjk 是否安装')


FONT = setup_font()
plt.rcParams.update({'font.size': 10.5, 'figure.dpi': 300,
                     'savefig.dpi': 300, 'axes.unicode_minus': False})

LW = 1.3          # 默认线宽
DEG = np.pi / 180.0


# --------------------------------------------------------------------------
def pol(c, r, ang_deg):
    """极坐标 → 直角坐标（角度制，逆时针为正）"""
    return (c[0] + r * np.cos(ang_deg * DEG), c[1] + r * np.sin(ang_deg * DEG))


class Fig:
    def __init__(self, w=16, h=10, xlim=None, ylim=None, margin=0.02):
        self.fig, self.ax = plt.subplots(figsize=(w / 2.54, h / 2.54))
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        if xlim:
            self.ax.set_xlim(*xlim)
        if ylim:
            self.ax.set_ylim(*ylim)
        self.fig.subplots_adjust(left=margin, right=1 - margin,
                                 bottom=margin, top=1 - margin)

    # ---------------- 基本图元 ----------------
    def line(self, p1, p2, lw=LW, ls='-', color='k'):
        self.ax.plot([p1[0], p2[0]], [p1[1], p2[1]], lw=lw, ls=ls,
                     color=color, solid_capstyle='round')

    def dashed(self, p1, p2, lw=1.0, color='k', pattern=(6, 4)):
        self.ax.plot([p1[0], p2[0]], [p1[1], p2[1]], lw=lw, color=color,
                     dashes=pattern)

    def arrow(self, p1, p2, lw=LW, color='k', ls='-'):
        self.ax.annotate('', xy=p2, xytext=p1,
                         arrowprops=dict(arrowstyle='-|>', lw=lw, color=color,
                                         shrinkA=0, shrinkB=0,
                                         mutation_scale=13, linestyle=ls))

    def mid_arrow(self, p1, p2, frac=0.5, lw=LW, color='k', size=13):
        """光线中段箭头 —— 光学作图惯例，避免箭头堆在顶点上"""
        p1, p2 = np.array(p1, float), np.array(p2, float)
        m = p1 + (p2 - p1) * frac
        self.ax.annotate('', xy=m + (p2 - p1) * 1e-6, xytext=m - (p2 - p1) * 1e-6,
                         arrowprops=dict(arrowstyle='-|>', lw=lw, color=color,
                                         shrinkA=0, shrinkB=0,
                                         mutation_scale=size))

    def poly(self, pts, lw=LW, fill=None, close=True, color='k', ls='-'):
        pts = list(pts) + ([pts[0]] if close else [])
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        if fill:
            self.ax.fill(xs, ys, color=fill, zorder=0)
        self.ax.plot(xs, ys, lw=lw, color=color, ls=ls, solid_capstyle='round')

    def circle(self, c, r, lw=LW, fill=None, color='k', ls='-'):
        t = np.linspace(0, 2 * np.pi, 200)
        self.ax.plot(c[0] + r * np.cos(t), c[1] + r * np.sin(t),
                     lw=lw, color=color, ls=ls)
        if fill:
            self.ax.fill(c[0] + r * np.cos(t), c[1] + r * np.sin(t), color=fill)

    def dot(self, c, r=0.05, color='k', zorder=5):
        """实心圆点。r 用数据坐标（不是 points），否则不同坐标范围下大小会失控"""
        from matplotlib.patches import Circle
        self.ax.add_patch(Circle(c, r, color=color, lw=0, zorder=zorder))

    # ---------------- 角度 ----------------
    def arc(self, c, r, a0, a1, lw=1.0, color='k', ls='-'):
        t = np.linspace(a0 * DEG, a1 * DEG, 120)
        self.ax.plot(c[0] + r * np.cos(t), c[1] + r * np.sin(t),
                     lw=lw, color=color, ls=ls)

    def angle(self, c, r, a0, a1, label=None, lr=1.55, fs=11, lw=1.0,
              arc=True, color='k'):
        """角标：c 顶点，r 半径，a0→a1（度）。label 放在角平分线上"""
        if arc:
            self.arc(c, r, a0, a1, lw=lw, color=color)
        if label:
            amid = (a0 + a1) / 2.0
            self.text(pol(c, r * lr, amid), label, fs=fs)

    def angle_dim(self, c, r, a0, a1, label=None, fs=11, lw=1.0):
        """带双箭头的角度标注（用于“望远镜转过 θ”这类）"""
        t = np.linspace(a0 * DEG, a1 * DEG, 120)
        xs, ys = c[0] + r * np.cos(t), c[1] + r * np.sin(t)
        self.ax.plot(xs, ys, lw=lw, color='k')
        for a, sgn in ((a1, 1), (a0, -1)):
            tip = pol(c, r, a)
            back = pol(c, r, a + 4 * sgn * -1 if False else a - 4 * sgn)
            self.ax.annotate('', xy=tip, xytext=back,
                             arrowprops=dict(arrowstyle='-|>', lw=lw, color='k',
                                             shrinkA=0, shrinkB=0, mutation_scale=11))
        if label:
            self.text(pol(c, r * 1.18, (a0 + a1) / 2.0), label, fs=fs)

    def right_angle(self, corner, d1, d2, u=1.0, lw=0.9, color='k'):
        """直角符号：corner 为角点，d1/d2 为两边方向（度）"""
        p1 = pol(corner, u, d1)
        p2 = pol(corner, u, d2)
        mid = (p1[0] + p2[0] - corner[0], p1[1] + p2[1] - corner[1])
        self.line(p1, mid, lw=lw, color=color)
        self.line(mid, p2, lw=lw, color=color)

    # ---------------- 文字与引线 ----------------
    def text(self, xy, s, fs=10.5, ha='center', va='center', rot=0,
             color='k', weight='normal'):
        self.ax.text(xy[0], xy[1], s, fontsize=fs, ha=ha, va=va,
                     rotation=rot, color=color, weight=weight)

    def leader(self, target, text_xy, s, fs=10.5, dot=True, lw=0.8,
               ha='center', va='center'):
        """引线标注：从文字指向目标点"""
        self.line(text_xy, target, lw=lw)
        if dot:
            self.dot(target, r=0.035)
        self.text(text_xy, s, fs=fs, ha=ha, va=va)

    # ---------------- 输出 ----------------
    def save(self, path, width_cm=None):
        """width_cm 给定时会等比缩放到该宽度（300 dpi）"""
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        if width_cm:
            w_in = width_cm / 2.54
            h_in = w_in * (self.fig.get_size_inches()[1] /
                           self.fig.get_size_inches()[0])
            self.fig.set_size_inches(w_in, h_in)
        self.fig.savefig(path, dpi=300, facecolor='white')
        plt.close(self.fig)
        from PIL import Image
        print('  ->', path, Image.open(path).size)
        return path
