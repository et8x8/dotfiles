# Spec: 二胡用数字譜 Web アプリ

最終更新: 2026-05-17
関連 ADR: [docs/adr/draft/erhu-numeric-notation-webapp.md](../adr/draft/erhu-numeric-notation-webapp.md)
関連 Requirements: [docs/requirements/erhu-numeric-notation-webapp.md](../requirements/erhu-numeric-notation-webapp.md)
関連 Design: [docs/design/erhu-numeric-notation-webapp.md](../design/erhu-numeric-notation-webapp.md)

## 概要

本仕様は、二胡向け数字譜 Web アプリが満たすべき検証可能な振る舞いを EARS 相当の構造（普遍・イベント駆動・状態駆動・異常系）で日本語により宣言する。根拠は単一 Draft ADR に限定する。

## 要件

### REQ-ERHU-001

二胡用数字譜 Web アプリケーションは、React・TypeScript・Vite による単一ページアプリケーションとして、かつ同一 `wrangler` プロジェクト内で静的資産および API ルートを提供する Cloudflare Workers 上の Hono アプリケーションとして提供されなければならない。

> 根拠: docs/adr/draft/erhu-numeric-notation-webapp.md (Decision: アーキテクチャ概要)

### REQ-ERHU-002

二胡用数字譜 Web アプリケーションは、パスワードハッシュを Argon2id で保存しなければならない。また認証済みリクエストは、httpOnly Cookie が参照するサーバ側セッションに紐づけられなければならない。

> 根拠: docs/adr/draft/erhu-numeric-notation-webapp.md (Decision: 認証)

### REQ-ERHU-003

有効なセッションを伴わずに保護された API ルートが呼び出された場合、Worker は HTTP ステータス 401 を返さなければならず、かつユーザー秘密データをレスポンスに含めてはならない。

> 根拠: docs/adr/draft/erhu-numeric-notation-webapp.md (Acceptance criteria 10, Decision: 非機能・スコープ境界)

### REQ-ERHU-004

認証済みユーザーが、自身が所有しない楽譜またはメディアオブジェクトを識別子により要求した場合、Worker は HTTP ステータス 403 を返さなければならない。

> 根拠: docs/adr/draft/erhu-numeric-notation-webapp.md (Acceptance criteria 10)

### REQ-ERHU-005

認証済みユーザーが楽譜一覧を要求したとき、システムは当該ユーザーが所有する楽譜のみを返さなければならない。

> 根拠: docs/adr/draft/erhu-numeric-notation-webapp.md (Acceptance criteria 1)

### REQ-ERHU-006

認証済みユーザーが新規楽譜を作成したとき、システムは当該ユーザー所有の楽譜レコードおよびバージョン付き JSON ドキュメントを永続化しなければならない。

> 根拠: docs/adr/draft/erhu-numeric-notation-webapp.md (Acceptance criteria 1)

### REQ-ERHU-007

認証済みユーザーが楽譜を削除したとき、システムは以降、当該ユーザーに対する通常の一覧取得および読み込み操作から当該楽譜を除外しなければならない（論理削除でよい）。

> 根拠: docs/adr/draft/erhu-numeric-notation-webapp.md (Acceptance criteria 1)

### REQ-ERHU-008

エディタは、少なくとも MVP 記号集合の範囲において、小節、第1小節における拍子、音符長、休符、八度記号、装飾音を含む二胡用数字譜の作成および編集を可能にしなければならない。

> 根拠: docs/adr/draft/erhu-numeric-notation-webapp.md (Acceptance criteria 2, Decision: 記号・表現)

### REQ-ERHU-009

ユーザーが楽曲全体またはパート単位で転調を適用したとき、編集画面、再生ビュー、印刷ビューは、同一の転調フィールドに基づき音高を解釈しなければならない。

> 根拠: docs/adr/draft/erhu-numeric-notation-webapp.md (Acceptance criteria 3)

### REQ-ERHU-010

楽譜ドキュメントは複数パートを保持しなければならない。また UI はパートごとの表示のオン／オフを可能とし、設計書に記載された既定の横方向および縦方向レイアウト規則に従わなければならない。

> 根拠: docs/adr/draft/erhu-numeric-notation-webapp.md (Acceptance criteria 4)

### REQ-ERHU-011

ユーザーがフリーレイヤー上でテキストボックスまたは画像参照を配置・移動・削除したとき、システムは当該要素を楽譜ドキュメントに永続化し、再読込後に復元しなければならない。

> 根拠: docs/adr/draft/erhu-numeric-notation-webapp.md (Acceptance criteria 5)

### REQ-ERHU-012

ユーザーが再生を開始したとき、Web Audio API に基づくシンセサイザは、テンポおよび有効拍子に従って発音イベントをスケジューリングし、音程の順序が明瞭に聴取可能でなければならない。

> 根拠: docs/adr/draft/erhu-numeric-notation-webapp.md (Acceptance criteria 6, Decision: 再生)

### REQ-ERHU-013

ユーザーが専用印刷ビューから印刷するか、ブラウザ機能により PDF として保存したとき、描画結果は小節線、小節の警告用背景、フリーレイヤー要素を含み、かつ ADR においてスコープ内とされるレイアウト破綻を起こしてはならない。

> 根拠: docs/adr/draft/erhu-numeric-notation-webapp.md (Acceptance criteria 7)

### REQ-ERHU-014

エディタは、楽譜の第1小節に常に明示的な拍子記号を表示しなければならない。

> 根拠: docs/adr/draft/erhu-numeric-notation-webapp.md (Acceptance criteria 8, Context, Decision: 拍子)

### REQ-ERHU-015

第1小節以降の小節について、単一共通アルゴリズムにより当該小節の音符および休符から算出した拍数が、直前までの小節から引き継がれた有効拍子と等しいとき、エディタは当該小節における拍子記号の表示を省略してよい。

> 根拠: docs/adr/draft/erhu-numeric-notation-webapp.md (Acceptance criteria 8, Context)

### REQ-ERHU-016

小節の拍数が有効拍子と等しくないとき、エディタは当該小節を黄色系の警告背景で表示しなければならない。また不一致を解消するため、音符・休符・拍子を自動変更してはならない。

> 根拠: docs/adr/draft/erhu-numeric-notation-webapp.md (Acceptance criteria 9, Decision: 拍子矛盾の自動解決禁止)

### REQ-ERHU-017

ユーザーが小節境界に明示的な拍子変更を挿入したとき、当該小節より後続の小節に対する有効拍子は、別の明示的な拍子変更が挿入されるまで、新しい拍子に従わなければならない。

> 根拠: docs/adr/draft/erhu-numeric-notation-webapp.md (Decision: 拍子)

### REQ-ERHU-018

小節の拍数を算出するアルゴリズムは、SPA および Worker の検証パスにおいて同一の結果を生成しなければならない。

> 根拠: docs/adr/draft/erhu-numeric-notation-webapp.md (Decision: 拍子)

### REQ-ERHU-019

HTTP API は、楽譜または R2 に保存されるユーザーメディアオブジェクトに対し、匿名による public read を可能にするエンドポイントを提供してはならない。

> 根拠: docs/adr/draft/erhu-numeric-notation-webapp.md (Decision: 非機能・スコープ境界, 永続化)

## 用語

- **有効拍子**: 第1小節の明示拍子を起点とし、ユーザーが挿入した明示的拍子変更により更新される、各小節を評価する時点での拍子。
- **拍数**: 小節内の音符および休符を、設計書で固定したルールにより拍単位に換算して合計した値。
- **フリーレイヤー**: 楽譜の主グリッドと座標的に独立し、テキストおよび画像を重ね合わせるためのオーバーレイの集合。
