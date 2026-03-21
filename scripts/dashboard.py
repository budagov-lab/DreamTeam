#!/usr/bin/env python3
"""Minimalistic Web Dashboard for DreamTeam Analytics.
No external dependencies required (uses http.server and sqlite3)."""

import os
import sys
import sqlite3
import json
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# Add scripts directory to path to absolute import project
_here = os.path.dirname(os.path.abspath(__file__))
if _here not in sys.path:
    sys.path.insert(0, _here)

import project # type: ignore

TASKS_DB = project.get_db_path()
EXP_DB = project.get_dev_experience_db_path()

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DreamTeam Analytics</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --bg: #f8f9fa;
            --surface: #ffffff;
            --text: #202124;
            --text-muted: #5f6368;
            --border: #dadce0;
            --primary: #1a73e8;
            --danger: #d93025;
            --success: #1e8e3e;
        }
        body {
            font-family: 'Inter', -apple-system, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--border);
        }
        .tabs {
            display: flex;
            gap: 16px;
            margin-bottom: 24px;
        }
        .tab {
            padding: 8px 16px;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.2s;
        }
        .tab.active {
            background: var(--primary);
            color: white;
            border-color: var(--primary);
        }
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 32px;
        }
        .kpi-card {
            background: var(--surface);
            padding: 20px;
            border-radius: 12px;
            border: 1px solid var(--border);
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }
        .kpi-value {
            font-size: 28px;
            font-weight: 600;
            margin-bottom: 4px;
        }
        .kpi-label {
            font-size: 13px;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .chart-container {
            background: var(--surface);
            padding: 20px;
            border-radius: 12px;
            border: 1px solid var(--border);
            margin-bottom: 24px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }
        .batch-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }
        .batch-card {
            background: var(--surface);
            padding: 16px;
            border-radius: 12px;
            border: 1px solid var(--border);
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }
        .batch-card h3 {
            margin: 0 0 12px 0;
            font-size: 16px;
        }
        .batch-item {
            display: flex;
            justify-content: space-between;
            gap: 12px;
            padding: 6px 0;
            border-bottom: 1px dashed var(--border);
            font-size: 13px;
        }
        .batch-item:last-child { border-bottom: none; }
        .batch-key { color: var(--text-muted); }
        .batch-val { font-weight: 500; }
        table {
            width: 100%;
            border-collapse: collapse;
            background: var(--surface);
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }
        th, td {
            padding: 12px 16px;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }
        th {
            background: #f1f3f4;
            font-weight: 500;
            color: var(--text-muted);
            font-size: 13px;
            text-transform: uppercase;
        }
        tr:last-child td { border-bottom: none; }
        .badge {
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
        }
        .badge.original { background: #e6f4ea; color: var(--success); }
        .badge.added { background: #fce8e6; color: var(--danger); }
        .badge.done { background: #e8f0fe; color: var(--primary); }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>DreamTeam Metrics</h1>
            <span style="color: var(--text-muted)">Project: <span id="proj-path"></span></span>
        </div>

        <div class="tabs">
            <div class="tab active" onclick="switchTab('analytics')">Analytics</div>
            <div class="tab" onclick="switchTab('table')">Task Table</div>
        </div>

        <div id="analytics" class="tab-content active">
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-value" id="kpi-total">0</div>
                    <div class="kpi-label">Total Tasks</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value" id="kpi-done">0</div>
                    <div class="kpi-label">Completed</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value" id="kpi-tokens">0</div>
                    <div class="kpi-label">Estimated Tokens</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value" id="kpi-friction">0.0</div>
                    <div class="kpi-label">Avg Attempts (Friction)</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value" id="kpi-calls-total">0</div>
                    <div class="kpi-label">Subagent Calls (Total)</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value" id="kpi-calls-open">0</div>
                    <div class="kpi-label">Open Calls</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value" id="kpi-active-batches">0</div>
                    <div class="kpi-label">Active Batches</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value" id="kpi-reviewer-cap">0 / 45</div>
                    <div class="kpi-label">Reviewer Calls (Active Batches)</div>
                </div>
            </div>

            <div class="chart-container">
                <canvas id="frictionChart" height="80"></canvas>
            </div>
            
            <div class="chart-container">
                <canvas id="tokensChart" height="80"></canvas>
            </div>

            <div class="chart-container">
                <canvas id="subagentTypeChart" height="80"></canvas>
            </div>

            <div class="chart-container">
                <canvas id="subagentOutcomeChart" height="80"></canvas>
            </div>

            <div class="batch-grid">
                <div class="batch-card">
                    <h3>Left Batch Details</h3>
                    <div id="batch-left"></div>
                </div>
                <div class="batch-card">
                    <h3>Right Batch Details</h3>
                    <div id="batch-right"></div>
                </div>
            </div>

            <div class="chart-container">
                <h3 style="margin-top: 0;">Recent Subagent Calls</h3>
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Orchestrator</th>
                            <th>Subagent</th>
                            <th>Task</th>
                            <th>Status</th>
                            <th>Duration</th>
                            <th>Started At</th>
                        </tr>
                    </thead>
                    <tbody id="calls-table-body">
                    </tbody>
                </table>
            </div>
        </div>

        <div id="table" class="tab-content">
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Type</th>
                        <th>Status</th>
                        <th>Title</th>
                        <th>Attempts</th>
                        <th>Minutes</th>
                        <th>Tokens</th>
                    </tr>
                </thead>
                <tbody id="table-body">
                </tbody>
            </table>
        </div>
    </div>

    <script>
        function switchTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            event.target.classList.add('active');
        }

        async function loadData() {
            const res = await fetch('/api/data');
            const data = await res.json();
            
            document.getElementById('proj-path').innerText = data.project_root;
            document.getElementById('kpi-total').innerText = data.tasks.length;
            
            const doneTasks = data.tasks.filter(t => t.status === 'done' || t.status === 'deprecated');
            document.getElementById('kpi-done').innerText = doneTasks.length;
            
            let totalTokens = 0;
            let totalAttempts = 0;
            let attemptCount = 0;

            const tableBody = document.getElementById('table-body');
            const labels = [];
            const tokenData = [];
            const attemptData = [];
            const timeData = [];

            data.tasks.forEach(t => {
                totalTokens += (t.tokens || 0);
                if (t.attempts) {
                    totalAttempts += t.attempts;
                    attemptCount++;
                }

                if (t.status === 'done') {
                    labels.push(t.id);
                    tokenData.push(t.tokens || 0);
                    attemptData.push(t.attempts || 1);
                    timeData.push(t.minutes || 0);
                }

                const typeClass = t.is_original ? 'original' : 'added';
                const typeText = t.is_original ? 'Original Plan' : 'Added Later';
                
                tableBody.insertAdjacentHTML('beforeend', `
                    <tr>
                        <td><strong>${t.id}</strong></td>
                        <td><span class="badge ${typeClass}">${typeText}</span></td>
                        <td><span class="badge ${t.status === 'done' ? 'done' : ''}">${t.status}</span></td>
                        <td style="max-width:300px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" title="${t.title}">${t.title}</td>
                        <td>${t.attempts || '-'}</td>
                        <td>${t.minutes ? t.minutes + 'm' : '-'}</td>
                        <td>${t.tokens ? t.tokens.toLocaleString() : '-'}</td>
                    </tr>
                `);
            });

            document.getElementById('kpi-tokens').innerText = (totalTokens / 1000).toFixed(1) + 'k';
            document.getElementById('kpi-friction').innerText = attemptCount > 0 ? (totalAttempts / attemptCount).toFixed(2) : '1.0';

            const subagent = data.subagent || {};
            const totals = subagent.totals || {};
            const orchestrators = subagent.orchestrators || {};
            const leftStats = orchestrators.left || {};
            const rightStats = orchestrators.right || {};

            document.getElementById('kpi-calls-total').innerText = totals.calls || 0;
            document.getElementById('kpi-calls-open').innerText = totals.open || 0;
            document.getElementById('kpi-active-batches').innerText = (leftStats.batch_id ? 1 : 0) + (rightStats.batch_id ? 1 : 0);
            const reviewerCompleted = (leftStats.reviewer_calls_completed || 0) + (rightStats.reviewer_calls_completed || 0);
            document.getElementById('kpi-reviewer-cap').innerText = `${reviewerCompleted} / 45`;

            // Charts
            new Chart(document.getElementById('frictionChart'), {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Attempts (Friction)',
                            data: attemptData,
                            borderColor: '#d93025',
                            backgroundColor: 'rgba(217, 48, 37, 0.1)',
                            fill: true,
                            tension: 0.3
                        },
                        {
                            label: 'Minutes',
                            data: timeData,
                            borderColor: '#fbbc04',
                            borderDash: [5, 5],
                            tension: 0.3
                        }
                    ]
                },
                options: {
                    responsive: true,
                    plugins: { title: { display: true, text: 'Hallucination & Time Spike Tracker' } },
                    scales: { y: { beginAtZero: true } }
                }
            });

            new Chart(document.getElementById('tokensChart'), {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Estimated Tokens per Task',
                        data: tokenData,
                        backgroundColor: '#1a73e8',
                        borderRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { title: { display: true, text: 'Token Consumption' } }
                }
            });

            const byType = subagent.by_type || [];
            new Chart(document.getElementById('subagentTypeChart'), {
                type: 'bar',
                data: {
                    labels: byType.map(x => x.subagent_type),
                    datasets: [{
                        label: 'Calls by Subagent Type',
                        data: byType.map(x => x.total || 0),
                        backgroundColor: '#34a853',
                        borderRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { title: { display: true, text: 'Subagent Call Volume by Type' } }
                }
            });

            const outcomeLabels = ['completed', 'failed', 'timeout', 'cancelled', 'open'];
            const outcomeData = [
                totals.completed || 0,
                totals.failed || 0,
                totals.timeout || 0,
                totals.cancelled || 0,
                totals.open || 0
            ];
            new Chart(document.getElementById('subagentOutcomeChart'), {
                type: 'doughnut',
                data: {
                    labels: outcomeLabels,
                    datasets: [{
                        data: outcomeData,
                        backgroundColor: ['#1e8e3e', '#d93025', '#fbbc04', '#5f6368', '#1a73e8']
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { title: { display: true, text: 'Subagent Call Outcomes' } }
                }
            });

            const callsTableBody = document.getElementById('calls-table-body');
            (subagent.recent_calls || []).forEach(c => {
                const dur = c.duration_ms ? `${Math.round(c.duration_ms / 1000)}s` : '-';
                callsTableBody.insertAdjacentHTML('beforeend', `
                    <tr>
                        <td><strong>${c.id}</strong></td>
                        <td>${c.orchestrator || '-'}</td>
                        <td>${c.subagent_type || '-'}</td>
                        <td>${c.task_id || '-'}</td>
                        <td>${c.status || '-'}</td>
                        <td>${dur}</td>
                        <td>${c.started_at || '-'}</td>
                    </tr>
                `);
            });

            function batchHtml(s) {
                const active = s.batch_id ? 'yes' : 'no';
                const cap45 = s.reviewer_cap_reached ? 'reached' : 'ok';
                const cap15 = s.task_cap_reached ? 'reached' : 'ok';
                return `
                    <div class="batch-item"><span class="batch-key">Active</span><span class="batch-val">${active}</span></div>
                    <div class="batch-item"><span class="batch-key">Batch ID</span><span class="batch-val">${s.batch_id || '-'}</span></div>
                    <div class="batch-item"><span class="batch-key">Started At</span><span class="batch-val">${s.started_at || '-'}</span></div>
                    <div class="batch-item"><span class="batch-key">Open Calls</span><span class="batch-val">${s.open_calls || 0}</span></div>
                    <div class="batch-item"><span class="batch-key">Total Calls</span><span class="batch-val">${s.total_calls || 0}</span></div>
                    <div class="batch-item"><span class="batch-key">Reviewer Calls</span><span class="batch-val">${s.reviewer_calls_completed || 0} / 45 (${cap45})</span></div>
                    <div class="batch-item"><span class="batch-key">Tasks in Batch</span><span class="batch-val">${s.tasks_completed_in_batch || 0} / 15 (${cap15})</span></div>
                `;
            }
            document.getElementById('batch-left').innerHTML = batchHtml(leftStats);
            document.getElementById('batch-right').innerHTML = batchHtml(rightStats);
        }

        loadData();
    </script>
</body>
</html>
"""

class DashboardHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass # Suppress command line output

    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode('utf-8'))
            
        elif parsed.path == "/api/data":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(self.get_data()).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def get_data(self):
        data = {
            "project_root": project.get_project_root(),
            "tasks": [],
            "subagent": {
                "available": False,
                "orchestrators": {
                    "left": {"batch_id": None, "reviewer_calls_completed": 0, "tasks_completed_in_batch": 0, "open_calls": 0, "total_calls": 0},
                    "right": {"batch_id": None, "reviewer_calls_completed": 0, "tasks_completed_in_batch": 0, "open_calls": 0, "total_calls": 0}
                },
                "totals": {"calls": 0, "completed": 0, "failed": 0, "timeout": 0, "cancelled": 0, "open": 0},
                "by_type": [],
                "recent_calls": []
            }
        }
        
        if not os.path.exists(TASKS_DB):
            return data
            
        conn = sqlite3.connect(TASKS_DB, timeout=10.0)
        try:
            # Attach DevExperience DB if it exists
            has_exp = os.path.exists(EXP_DB)
            if has_exp:
                conn.execute(f"ATTACH DATABASE '{EXP_DB}' AS exp")
                
            cursor = conn.cursor()
            
            # Find the minimum created_at to determine "Original" vs "Added Later"
            cursor.execute("SELECT MIN(created_at) FROM tasks")
            min_date_str = cursor.fetchone()[0]
            
            if has_exp:
                cursor.execute("""
                    SELECT t.id, t.title, t.status, t.created_at,
                           e.attempts_count, e.time_spent_minutes, e.tokens_estimated
                    FROM tasks t
                    LEFT JOIN exp.task_experience e
                        ON e.id = (
                            SELECT e2.id
                            FROM exp.task_experience e2
                            WHERE e2.task_id = t.id
                            ORDER BY e2.created_at DESC, e2.id DESC
                            LIMIT 1
                        )
                    ORDER BY t.id ASC
                """)
            else:
                cursor.execute("""
                    SELECT id, title, status, created_at, NULL, NULL, NULL
                    FROM tasks
                    ORDER BY id ASC
                """)
                
            for row in cursor.fetchall():
                tid, title, status, created_at, attempts, mins, tokens = row
                
                # Heuristic: Original tasks are created within 1 hour of the very first task (initial planning)
                # Later tasks (FixPlanner / Replanning) are created significantly later
                is_original = True
                if min_date_str and created_at:
                    try:
                        from datetime import datetime
                        d_min = datetime.strptime(min_date_str, "%Y-%m-%d %H:%M:%S")
                        d_cur = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
                        is_original = (d_cur - d_min).total_seconds() < 3600
                    except Exception:
                        pass

                data["tasks"].append({
                    "id": tid,
                    "title": title or "",
                    "status": status,
                    "is_original": is_original,
                    "attempts": attempts,
                    "minutes": mins,
                    "tokens": tokens
                })

            if has_exp:
                data["subagent"]["available"] = True
                try:
                    def get_orchestrator_stats(orchestrator: str) -> dict:
                        cursor.execute(
                            """
                            SELECT batch_id, started_at
                            FROM exp.batch_sessions
                            WHERE orchestrator = ? AND status = 'active'
                            ORDER BY started_at DESC
                            LIMIT 1
                            """,
                            (orchestrator,),
                        )
                        row = cursor.fetchone()
                        if not row:
                            return {
                                "batch_id": None,
                                "started_at": None,
                                "reviewer_calls_completed": 0,
                                "tasks_completed_in_batch": 0,
                                "open_calls": 0,
                                "total_calls": 0,
                                "reviewer_cap_reached": False,
                                "task_cap_reached": False,
                            }
                        batch_id = row[0]
                        started_at = row[1]
                        cursor.execute("SELECT COUNT(*) FROM exp.subagent_calls WHERE batch_id = ?", (batch_id,))
                        total_calls = int(cursor.fetchone()[0])
                        cursor.execute("SELECT COUNT(*) FROM exp.subagent_calls WHERE batch_id = ? AND ended_at IS NULL", (batch_id,))
                        open_calls = int(cursor.fetchone()[0])
                        cursor.execute(
                            "SELECT COUNT(*) FROM exp.subagent_calls WHERE batch_id = ? AND subagent_type = 'reviewer' AND status = 'completed'",
                            (batch_id,),
                        )
                        reviewer_calls_completed = int(cursor.fetchone()[0])
                        cursor.execute(
                            "SELECT COUNT(DISTINCT task_id) FROM exp.subagent_calls WHERE batch_id = ? AND subagent_type = 'git-ops' AND status = 'completed' AND task_id IS NOT NULL",
                            (batch_id,),
                        )
                        tasks_completed_in_batch = int(cursor.fetchone()[0])
                        return {
                            "batch_id": batch_id,
                            "started_at": started_at,
                            "reviewer_calls_completed": reviewer_calls_completed,
                            "tasks_completed_in_batch": tasks_completed_in_batch,
                            "open_calls": open_calls,
                            "total_calls": total_calls,
                            "reviewer_cap_reached": reviewer_calls_completed >= 45,
                            "task_cap_reached": tasks_completed_in_batch >= 15,
                        }

                    data["subagent"]["orchestrators"]["left"] = get_orchestrator_stats("left")
                    data["subagent"]["orchestrators"]["right"] = get_orchestrator_stats("right")

                    cursor.execute(
                        """
                        SELECT
                            COUNT(*) AS calls,
                            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed,
                            SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failed,
                            SUM(CASE WHEN status = 'timeout' THEN 1 ELSE 0 END) AS timeout,
                            SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled,
                            SUM(CASE WHEN ended_at IS NULL THEN 1 ELSE 0 END) AS open
                        FROM exp.subagent_calls
                        """
                    )
                    row = cursor.fetchone()
                    data["subagent"]["totals"] = {
                        "calls": int(row[0] or 0),
                        "completed": int(row[1] or 0),
                        "failed": int(row[2] or 0),
                        "timeout": int(row[3] or 0),
                        "cancelled": int(row[4] or 0),
                        "open": int(row[5] or 0),
                    }

                    cursor.execute(
                        """
                        SELECT
                            subagent_type,
                            COUNT(*) AS total,
                            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed,
                            SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failed,
                            SUM(CASE WHEN status = 'timeout' THEN 1 ELSE 0 END) AS timeout,
                            SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled,
                            SUM(CASE WHEN ended_at IS NULL THEN 1 ELSE 0 END) AS open
                        FROM exp.subagent_calls
                        GROUP BY subagent_type
                        ORDER BY total DESC, subagent_type ASC
                        """
                    )
                    data["subagent"]["by_type"] = [
                        {
                            "subagent_type": r[0],
                            "total": int(r[1] or 0),
                            "completed": int(r[2] or 0),
                            "failed": int(r[3] or 0),
                            "timeout": int(r[4] or 0),
                            "cancelled": int(r[5] or 0),
                            "open": int(r[6] or 0),
                        }
                        for r in cursor.fetchall()
                    ]

                    cursor.execute(
                        """
                        SELECT id, orchestrator, subagent_type, task_id, status, duration_ms, started_at
                        FROM exp.subagent_calls
                        ORDER BY id DESC
                        LIMIT 50
                        """
                    )
                    data["subagent"]["recent_calls"] = [
                        {
                            "id": int(r[0]),
                            "orchestrator": r[1] or "",
                            "subagent_type": r[2] or "",
                            "task_id": r[3] or "",
                            "status": r[4] or "",
                            "duration_ms": int(r[5] or 0),
                            "started_at": r[6] or "",
                        }
                        for r in cursor.fetchall()
                    ]
                except sqlite3.Error:
                    # Graceful fallback for older DevExperience schemas.
                    pass
        finally:
            conn.close()
            
        return data

def main():
    import argparse
    parser = argparse.ArgumentParser(description="DreamTeam Analytics Dashboard")
    parser.add_argument("--external", action="store_true", help="Open in external system browser")
    args = parser.parse_args()

    port = 8080
    url = f"http://localhost:{port}"
    print("=====================================================")
    print("DreamTeam Analytics Dashboard is running!")
    print("=====================================================")
    print(f"INTERNAL BROWSER: Ctrl+Click (or Cmd+Click) this link: {url}")
    if args.external:
        print(f"Opening in external browser automatically...")
    else:
        print(f"EXTERNAL BROWSER: Open the link above in Chrome or run with --external")
    print("=====================================================")
    print("Press Ctrl+C to stop.")
    
    if args.external:
        try:
            webbrowser.open(url)
        except Exception:
            pass
        
    server = HTTPServer(('localhost', port), DashboardHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping dashboard...")

if __name__ == "__main__":
    main()
