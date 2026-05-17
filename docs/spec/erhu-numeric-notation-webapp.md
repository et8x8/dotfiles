# Spec: 二胡用数字譜 Web アプリ

最終更新: 2026-05-17
関連 ADR: [docs/adr/draft/erhu-numeric-notation-webapp.md](../adr/draft/erhu-numeric-notation-webapp.md)
関連 Requirements: [docs/requirements/erhu-numeric-notation-webapp.md](../requirements/erhu-numeric-notation-webapp.md)
関連 Design: [docs/design/erhu-numeric-notation-webapp.md](../design/erhu-numeric-notation-webapp.md)

## 概要

本仕様は、二胡向け数字譜 Web アプリが満たすべき検証可能な振る舞いを EARS 相当の構造（普遍・イベント駆動・状態駆動・異常系）で日本語により宣言する。根拠は単一 Draft ADR に限定する。**装飾音および音楽記号は総称で省略せず、下記「装飾音の一覧（MVP）」「音楽記号の一覧（MVP）」に列挙した種別を正本とする**（ADR の「MVP: 装飾音の個別対象」「MVP: 音楽記号の個別対象」と同一内容）。

## 装飾音の一覧（MVP）

個別に入力・譜面表示・JSON 保存の対象とする装飾音。拍数への寄与は **本節「装飾音の拍寄与（MVP）」** に従い、REQ-ERHU-018 の共有アルゴリズムで適用する。

- **前倚音**
- **後倚音**
- **波音**
- **逆波音**
- **回音**
- **顫音**（`tr` に相当する揺れ。長さは主音の音価に紐づける）
- **上滑音**・**下滑音**（滑音）
- **打音**

### 装飾音の拍寄与（MVP）

拍数警告（REQ-ERHU-015〜018）に用いる合算において、上記いずれの装飾音種別も **拍へは加算しない（寄与 0）**。小節拍数は四分基準の主音・休符・八分・十六分・**三連符（下記「三連符の拍数（MVP）」）**のみから算出する。

### 三連符の拍数（MVP）

三連符グループは **子音符ちょうど 3 個** を含み、各子音符の基礎音価（付点含む）は等しいものとする。3 子を三連符なしで通常配置した場合の合計拍数を `T` とすると、当該三連符グループが占有する拍数は **`(2/3) * T`** である。MVP では **三連符の入れ子** を許可しない。

## 音楽記号の一覧（MVP）

個別に入力・譜面表示・JSON 保存の対象とする音楽記号・演奏指示。**再生での数値的挙動は本節「再生解釈（MVP・仕様固定）」にのみ従い**、実装側の独自解釈を許さない。

- **強弱記号**: 保存値は **次の 6 語の列挙子のみ** とする（この以外は REQ-ERHU-022 により拒否）: `pp`, `p`, `mp`, `mf`, `f`, `ff`。
- **フェルマータ**（取り止め）
- **コーダ記号**
- **セーニョ（Dal Segno）記号**
- **ファイン（Fine）**
- **ダブルバー**（区画終端。小節線とは別表現でもよい）
- **速度・表情指示**: 自由記述ではなく、下記「許可される速度・表情テキスト（MVP）」に列挙した語のみを保存する（正規化手順は同節に従う）。

### 許可される速度・表情テキスト（MVP）

次の文字列のみを速度・表情指示として保存してよい。照合は **「正規化手順（速度・表情テキスト）」適用後**の文字列と、下記リストの **完全一致**（コードポイント単位）で行う。

- `rit.`
- `ritardando`
- `accel.`
- `accelerando`
- `a tempo`
- `rall.`
- `rallentando`
- `string.`
- `stringendo`
- `dim.`
- `diminuendo`
- `cresc.`
- `crescendo`
- `sostenuto`
- `espressivo`
- `dolce`
- `cantabile`
- `smorz.`
- `morendo`
- `agitato`
- `漸慢`
- `漸快`
- `元の速度`

### 正規化手順（速度・表情テキスト）

1. 文字列両端から、次の文字を繰り返し除去する: U+0020（SPACE）、U+0009（TAB）、U+000A（LF）、U+000D（CR）、U+3000（IDEOGRAPHIC SPACE）。
2. 先頭から末尾まで走査し、連続する ASCII ラテン文字（`A`–`Z`, `a`–`z`）のみを小文字へ変換する（数字・句読点・日本語は変換しない）。
3. 手順 1 を再度適用してから、上記許可リストと照合する。

### 再生解釈（MVP・仕様固定）

Web Audio スケジューリングは次に従う（ゲインは線形振幅倍率。既定の基準ゲインを 1.0 とする）。

- **強弱記号**: 直近の強弱マーカー以降の発音にゲインを適用する。`pp`→0.50、`p`→0.65、`mp`→0.80、`mf`→1.00、`f`→1.25、`ff`→1.55。曲先頭から最初の強弱マーカーまでは `mf` とみなす。
- **フェルマータ**: 付随する音符は譜面音価の **1.5 倍** の持続で発音する（休符に付く場合はその休符を 1.5 倍）。拍数警告用の拍合算（REQ-ERHU-018）には **元の譜面音価のみ** を用い、フェルマータによる伸長は含めない。
- **コーダ記号・セーニョ記号・ファイン（Fine）**: MVP の再生では **小節順をジャンプしない**。保存および印刷は必須。再生では当該イベントを **無視** し、UI に「反復ジャンプは未対応」と表示してよい。
- **ダブルバー**: 再生に影響しない（表示のみ）。
- **速度・表情指示**: `rit.`, `ritardando`, `rall.`, `rallentando`, `smorz.`, `morendo`, `漸慢` が付いた小節の再生中、BPM は **その小節の実時間長にわたり現在値から 85% へ線形減速** する。`accel.`, `agitato`, `漸快` は **115% へ線形加速** する。`a tempo` および `元の速度` は直前に記録した BPM に **即時復帰** する。その他の許可語は **BPM を変更せず**、譜面表示のみに用いる。

### 小節繰り返しの再生（MVP）

繰り返しイベントは **`repeatKind` フィールド**を持ち、その値は **`repeatOneBar` または `repeatTwoBars` のみ** とする。

次の手順に従い論理タイムラインを生成する（REQ-ERHU-012）。

1. `parts[]` 内の繰り返し記号イベントを走査する。
2. 繰り返し種別コードが **`repeatOneBar`** のとき反復対象は **直前の 1 小節全体**、**`repeatTwoBars`** のときは **直前の 2 小節全体** とする。いずれでもない種別の場合は手順 4 に進む。
3. 反復対象小節のイベント列を、**繰り返し記号イベントの直後**に挿入し、当該小節列が **連続して 2 回演奏される** よう単一タイムラインへ連結する（元の小節の 1 回目の演奏はそのまま残す）。
4. 反復対象が定まらない配置では、当該位置の再生を **スキップ**（無音）し、UI に警告を表示する。

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

エディタは、少なくとも MVP 記号集合の範囲において、**小節境界**、**小節線**、第1小節における拍子、四分音符を基準とする音価表現、**八分音符および十六分音符**、**三連符（三連複）**、休符、八度記号、**小節の繰り返し記号**について、二胡用数字譜の作成および編集を可能にしなければならない。

> 根拠: docs/adr/draft/erhu-numeric-notation-webapp.md (Acceptance criteria 2, Decision: 記号・表現)

### REQ-ERHU-020

エディタは、本書「装飾音の一覧（MVP）」に列挙した装飾音種別それぞれについて、個別に入力・譜面表示・楽譜 JSON への保存を可能にしなければならない。

> 根拠: docs/adr/draft/erhu-numeric-notation-webapp.md (Acceptance criteria 2, Decision: MVP: 装飾音の個別対象)

### REQ-ERHU-021

エディタは、本書「音楽記号の一覧（MVP）」に列挙した記号・指示それぞれについて、個別に入力・譜面表示・楽譜 JSON への保存を可能にしなければならない。

### REQ-ERHU-022

楽譜 JSON に強弱を保存する場合、対応する文字列は **`pp`, `p`, `mp`, `mf`, `f`, `ff` のいずれか** でなければならない。速度・表情指示テキストを保存する場合、**「正規化手順（速度・表情テキスト）」**を適用した結果が、**「許可される速度・表情テキスト（MVP）」**のいずれかと **完全一致** しなければならない。いずれかに違反する楽譜ドキュメントを `PUT /api/scores/:id` 等で保存しようとした場合、Worker は **HTTP 400** を返さなければならない。また SPA は同一検証により当該内容の送信を完了させてはならない。

> 根拠: docs/adr/draft/erhu-numeric-notation-webapp.md (Decision: MVP: 音楽記号の個別対象)

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

ユーザーが再生を開始したとき、Web Audio API に基づくシンセサイザは、テンポおよび有効拍子に従い、**八分音符・十六分音符・三連符**の音価を**本書「三連符の拍数（MVP）」**に従って解釈し、**音楽記号**は**本書「再生解釈（MVP・仕様固定）」**に従ってゲイン・BPM・フェルマータ伸長を適用し、**装飾音**は主音の発音スケジュールに重ねて出力する（装飾音の拍寄与は**本書「装飾音の拍寄与（MVP）」**により 0）、**小節繰り返し記号**は**本書「小節繰り返しの再生（MVP）」**に従って論理タイムラインへ展開したうえで発音イベントをスケジューリングし、音程の順序が明瞭に聴取可能でなければならない。

> 根拠: docs/adr/draft/erhu-numeric-notation-webapp.md (Acceptance criteria 6, Decision: 再生)

### REQ-ERHU-013

ユーザーが専用印刷ビューから印刷するか、ブラウザ機能により PDF として保存したとき、描画結果は**小節線**、**小節繰り返し記号**、「装飾音の一覧（MVP）」および「音楽記号の一覧（MVP）」に基づく記号描画、小節の警告用背景、フリーレイヤー要素を含み、かつ ADR においてスコープ内とされるレイアウト破綻を起こしてはならない。

> 根拠: docs/adr/draft/erhu-numeric-notation-webapp.md (Acceptance criteria 7)

### REQ-ERHU-014

エディタは、楽譜の第1小節に常に明示的な拍子記号を表示しなければならない。

> 根拠: docs/adr/draft/erhu-numeric-notation-webapp.md (Acceptance criteria 8, Context, Decision: 拍子)

### REQ-ERHU-015

第1小節以降の小節について、単一共通アルゴリズムにより当該小節の音符・休符、**三連符グループ**、および**「装飾音の一覧（MVP）」の各装飾音**から算出した拍数が、直前までの小節から引き継がれた有効拍子と等しいとき、エディタは当該小節における拍子記号の表示を省略してよい。

> 根拠: docs/adr/draft/erhu-numeric-notation-webapp.md (Acceptance criteria 8, Context)

### REQ-ERHU-016

小節の拍数が有効拍子と等しくないとき、エディタは当該小節を黄色系の警告背景で表示しなければならない。また不一致を解消するため、音符・休符・拍子・**三連符境界**、**「装飾音の一覧（MVP）」に属する装飾イベント**を自動変更してはならない。

> 根拠: docs/adr/draft/erhu-numeric-notation-webapp.md (Acceptance criteria 9, Decision: 拍子矛盾の自動解決禁止)

### REQ-ERHU-017

ユーザーが小節境界に明示的な拍子変更を挿入したとき、当該小節より後続の小節に対する有効拍子は、別の明示的な拍子変更が挿入されるまで、新しい拍子に従わなければならない。

> 根拠: docs/adr/draft/erhu-numeric-notation-webapp.md (Decision: 拍子)

### REQ-ERHU-018

小節の拍数を算出するアルゴリズムは、SPA および Worker の検証パスにおいて同一の結果を生成しなければならない。このアルゴリズムは、当該小節に含まれる**八分音符・十六分音符**および**三連符（本書「三連符の拍数（MVP）」）**、ならびに**装飾音（本書「装飾音の拍寄与（MVP）」により常に 0 拍）**を、四分基準の休符・付点・連桁・タイとあわせて一貫して扱わなければならない。

> 根拠: docs/adr/draft/erhu-numeric-notation-webapp.md (Decision: 拍子, Acceptance criteria 8–9)

### REQ-ERHU-019

HTTP API は、楽譜または R2 に保存されるユーザーメディアオブジェクトに対し、匿名による public read を可能にするエンドポイントを提供してはならない。

> 根拠: docs/adr/draft/erhu-numeric-notation-webapp.md (Decision: 非機能・スコープ境界, 永続化)

## 用語

- **有効拍子**: 第1小節の明示拍子を起点とし、ユーザーが挿入した明示的拍子変更により更新される、各小節を評価する時点での拍子。
- **拍数**: 小節内の音符および休符を、**本書「三連符の拍数（MVP）」**および**「装飾音の拍寄与（MVP）」**に従い拍単位に換算して合計した値。
- **三連符（三連複）**: **本書「三連符の拍数（MVP）」**の式に従い拍を占有する。
- **小節繰り返し記号**: **本書「小節繰り返しの再生（MVP）」**に従い論理タイムラインへ展開する。
- **フリーレイヤー**: 楽譜の主グリッドと座標的に独立し、テキストおよび画像を重ね合わせるためのオーバーレイの集合。
