# 04. データベース設計

---

# 1. ドキュメント情報

|項目|内容|
|------|------|
|ドキュメント名|データベース設計書|
|システム名|SaaS会計システム|
|バージョン|1.0|
|作成日|2026-06-30|
|DBMS|PostgreSQL 16|
|ORM|Django ORM|
|文字コード|UTF-8|
|タイムゾーン|Asia/Tokyo|
|命名規則|snake_case|
|主キー|UUID|
|削除方式|論理削除|

---

# 2. データベース設計方針

## 2.1 基本方針

本システムは、小規模法人向けSaaS会計システムとして設計する。

複数企業が同一システムを利用するマルチテナント構成を採用し、すべての業務データは会社（Tenant）単位で管理する。

将来的な機能追加や利用企業数の増加を考慮し、保守性・拡張性・可用性を重視した設計とする。

---

## 2.2 設計ポリシー

### マルチテナント

すべての業務テーブルは tenant_id を保持する。

会社間でデータが参照できないようにアプリケーションレベルおよびDBレベルで管理する。

---

### UUID採用

すべての主キーはUUIDを採用する。

理由

- URLから件数が推測できない
- データマージしやすい
- 将来の分散DBへ対応しやすい
- Django標準対応

---

### 論理削除

DELETEは行わない。

deleted_atに日時を保存する。

論理削除されたデータは通常検索対象外とする。

---

### 監査性

作成者・更新者・更新日時を保持する。

監査ログ(Audit Log)によって重要操作を記録する。

---

### 正規化

第三正規形(3NF)を基本とする。

必要に応じてパフォーマンス改善目的で一部非正規化を許可する。

---

### 楽観ロック

versionカラムを利用する。

同時更新時のデータ不整合を防止する。

---

### 外部キー

整合性を保証するため外部キー制約を利用する。

ただし大量データが想定されるログ系テーブルは必要最低限とする。

---

# 3. 命名規則

## 3.1 テーブル名

すべて小文字。

snake_caseを使用する。

例

```
tenant

company_setting

employee

travel_expense

invoice_item
```

---

## 3.2 カラム名

snake_case

例

```
employee_no

project_name

created_at

updated_at

deleted_at
```

---

## 3.3 インデックス

```
idx_<table>_<column>

例

idx_employee_email

idx_invoice_no
```

---

## 3.4 外部キー

```
fk_<table>_<reference>

例

fk_employee_department

fk_invoice_customer
```

---

## 3.5 Unique

```
uq_<table>_<column>

例

uq_employee_email

uq_invoice_no
```

---

# 4. 共通カラム設計

業務テーブルには原則として以下の共通項目を持つ。

|論理名|物理名|型|PK|NN|Default|説明|
|------|------|----|----|----|---------|------|
|ID|id|UUID|○|○||主キー|
|会社ID|tenant_id|UUID||○||所属会社ID（Tenant）|
|作成者|created_by|UUID|||NULL|レコード作成ユーザー|
|更新者|updated_by|UUID|||NULL|レコード更新ユーザー|
|作成日時|created_at|timestamp||○|CURRENT_TIMESTAMP|作成日時|
|更新日時|updated_at|timestamp||○|CURRENT_TIMESTAMP|更新日時|
|削除日時|deleted_at|timestamp|||NULL|論理削除日時|
|Version|version|integer||○|1|楽観ロック用バージョン番号|

---

## 共通ルール

### created_at

INSERT時に自動設定する。

---

### updated_at

UPDATE時に自動更新する。

---

### deleted_at

NULL

= 有効

日時あり

= 論理削除済

---

### version

更新時

version +1

楽観ロック制御に利用する。

---

# 5. データ型一覧

|型|用途|
|------|------|
|UUID|主キー|
|varchar(n)|文字列|
|text|長文|
|boolean|真偽値|
|integer|整数|
|numeric(12,2)|金額|
|date|日付|
|timestamp|日時|
|jsonb|JSONデータ|

---

## 金額型

すべて

numeric(12,2)

を使用する。

例

```
100.00

1500000.50
```

---

# 6. 共通制約

|制約|内容|
|------|------|
|NOT NULL|必須項目|
|PRIMARY KEY|UUID|
|FOREIGN KEY|関連整合性保証|
|UNIQUE|重複禁止|
|CHECK|値チェック|

---

# 7. インデックス設計方針

以下の列には原則インデックスを付与する。

- tenant_id
- created_at
- updated_at
- email
- employee_no
- invoice_no
- project_id
- customer_id
- employee_id
- expense_date
- issue_date

複合検索が多い場合は複合インデックスを追加する。

例

```
tenant_id

+

employee_no
```

---

# 8. ER図（システム全体）

```
Tenant
│
├── CompanySetting
│
├── User
│      │
│      ├── UserRole
│      │      │
│      │      └── Role
│      │              │
│      │              └── RolePermission
│      │                        │
│      │                        └── Permission
│
├── Department
│      │
│      └── Employee
│              │
│              ├── Expense
│              │      │
│              │      └── Approval
│              │
│              └── TravelExpense
│
├── Customer
│      │
│      └── Project
│              │
│              ├── Invoice
│              │      │
│              │      └── InvoiceItem
│              │
│              └── Attachment
│
├── Notification
│
├── AuditLog
│
└── LoginHistory
```

---

# 9. テーブル一覧

|No|テーブル名|概要|
|--|-----------|----------------------------|
|01|tenant|会社情報|
|02|company_setting|会社設定|
|03|user|ログインユーザー|
|04|role|ロール|
|05|permission|権限|
|06|role_permission|ロール権限|
|07|user_role|ユーザーロール|
|08|department|部署|
|09|employee|社員|
|10|customer|取引先|
|11|project|案件|
|12|expense_category|経費分類|
|13|expense|経費申請|
|14|travel_expense|交通費|
|15|approval|承認履歴|
|16|invoice|請求書|
|17|invoice_item|請求明細|
|18|attachment|添付ファイル|
|19|notification|通知|
|20|audit_log|監査ログ|
|21|login_history|ログイン履歴|

---

# 10. 今後追加予定テーブル

以下はVersion 2以降で追加予定とする。

|テーブル|概要|
|----------|----------------|
|journal_entry|仕訳|
|account_title|勘定科目|
|bank_account|銀行口座|
|payroll|給与|
|attendance|勤怠|
|ocr_result|OCR解析結果|
|api_token|API認証|
|webhook|Webhook設定|
|subscription|契約プラン|
|payment_history|決済履歴|
|ai_chat_history|AI利用履歴|

---

# 11. テーブル詳細

# 11.1 tenant

## テーブル概要

会社（テナント）の基本情報を管理する。

本システムはマルチテナント方式を採用するため、すべての業務データは Tenant に所属する。

---

## 業務概要

- SaaS利用会社の管理
- 契約会社情報
- 請求書発行会社情報
- 全データの親テーブル

---

## テーブル定義

|項目|内容|
|------|------|
|物理名|tenant|
|論理名|会社|
|主キー|id|
|データ保持|論理削除|
|更新頻度|低|

---

## カラム一覧

|論理名|物理名|型|PK|FK|NN|Default|説明|
|------|------|------|---|---|---|-------|------|
|会社ID|id|UUID|〇||| |会社を一意に識別するID|
|会社名|company_name|varchar(200)|||〇||正式な会社名|
|会社名（カナ）|company_name_kana|varchar(200)|||||会社名（カタカナ）|
|法人番号|corporate_number|varchar(20)||||NULL|法人番号（任意）|
|適格請求書番号|invoice_number|varchar(30)||||NULL|インボイス登録番号|
|郵便番号|postal_code|varchar(20)||||NULL|会社所在地の郵便番号|
|住所|address|text||||NULL|会社住所|
|電話番号|phone|varchar(30)||||NULL|代表電話番号|
|メールアドレス|email|varchar(255)||||NULL|代表メールアドレス|
|ホームページ|website|varchar(255)||||NULL|会社ホームページURL|
|決算月|fiscal_month|smallint|||〇|3|決算月（1～12）|
|契約開始日|contract_start_date|date||||NULL|サービス利用開始日|
|契約終了日|contract_end_date|date||||NULL|契約終了日|
|契約状態|contract_status|varchar(20)|||〇|ACTIVE|契約状態|
|作成者|created_by|UUID||〇|||作成ユーザー|
|更新者|updated_by|UUID||〇|||更新ユーザー|
|作成日時|created_at|timestamp|||〇|CURRENT_TIMESTAMP|作成日時|
|更新日時|updated_at|timestamp|||〇|CURRENT_TIMESTAMP|更新日時|
|削除日時|deleted_at|timestamp||||NULL|論理削除日時|
|Version|version|integer|||〇|1|楽観ロック用|

---

## インデックス

|名称|対象|
|------|------|
|PK_tenant|id|
|IDX_tenant_company_name|company_name|
|IDX_tenant_contract_status|contract_status|
|IDX_tenant_invoice_number|invoice_number|

---

## 外部キー

なし

（最上位テーブル）

---

## UNIQUE制約

|項目|
|------|
|corporate_number|
|invoice_number|

---

## CHECK制約

```
fiscal_month BETWEEN 1 AND 12
```

---

## 業務ルール

- 契約停止会社はログイン不可
- 論理削除のみ許可
- インボイス番号は会社単位で一意
- 決算月は変更可能

---

## Django Model実装方針

- UUIDPrimaryKey
- TimeStampedModel継承
- SoftDeleteMixin継承
- TenantMixinの親モデル

---

## 将来拡張

追加予定

- Stripe Customer ID
- 利用プラン
- 利用人数
- ストレージ容量
- AI利用上限

---

# 11.2 company_setting

## テーブル概要

会社ごとのシステム設定を保持する。

Tenantと1対1の関係を持つ。

---

## 業務概要

会社設定

- ロゴ
- 消費税
- 通貨
- 表示言語
- タイムゾーン

---

## テーブル定義

|項目|内容|
|------|------|
|物理名|company_setting|
|論理名|会社設定|
|PK|id|

---

## カラム一覧

|論理名|物理名|型|PK|FK|NN|Default|説明|
|------|------|------|---|---|---|------|------|
|設定ID|id|UUID|〇||||設定ID|
|会社ID|tenant_id|UUID||〇|〇||対象会社|
|会社ロゴ|logo_path|varchar(300)|||||S3保存先|
|標準消費税率|default_tax_rate|numeric(5,2)|||〇|10.00|既定税率|
|通貨|currency|varchar(10)|||〇|JPY|利用通貨|
|言語|language|varchar(10)|||〇|ja|表示言語|
|タイムゾーン|timezone|varchar(50)|||〇|Asia/Tokyo|タイムゾーン|
|小数点桁数|decimal_digits|integer|||〇|0|金額表示桁数|
|日付表示形式|date_format|varchar(30)|||〇|YYYY-MM-DD|日付フォーマット|
|作成者|created_by|UUID||〇|||作成者|
|更新者|updated_by|UUID||〇|||更新者|
|作成日時|created_at|timestamp|||〇|CURRENT_TIMESTAMP|作成日時|
|更新日時|updated_at|timestamp|||〇|CURRENT_TIMESTAMP|更新日時|
|削除日時|deleted_at|timestamp||||NULL|論理削除|
|Version|version|integer|||〇|1|楽観ロック|

---

## インデックス

PK_company_setting

IDX_company_setting_tenant

---

## 外部キー

tenant_id

↓

tenant.id

---

## UNIQUE制約

tenant_id

（1会社1設定）

---

## CHECK制約

default_tax_rate >=0

---

## 業務ルール

- 会社設定は必ず1件存在する
- 削除不可
- 初回登録時に自動生成

---

## Django Model実装方針

OneToOneField(Tenant)

---

## 将来拡張

- ダークモード
- PDFテンプレート
- メール署名
- 電子印影
- AI設定

---

# 11.3 role

## テーブル概要

RBAC（Role Based Access Control）のロールを管理する。

---

## 業務概要

利用者へ付与する権限グループを定義する。

---

## テーブル定義

|項目|内容|
|------|------|
|物理名|role|
|論理名|ロール|

---

## カラム一覧

|論理名|物理名|型|PK|FK|NN|Default|説明|
|------|------|------|---|---|---|------|------|
|ロールID|id|UUID|〇||||ロールID|
|会社ID|tenant_id|UUID||〇|〇||所属会社|
|ロール名|role_name|varchar(100)|||〇||表示名|
|ロールコード|role_code|varchar(50)|||〇||システム内部コード|
|説明|description|text||||NULL|ロール説明|
|システムロール|is_system|boolean|||〇|false|システム固定ロール|
|作成者|created_by|UUID||〇|||作成者|
|更新者|updated_by|UUID||〇|||更新者|
|作成日時|created_at|timestamp|||〇|CURRENT_TIMESTAMP|作成日時|
|更新日時|updated_at|timestamp|||〇|CURRENT_TIMESTAMP|更新日時|
|削除日時|deleted_at|timestamp||||NULL|論理削除|
|Version|version|integer|||〇|1|楽観ロック|

---

## インデックス

PK_role

IDX_role_tenant

IDX_role_code

---

## 外部キー

tenant_id

↓

tenant.id

---

## UNIQUE制約

tenant_id + role_code

---

## CHECK制約

なし

---

## 業務ルール

- システムロールは削除不可
- ロールコードは会社内で一意
- ロール削除時は利用者への割当を解除してから削除する

---

## Django Model実装方針

ManyToManyでPermissionと関連付ける。

---

## 将来拡張

- ロールテンプレート
- 権限コピー
- 権限エクスポート
- 権限インポート

---

# 11.4 permission

## テーブル概要

システムで利用する操作権限を管理する。

RBAC（Role Based Access Control）の権限マスタとして利用する。

---

## 業務概要

ロールへ割り当てる操作権限を管理する。

例

- 社員閲覧
- 社員登録
- 社員編集
- 請求書承認
- 経費承認

---

## テーブル定義

|項目|内容|
|------|------|
|物理名|permission|
|論理名|権限|

---

## カラム一覧

|論理名|物理名|型|PK|FK|NN|Default|説明|
|------|------|------|---|---|---|------|------|
|権限ID|id|UUID|〇||||権限ID|
|会社ID|tenant_id|UUID||〇|〇||所属会社|
|権限コード|permission_code|varchar(100)|||〇||システム内部コード|
|権限名|permission_name|varchar(200)|||〇||画面表示名称|
|対象機能|module_name|varchar(100)|||〇||対象モジュール|
|説明|description|text||||NULL|権限説明|
|システム権限|is_system|boolean|||〇|false|システム固定権限|
|作成者|created_by|UUID||〇|||作成ユーザー|
|更新者|updated_by|UUID||〇|||更新ユーザー|
|作成日時|created_at|timestamp|||〇|CURRENT_TIMESTAMP|作成日時|
|更新日時|updated_at|timestamp|||〇|CURRENT_TIMESTAMP|更新日時|
|削除日時|deleted_at|timestamp||||NULL|論理削除日時|
|Version|version|integer|||〇|1|楽観ロック用|

---

## インデックス

- PK_permission
- IDX_permission_tenant
- IDX_permission_code
- IDX_permission_module

---

## 外部キー

tenant_id → tenant.id

---

## UNIQUE制約

- tenant_id + permission_code

---

## CHECK制約

なし

---

## 業務ルール

- システム権限は削除不可
- 権限コードは会社内で一意
- 権限はロールを通してユーザーへ付与する

---

## サンプルデータ

|permission_code|permission_name|
|---------------|---------------|
|employee.view|社員閲覧|
|employee.create|社員登録|
|employee.update|社員更新|
|employee.delete|社員削除|
|expense.approve|経費承認|
|invoice.issue|請求書発行|

---

## ER図（部分）

```
Permission

↑

RolePermission

↓

Role
```

---

## Django Model実装方針

RoleとはManyToMany。

---

## 将来拡張

- Resource管理
- Action管理
- API Scope

---

# 11.5 role_permission

## テーブル概要

ロールと権限の関連を管理する中間テーブル。

---

## 業務概要

1つのロールに複数権限を付与する。

---

## テーブル定義

|項目|内容|
|------|------|
|物理名|role_permission|
|論理名|ロール権限|

---

## カラム一覧

|論理名|物理名|型|PK|FK|NN|Default|説明|
|------|------|------|---|---|---|------|------|
|ID|id|UUID|〇||||主キー|
|会社ID|tenant_id|UUID||〇|〇||所属会社|
|ロールID|role_id|UUID||〇|〇||対象ロール|
|権限ID|permission_id|UUID||〇|〇||対象権限|
|作成者|created_by|UUID||〇|||作成ユーザー|
|更新者|updated_by|UUID||〇|||更新ユーザー|
|作成日時|created_at|timestamp|||〇|CURRENT_TIMESTAMP|作成日時|
|更新日時|updated_at|timestamp|||〇|CURRENT_TIMESTAMP|更新日時|
|削除日時|deleted_at|timestamp||||NULL|論理削除日時|
|Version|version|integer|||〇|1|楽観ロック用|

---

## インデックス

- PK_role_permission
- IDX_role_permission_role
- IDX_role_permission_permission

---

## 外部キー

- tenant_id → tenant.id
- role_id → role.id
- permission_id → permission.id

---

## UNIQUE制約

- role_id + permission_id

---

## CHECK制約

なし

---

## 業務ルール

- 同一権限の重複登録は禁止
- ロール削除時は論理削除する
- 権限削除前に関連データを解除する

---

## サンプルデータ

|Role|Permission|
|------|-----------|
|CompanyAdmin|employee.view|
|CompanyAdmin|employee.create|
|CompanyAdmin|expense.approve|

---

## ER図

```
Role

↓

RolePermission

↓

Permission
```

---

## Django Model実装方針

throughテーブルとして利用する。

---

## 将来拡張

権限有効期限

---

# 11.6 user_role

## テーブル概要

ユーザーへロールを割り当てる中間テーブル。

---

## 業務概要

ユーザーは複数ロールを持つことができる。

---

## テーブル定義

|項目|内容|
|------|------|
|物理名|user_role|
|論理名|ユーザーロール|

---

## カラム一覧

|論理名|物理名|型|PK|FK|NN|Default|説明|
|------|------|------|---|---|---|------|------|
|ID|id|UUID|〇||||主キー|
|会社ID|tenant_id|UUID||〇|〇||所属会社|
|ユーザーID|user_id|UUID||〇|〇||対象ユーザー|
|ロールID|role_id|UUID||〇|〇||割当ロール|
|有効開始日|effective_from|date||||NULL|適用開始日|
|有効終了日|effective_to|date||||NULL|適用終了日|
|作成者|created_by|UUID||〇|||作成ユーザー|
|更新者|updated_by|UUID||〇|||更新ユーザー|
|作成日時|created_at|timestamp|||〇|CURRENT_TIMESTAMP|作成日時|
|更新日時|updated_at|timestamp|||〇|CURRENT_TIMESTAMP|更新日時|
|削除日時|deleted_at|timestamp||||NULL|論理削除日時|
|Version|version|integer|||〇|1|楽観ロック用|

---

## インデックス

- PK_user_role
- IDX_user_role_user
- IDX_user_role_role

---

## 外部キー

- tenant_id → tenant.id
- user_id → auth_user.id
- role_id → role.id

---

## UNIQUE制約

- user_id + role_id

---

## CHECK制約

effective_to >= effective_from

---

## 業務ルール

- ユーザーは複数ロールを持てる
- 有効期限切れロールは認可対象外
- システム管理者ロールは削除不可

---

## サンプルデータ

|User|Role|
|----|----|
|admin@example.com|SuperAdmin|
|manager@example.com|CompanyAdmin|
|employee@example.com|Employee|

---

## ER図

```
auth_user

↓

UserRole

↓

Role

↓

RolePermission

↓

Permission
```

---

## Django Model実装方針

ManyToMany(User, Role) の through モデルとして実装する。

---

## 将来拡張

- 組織別ロール
- 一時ロール
- 承認者ロール
- プロジェクト単位ロール

---

<!-- # Part3 -->

# 12. テーブル詳細

# 12.1 user

## テーブル概要

システムへログインするユーザーアカウントを管理する。

本テーブルは Django の `AbstractUser` を継承したカスタムユーザーモデルとして実装する。

社員（employee）とは分離して管理し、社員以外の管理者アカウントにも対応する。

---

## 業務概要

- ログイン認証
- パスワード管理
- メール認証
- MFA（将来）
- ログイン状態管理

---

## テーブル定義

|項目|内容|
|------|------|
|物理名|user|
|論理名|ユーザー|
|親テーブル|tenant|

---

## カラム一覧

|論理名|物理名|型|PK|FK|NN|Default|説明|
|------|------|------|---|---|---|------|------|
|ユーザーID|id|UUID|〇||||ユーザーID|
|会社ID|tenant_id|UUID||〇|〇||所属会社|
|ユーザー名|username|varchar(150)|||〇||ログインID|
|メールアドレス|email|varchar(255)|||〇||ログインメール|
|パスワード|password|varchar(255)|||〇||ハッシュ化済パスワード|
|姓|last_name|varchar(100)|||||姓|
|名|first_name|varchar(100)|||||名|
|有効|is_active|boolean|||〇|true|利用可能|
|スタッフ|is_staff|boolean|||〇|false|管理画面利用|
|管理者|is_superuser|boolean|||〇|false|システム管理者|
|最終ログイン|last_login|timestamp||||NULL|最終ログイン日時|
|作成日時|created_at|timestamp|||〇|CURRENT_TIMESTAMP|作成日時|
|更新日時|updated_at|timestamp|||〇|CURRENT_TIMESTAMP|更新日時|
|削除日時|deleted_at|timestamp||||NULL|論理削除|
|Version|version|integer|||〇|1|楽観ロック|

---

## インデックス

- PK_user
- IDX_user_username
- IDX_user_email

---

## UNIQUE制約

- username
- email

---

## 業務ルール

- メールアドレスはログインIDとして利用可能
- パスワードは暗号化保存
- 削除ではなく無効化を推奨

---

## Django実装方針

AbstractUser 継承

UUID PrimaryKey

Custom User Model

---

## 将来拡張

- Google Login
- Microsoft Login
- MFA
- Passkey
- OAuth2

---

# 12.2 department

## テーブル概要

会社内の組織（部署）を管理する。

---

## 業務概要

- 部署管理
- 社員所属先
- 組織管理

---

## テーブル定義

|項目|内容|
|------|------|
|物理名|department|
|論理名|部署|

---

## カラム一覧

|論理名|物理名|型|PK|FK|NN|Default|説明|
|------|------|------|---|---|---|------|------|
|部署ID|id|UUID|〇||||部署ID|
|会社ID|tenant_id|UUID||〇|〇||所属会社|
|部署コード|department_code|varchar(20)|||〇||部署コード|
|部署名|department_name|varchar(100)|||〇||部署名|
|親部署ID|parent_department_id|UUID||〇|||親部署|
|表示順|display_order|integer|||〇|1|表示順|
|有効|is_active|boolean|||〇|true|有効フラグ|
|作成者|created_by|UUID||〇|||作成者|
|更新者|updated_by|UUID||〇|||更新者|
|作成日時|created_at|timestamp|||〇|CURRENT_TIMESTAMP|作成日時|
|更新日時|updated_at|timestamp|||〇|CURRENT_TIMESTAMP|更新日時|
|削除日時|deleted_at|timestamp||||NULL|論理削除|
|Version|version|integer|||〇|1|楽観ロック|

---

## インデックス

- IDX_department_code
- IDX_department_parent

---

## 外部キー

tenant

department（自己参照）

---

## UNIQUE制約

tenant_id

+

department_code

---

## 業務ルール

- 部署コードは会社内一意
- 階層構造対応
- 最大10階層程度

---

## Django実装方針

Self ForeignKey

---

## 将来拡張

- 組織図
- 部署責任者
- コストセンター

---

# 12.3 employee

## テーブル概要

社員情報を管理する。

ログインアカウントとは分離し、Userとは1対1または未紐付けとする。

---

## 業務概要

- 社員情報
- 経費申請
- 交通費
- 承認対象

---

## テーブル定義

|項目|内容|
|------|------|
|物理名|employee|
|論理名|社員|

---

## カラム一覧

|論理名|物理名|型|PK|FK|NN|Default|説明|
|------|------|------|---|---|---|------|------|
|社員ID|id|UUID|〇||||社員ID|
|会社ID|tenant_id|UUID||〇|〇||所属会社|
|ユーザーID|user_id|UUID||〇|||ログインユーザー|
|部署ID|department_id|UUID||〇|||所属部署|
|社員番号|employee_no|varchar(30)|||〇||社員番号|
|姓|last_name|varchar(100)|||〇||姓|
|名|first_name|varchar(100)|||〇||名|
|メール|email|varchar(255)|||||業務メール|
|電話番号|phone|varchar(30)|||||電話番号|
|入社日|hire_date|date||||NULL|入社日|
|退職日|retirement_date|date||||NULL|退職日|
|役職|position|varchar(100)|||||役職|
|雇用区分|employment_type|varchar(30)|||〇|FULL_TIME|雇用区分|
|状態|status|varchar(30)|||〇|ACTIVE|在籍状態|
|作成者|created_by|UUID||〇|||作成者|
|更新者|updated_by|UUID||〇|||更新者|
|作成日時|created_at|timestamp|||〇|CURRENT_TIMESTAMP|作成日時|
|更新日時|updated_at|timestamp|||〇|CURRENT_TIMESTAMP|更新日時|
|削除日時|deleted_at|timestamp||||NULL|論理削除|
|Version|version|integer|||〇|1|楽観ロック|

---

## インデックス

- IDX_employee_no
- IDX_employee_department
- IDX_employee_status

---

## 外部キー

tenant

department

user

---

## UNIQUE制約

tenant_id

+

employee_no

---

## 業務ルール

- 社員番号は会社内で一意
- EmployeeはUserが無くても登録可能
- UserはEmployeeを持たない場合がある
- 退職社員は論理削除しない

---

## Django実装方針

Employee

↓

OneToOne(User)

Department

↓

ForeignKey

---

## 将来拡張

- 顔写真
- 緊急連絡先
- マイナンバー管理（暗号化）
- 資格情報
- スキル管理

---

<!-- # Part4 -->

# 13. テーブル詳細

# 13.1 customer

## テーブル概要

取引先（顧客）情報を管理する。

請求書・案件・売上管理の基礎となるマスタテーブルである。

---

## 業務概要

- 顧客管理
- 請求先管理
- 案件管理
- 売上管理

---

## テーブル定義

|項目|内容|
|------|------|
|物理名|customer|
|論理名|取引先|

---

## カラム一覧

|論理名|物理名|型|PK|FK|NN|Default|説明|
|------|------|------|---|---|---|------|------|
|取引先ID|id|UUID|〇||||取引先を一意に識別するID|
|会社ID|tenant_id|UUID||〇|〇||所属会社|
|取引先コード|customer_code|varchar(30)|||〇||会社内で一意の顧客コード|
|取引先名|customer_name|varchar(200)|||〇||正式名称|
|取引先名（カナ）|customer_name_kana|varchar(200)|||||カタカナ名称|
|担当者名|contact_name|varchar(100)|||||取引先担当者名|
|メールアドレス|email|varchar(255)|||||担当者メールアドレス|
|電話番号|phone|varchar(30)|||||代表電話番号|
|郵便番号|postal_code|varchar(20)|||||郵便番号|
|住所|address|text|||||所在地|
|適格請求書番号|invoice_number|varchar(30)|||||インボイス登録番号|
|支払条件|payment_terms|varchar(100)||||月末締め翌月末払いなど|
|取引状態|status_code|varchar(30)|||〇|ACTIVE|取引状態コード|
|備考|remarks|text|||||備考|
|作成者|created_by|UUID||〇|||作成ユーザー|
|更新者|updated_by|UUID||〇|||更新ユーザー|
|作成日時|created_at|timestamp|||〇|CURRENT_TIMESTAMP|作成日時|
|更新日時|updated_at|timestamp|||〇|CURRENT_TIMESTAMP|更新日時|
|削除日時|deleted_at|timestamp||||NULL|論理削除日時|
|Version|version|integer|||〇|1|楽観ロック用|

---

## インデックス

- PK_customer
- IDX_customer_code
- IDX_customer_name
- IDX_customer_status
- IDX_customer_email

---

## 外部キー

- tenant_id → tenant.id

---

## UNIQUE制約

- tenant_id + customer_code

---

## CHECK制約

なし

---

## 業務ルール

- 取引先コードは会社内で一意とする
- 削除は論理削除のみとする
- 取引停止中の取引先は新規案件を登録できない
- インボイス番号は登録時に形式チェックを行う

---

## サンプルデータ

|customer_code|customer_name|
|--------------|-------------|
|C0001|株式会社ABC|
|C0002|合同会社XYZ|

---

## ER図

```
Tenant
   │
   ▼
Customer
```

---

## Django Model実装方針

- UUIDPrimaryKey
- TenantMixin継承
- SoftDeleteMixin継承
- CustomerCodeは会社単位で一意

---

## 将来拡張

- 与信限度額
- 請求先住所（複数）
- 担当営業
- API連携ID
- 電子請求設定

---

# 13.2 project

## テーブル概要

顧客との契約案件を管理する。

請求書・経費・工数・売上の基準となる業務テーブルである。

---

## 業務概要

- 案件管理
- 契約金額管理
- 売上予定管理
- 請求対象管理

---

## テーブル定義

|項目|内容|
|------|------|
|物理名|project|
|論理名|案件|

---

## カラム一覧

|論理名|物理名|型|PK|FK|NN|Default|説明|
|------|------|------|---|---|---|------|------|
|案件ID|id|UUID|〇||||案件ID|
|会社ID|tenant_id|UUID||〇|〇||所属会社|
|取引先ID|customer_id|UUID||〇|〇||対象取引先|
|案件コード|project_code|varchar(30)|||〇||案件コード|
|案件名|project_name|varchar(200)|||〇||案件名|
|案件略称|project_short_name|varchar(100)|||||略称|
|契約番号|contract_no|varchar(50)|||||契約番号|
|開始日|start_date|date|||||案件開始日|
|終了日|end_date|date|||||案件終了日|
|契約金額|contract_amount|numeric(18,2)||||0|契約金額（税込または税抜は設定に従う）|
|売上予定額|planned_sales_amount|numeric(18,2)||||0|売上予定金額|
|案件状態|status_code|varchar(30)|||〇|ACTIVE|案件状態コード|
|案件概要|description|text|||||案件概要|
|作成者|created_by|UUID||〇|||作成ユーザー|
|更新者|updated_by|UUID||〇|||更新ユーザー|
|作成日時|created_at|timestamp|||〇|CURRENT_TIMESTAMP|作成日時|
|更新日時|updated_at|timestamp|||〇|CURRENT_TIMESTAMP|更新日時|
|削除日時|deleted_at|timestamp||||NULL|論理削除日時|
|Version|version|integer|||〇|1|楽観ロック用|

---

## インデックス

- PK_project
- IDX_project_code
- IDX_project_customer
- IDX_project_status
- IDX_project_start_date

---

## 外部キー

- tenant_id → tenant.id
- customer_id → customer.id

---

## UNIQUE制約

- tenant_id + project_code

---

## CHECK制約

- contract_amount >= 0
- planned_sales_amount >= 0
- end_date >= start_date

---

## 業務ルール

- 案件コードは会社内で一意
- 案件終了後も履歴として保持する
- 契約金額は0円以上
- 取引停止中の顧客には案件を登録できない

---

## サンプルデータ

|project_code|project_name|
|-------------|------------|
|P0001|2026年度システム開発|
|P0002|クラウド移行支援|

---

## ER図

```
Customer
    │
    ▼
 Project
```

---

## Django Model実装方針

- CustomerへのForeignKey
- DecimalField(max_digits=18, decimal_places=2)
- ProjectCodeは会社単位で一意
- 将来は工数管理・請求管理・経費管理と関連付ける

---

## 将来拡張

- プロジェクトマネージャー
- メンバー管理
- 予算管理
- 工数管理
- ガントチャート
- WBS
- 契約書添付

---

<!-- # Part5 -->

# 14. テーブル詳細

# 14.1 expense_category

## テーブル概要

経費申請で利用する経費分類マスタを管理する。

会社ごとに自由に分類を追加・変更できる。

---

## 業務概要

- 経費分類管理
- 税率初期値設定
- 領収書必須設定
- 勘定科目連携（将来）

---

## テーブル定義

|項目|内容|
|------|------|
|物理名|expense_category|
|論理名|経費分類|

---

## カラム一覧

|論理名|物理名|型|PK|FK|NN|Default|説明|
|------|------|------|---|---|---|------|------|
|経費分類ID|id|UUID|〇||||経費分類ID|
|会社ID|tenant_id|UUID||〇|〇||所属会社|
|分類コード|category_code|varchar(30)|||〇||経費分類コード|
|分類名|category_name|varchar(100)|||〇||経費分類名称|
|標準税率|default_tax_rate|numeric(5,2)|||〇|10.00|初期税率|
|領収書必須|require_receipt|boolean|||〇|true|領収書添付必須フラグ|
|表示順|display_order|integer|||〇|1|画面表示順|
|有効|is_active|boolean|||〇|true|利用可否|
|作成者|created_by|UUID||〇|||作成ユーザー|
|更新者|updated_by|UUID||〇|||更新ユーザー|
|作成日時|created_at|timestamp|||〇|CURRENT_TIMESTAMP|作成日時|
|更新日時|updated_at|timestamp|||〇|CURRENT_TIMESTAMP|更新日時|
|削除日時|deleted_at|timestamp||||NULL|論理削除日時|
|Version|version|integer|||〇|1|楽観ロック|

### インデックス

- PK_expense_category
- IDX_expense_category_code
- IDX_expense_category_active

### 外部キー

- tenant_id → tenant.id

### UNIQUE制約

- tenant_id + category_code

### 業務ルール

- 分類コードは会社内で一意
- システム初期分類は削除不可
- 無効化された分類は新規申請で選択不可

### サンプルデータ

|category_code|category_name|
|--------------|-------------|
|TRAVEL|交通費|
|MEAL|会議費|
|OFFICE|消耗品費|
|BOOK|書籍費|

### Django Model実装方針

- UUID Primary Key
- DecimalField(max_digits=5, decimal_places=2)

---

# 14.2 expense

## テーブル概要

社員が申請する経費情報を管理する。

---

## 業務概要

- 経費申請
- 承認対象
- 原価集計
- プロジェクト別集計

---

## テーブル定義

|項目|内容|
|------|------|
|物理名|expense|
|論理名|経費申請|

---

## カラム一覧

|論理名|物理名|型|PK|FK|NN|Default|説明|
|------|------|------|---|---|---|------|------|
|経費ID|id|UUID|〇||||経費ID|
|会社ID|tenant_id|UUID||〇|〇||所属会社|
|社員ID|employee_id|UUID||〇|〇||申請者|
|案件ID|project_id|UUID||〇|||関連案件|
|経費分類ID|expense_category_id|UUID||〇|〇||経費分類|
|申請番号|expense_no|varchar(30)|||〇||経費申請番号|
|利用日|expense_date|date|||〇||利用日|
|金額|amount|numeric(18,2)|||〇|0|税込金額|
|税率|tax_rate|numeric(5,2)|||〇|10.00|適用税率|
|通貨コード|currency_code|varchar(10)|||〇|JPY|通貨|
|為替レート|exchange_rate|numeric(18,6)||||1|為替レート|
|内容|description|text|||||利用内容|
|領収書必須|receipt_required|boolean|||〇|true|領収書必須|
|領収書添付済|receipt_uploaded|boolean|||〇|false|添付状況|
|申請状態|status_code|varchar(30)|||〇|DRAFT|申請状態|
|作成者|created_by|UUID||〇|||作成ユーザー|
|更新者|updated_by|UUID||〇|||更新ユーザー|
|作成日時|created_at|timestamp|||〇|CURRENT_TIMESTAMP|作成日時|
|更新日時|updated_at|timestamp|||〇|CURRENT_TIMESTAMP|更新日時|
|削除日時|deleted_at|timestamp||||NULL|論理削除日時|
|Version|version|integer|||〇|1|楽観ロック|

### インデックス

- IDX_expense_employee
- IDX_expense_project
- IDX_expense_date
- IDX_expense_status
- IDX_expense_no

### 外部キー

- tenant_id → tenant.id
- employee_id → employee.id
- project_id → project.id
- expense_category_id → expense_category.id

### UNIQUE制約

- tenant_id + expense_no

### CHECK制約

- amount >= 0
- exchange_rate > 0

### 業務ルール

- 申請番号は会社内で一意
- 承認済みは編集不可
- 却下時のみ再申請可能
- 領収書必須分類は添付必須

---

# 14.3 travel_expense

## テーブル概要

交通費申請を管理する。

経費申請とは分離し、交通費特有の情報を保持する。

---

## カラム一覧

|論理名|物理名|型|説明|
|------|------|------|------|
|交通費ID|id|UUID|主キー|
|会社ID|tenant_id|UUID|所属会社|
|社員ID|employee_id|UUID|申請者|
|案件ID|project_id|UUID|関連案件|
|利用日|travel_date|date|利用日|
|出発地|from_location|varchar(200)|出発地|
|到着地|to_location|varchar(200)|到着地|
|交通手段|transport_type|varchar(30)|JR・地下鉄・バス等|
|片道/往復|trip_type|varchar(20)|ONE_WAY / ROUND_TRIP|
|金額|amount|numeric(18,2)|交通費|
|備考|remarks|text|備考|
|申請状態|status_code|varchar(30)|申請状態|
|作成日時|created_at|timestamp|作成日時|
|更新日時|updated_at|timestamp|更新日時|

### 業務ルール

- 金額は0円以上
- 往復の場合は金額を往復合計とする
- プロジェクト未指定でも申請可能

---

# 14.4 approval_request

## テーブル概要

各種申請の承認依頼を管理する。

経費・交通費・請求書など共通の承認エンジンとして利用する。

---

## カラム一覧

|論理名|物理名|型|説明|
|------|------|------|------|
|承認依頼ID|id|UUID|主キー|
|会社ID|tenant_id|UUID|所属会社|
|対象種別|approval_type|varchar(30)|EXPENSE / TRAVEL / INVOICE|
|対象ID|target_id|UUID|対象レコードID|
|申請者|requester_id|UUID|申請者|
|現在承認者|current_approver_id|UUID|現在の承認者|
|承認状態|status_code|varchar(30)|PENDING / APPROVED / REJECTED|
|申請日時|requested_at|timestamp|申請日時|
|完了日時|completed_at|timestamp|承認完了日時|
|Version|version|integer|楽観ロック|

### インデックス

- IDX_approval_target
- IDX_approval_status
- IDX_approval_requester

### 業務ルール

- 1つの申請に対して承認依頼は1件
- 承認完了後は履歴のみ保持
- 承認履歴は approval_history で管理する

### 将来拡張

- 多段階承認
- 条件分岐承認
- 金額による承認ルート変更
- 代理承認
- 承認期限

---

<!-- # Part6 -->

# 15. テーブル詳細

# 15.1 approval_history

## テーブル概要

承認処理の履歴を管理する。

すべての承認操作を監査目的で保存する。

---

## 業務概要

- 承認履歴
- 差戻し履歴
- コメント保存
- 監査証跡

---

## カラム一覧

|論理名|物理名|型|説明|
|------|------|------|------|
|履歴ID|id|UUID|主キー|
|会社ID|tenant_id|UUID|所属会社|
|承認依頼ID|approval_request_id|UUID|承認依頼|
|承認者|approver_id|UUID|承認実施者|
|承認結果|result_code|varchar(30)|APPROVED / REJECTED|
|コメント|comment|text|承認コメント|
|承認日時|approved_at|timestamp|承認日時|
|作成日時|created_at|timestamp|作成日時|
|Version|version|integer|楽観ロック|

### 外部キー

approval_request

employee

---

### 業務ルール

履歴は更新不可

削除不可

---

# 15.2 invoice

## テーブル概要

請求書ヘッダー情報。

---

## 業務概要

顧客への請求管理。

---

## カラム一覧

|論理名|物理名|型|説明|
|------|------|------|------|
|請求書ID|id|UUID|主キー|
|会社ID|tenant_id|UUID|所属会社|
|請求書番号|invoice_no|varchar(30)|請求番号|
|取引先ID|customer_id|UUID|請求先|
|案件ID|project_id|UUID|対象案件|
|発行日|issue_date|date|請求日|
|支払期限|due_date|date|支払期限|
|請求期間開始日|billing_start_date|date|請求対象開始|
|請求期間終了日|billing_end_date|date|請求対象終了|
|税抜金額|subtotal|numeric(18,2)|税抜|
|消費税額|tax_amount|numeric(18,2)|消費税|
|税込金額|total_amount|numeric(18,2)|請求総額|
|入金済金額|paid_amount|numeric(18,2)|入金済|
|未入金金額|balance_amount|numeric(18,2)|残額|
|通貨|currency_code|varchar(10)|JPY|
|状態|status_code|varchar(30)|請求状態|
|備考|remarks|text|備考|
|Version|version|integer|楽観ロック|

---

### 業務ルール

請求書番号は会社内一意

削除ではなく取消

金額はマイナス不可

---

# 15.3 invoice_item

## テーブル概要

請求書明細。

---

## カラム一覧

|論理名|物理名|型|説明|
|------|------|------|------|
|明細ID|id|UUID|主キー|
|請求書ID|invoice_id|UUID|親請求書|
|行番号|line_no|integer|表示順|
|品目|item_name|varchar(200)|請求内容|
|数量|quantity|numeric(18,2)|数量|
|単価|unit_price|numeric(18,2)|単価|
|金額|amount|numeric(18,2)|金額|
|税率|tax_rate|numeric(5,2)|税率|
|備考|remarks|text|備考|

---

### 業務ルール

line_no

1

2

3

順で管理

---

# 15.4 attachment

## テーブル概要

添付ファイル管理。

Amazon S3保存。

---

## カラム一覧

|論理名|物理名|型|説明|
|------|------|------|------|
|添付ID|id|UUID|主キー|
|会社ID|tenant_id|UUID|所属会社|
|対象種別|entity_type|varchar(50)|EXPENSE等|
|対象ID|entity_id|UUID|対象UUID|
|ファイル名|file_name|varchar(255)|表示名|
|S3キー|s3_key|varchar(500)|S3保存先|
|MIMEタイプ|content_type|varchar(100)|ContentType|
|サイズ|file_size|bigint|Byte|
|アップロード日時|uploaded_at|timestamp|登録日時|

---

### 業務ルール

S3削除と同期

論理削除

---

# 15.5 payment

## テーブル概要

入金管理。

---

## 業務概要

請求書への入金を管理する。

部分入金にも対応する。

---

## カラム一覧

|論理名|物理名|型|説明|
|------|------|------|------|
|入金ID|id|UUID|主キー|
|会社ID|tenant_id|UUID|所属会社|
|請求書ID|invoice_id|UUID|対象請求書|
|入金日|payment_date|date|入金日|
|入金額|amount|numeric(18,2)|入金額|
|入金方法|payment_method|varchar(30)|銀行振込等|
|参照番号|reference_no|varchar(100)|振込番号|
|状態|status_code|varchar(30)|CONFIRMED等|
|備考|remarks|text|備考|

---

### 業務ルール

部分入金可

複数回入金可

請求書残高自動更新

---

<!-- # Part7 -->

# 16. Platform Domain

本ドメインでは、システム全体を支える共通基盤機能を管理する。

対象機能

- 通知
- 操作監査
- ログイン履歴

---

# 16.1 notification

## テーブル概要

システム通知を管理する。

各ユーザーへの通知、システムメッセージ、承認依頼通知などを保持する。

---

## 業務概要

- 承認依頼通知
- システム通知
- お知らせ
- メール通知履歴（将来）

---

## テーブル定義

|項目|内容|
|------|------|
|物理名|notification|
|論理名|通知|

---

## カラム一覧

|論理名|物理名|型|PK|FK|NN|Default|説明|
|------|------|------|---|---|---|------|------|
|通知ID|id|UUID|〇||||通知ID|
|会社ID|tenant_id|UUID||〇|〇||所属会社|
|受信ユーザーID|user_id|UUID||〇|〇||通知対象ユーザー|
|通知種別|notification_type|varchar(30)|||〇||SYSTEM・APPROVAL・INVOICE 等|
|タイトル|title|varchar(200)|||〇||通知タイトル|
|本文|message|text|||〇||通知本文|
|対象種別|entity_type|varchar(50)|||||対象エンティティ|
|対象ID|entity_id|UUID||〇|||対象レコードID|
|既読フラグ|is_read|boolean|||〇|false|既読状態|
|既読日時|read_at|timestamp||||NULL|既読日時|
|作成日時|created_at|timestamp|||〇|CURRENT_TIMESTAMP|通知作成日時|
|Version|version|integer|||〇|1|楽観ロック|

---

## インデックス

- PK_notification
- IDX_notification_user
- IDX_notification_type
- IDX_notification_read
- IDX_notification_created_at

---

## 外部キー

- tenant_id → tenant.id
- user_id → user.id

---

## UNIQUE制約

なし

---

## CHECK制約

なし

---

## 業務ルール

- 通知は削除せず論理削除とする
- 未読通知件数をダッシュボードへ表示する
- 通知クリック時に対象画面へ遷移する

---

## サンプルデータ

|notification_type|title|
|-----------------|-----|
|APPROVAL|経費申請が承認待ちです|
|SYSTEM|システムメンテナンスのお知らせ|

---

## Django Model実装方針

- UserへのForeignKey
- is_readで未読管理
- 将来はWebSocket通知に対応

---

## 将来拡張

- Push通知
- Slack通知
- Teams通知
- メール通知
- LINE通知

---

# 16.2 audit_log

## テーブル概要

システム内の重要操作を記録する監査ログテーブル。

監査証跡として利用し、更新・削除を禁止する。

---

## 業務概要

- 操作履歴
- セキュリティ監査
- 不正アクセス調査
- システム障害調査

---

## テーブル定義

|項目|内容|
|------|------|
|物理名|audit_log|
|論理名|監査ログ|

---

## カラム一覧

|論理名|物理名|型|PK|FK|NN|Default|説明|
|------|------|------|---|---|---|------|------|
|監査ログID|id|UUID|〇||||監査ログID|
|会社ID|tenant_id|UUID||〇|||所属会社|
|ユーザーID|user_id|UUID||〇|||操作ユーザー|
|操作種別|action|varchar(30)|||〇||CREATE・UPDATE・DELETE・LOGIN 等|
|対象種別|entity_type|varchar(50)|||〇||対象テーブル|
|対象ID|entity_id|UUID|||||対象レコードID|
|変更前データ|before_data|jsonb||||NULL|変更前情報|
|変更後データ|after_data|jsonb||||NULL|変更後情報|
|IPアドレス|ip_address|varchar(45)|||||IPv4 / IPv6|
|UserAgent|user_agent|text|||||ブラウザ情報|
|実行日時|executed_at|timestamp|||〇|CURRENT_TIMESTAMP|操作日時|
|Version|version|integer|||〇|1|楽観ロック|

---

## インデックス

- PK_audit_log
- IDX_audit_log_user
- IDX_audit_log_action
- IDX_audit_log_entity
- IDX_audit_log_executed_at

---

## 外部キー

- tenant_id → tenant.id
- user_id → user.id

---

## UNIQUE制約

なし

---

## CHECK制約

なし

---

## 業務ルール

- 更新・削除は禁止
- 監査ログは自動生成する
- JSON形式で変更前後のデータを保持する
- 監査ログの閲覧はシステム管理者のみ

---

## サンプルデータ

|action|entity_type|
|------|-----------|
|LOGIN|user|
|CREATE|invoice|
|UPDATE|expense|
|DELETE|customer|

---

## Django Model実装方針

- Django Signalsで自動記録
- JSONField(PostgreSQL jsonb)を利用
- MiddlewareでIPアドレスを取得

---

## 将来拡張

- CSV出力
- SIEM連携
- AWS CloudWatch Logs連携
- Amazon OpenSearch連携

---

# 16.3 login_history

## テーブル概要

ユーザーのログイン履歴を管理する。

セキュリティ監査および不正アクセス検知に利用する。

---

## 業務概要

- ログイン履歴
- ログイン失敗履歴
- アカウントロック判定
- 利用状況分析

---

## テーブル定義

|項目|内容|
|------|------|
|物理名|login_history|
|論理名|ログイン履歴|

---

## カラム一覧

|論理名|物理名|型|PK|FK|NN|Default|説明|
|------|------|------|---|---|---|------|------|
|履歴ID|id|UUID|〇||||履歴ID|
|会社ID|tenant_id|UUID||〇|||所属会社|
|ユーザーID|user_id|UUID||〇|||対象ユーザー|
|ログイン結果|login_result|varchar(20)|||〇||SUCCESS・FAILED|
|ログイン日時|login_at|timestamp|||〇|CURRENT_TIMESTAMP|ログイン日時|
|ログアウト日時|logout_at|timestamp||||NULL|ログアウト日時|
|IPアドレス|ip_address|varchar(45)|||||接続元IP|
|UserAgent|user_agent|text|||||ブラウザ情報|
|OS|os_name|varchar(100)|||||OS情報|
|ブラウザ|browser_name|varchar(100)|||||ブラウザ名|
|Version|version|integer|||〇|1|楽観ロック|

---

## インデックス

- PK_login_history
- IDX_login_history_user
- IDX_login_history_login_at
- IDX_login_history_result

---

## 外部キー

- tenant_id → tenant.id
- user_id → user.id

---

## UNIQUE制約

なし

---

## CHECK制約

なし

---

## 業務ルール

- ログイン履歴は削除しない
- ログイン失敗回数を集計できること
- 一定回数以上失敗した場合はアカウントロック対象とする

---

## サンプルデータ

|login_result|
|-------------|
|SUCCESS|
|FAILED|

---

## Django Model実装方針

- Django Authentication Signalsを利用
- MiddlewareでIP・UserAgentを取得
- ログアウト時にlogout_atを更新

---

## 将来拡張

- MFAログ
- デバイス管理
- 異常ログイン検知
- 地理情報分析
- セッション管理

---

<!-- # Part8 -->

# 17. データベース設計標準

本章では、本システムにおけるデータベース設計の共通ルールを定義する。

---

# 17.1 命名規約

## テーブル

- すべて小文字
- スネークケース
- 単数形

例

```
tenant
customer
invoice
expense
payment
```

---

## カラム

すべて

```
snake_case
```

例

```
created_at
updated_at
status_code
tenant_id
invoice_no
```

---

## PK

```
PK_<table>

例

PK_invoice

PK_customer
```

---

## FK

```
FK_<table>_<parent>

例

FK_invoice_customer

FK_project_customer

FK_expense_employee
```

---

## Index

```
IDX_<table>_<column>

例

IDX_invoice_no

IDX_customer_name

IDX_payment_date
```

---

## Unique

```
UK_<table>_<column>

例

UK_customer_code

UK_invoice_no
```

---

# 17.2 データ型標準

|用途|型|
|------|------|
|ID|UUID|
|文字列|varchar|
|長文|text|
|金額|numeric(18,2)|
|税率|numeric(5,2)|
|数量|numeric(18,2)|
|日時|timestamp|
|日付|date|
|真偽値|boolean|
|JSON|jsonb|

---

# 17.3 共通カラム

全テーブルは以下の共通項目を持つ。

|項目|型|
|------|------|
|id|UUID|
|tenant_id|UUID|
|created_by|UUID|
|updated_by|UUID|
|created_at|timestamp|
|updated_at|timestamp|
|deleted_at|timestamp|
|version|integer|

---

## 共通Mixin

Djangoでは以下Mixinを利用する。

```
BaseModel

TenantMixin

TimestampMixin

SoftDeleteMixin
```

---

# 17.4 インデックス設計

基本方針

- PK
- FK
- 検索条件
- ORDER BY
- UNIQUE

に対してIndexを作成する。

不要なIndexは作成しない。

---

# 17.5 外部キー一覧

|子テーブル|親テーブル|
|------|------|
|user|tenant|
|department|tenant|
|employee|department|
|employee|user|
|customer|tenant|
|project|customer|
|expense|employee|
|expense|project|
|invoice|customer|
|invoice|project|
|invoice_item|invoice|
|payment|invoice|
|approval_request|employee|
|approval_history|approval_request|
|attachment|tenant|
|notification|user|

---

# 17.6 インデックス一覧

主要Index

|テーブル|Index|
|------|------|
|customer|customer_code|
|project|project_code|
|employee|employee_no|
|invoice|invoice_no|
|expense|expense_no|
|payment|payment_date|
|notification|user_id|
|audit_log|executed_at|
|login_history|login_at|

---

# 17.7 ER図

```text
Tenant
 │
 ├───────────────┐
 │               │
Customer      Employee
 │               │
 │               ├──Department
 │               │
 │               └──User
 │
Project
 │
 ├──────────┐
 │          │
Expense   Invoice
 │          │
 │          ├──InvoiceItem
 │          └──Payment
 │
ApprovalRequest
 │
ApprovalHistory

Attachment

Notification

AuditLog

LoginHistory
```

---

# 17.8 PostgreSQL実装方針

採用機能

- UUID
- JSONB
- Partial Index
- Transaction
- Foreign Key
- CHECK Constraint

採用しない機能

- Trigger
- Stored Procedure

業務ロジックはDjangoで実装する。

---

# 17.9 Django ORM実装方針

Model構成

```
Abstract BaseModel

↓

TenantMixin

↓

各Model
```

利用機能

- UUIDField
- ForeignKey
- OneToOneField
- ManyToMany
- JSONField
- DecimalField

---

# 17.10 バックアップ方針

## 概要

本システムでは、データ消失および障害発生時の迅速な復旧を目的として、AWS のマネージドサービスを利用したバックアップを実施する。

---

## バックアップ対象

|対象|内容|
|------|------|
|PostgreSQL|業務データベース|
|Amazon S3|添付ファイル|
|Terraform|IaCコード（GitHub管理）|
|GitHub Repository|ソースコード・設計書|

---

## バックアップ方式

|対象|方式|
|------|------|
|PostgreSQL|Amazon RDS 自動バックアップ|
|S3|Versioning + AWS Backup|
|ソースコード|GitHub Repository|
|Terraform State|Amazon S3 + DynamoDB Lock|

---

## バックアップスケジュール

|項目|内容|
|------|------|
|取得頻度|毎日|
|取得時間|深夜帯（業務時間外）|
|保持期間|35日|
|Point In Time Recovery|有効|

---

## 障害復旧方針

- PostgreSQL は Point In Time Recovery を利用して復旧する。
- 添付ファイルは Amazon S3 Versioning により復元する。
- Infrastructure は Terraform により再構築可能とする。

---

## 将来拡張

- クロスリージョンバックアップ
- AWS Backup Vault
- Disaster Recovery（DR）対応

---

# 17.11 データ保持ポリシー

## 概要

各データの保持期間を以下の通り定義する。

---

## 保持期間

|データ|保持期間|備考|
|------|---------|------|
|請求書|7年間|電子帳簿保存法対応|
|経費申請|7年間|会計監査対応|
|入金情報|7年間|会計監査対応|
|添付ファイル|7年間|証憑保管|
|監査ログ|7年間|監査証跡|
|ログイン履歴|1年間|セキュリティ監査|
|通知|1年間|運用管理|

---

## 運用ルール

- 保持期間経過後は管理者による削除対象とする。
- 法令により保持が必要なデータは削除対象外とする。
- 削除対象データは論理削除後に物理削除を実施する。

---

# 17.12 パフォーマンス設計

## 概要

本システムは小規模法人向け SaaS として、100社程度の利用を想定して設計する。

---

## 想定規模

|項目|想定値|
|------|------:|
|契約会社数|100社|
|1社あたりユーザー数|100人|
|経費申請件数|1,000,000件|
|請求書件数|500,000件|

---

## 性能目標

|処理|目標応答時間|
|------|-----------:|
|一覧画面|1秒以内|
|詳細画面|500ms以内|
|登録処理|2秒以内|
|検索処理|2秒以内|

---

## パフォーマンス対策

- 適切なインデックスを作成する。
- `select_related()` を利用し、N+1問題を防止する。
- `prefetch_related()` を利用し、多対多の取得性能を向上させる。
- 一覧画面はページネーション（100件単位）を採用する。
- 将来的に Redis によるキャッシュ機能を導入可能とする。

---

## 将来拡張

- Amazon ElastiCache（Redis）
- Read Replica
- 非同期処理（Celery）
- CDN（Amazon CloudFront）

---

# DB設計完了

総テーブル数

約30テーブル

採用技術

- PostgreSQL
- Django ORM
- UUID
- Multi Tenant
- RBAC
- Soft Delete
- Optimistic Lock
- Amazon S3
- Approval Workflow

以上を本システムのデータベース設計標準とする。