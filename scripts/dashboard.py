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
            </div>

            <div class="chart-container">
                <canvas id="frictionChart" height="80"></canvas>
            </div>
            
            <div class="chart-container">
                <canvas id="tokensChart" height="80"></canvas>
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
            "tasks": []
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
                    LEFT JOIN exp.task_experience e ON t.id = e.task_id
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
