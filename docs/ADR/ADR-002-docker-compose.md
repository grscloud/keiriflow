# ADR-002 Docker Composeを採用する

## 背景

KeiriFlowは単一サーバー構成を採用する。

---

## 決定

Docker Composeを利用する。

---

## 採用理由

- 構成がシンプル
- 学習コストが低い
- Djangoとの相性が良い
- Terraformとの連携が容易

---

## 採用しなかった案

Kubernetes

理由

初期構成では運用負荷が高く、得られるメリットが少ない。

---

## 将来の見直し

ECSまたはEKSへ移行する際に再評価する。