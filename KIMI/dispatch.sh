#!/bin/bash
# ============================================================
# Kimi + Aider 混合调度器 v2
#
# 改进点:
#   1. Kimi 任务完成后通过状态文件通知 Hermes
#   2. Aider 调度自动记录日志
#   3. status 命令显示完整状态
# ============================================================

ACTION="${1:-help}"
TASK="${2:-}"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
PROJECT_ROOT=$(pwd)
KIMI_DIR="$PROJECT_ROOT/KIMI"
TASKS_DIR="$KIMI_DIR/tasks"
STATUS_DIR="$KIMI_DIR/status"
LOGS_DIR="$KIMI_DIR/logs"

mkdir -p "$TASKS_DIR" "$STATUS_DIR" "$LOGS_DIR"

# ── Kimi 完成后的回调检测 ──
check_kimi_done() {
    local task_file="$1"
    local task_basename
    task_basename=$(basename "$task_file" .md)
    local status_file="$STATUS_DIR/${task_basename}.json"

    if [ -f "$status_file" ]; then
        STATUS=$(python3 -c "import json; print(json.load(open('$status_file')).get('status',''))" 2>/dev/null)
        if [ "$STATUS" = "done" ]; then
            local commit_hash
            commit_hash=$(python3 -c "import json; print(json.load(open('$status_file')).get('commit_hash',''))" 2>/dev/null)
            echo "✅ Kimi 任务完成! Commit: $commit_hash"
            return 0
        elif [ "$STATUS" = "blocked" ]; then
            echo "⚠️  Kimi 任务阻塞，需要检查"
            return 2
        else
            echo "⏳ Kimi 任务状态: $STATUS"
            return 1
        fi
    fi
    echo "⏳ 等待 Kimi 开始执行..."
    return 1
}

case "$ACTION" in
    kimi)
        # 创建 Kimi 任务文件
        TASK_FILE="$TASKS_DIR/kimi_task_${TIMESTAMP}.md"
        STATUS_FILE="$STATUS_DIR/kimi_task_${TIMESTAMP}.json"

        # 初始化状态文件
        cat > "$STATUS_FILE" << JSONEOF
{
  "task_id": "kimi_task_${TIMESTAMP}",
  "status": "pending",
  "created_at": "$(date '+%Y-%m-%d %H:%M:%S')",
  "commit_hash": null,
  "note": null
}
JSONEOF

        # 创建任务文件
        cat > "$TASK_FILE" << TASKEOF
# Kimi 任务 — $(date '+%Y-%m-%d %H:%M')

$(cat KIMI/aider_context.md 2>/dev/null || echo "")

## 执行要求
1. 读取相关文件了解上下文
2. 实现任务描述中的功能
3. 完成后: python3 -m pytest -q (如果有测试)
4. 提交: git add -A && git commit -m "feat: 任务摘要"
5. **更新状态**: 将以下 JSON 写入 KIMI/status/$(basename "$STATUS_FILE")

\`\`\`json
{
  "status": "done",
  "commit_hash": "\$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')",
  "note": "实现完成，测试通过"
}
\`\`\`

如果遇到问题无法继续:
\`\`\`json
{
  "status": "blocked",
  "note": "描述遇到的问题"
}
\`\`\`

## 任务描述
${TASK}

## 注意
- 遵循 AGENTS.md 安全红线
- 不要修改 AGENTS.md 和 docs/arch/ 下的文件
TASKEOF

        echo "════════════════════════════════════════"
        echo "  📋 Kimi 任务已创建"
        echo "  文件: $TASK_FILE"
        echo ""
        echo "  启动 Kimi:"
        echo "    cd $PROJECT_ROOT && kimi"
        echo ""
        echo "  在 Kimi 终端输入:"
        echo "   请读取 $TASK_FILE 并执行其中的任务"
        echo ""
        echo "  Kimi 完成后会自动更新状态文件"
        echo "  我可以通过 dispatch.sh kimi-check 检测完成状态"
        echo "════════════════════════════════════════"
        ;;

    kimi-check)
        # 检查最近一个 Kimi 任务是否完成
        LATEST_TASK=$(ls -t "$TASKS_DIR"/kimi_task_*.md 2>/dev/null | head -1)
        if [ -z "$LATEST_TASK" ]; then
            echo "❌ 没有找到 Kimi 任务"
            exit 1
        fi
        check_kimi_done "$LATEST_TASK"
        ;;

    kimi-wait)
        # 等待 Kimi 完成任务（轮询，最多 N 秒）
        TIMEOUT="${2:-300}"
        INTERVAL=10
        ELAPSED=0
        LATEST_TASK=$(ls -t "$TASKS_DIR"/kimi_task_*.md 2>/dev/null | head -1)
        if [ -z "$LATEST_TASK" ]; then
            echo "❌ 没有找到 Kimi 任务"
            exit 1
        fi
        echo "⏳ 等待 Kimi 完成任务，最长 ${TIMEOUT}s..."
        while [ $ELAPSED -lt $TIMEOUT ]; do
            check_kimi_done "$LATEST_TASK" && exit 0
            sleep $INTERVAL
            ELAPSED=$((ELAPSED + INTERVAL))
        done
        echo "⏰ 等待超时"
        exit 1
        ;;

    aider|aider-auto)
        # 调度 Aider
        if [ -z "$TASK" ]; then
            echo "❌ 请提供任务描述"
            exit 1
        fi

        SELF_CHECK=0
        MAX_RETRY=1
        [ "$ACTION" = "aider-auto" ] && SELF_CHECK=1 && MAX_RETRY=2

        echo "🤖 调度 Aider: ${TASK:0:80}..."
        AIDER_CONTEXT_FILE="KIMI/aider_context.md" \
        AIDER_SELF_CHECK=$SELF_CHECK \
        AIDER_MAX_RETRY=$MAX_RETRY \
            bash /home/fu/.hermes/bin/aidexec.sh "$TASK"
        ;;

    log)
        # 查看调度日志
        echo "════════════════════════════════════════"
        echo "  Aider 执行历史"
        echo "════════════════════════════════════════"
        cat "$LOGS_DIR/aider_exec.log" 2>/dev/null || echo "(暂无记录)"
        echo ""
        echo "📋 待处理的 Kimi 任务:"
        ls "$TASKS_DIR"/kimi_task_*.md 2>/dev/null | while read -r f; do
            name=$(basename "$f")
            status_file="$STATUS_DIR/${name%.md}.json"
            if [ -f "$status_file" ]; then
                python3 -c "
import json
s = json.load(open('$status_file'))
print(f'  {s.get(\"task_id\",\"?\")}: {s.get(\"status\",\"?\")}')
" 2>/dev/null || echo "  $name: 状态未知"
            else
                echo "  $name: 待启动"
            fi
        done
        ;;

    status)
        echo "════════════════════════════════════════"
        echo "  调度状态"
        echo "════════════════════════════════════════"
        echo ""
        echo "🔧 工具:"
        which aider 2>/dev/null && echo "  Aider: $(aider --version 2>/dev/null)" || echo "  Aider: ❌"
        which kimi 2>/dev/null && echo "  Kimi: 可用" || echo "  Kimi: ❌"
        echo ""
        echo "🕐 最近代码变更:"
        git log --oneline -3 2>/dev/null || echo "  (无)"
        echo ""
        echo "📋 待处理任务:"
        ls "$TASKS_DIR"/kimi_task_*.md 2>/dev/null | head -3 || echo "  (无)"
        echo ""
        echo "📊 调度统计:"
        if [ -f "$LOGS_DIR/aider_exec.log" ]; then
            TOTAL=$(wc -l < "$LOGS_DIR/aider_exec.log")
            DONE=$(grep -c "DONE" "$LOGS_DIR/aider_exec.log" 2>/dev/null || echo 0)
            FAIL=$(grep -c "FAIL" "$LOGS_DIR/aider_exec.log" 2>/dev/null || echo 0)
            echo "  Aider 调度: 总计 $TOTAL, 成功 $DONE, 失败 $FAIL"
        else
            echo "  Aider 调度: 暂无记录"
        fi
        ;;

    reset)
        # 清除所有 Kimi 任务和状态
        echo "⚠️  清除所有 Kimi 任务和状态?"
        echo "   Tasks: $(ls "$TASKS_DIR" 2>/dev/null | wc -l) 个"
        echo "   Status: $(ls "$STATUS_DIR" 2>/dev/null | wc -l) 个"
        echo "  确认请运行: rm -rf $TASKS_DIR/* $STATUS_DIR/*"
        ;;

    help|*)
        echo "用法: bash KIMI/dispatch.sh <命令> [参数]"
        echo ""
        echo "  kimi \"任务描述\"           — 创建 Kimi 任务（你手动启动 Kimi）"
        echo "  kimi-check                — 检查最近的 Kimi 任务是否完成"
        echo "  kimi-wait [超时秒数]      — 等待 Kimi 任务完成"
        echo "  aider \"任务描述\"          — 调度 Aider"
        echo "  aider-auto \"任务描述\"     — Aider 带自检"
        echo "  log                       — 查看调度日志"
        echo "  status                    — 查看完整状态"
        echo "  reset                     — 清除所有任务"
        ;;
esac
