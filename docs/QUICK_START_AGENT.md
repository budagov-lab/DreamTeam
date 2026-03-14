# Старт через Cursor Agent

## Вариант A: Команда /start (рекомендуется)

1. В чате Composer введи **`/start`** и опиши цель:
   ```
   /start Создай REST API для todo-приложения с авторизацией
   ```

2. Planner создаст:
   - Epic в `.dreamteam/docs/epics/epic_001-<slug>.md` — самая большая задача
   - 50–500 задач в `.dreamteam/tasks/task_XXX.md`

3. Дальше:
   ```powershell
   dreamteam run-next
   ```
   Получишь первую задачу и инструкции.

---

## Вариант B: Ручное создание задачи

### 1. Создай задачу

Файл `.dreamteam/tasks/task_001.md`:

```markdown
id: T001
title: Add hello world endpoint
status: todo
priority: 1
dependencies: []
```

### 2. Синхронизируй и получи задачу

```powershell
dreamteam sync-tasks
dreamteam run-next
```

### 3. Передай агенту

В Composer: `Выполни задачу T001` или используй @developer.

### 4. После выполнения

```powershell
dreamteam update-task T001 done
dreamteam task-counter
dreamteam run-next
```

---

**Формат задачи:** `id`, `title`, `status`, `priority`, `dependencies`  
**Статусы:** `todo`, `in_progress`, `done`, `blocked`
