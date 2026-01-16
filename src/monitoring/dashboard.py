from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import datetime
from src.monitoring.metrics import MetricsCollector
from src.utils.health_check import HealthCheck
from src.database.db import get_connection

class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/dashboard':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_dashboard_html().encode())
        elif self.path == '/api/health':
            self.send_json_response(HealthCheck().get_full_health())
        elif self.path == '/api/metrics':
            self.send_json_response(MetricsCollector.get_report())
        elif self.path == '/api/stats':
            self.send_json_response(self.get_stats())
        else:
            self.send_response(404)
            self.end_headers()
    
    def send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2, default=str).encode())
    
    def get_stats(self):
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM appointments')
        total_appointments = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM email_logs WHERE status = "sent"')
        emails_sent = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM email_logs WHERE status = "failed"')
        emails_failed = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM email_logs WHERE sent_at > datetime("now", "-24 hours")')
        recent_emails = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_appointments': total_appointments,
            'emails_sent': emails_sent,
            'emails_failed': emails_failed,
            'recent_emails_24h': recent_emails,
            'success_rate': (emails_sent / (emails_sent + emails_failed) * 100) if (emails_sent + emails_failed) > 0 else 0
        }
    
    def get_dashboard_html(self):
        health = HealthCheck().get_full_health()
        metrics = MetricsCollector.get_report()
        stats = self.get_stats()
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Fresha Email Automation Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; padding: 20px; }
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ color: #333; margin-bottom: 30px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 20px; }}
        .card {{ background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .card h2 {{ font-size: 18px; margin-bottom: 15px; color: #555; }}
        .stat {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #eee; }}
        .stat:last-child {{ border-bottom: none; }}
        .stat-label {{ color: #666; }}
        .stat-value {{ font-weight: bold; color: #333; }}
        .status-healthy {{ color: #28a745; }}
        .status-unhealthy {{ color: #dc3545; }}
        .refresh-btn {{ background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; margin-bottom: 20px; }}
        .refresh-btn:hover {{ background: #0056b3; }}
    </style>
    <script>
        function refresh() { location.reload(); }
        setInterval(refresh, 60000); // Auto-refresh every minute
    </script>
</head>
<body>
    <div class="container">
        <h1>📊 Fresha Email Automation Dashboard</h1>
        <button class="refresh-btn" onclick="refresh()">🔄 Refresh</button>
        
        <div class="grid">
            <div class="card">
                <h2>System Health</h2>
                <div class="stat">
                    <span class="stat-label">Overall Status:</span>
                    <span class="stat-value status-{health['overall']}">{health['overall'].upper()}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Database:</span>
                    <span class="stat-value status-{health['checks']['database']['status']}">{health['checks']['database']['status'].upper()}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">SMTP:</span>
                    <span class="stat-value status-{health['checks']['smtp']['status']}">{health['checks']['smtp']['status'].upper()}</span>
                </div>
            </div>
            
            <div class="card">
                <h2>Statistics</h2>
                <div class="stat">
                    <span class="stat-label">Total Appointments:</span>
                    <span class="stat-value">{stats['total_appointments']}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Emails Sent:</span>
                    <span class="stat-value">{stats['emails_sent']}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Emails Failed:</span>
                    <span class="stat-value">{stats['emails_failed']}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Success Rate:</span>
                    <span class="stat-value">{stats['success_rate']:.1f}%</span>
                </div>
            </div>
            
            <div class="card">
                <h2>Recent Activity (24h)</h2>
                <div class="stat">
                    <span class="stat-label">Emails Sent:</span>
                    <span class="stat-value">{stats['recent_emails_24h']}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Success Rate (24h):</span>
                    <span class="stat-value">{metrics['success_rate_24h']:.1f}%</span>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>API Endpoints</h2>
            <div class="stat">
                <span class="stat-label">Health Check:</span>
                <span class="stat-value"><a href="/api/health">/api/health</a></span>
            </div>
            <div class="stat">
                <span class="stat-label">Metrics:</span>
                <span class="stat-value"><a href="/api/metrics">/api/metrics</a></span>
            </div>
            <div class="stat">
                <span class="stat-label">Stats:</span>
                <span class="stat-value"><a href="/api/stats">/api/stats</a></span>
            </div>
        </div>
    </div>
</body>
</html>
        """

def run_dashboard(port=8080):
    server = HTTPServer(('0.0.0.0', port), DashboardHandler)
    print(f'Monitoring dashboard running on http://localhost:{port}')
    print('Press Ctrl+C to stop')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down dashboard...')
        server.shutdown()

if __name__ == '__main__':
    run_dashboard()
