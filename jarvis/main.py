#!/usr/bin/env python3
"""
贾维斯多智能体框架 v2 - 启动入口

CLI 模式：python main.py
HTTP 模式：python main.py --http
"""

import sys


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--http":
        import uvicorn
        uvicorn.run("jarvis.entry.http:app", host="0.0.0.0", port=8000, reload=False)
    else:
        from jarvis.entry.cli import main as cli_main
        config = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None
        cli_main(config)


if __name__ == "__main__":
    main()
