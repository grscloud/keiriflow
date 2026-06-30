# ADR-015 バックアップ方針

## ステータス

Accepted

---

## 日付

2026-06-30

---

## 背景

障害や誤操作によるデータ損失を防止するため、バックアップ方針を定義する。

---

## 決定

データベースおよび添付ファイルのバックアップを定期的に取得する。

---

## バックアップ対象

- PostgreSQL
- Amazon S3
- Terraform State
- 設定ファイル

---

## バックアップ方式

### PostgreSQL

- 毎日フルバックアップ
- 30日保持

### Amazon S3

- Versioning有効
- Lifecycle管理

### Terraform

- GitHub Repository
- S3 Backend

---

## リストア

障害発生時は最新のバックアップから復元する。

復旧手順は運用手順書に従う。

---

## 将来の見直し

Amazon RDS移行後は、自動バックアップおよびPoint-in-Time Recovery（PITR）を利用する。