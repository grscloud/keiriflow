# ADR-014 ログ管理方針

## ステータス

Accepted

---

## 日付

2026-06-30

---

## 背景

障害調査、監査および運用保守のため、ログ管理方針を定義する。

---

## 決定

アプリケーションログ、アクセスログ、監査ログ、エラーログを取得する。

ログはAmazon CloudWatch Logsへ集約する。

---

## ログ種別

### Application Log

アプリケーション動作ログ

### Access Log

HTTPアクセスログ

### Audit Log

ログイン、権限変更、承認操作などの監査ログ

### Error Log

システムエラーおよび例外情報

---

## 保持期間

| ログ種別 | 保持期間 |
|----------|----------|
| Application Log | 90日 |
| Access Log | 90日 |
| Error Log | 180日 |
| Audit Log | 1年 |

---

## 将来の見直し

ログ分析基盤としてAmazon OpenSearch Serviceの導入を検討する。