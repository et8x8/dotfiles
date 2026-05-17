# Requirements: 二胡用数字譜 Web アプリ

最終更新: 2026-05-17
関連 ADR: [docs/adr/draft/erhu-numeric-notation-webapp.md](../adr/draft/erhu-numeric-notation-webapp.md)
関連 Design: [docs/design/erhu-numeric-notation-webapp.md](../design/erhu-numeric-notation-webapp.md)
関連 Spec: [docs/spec/erhu-numeric-notation-webapp.md](../spec/erhu-numeric-notation-webapp.md)

## 目的・背景

二胡向け数字譜をブラウザで扱い、個人のクラウド保管下で編集・再生・印刷まで一貫させる。共有や公開は扱わず、拍子整合はユーザー主導で行う（ADR の Context / Decision に準拠）。

## スコープ

- 認証済みユーザーの楽譜 CRUD と JSON 楽譜モデルの永続化
- 数字譜エディタ（MVP: **八分・十六分・三連符・小節線・小節繰り返し**に加え、**装飾音・強弱・コーダ等は ADR / Spec の個別一覧に列挙した種別**をすべて含む。詳細は ADR）
- 簡易再生、印刷用ビューとブラウザ PDF 保存
- 拍子の明示・省略・警告（自動解決なし）
- Cloudflare Workers 統合デプロイ（静的 SPA + Worker API）

## アウトオブスコープ

- 楽譜の共有 URL、public 読み取り、コラボレーション
- 著作権監査・コンテンツモデレーション
- 拍子矛盾の自動補正
- サーバサイド必須 PDF 生成（初期）
- 厳密な二胡物理音源・完全 MIDI 互換

## 機能要件

- F-1. 自分の楽譜のみ一覧・新規・削除（論理削除可）→ [REQ-ERHU-005](../spec/erhu-numeric-notation-webapp.md#req-erhu-005), [REQ-ERHU-006](../spec/erhu-numeric-notation-webapp.md#req-erhu-006), [REQ-ERHU-007](../spec/erhu-numeric-notation-webapp.md#req-erhu-007)
- F-2. 二胡数字譜の入力（小節・小節線・拍子・四分基準の音価・八分・十六分・三連符・休符・八度・小節繰り返し、**装飾音・音楽記号は Spec の個別一覧どおり**）→ [REQ-ERHU-008](../spec/erhu-numeric-notation-webapp.md#req-erhu-008), [REQ-ERHU-020](../spec/erhu-numeric-notation-webapp.md#req-erhu-020), [REQ-ERHU-021](../spec/erhu-numeric-notation-webapp.md#req-erhu-021), [REQ-ERHU-022](../spec/erhu-numeric-notation-webapp.md#req-erhu-022), [REQ-ERHU-012](../spec/erhu-numeric-notation-webapp.md#req-erhu-012), [REQ-ERHU-013](../spec/erhu-numeric-notation-webapp.md#req-erhu-013), [REQ-ERHU-018](../spec/erhu-numeric-notation-webapp.md#req-erhu-018)
- F-3. 転調指定が編集・再生・印刷で一貫 → [REQ-ERHU-009](../spec/erhu-numeric-notation-webapp.md#req-erhu-009)
- F-4. 複数パートの保持と表示オン／オフ・基本レイアウト → [REQ-ERHU-010](../spec/erhu-numeric-notation-webapp.md#req-erhu-010)
- F-5. 任意位置テキスト・画像の配置と永続化 → [REQ-ERHU-011](../spec/erhu-numeric-notation-webapp.md#req-erhu-011)
- F-6. テンポ・拍子に沿う簡易再生 → [REQ-ERHU-012](../spec/erhu-numeric-notation-webapp.md#req-erhu-012)
- F-7. 印刷ビューから小節線・警告背景・フリーレイヤーを含め印刷／PDF 保存 → [REQ-ERHU-013](../spec/erhu-numeric-notation-webapp.md#req-erhu-013)
- F-8. 第1小節は常に拍子表示、以降は有効拍子と小節拍数が一致するときのみ省略 → [REQ-ERHU-014](../spec/erhu-numeric-notation-webapp.md#req-erhu-014), [REQ-ERHU-015](../spec/erhu-numeric-notation-webapp.md#req-erhu-015)
- F-9. 拍子不一致小節の警告表示、自動修正なし → [REQ-ERHU-016](../spec/erhu-numeric-notation-webapp.md#req-erhu-016)
- F-10. 全 API 認証必須・他ユーザー資源へのアクセス拒否 → [REQ-ERHU-002](../spec/erhu-numeric-notation-webapp.md#req-erhu-002), [REQ-ERHU-003](../spec/erhu-numeric-notation-webapp.md#req-erhu-003), [REQ-ERHU-004](../spec/erhu-numeric-notation-webapp.md#req-erhu-004), [REQ-ERHU-019](../spec/erhu-numeric-notation-webapp.md#req-erhu-019)
- F-11. Cloudflare Workers 統合構成へのデプロイ可能 → [REQ-ERHU-001](../spec/erhu-numeric-notation-webapp.md#req-erhu-001)
- F-12. 途中の明示的拍子変更以降の有効拍子更新 → [REQ-ERHU-017](../spec/erhu-numeric-notation-webapp.md#req-erhu-017)
- F-13. 小節拍数算出ルールのクライアント／サーバ一致 → [REQ-ERHU-018](../spec/erhu-numeric-notation-webapp.md#req-erhu-018)

## 非機能要件

- セキュリティ: セッションは httpOnly Cookie、パスワードは Argon2id（ADR の Decision）。
- データ分離: R2 オブジェクトキーは `userId` 配下に限定し、匿名公開 URL を設けない（ADR）。
- 互換性: 楽譜 JSON は `schemaVersion` を含み後方拡張可能（ADR）。
- 運用: 同一 `wrangler` プロジェクトで静的資産と Worker API を配信（ADR）。

## 制約事項

- ADR に記載の技術スタック・境界（React + TS + Vite、Hono、D1、R2、Web Audio、ブラウザ PDF）に従う。

## 前提条件・依存関係

- Cloudflare（Workers 統合環境）アカウントおよび D1 / R2 バインディングが利用可能であること。
- クライアントが Web Audio API と印刷ダイアログをサポートすること（対象ブラウザは実装フェーズで定義）。
