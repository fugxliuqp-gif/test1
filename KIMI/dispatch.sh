#!/bin/bash
# ============================================================
# Kimi + Aider 混合调度器
#
# 原则:
#   复杂逻辑/跨文件关联 → Kimi（交互式，人工启动）
#   批量机械性修改      → Aider（自动化，Hermes 调度）
#
# 用法:
#   bash KIMI/dispatch.sh kimi "任务描述"   — 生成 Kimi 任务文件
#   bash KIMI/dispatch.sh aider "任务描述"  — 直接调度 Aider
#   bash KIMI/dispatch.sh status           — 查看当前状态
# ============================================================

ACTION="${1:-help}"
TASK="${2:-}"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')

case "$ACTION" in
    kimi)
        # 生成 Kimi 任务文件 → 你手动启动 Kimi 执行
        FILE="KIMI/tasks/kimi_task_${TIMESTAMP}.md"
        mkdir -p KIMI/tasks
        cat > "$FILE" << TASKEOF
# Kimi 任务 — $(date '+%Y-%m-%d %H:%M')

$(cat KIMI/aider_context.md 2>/dev/null || echo "")

## 执行要求
1. 读取项目相关文件了解上下文
2. 按照 TDD 方式实现
3. 完成后 python3 -m pytest -q 验证
4. git add && git commit
5. 在 KIMI/status/current.json 更新状态为 done

## 任务描述
${TASK}

## 注意
- 遵循 AGENTS.md 安全红线 SEC-001~005
- 不要修改 ARCHITECTURE.md 和 AGENTS.md
- 复杂逻辑请先确认再实现
TASKEOF

        echo "════════════════════════════════════════"
        echo "  📋 Kimi 任务已创建"
        echo "  文件: $FILE"
        echo ""
        echo "  启动 Kimi:"
        echo "    cd $(pwd) && kimi"
        echo ""
        echo "  在 Kimi 终端输入:"
        echo "    请读取 KIMI/tasks/kimi_task_${TIMESTAMP}.md 并执行其中的任务"
        echo "════════════════════════════════════════"
        ;;

    aider)
        # 直接调度 Aider
        if [ -z "$TASK" ]; then
            echo "❌ 请提供任务描述"
            exit 1
        fi
        echo "🤖 调度 Aider 执行: ${TASK:0:80}..."
        AIDER_CONTEXT_FILE="KIMI/aider_context.md" bash /home/fu/.hermes/bin/aidexec.sh "$TASK"
        ;;

    aider-auto)
        # Aider 带自检模式
        if [ -z "$TASK" ]; then
            echo "❌ 请提供任务描述"
            exit 1
        fi
        echo "🤖 调度 Aider (自检模式): ${TASK:0:80}..."
        AIDER_CONTEXT_FILE="KIMI/aider_context.md" AIDER_SELF_CHECK=1 AIDER_MAX_RETRY=2 \
            bash /home/fu/.hermes/bin/aidexec.sh "$TASK"
        ;;

    status)
        echo "════════════════════════════════════════"
        echo "  混合调度状态"
        echo "════════════════════════════════════════"
        echo ""
        echo "📋 待处理的 Kimi 任务:"
        ls KIMI/tasks/ 2>/dev/null | head -5 || echo "   (无)"
        echo ""
        echo "🕐 上次 Aider 执行:"
        git log --oneline -3 2>/dev/null || echo "   (无)"
        echo ""
        echo "🔧 工具可用性:"
        which aider 2>/dev/null && echo "  Aider: $(aider --version 2>/dev/null)" || echo "  Aider: ❌ 未安装"
        which kimi 2>/dev/null && echo "  Kimi: 可用" || echo "  Kimi: ❌ 未安装"
        ;;

    help|*)
        echo "用法:"
        echo "  bash KIMI/dispatch.sh kimi \"任务描述\"   — 创建 Kimi 交互式任务"
        echo "  bash KIMI/dispatch.sh aider \"任务描述\"  — 调度 Aider 自动化"
        echo "  bash KIMI/dispatch.sh aider-auto \"描述\" — Aider 带自检"
        echo "  bash KIMI/dispatch.sh status            — 查看状态"
        ;;
esac
