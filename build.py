#!/usr/bin/env python3
"""まとの森（Forest Of Mvto）公開ページのビルドスクリプト。

CardGallery リポジトリの store/*.md を読んで、GitHub Pages 用の HTML を生成する。
規約を直したら `python3 build.py` を実行し、生成された HTML をコミットして push する。

使い方:
    python3 build.py            # 既定のパスから生成
    python3 build.py --check    # 生成せず、元の md が見つかるかだけ確認
"""

import argparse
import html
import re
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent
STORE = Path("/Users/aki/Documents/AppFolder/CardGallery/store")

BASE_PATH = "/forest-of-mvto"  # GitHub Pages のプロジェクトページはリポジトリ名が先頭に付く
BASE_URL = "https://aktlabdeveloper-collab.github.io" + BASE_PATH
APP_JA = "まとの森"
APP_EN = "Forest Of Mvto"
CONTACT = "akt.lab.developer@gmail.com"

NAV = [("/", "ホーム"), ("/support/", "サポート"), ("/terms/", "利用規約"), ("/privacy/", "プライバシーポリシー")]


# --- Markdown → HTML（規約類で使っている記法だけを扱う最小実装） -------------

INLINE_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
BOLD = re.compile(r"\*\*([^*]+)\*\*")
BARE_URL = re.compile(r"(?<![\"'=(])\bhttps?://[^\s<>）」]+")


def inline(text: str) -> str:
    out = html.escape(text, quote=False)
    out = INLINE_LINK.sub(lambda m: f'<a href="{html.escape(m.group(2), quote=True)}">{m.group(1)}</a>', out)
    out = BOLD.sub(r"<strong>\1</strong>", out)
    out = BARE_URL.sub(lambda m: f'<a href="{m.group(0)}">{m.group(0)}</a>', out)
    return out


def md_to_html(md: str) -> str:
    lines = md.split("\n")
    out, i = [], 0
    list_tag = None

    def close_list():
        nonlocal list_tag
        if list_tag:
            out.append(f"</{list_tag}>")
            list_tag = None

    while i < len(lines):
        line = lines[i].rstrip()

        if not line.strip():
            close_list()
            i += 1
            continue

        if line.strip() == "---":
            close_list()
            out.append("<hr>")
            i += 1
            continue

        m = re.match(r"^(#{1,4})\s+(.*)$", line)
        if m:
            close_list()
            level = len(m.group(1))
            out.append(f"<h{level}>{inline(m.group(2))}</h{level}>")
            i += 1
            continue

        # テーブル（| 見出し | ... | の次行が区切り行）
        if line.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[i + 1].strip()):
            close_list()
            header = [c.strip() for c in line.strip().strip("|").split("|")]
            i += 2
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            out.append('<div class="table-wrap"><table>')
            out.append("<thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in header) + "</tr></thead>")
            out.append("<tbody>")
            for row in rows:
                out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in row) + "</tr>")
            out.append("</tbody></table></div>")
            continue

        m = re.match(r"^(\d+)\.\s+(.*)$", line)
        if m:
            if list_tag != "ol":
                close_list()
                out.append("<ol>")
                list_tag = "ol"
            out.append(f"<li>{inline(m.group(2))}</li>")
            i += 1
            continue

        m = re.match(r"^[-*]\s+(.*)$", line)
        if m:
            if list_tag != "ul":
                close_list()
                out.append("<ul>")
                list_tag = "ul"
            out.append(f"<li>{inline(m.group(1))}</li>")
            i += 1
            continue

        # 段落（空行まで連結）
        close_list()
        para = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#{1,4}\s|[-*]\s|\d+\.\s|\||---$)", lines[i].strip()):
            para.append(lines[i].rstrip())
            i += 1
        out.append("<p>" + "<br>".join(inline(p) for p in para) + "</p>")

    close_list()
    return "\n".join(out)


# --- ページの組み立て -------------------------------------------------------

def page(title: str, path: str, body: str, description: str) -> str:
    links = []
    for href, label in NAV:
        current = ' aria-current="page"' if href == path else ""
        links.append(f'<a href="{BASE_PATH}{href}"{current}>{label}</a>')
    nav = "".join(links)
    full_title = f"{title}｜{APP_JA}" if title != APP_JA else f"{APP_JA}（{APP_EN}）"
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(full_title)}</title>
<meta name="description" content="{html.escape(description)}">
<link rel="canonical" href="{BASE_URL}{path}">
<link rel="stylesheet" href="{BASE_PATH}/assets/style.css">
</head>
<body>
<header class="site-header">
  <a class="brand" href="{BASE_PATH}/">
    <span class="brand-ja">{APP_JA}</span>
    <span class="brand-en">{APP_EN}</span>
  </a>
  <nav class="site-nav">{nav}</nav>
</header>
<main>
{body}
</main>
<footer class="site-footer">
  <p>{APP_JA}（{APP_EN}）</p>
  <p>運営者：AKT.LAB　お問い合わせ：<a href="mailto:{CONTACT}">{CONTACT}</a></p>
</footer>
</body>
</html>
"""


LANDING_BODY = f"""
<section class="hero">
  <h1>{APP_JA}<span class="hero-en">{APP_EN}</span></h1>
  <p class="lead">深い藍と金に彩られた、オラクルカードのコレクションアプリ。<br>
  カードを一枚引いて、今日のあなたへのメッセージを受け取ります。</p>
</section>

<section class="cards">
  <a class="card" href="{BASE_PATH}/support/">
    <h2>サポート</h2>
    <p>使い方・よくある質問・お問い合わせ先</p>
  </a>
  <a class="card" href="{BASE_PATH}/terms/">
    <h2>利用規約</h2>
    <p>アプリをご利用いただく際の条件</p>
  </a>
  <a class="card" href="{BASE_PATH}/privacy/">
    <h2>プライバシーポリシー</h2>
    <p>取得する情報と取り扱いについて</p>
  </a>
</section>

<section class="note">
  <h2>このアプリについて</h2>
  <p>カードの文言やリーディング結果は、娯楽および自己内省のきっかけを目的としたものです。
  医療・健康・法律・税務・投資などの専門的な助言に代わるものではありません。</p>
</section>
"""

SUPPORT_BODY = f"""
<h1>サポート</h1>
<p>{APP_JA}（{APP_EN}）の使い方と、よくあるご質問をまとめています。
解決しない場合は、このページ下部のお問い合わせ先までご連絡ください。</p>

<h2>よくあるご質問</h2>

<h3>コインはどうやって手に入りますか？</h3>
<p>毎日のログインボーナス、ミッションの達成、動画広告の視聴で無料コインがもらえます。
現在、コインの販売（アプリ内課金）は行っていません。</p>

<h3>「広告を見てコインをもらう」が動きません</h3>
<p>通信環境が不安定なときや、広告の在庫がないときは読み込みに失敗することがあります。
しばらく時間をおいてからお試しください。コインはログインボーナスやミッションからも入手できます。</p>

<h3>カードの画像が表示されません</h3>
<p>通信環境をご確認のうえ、カード一覧を下に引っ張って更新してください。
アプリはカード情報を一定時間保存しているため、最新の状態になるまで少し時間がかかることがあります。</p>

<h3>引いたカードが増えていません</h3>
<p>通信が途中で切れた場合、コインの返還またはカードの付与のいずれかで対応します。
お手数ですが、発生した日時とカード名をそえてお問い合わせください。</p>

<h3>表示言語を英語に変えたい</h3>
<p>マイページ →「言語設定」から日本語／English を切り替えられます。</p>

<h3>別の端末でも同じデータを使えますか？</h3>
<p>同じアカウントでログインすれば、保有カード・コイン・履歴は引き継がれます。</p>

<h3>アカウントを削除したい</h3>
<p>マイページの一番下にある「アカウントを削除」から、いつでも削除できます。
削除すると、保有カード・コイン・ポイント・履歴のすべてが完全に削除され、復元できません。</p>
<p>最後のログインから時間が経っている場合は、安全のため再ログインを求められます。
その場合、ログインし直してから再度お試しください（データは削除されません）。</p>

<h3>パスワードを忘れました</h3>
<p>ログイン画面の「パスワードをお忘れですか？」から、登録したメールアドレスに再設定メールを送れます。
Apple または Google でログインしている場合は、それぞれのサービス側でご確認ください。</p>

<h2>お問い合わせ</h2>
<p>不具合のご報告やご質問は、以下までご連絡ください。
ご返信までお時間をいただくことがあります。</p>
<p class="contact"><a href="mailto:{CONTACT}">{CONTACT}</a></p>
<p>不具合のご報告の際は、次の情報をそえていただけると調査がスムーズです。</p>
<ul>
  <li>発生日時</li>
  <li>端末（iPhone の機種）と iOS のバージョン</li>
  <li>どの画面で何をしたときに起きたか</li>
</ul>
"""


def build(check_only: bool = False) -> int:
    sources = {
        "terms": STORE / "利用規約.md",
        "privacy": STORE / "プライバシーポリシー.md",
    }
    missing = [str(p) for p in sources.values() if not p.exists()]
    if missing:
        print("元ファイルが見つかりません:\n  " + "\n  ".join(missing), file=sys.stderr)
        return 1
    if check_only:
        print("OK: 元ファイルはすべて見つかりました")
        return 0

    pages = {
        "index.html": page(APP_JA, "/", LANDING_BODY, f"{APP_JA}（{APP_EN}）の公式ページ。サポート・利用規約・プライバシーポリシー。"),
        "support/index.html": page("サポート", "/support/", SUPPORT_BODY, f"{APP_JA}（{APP_EN}）のよくあるご質問とお問い合わせ先。"),
        "terms/index.html": page("利用規約", "/terms/", md_to_html(sources["terms"].read_text()), f"{APP_JA}（{APP_EN}）の利用規約。"),
        "privacy/index.html": page("プライバシーポリシー", "/privacy/", md_to_html(sources["privacy"].read_text()), f"{APP_JA}（{APP_EN}）のプライバシーポリシー。"),
    }
    for rel, content in pages.items():
        dest = SITE / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content)
        print(f"書き出し: {rel}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="生成せず元ファイルの存在だけ確認する")
    raise SystemExit(build(ap.parse_args().check))
