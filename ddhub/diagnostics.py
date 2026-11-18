"""`ddhub doctor`: what is installed, what each platform needs, what has actually been tested."""

from __future__ import annotations

import platform as pyplatform
import shutil
import sys

from . import __version__, paths
from .backends import Context, find_core, version_of
from .library import Library
from .readiness import evaluate


def system_summary() -> list[str]:
    lines = [f"DD Hub {__version__} | Python {sys.version.split()[0]} | {pyplatform.platform()}",
             f"Hub data: {paths.hub_home()}"]
    try:
        import psutil
        lines.append(f"CPU threads: {psutil.cpu_count()} | RAM: {psutil.virtual_memory().total / 2**30:.1f} GiB | "
                     f"Free disk (hub dir): {shutil.disk_usage(paths.hub_home()).free / 2**30:.1f} GiB")
    except Exception:
        pass
    try:
        import os
        os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
        import pygame
        pygame.joystick.init()
        from pygame._sdl2 import controller
        controller.init()
        n = controller.get_count()
        names = [controller.Controller(i).name for i in range(n) if controller.is_controller(i)]
        lines.append(f"Controllers: {n} ({', '.join(names) or 'none detected'})")
        pygame.quit()
    except Exception as e:
        lines.append(f"Controllers: could not query ({e.__class__.__name__})")
    return lines


def report(ctx: Context, lib: Library) -> str:
    out = system_summary()
    out.append("\nPrograms:")
    for pid, spec in sorted(ctx.catalog.programs.items()):
        rp = ctx.program(pid)
        if rp:
            out.append(f"  [found]   {spec['name']:<38} {version_of(ctx, pid):<40} via {rp.via}: {rp.location}")
        elif spec.get("find", {}).get(paths.os_key()):
            out.append(f"  [missing] {spec['name']}")
        else:
            out.append(f"  [n/a]     {spec['name']} (no build for this OS)")
    rp = ctx.program("retroarch")
    if rp:
        cores = sorted({b["core"] for b in ctx.catalog.backends.values() if b.get("core")})
        have = [c for c in cores if find_core(rp, c)]
        out.append(f"\nRetroArch cores installed: {', '.join(have) or 'none'}")
        out.append(f"RetroArch cores missing:   {', '.join(c for c in cores if c not in have)}")
    out.append("\nLibrary:")
    counts: dict[str, int] = {}
    for g in lib.sorted():
        r = evaluate(g, ctx)
        counts[r.status] = counts.get(r.status, 0) + 1
        t = g.local_test
        tested = f"tested {t.get('result')} on {t.get('date', '?')} with {t.get('backend_version', '?')}" if t else "not tested here"
        out.append(f"  {r.status:<15} {g.title[:36]:<36} {ctx.catalog.platform_name(g.platform):<22} {r.backend:<24} {tested}")
        for p in r.problems:
            out.append(f"      ! {p.message}\n        -> {p.action}")
    out.append("\nSummary: " + ", ".join(f"{k}: {v}" for k, v in sorted(counts.items())) if counts else "\nLibrary is empty.")
    return "\n".join(out)
