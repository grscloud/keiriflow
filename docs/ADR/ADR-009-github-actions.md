# ADR-009 GitHub Actionsを採用する

## 背景

ソースコード品質を維持し、デプロイ作業を自動化する必要がある。

---

## 決定

CI/CDにはGitHub Actionsを採用する。

---

## 採用理由

- GitHubとの統合が容易
- Terraformとの連携が容易
- Docker Buildを自動化できる
- OSSで広く利用されている

---

## 将来

AWS CodePipelineとの連携も検討する。