# Architecture Decision Records（ADR）

## 概要

本ディレクトリでは、KeiriFlowにおける主要なアーキテクチャ上の意思決定を記録する。

ADR（Architecture Decision Record）は、システム設計における背景、採用理由、代替案、および将来の見直し条件を記録するためのドキュメントである。

新たな重要な設計判断が行われた場合は、新しいADRを追加する。

---

# ADR一覧

| No. | タイトル | ステータス | カテゴリ |
|------|----------|------------|----------|
| ADR-001 | 初期構成でAmazon EC2を採用する | Accepted | Infrastructure |
| ADR-002 | Docker Composeを採用する | Accepted | Container |
| ADR-003 | PostgreSQLをEC2上で運用する | Accepted | Database |
| ADR-004 | Nginxをリバースプロキシとして採用する | Accepted | Network |
| ADR-005 | 添付ファイルはAmazon S3へ保存する | Accepted | Storage |
| ADR-006 | モノリシックアーキテクチャを採用する | Accepted | Architecture |
| ADR-007 | Djangoを採用する | Accepted | Application |
| ADR-008 | Terraformを採用する | Accepted | Infrastructure |
| ADR-009 | GitHub Actionsを採用する | Accepted | CI/CD |
| ADR-010 | PostgreSQLからAmazon RDSへの移行方針 | Planned | Database |
| ADR-011 | Amazon EC2からAmazon ECSへの移行方針 | Planned | Infrastructure |
| ADR-012 | マルチテナント設計を採用する | Accepted | SaaS |
| ADR-013 | Redis導入方針 | Planned | Cache |
| ADR-014 | ログ管理方針 | Accepted | Operations |
| ADR-015 | バックアップ方針 | Accepted | Operations |

---

# ADRライフサイクル

各ADRは以下のいずれかのステータスを持つ。

| ステータス | 説明 |
|------------|------|
| Proposed | 提案中 |
| Accepted | 採用済み |
| Deprecated | 廃止 |
| Superseded | 新しいADRに置き換えられた |

---

# 更新ルール

- 過去のADRは原則として書き換えない。
- 設計方針が変更された場合は、新しいADRを追加する。
- 旧ADRは「Superseded」とし、後続ADRを参照する。