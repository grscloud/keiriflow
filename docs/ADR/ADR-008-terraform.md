# ADR-008 Terraformを採用する

## 背景

インフラ構成をコードで管理し、再現性を確保する必要がある。

---

## 決定

Infrastructure as CodeにはTerraformを採用する。

---

## 採用理由

- AWSとの親和性が高い
- バージョン管理が容易
- GitHub Actionsと連携しやすい
- 将来的にマルチクラウドへ対応できる

---

## 採用しなかった案

CloudFormation

理由

AWS専用であり、Terraformよりコミュニティが限定的である。

AWS CDK

理由

IaC学習およびポートフォリオとしてTerraformを優先する。

---

## 移行条件

現時点では変更予定なし。