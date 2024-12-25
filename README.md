# Public Proxy Tester and Updater

This project provides an automated solution for testing public proxies and updating their details in a GitHub repository. The workflow fetches proxy lists from known sources, tests their speed and type, and generates a detailed Markdown report (`proxy_report.md`) with the results.

## Features

- **Proxy Testing:** Automatically tests public proxies for speed and type.
- **Anonymity Classification:** Determines proxy types (e.g., Transparent, Anonymous, High Anonymity).
- **Automated Updates:** A GitHub Actions workflow tests proxies and updates the report regularly.
- **Markdown Report:** Outputs a detailed and compact report of working proxies.
- **Concurrency Management:** Ensures workflows do not overlap and run sequentially.

## Proxy Sources

The proxies are sourced from the following repo:
- https://github.com/zloi-user/hideip.me

These files must be present in the repository root and formatted as `IP:Port` (additional metadata like `:Country` is ignored).

## How It Works

1. The GitHub Actions workflow is triggered on a schedule (default: every hour).
2. The `test_proxies.py` script:
   - Loads proxies from the source files.
   - Tests each proxy's connectivity, speed, and anonymity level.
   - Generates a Markdown report with the results.
3. The workflow commits and pushes the updated `proxy_report.md` to the repository.

## Workflow Triggers

The workflow is triggered by:
- **Scheduled Runs:** Default is every hour, but it can run as frequently as every 5 minutes.
- **Manual Trigger:** Using the `workflow_dispatch` event.

## Report Format

The `proxy_report.md` file is updated with the following format:

| Proxy           | Type    | Response Time (s) | Anonymity       |
|-----------------|---------|-------------------|-----------------|
| xxx.xxx.xxx.xxx:xxxx | HTTP    | 0.34              | High Anonymity   |
