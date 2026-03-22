# DevSecOps Quiz App

A simple quiz app used as the vehicle for demonstrating a complete DevSecOps pipeline.

## What this app does
- Serves a 5-question DevSecOps quiz
- Accepts name + email from trainees
- Shows pass/fail result with score
- Exposes `/health` endpoint for Kubernetes probes
- Exposes `/metrics` endpoint for Prometheus scraping

## Run locally
```bash
pip install flask
python app.py
```
Open http://localhost:5000

## Endpoints
| Endpoint | Description |
|----------|-------------|
| `/` | Home page |
| `/quiz` | Quiz page |
| `/submit` | Submit answers |
| `/health` | Health check → returns JSON |
| `/metrics` | App metrics → returns JSON |

## Tech Stack (Pipeline)
- CI: GitHub Actions + SonarQube
- CD: ArgoCD (GitOps)
- Container: Docker + Local Registry
- Infra: Terraform + Minikube
- Service Mesh: Istio (mTLS)
- Observability: Prometheus + Grafana
- SRE: SLOs + Error Budgets
