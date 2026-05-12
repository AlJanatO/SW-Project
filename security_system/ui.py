def layout(content: str) -> str:
    return f"""
    <html>
        <head>
            <title>Security Monitoring System</title>
            <style>
                body {{
                    font-family: Arial;
                    margin: 0;
                    background: #0f172a;
                    color: white;
                }}

                .navbar {{
                    background: #111827;
                    padding: 15px;
                    display: flex;
                    gap: 12px;
                    align-items: center;
                }}

                .navbar a {{
                    color: white;
                    text-decoration: none;
                    padding: 8px 14px;
                    background: #2563eb;
                    border-radius: 6px;
                    font-size: 14px;
                }}

                .navbar a:hover {{
                    background: #1d4ed8;
                }}

                .content {{
                    padding: 40px;
                    max-width: 980px;
                    margin: 0 auto;
                }}

                .card {{
                    background: #1e293b;
                    padding: 20px;
                    border-radius: 10px;
                    margin-top: 20px;
                    overflow-wrap: anywhere;
                    word-break: break-word;
                }}

                pre {{
                    white-space: pre-wrap;
                    overflow-wrap: anywhere;
                    word-break: break-word;
                    max-width: 100%;
                    margin: 0;
                }}
            </style>
        </head>

        <body>

            <div class="navbar">
                <a href="/">Home</a>
                <a href="/dashboard">Dashboard</a>
                <a href="/api/query/health">Health</a>
                <a href="/api/query/logs">Logs</a>
                <a href="/analyze">Analyze</a>
                <a href="/docs">API Docs</a>
            </div>

            <div class="content">
                {content}
            </div>

        </body>
    </html>
    """
