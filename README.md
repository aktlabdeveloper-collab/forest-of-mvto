# まとの森（Forest Of Mvto）公開ページ

iOS アプリ「まとの森」の公開ページ。GitHub Pages で配信する。

- トップ：https://aktlabdeveloper-collab.github.io/forest-of-mvto/
- サポート：https://aktlabdeveloper-collab.github.io/forest-of-mvto/support/
- 利用規約：https://aktlabdeveloper-collab.github.io/forest-of-mvto/terms/
- プライバシーポリシー：https://aktlabdeveloper-collab.github.io/forest-of-mvto/privacy/

App Store Connect にはサポートURLとプライバシーポリシーURLを登録する。

## 構成

```
build.py            HTML 生成スクリプト
assets/style.css    スタイル（アプリの配色に合わせた深い藍 × 金）
index.html          トップ         ← build.py が生成
support/index.html  サポート・FAQ  ← build.py が生成（本文は build.py 内に記述）
terms/index.html    利用規約       ← build.py が生成（本文は下記の md が元）
privacy/index.html  プライバシーポリシー ← 同上
```

**HTML を直接編集しない。** `build.py` を実行すると上書きされる。

## 規約を直したいとき

本文の元は CardGallery リポジトリ側にある。

- `~/Documents/AppFolder/CardGallery/store/利用規約.md`
- `~/Documents/AppFolder/CardGallery/store/プライバシーポリシー.md`

md を直したら、このフォルダで次を実行して HTML を作り直し、コミットして push する。

```bash
python3 build.py
```

サポートページ（FAQ）の文面だけは `build.py` 内の `SUPPORT_BODY` にある。

## 公開（初回のみ）

1. GitHub で公開リポジトリ `forest-of-mvto` を作る
2. このフォルダを push する
3. リポジトリの Settings → Pages → Source を「Deploy from a branch」、ブランチ `main` / フォルダ `/ (root)` にする
4. 数分後に上記 URL で見られるようになる

リポジトリ名がそのまま URL に入るので、**リポジトリ名は変えない**。変えると App Store Connect に登録した URL が切れる。
