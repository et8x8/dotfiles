# Spec: 二胡用数字譜 Web アプリ

最終更新: 2026-05-17
関連 ADR: [docs/adr/draft/erhu-numeric-notation-webapp.md](../adr/draft/erhu-numeric-notation-webapp.md)
関連 Requirements: [docs/requirements/erhu-numeric-notation-webapp.md](../requirements/erhu-numeric-notation-webapp.md)
関連 Design: [docs/design/erhu-numeric-notation-webapp.md](../design/erhu-numeric-notation-webapp.md)

## 概要

本仕様は、二胡向け数字譜 Web アプリが満たすべき検証可能な振る舞いを EARS で宣言する。根拠は単一 Draft ADR に限定する。

## 要件

### REQ-ERHU-001

The erhu numeric notation web application shall be delivered as a React TypeScript Vite single-page application and a Hono application on Cloudflare Workers within one wrangler project that serves static assets and API routes.

> Source: docs/adr/draft/erhu-numeric-notation-webapp.md (Decision: アーキテクチャ概要)

### REQ-ERHU-002

The erhu numeric notation web application shall store password hashes using Argon2id and shall bind authenticated requests to a server-side session referenced by an httpOnly cookie.

> Source: docs/adr/draft/erhu-numeric-notation-webapp.md (Decision: 認証)

### REQ-ERHU-003

If a client calls any protected API route without a valid session, then the Worker shall respond with HTTP status 401 and shall not return private user data.

> Source: docs/adr/draft/erhu-numeric-notation-webapp.md (Acceptance criteria 10, Decision: 非機能・スコープ境界)

### REQ-ERHU-004

If an authenticated user requests a score or media object by identifier that is not owned by that user, then the Worker shall respond with HTTP status 403.

> Source: docs/adr/draft/erhu-numeric-notation-webapp.md (Acceptance criteria 10)

### REQ-ERHU-005

When an authenticated user requests the list of scores, the system shall return only scores owned by that user.

> Source: docs/adr/draft/erhu-numeric-notation-webapp.md (Acceptance criteria 1)

### REQ-ERHU-006

When an authenticated user creates a new score, the system shall persist a score record and versioned JSON document owned by that user.

> Source: docs/adr/draft/erhu-numeric-notation-webapp.md (Acceptance criteria 1)

### REQ-ERHU-007

When an authenticated user deletes a score, the system shall thereafter exclude that score from normal list and load operations for that user (logical deletion satisfies this requirement).

> Source: docs/adr/draft/erhu-numeric-notation-webapp.md (Acceptance criteria 1)

### REQ-ERHU-008

The editor shall allow authoring and editing erhu numeric notation including measures, meter on the first measure, note durations, rests, octave marks, and grace notes at least within the MVP symbol set.

> Source: docs/adr/draft/erhu-numeric-notation-webapp.md (Acceptance criteria 2, Decision: 記号・表現)

### REQ-ERHU-009

When the user applies transposition globally or per part, the editor view, playback, and print view shall interpret pitch using the same transposition fields.

> Source: docs/adr/draft/erhu-numeric-notation-webapp.md (Acceptance criteria 3)

### REQ-ERHU-010

The score document shall support multiple parts, and the UI shall allow toggling visibility per part and shall follow the default horizontal and vertical layout rules documented in the design document.

> Source: docs/adr/draft/erhu-numeric-notation-webapp.md (Acceptance criteria 4)

### REQ-ERHU-011

When the user places, moves, or removes text boxes or image references on the free layer, the system shall persist those elements in the score document and restore them after reload.

> Source: docs/adr/draft/erhu-numeric-notation-webapp.md (Acceptance criteria 5)

### REQ-ERHU-012

When the user starts playback, the Web Audio-based synthesizer shall schedule notes following tempo and effective meter such that pitch order is clearly audible.

> Source: docs/adr/draft/erhu-numeric-notation-webapp.md (Acceptance criteria 6, Decision: 再生)

### REQ-ERHU-013

When the user prints from the dedicated print view or saves as PDF through the browser, the rendered output shall include bar lines, measure warning backgrounds, and free-layer elements without the layout breakages enumerated as in scope in the ADR.

> Source: docs/adr/draft/erhu-numeric-notation-webapp.md (Acceptance criteria 7)

### REQ-ERHU-014

The editor shall always display an explicit time signature on the first measure of the score.

> Source: docs/adr/draft/erhu-numeric-notation-webapp.md (Acceptance criteria 8, Context, Decision: 拍子)

### REQ-ERHU-015

When a measure after the first has a beat sum, computed from its notes and rests using the single shared algorithm, equal to the effective time signature carried forward from previous measures, the editor shall omit displaying a time signature on that measure.

> Source: docs/adr/draft/erhu-numeric-notation-webapp.md (Acceptance criteria 8, Context)

### REQ-ERHU-016

When a measure's beat sum does not equal the effective time signature, the editor shall render that measure with a yellow warning background and shall not automatically change notes, rests, or time signatures to fix the mismatch.

> Source: docs/adr/draft/erhu-numeric-notation-webapp.md (Acceptance criteria 9, Decision: 拍子矛盾の自動解決禁止)

### REQ-ERHU-017

When the user inserts an explicit time signature change at a measure boundary, the effective time signature for subsequent measures shall follow the new signature until another explicit change is inserted.

> Source: docs/adr/draft/erhu-numeric-notation-webapp.md (Decision: 拍子)

### REQ-ERHU-018

The beat sum algorithm for a measure shall produce identical results in the SPA and in the Worker validation path.

> Source: docs/adr/draft/erhu-numeric-notation-webapp.md (Decision: 拍子)

### REQ-ERHU-019

The HTTP API shall not provide anonymous public read endpoints for scores or for user media objects stored in R2.

> Source: docs/adr/draft/erhu-numeric-notation-webapp.md (Decision: 非機能・スコープ境界, 永続化)

## 用語

- **有効拍子 (effective time signature)**: 第1小節の明示拍子を起点とし、ユーザーが挿入した明示的拍子変更により更新される、各小節評価時点の拍子。
- **拍数 (beat sum)**: 小節内の音符・休符を、設計で固定したルールにより拍単位に換算して合計した値。
- **フリーレイヤー (free layer)**: 楽譜主グリッドと独立したテキスト・画像オーバーレイの集合。
