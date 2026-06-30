# KeiriFlow システムアーキテクチャ設計書

Version：1.0

---

# 1. 目的

本書は、KeiriFlow のシステムアーキテクチャおよび設計方針を定義することを目的とする。

本システムは、小規模法人向けSaaSとして提供することを前提とし、初期開発では「低コスト」「シンプルな運用」「拡張性」の3点を重視する。

利用企業数やアクセス数の増加に応じて、AWSマネージドサービスを段階的に採用し、システムを拡張できる構成とする。

---

# 2. アーキテクチャ設計方針

本システムでは以下の設計方針を採用する。

* MVP（Minimum Viable Product）を短期間で提供する。
* 初期運用コストを最小限に抑える。
* Infrastructure as Code（Terraform）によるインフラ管理を実施する。
* Dockerを利用し、開発環境と本番環境の差異を最小化する。
* 将来的なスケールアウトを考慮し、各コンポーネントを疎結合に設計する。
* AWSマネージドサービスへの移行を容易にする。

---

# 3. システム構成（Phase 1）

## 3.1 概要

サービス開始時点では、利用者数が限定的であることを想定し、AWS利用料金を最小限に抑える構成を採用する。

データベースについてはAmazon RDSを利用せず、EC2上でDockerコンテナとしてPostgreSQLを稼働させる。

Webサーバー、アプリケーション、データベースを1台のEC2インスタンスに集約し、シンプルな構成とする。

---

## 3.2 システム構成図

```text
                +------------------+
                |      User        |
                +---------+--------+
                          |
                     HTTPS (443)
                          |
                      Route53
                          |
                     Elastic IP
                          |
                 +--------v---------+
                 |       EC2        |
                 |------------------|
                 | Nginx            |
                 | Docker Compose   |
                 | Django           |
                 | PostgreSQL       |
                 | Redis            |
                 +--------+---------+
                          |
                    Amazon S3
      （領収書・請求書・添付ファイル保存）
```

---

## 3.3 利用AWSサービス

| サービス                    | 用途         |
| ----------------------- | ---------- |
| Amazon EC2              | Web/APサーバー |
| Amazon S3               | 添付ファイル保存   |
| Amazon Route 53         | DNS管理      |
| AWS Certificate Manager | SSL証明書     |
| AWS IAM                 | アクセス制御     |
| Amazon CloudWatch       | ログ監視・メトリクス |

---

## 3.4 Docker構成

```text
docker-compose

├── nginx
├── django
├── postgres
└── redis
```

---

# 4. 採用理由

## Amazon EC2

開発初期では利用企業数が少ないことを想定しているため、EC2へシステムを集約する。

運用コストを抑えながら、Dockerを利用することで将来的な構成変更にも対応しやすい。

---

## Docker Compose

単一ホストでの運用で十分なため、Docker Composeを採用する。

コンテナ管理を容易にし、開発環境と本番環境の差異を最小化する。

---

## PostgreSQL（Docker）

初期段階ではデータ容量およびアクセス数は限定的である。

そのためAmazon RDSではなくDockerコンテナ上のPostgreSQLを採用し、運用コストを削減する。

---

## Amazon S3

領収書や請求書などのファイルはAmazon S3へ保存する。

アプリケーションサーバーとは分離して保存することで、バックアップ性と拡張性を確保する。

---

# 5. アーキテクチャロードマップ

KeiriFlowでは、サービスの成長に合わせて段階的にシステム構成を変更する。

---

## Phase 1（MVP）

対象

* 利用企業：20社以下
* 利用ユーザー：100名以下

構成

* EC2
* Docker Compose
* PostgreSQL
* Amazon S3

目的

* 初期コスト最小化
* MVP提供

---

## Phase 2（サービス拡大）

対象

* 利用企業：約300社
* 利用ユーザー：約2,000名

追加構成

* Application Load Balancer
* Auto Scaling
* Amazon RDS for PostgreSQL

目的

* 可用性向上
* スケールアウト対応
* データベース運用負荷軽減

---

## Phase 3（SaaS成熟）

対象

* 利用企業：1,000社以上

追加構成

* Amazon CloudFront
* Amazon ECS
* Amazon Aurora PostgreSQL
* Amazon ElastiCache
* Amazon OpenSearch Service
* Amazon Bedrock

目的

* 高可用性
* 高性能
* AI機能追加
* グローバル展開対応

---

# 6. アーキテクチャ進化イメージ

```text
          Phase1
┌──────────────────────┐
│ EC2                  │
│ Docker Compose       │
│ PostgreSQL           │
│ Amazon S3            │
└──────────┬───────────┘
           │
           ▼
          Phase2
┌──────────────────────┐
│ ALB                  │
│ EC2 Auto Scaling     │
│ Amazon RDS           │
│ Amazon S3            │
└──────────┬───────────┘
           │
           ▼
          Phase3
┌──────────────────────┐
│ CloudFront           │
│ Amazon ECS           │
│ Aurora PostgreSQL    │
│ ElastiCache          │
│ OpenSearch           │
│ Amazon Bedrock       │
└──────────────────────┘
```

---

# 7. 各フェーズ比較

| 項目       | Phase 1            | Phase 2          | Phase 3       |
| -------- | ------------------ | ---------------- | ------------- |
| 利用企業数    | ～20社               | ～300社            | 1,000社以上      |
| 利用ユーザー数  | ～100名              | ～2,000名          | 10,000名以上     |
| Web/AP   | Amazon EC2         | EC2 Auto Scaling | Amazon ECS    |
| データベース   | PostgreSQL（Docker） | Amazon RDS       | Amazon Aurora |
| ロードバランサー | なし                 | ALB              | ALB           |
| CDN      | なし                 | なし               | CloudFront    |
| キャッシュ    | Redis（Docker）      | Redis            | ElastiCache   |
| IaC      | Terraform          | Terraform        | Terraform     |
| コンテナ     | Docker Compose     | Docker Compose   | Amazon ECS    |
| 運用コスト    | 低                  | 中                | 高             |
| 拡張性      | ○                  | ◎                | ◎◎            |

---

# 8. 今後の方針

KeiriFlowは、事業規模に応じてAWSマネージドサービスを段階的に採用することで、運用コストと拡張性のバランスを維持する。

初期段階ではシンプルな構成を採用し、利用企業数およびトラフィックの増加に応じて高可用性構成へ移行する。
