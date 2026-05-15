# Sample Request Data

## Purpose

This folder contains safe sample JSON payloads for manually testing the security monitoring system through `/analyze` or `/api/analyze`.

## File

- `example_requests.json`: request examples for normal traffic, SQL injection, XSS, path traversal, command injection, recursive API abuse, and ambiguous LLM review.

## How The Samples Relate To The Code

The payloads are designed around `security_system/security.py` and its `detect_anomaly()` function:

- SQL patterns should return `SQL Injection Attempt`.
- Script payloads should return `XSS Attempt`.
- Directory traversal strings should return `Path Traversal Attempt`.
- Shell command separators should return `Command Injection Attempt`.
- Recursive `/vuln/recursive` URLs should return `Recursive API Abuse`.
- Normal login-style payloads should return `Normal`.

## Safety Note

The examples are strings used for local educational detection tests. They are not connected to a real authentication system, shell, or file system command execution path.
