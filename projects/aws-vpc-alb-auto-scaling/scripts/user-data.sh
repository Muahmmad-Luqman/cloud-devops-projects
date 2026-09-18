#!/bin/bash
set -euo pipefail
dnf install -y httpd
printf '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AWS Auto Scaling Lab</title><style>body{margin:0;background:#101827;color:#edf2f7;font-family:system-ui;padding:8vw}main{max-width:800px}h1{font-size:clamp(2rem,6vw,4rem)}strong{color:#ff9900}p{line-height:1.7}</style></head><body><main><strong>AWS NETWORKING LAB</strong><h1>Load balanced.<br>Automatically scaled.</h1><p>Built by Muhammad Luqman using Amazon VPC, an Application Load Balancer and EC2 Auto Scaling.</p><p>Serving host: %s</p></main></body></html>' "$(hostname)" > /var/www/html/index.html
systemctl enable --now httpd
