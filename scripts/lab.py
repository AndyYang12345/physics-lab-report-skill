#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
物理实验报告 · 命令行入口

  python lab.py doctor                      检查环境（依赖/模板/个人信息/LibreOffice）
  python lab.py profile                     查看个人信息与缺失字段
  python lab.py build   <spec.json>         预习模式：生成报告 docx
  python lab.py data    <data.json>         数据模式：填实验日期 + 原始数据表
  python lab.py export  <实验名称>           导出 PDF 到 提交/（同名覆盖）
  python lab.py check   <实验名称> --figs N  交付前自检

依赖：python-docx、Pillow、matplotlib、lxml；导出 PDF 另需 LibreOffice。
先跑 `python lab.py doctor` 确认环境。
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import labkit as K


def _spec_path(p):
    p = Path(p).resolve()
    if not p.exists():
        sys.exit('找不到文件：%s' % p)
    return p


def _load(p):
    """读 JSON（容错：允许 # 注释）"""
    raw = Path(p).read_text(encoding='utf-8')
    raw = '\n'.join(l.split('#')[0] if l.strip().startswith('#') else l
                    for l in raw.splitlines())
    return json.loads(raw)


def _img_dir(spec_file):
    return spec_file.parent


def _resolve_figs(spec, base):
    for s in spec.get('sections', []):
        if 'f' in s and not Path(s['f']).is_absolute():
            s['f'] = str((base / s['f']).resolve())
    return spec


def cmd_doctor(args):
    fatal, warn, info = K.check_environment()
    print('环境自检\n' + '=' * 52)
    for line in info:
        print('  ' + line)
    print()
    for w in warn:
        print('  ⚠ ' + w)
    for f in fatal:
        print('  ✗ ' + f)
    if fatal:
        print('\n环境不完整，先解决上面标 ✗ 的问题。')
        return 1
    print('✓ 环境就绪' + ('（有提醒项，不影响运行）' if warn else ''))
    return 0


def cmd_profile(args):
    prof = K.read_profile()
    if not prof:
        sys.exit('未找到 %s，请先创建个人信息文件' % K.PROFILE)
    print('个人信息文件：%s\n' % K.PROFILE)
    for k, v in prof.items():
        print('  %-8s %s' % (k + ':', v))
    miss = K.missing_fields(prof)
    print()
    if miss:
        print('⚠ 需要向用户确认/补充的字段：%s' % '、'.join(miss))
        return 1
    print('✓ 字段齐全')
    return 0


def cmd_build(args):
    sf = _spec_path(args.spec)
    spec = _resolve_figs(_load(sf), _img_dir(sf))
    prof = K.read_profile()
    miss = K.missing_fields(prof)
    if miss:
        sys.exit('⚠ .profile 缺少字段，先问用户补齐：%s' % '、'.join(miss))

    name = K.safe_name(spec['experiment'])
    outdir = K.BUILD / name
    outdir.mkdir(parents=True, exist_ok=True)
    docx_path = outdir / 'report.docx'

    K.build_report(spec, docx_path, profile=prof)
    nfig = sum(1 for s in spec['sections'] if 'f' in s)
    print('✓ 已生成 %s' % docx_path)
    print('  实验名称：%s' % spec['experiment'])
    print('  插图：%d 张' % nfig)
    if nfig == 0:
        print('  ⚠ 没有插图！原理图是硬要求，请先画图再 build')
    print('\n下一步：  python lab.py export "%s"' % spec['experiment'])
    return 0


def cmd_data(args):
    df = _spec_path(args.data)
    spec = _load(df)
    exp = spec.get('experiment')
    if not exp:
        sys.exit('data.json 里必须写 "experiment"')
    docx_path = K.BUILD / K.safe_name(exp) / 'report.docx'
    if not docx_path.exists():
        sys.exit('找不到 %s —— 请先跑 build' % docx_path)

    K.fill_data(spec, docx_path, profile=K.read_profile())
    print('✓ 已填入原始数据 → %s' % docx_path)
    if spec.get('date'):
        print('  实验日期：%s' % spec['date'])
    print('  数据表：%d 列 × %d 行' % (len(spec['header']), len(spec['rows'])))
    print('\n下一步：  python lab.py export "%s"' % exp)
    return 0


def cmd_export(args):
    prof = K.read_profile()
    exp = K.safe_name(args.experiment)
    docx_path = K.BUILD / exp / 'report.docx'
    if not docx_path.exists():
        sys.exit('找不到 %s —— 请先跑 build' % docx_path)
    pdf = K.SUBMIT / K.submission_name(prof, exp)
    K.export_pdf(docx_path, pdf)
    print('✓ 已导出 %s' % pdf)
    print('  页数：%d' % K.pdf_pages(pdf))
    return 0


def cmd_check(args):
    prof = K.read_profile()
    exp = K.safe_name(args.experiment)
    docx_path = K.BUILD / exp / 'report.docx'
    pdf = K.SUBMIT / K.submission_name(prof, exp)
    if not docx_path.exists():
        sys.exit('找不到 %s' % docx_path)

    problems, info = K.verify(docx_path, expect_figs=args.figs,
                              prof=prof, experiment=exp)
    print('实验：%s' % exp)
    print('插图数：%s' % info.get('插图数'))
    print('提交文件：%s' % pdf.name)
    if pdf.exists():
        print('PDF 页数：%d' % K.pdf_pages(pdf))
    else:
        print('⚠ PDF 还没导出')
    print()
    if problems:
        print('⚠ 发现问题：')
        for p in problems:
            print('   - %s' % p)
        return 1
    print('✓ 自检通过')
    print('※ 仍需人工目视核对 PDF 分页（LibreOffice 不认表格内的“与下段同页”）')
    return 0


def main():
    ap = argparse.ArgumentParser(description='物理实验报告工具')
    sub = ap.add_subparsers(dest='cmd', required=True)

    sub.add_parser('doctor').set_defaults(fn=cmd_doctor)
    sub.add_parser('profile').set_defaults(fn=cmd_profile)

    b = sub.add_parser('build'); b.add_argument('spec'); b.set_defaults(fn=cmd_build)
    d = sub.add_parser('data');  d.add_argument('data'); d.set_defaults(fn=cmd_data)

    e = sub.add_parser('export'); e.add_argument('experiment'); e.set_defaults(fn=cmd_export)
    c = sub.add_parser('check');  c.add_argument('experiment')
    c.add_argument('--figs', type=int, default=0); c.set_defaults(fn=cmd_check)

    args = ap.parse_args()
    sys.exit(args.fn(args))


if __name__ == '__main__':
    main()
