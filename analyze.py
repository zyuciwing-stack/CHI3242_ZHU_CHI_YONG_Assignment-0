#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CHI3242 作業：《論衡·超奇》關鍵稱謂頻次統計＋KWIC 語境檢索＋全文回查頁。

讀取專案內 chaoqi.txt（原始全文，未改動，保留校勘記標記與疑字），
以單趟掃描計算「儒生／通人／文人／鴻儒」的全部命中（段落編號、段內字位、
前後各約 20 字語境），產生離線可開啟的 index.html。

所有次數、條數、段落號均由程式計算；腳本內不寫死任何預期值，
並在結束前核對「KWIC 條數＝字串計數」，不一致即中止。
"""

import html
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "chaoqi.txt"
OUT = ROOT / "index.html"

TERMS = ["儒生", "通人", "文人", "鴻儒"]
TERM_RE = re.compile("|".join(TERMS))
CONTEXT = 20

SOURCE_NOTE = (
    "維基文庫〈超奇篇第三十九〉（https://zh.wikisource.org/wiki/論衡/39，"
    "修訂版 oldid 2326276，頁面最後編輯 2023-10-25）"
)

QUOTES = {
    "def": "能說一經者為儒生",
    "beyond": "超而又超",
    "rare_browse": "通覽者，世間比有",
    "rare_hongru": "夫鴻儒希有",
    "inner_outer": "外內表里，自相副稱",
    "no_flower_only": "苟有文無實",
    "not_just_carve": "豈徒雕文飾辭",
    "flower_fruit": "夫華與實俱成者也",
    "zhou_shengsheng": "非徒文人，所謂鴻儒者也",
}


def load_paras() -> list[str]:
    lines = SRC.read_text(encoding="utf-8").splitlines()
    return [ln for ln in lines if ln.strip()]


def find_para(paras: list[str], key: str) -> int:
    for i, p in enumerate(paras, 1):
        if key in p:
            return i
    raise SystemExit(f"引文未能在 chaoqi.txt 中定位：{key}")


def scan(paras: list[str]):
    hits: dict[str, list[dict]] = {t: [] for t in TERMS}
    counter: dict[str, int] = {t: 0 for t in TERMS}
    rendered: dict[int, str] = {}
    for pno, para in enumerate(paras, 1):
        parts: list[str] = []
        last = 0
        for m in TERM_RE.finditer(para):
            parts.append(html.escape(para[last : m.start()]))
            term = m.group()
            counter[term] += 1
            hits[term].append(
                {
                    "idx": counter[term],
                    "para": pno,
                    "pos": m.start(),
                    "left": para[max(0, m.start() - CONTEXT) : m.start()].strip(),
                    "right": para[m.end() : m.end() + CONTEXT].strip(),
                }
            )
            k = TERMS.index(term) + 1
            parts.append(
                f'<mark class="kw k{k}" id="hit-{term}-{counter[term]}">{term}</mark>'
            )
            last = m.end()
        parts.append(html.escape(para[last:]))
        rendered[pno] = "".join(parts)
    return hits, counter, rendered


def verify(paras: list[str], hits, counter) -> dict[str, int]:
    full_counts = {t: sum(p.count(t) for p in paras) for t in TERMS}
    for t in TERMS:
        if not (counter[t] == full_counts[t] == len(hits[t])):
            raise SystemExit(
                f"核對失敗：{t} 掃描計數 {counter[t]}、字串計數 {full_counts[t]}、"
                f"KWIC 條數 {len(hits[t])} 不一致"
            )
    return full_counts


CSS = """
:root{--ink:#23282f;--muted:#6b7280;--paper:#faf9f6;--card:#ffffff;--line:#e5e2da;
--k1:#1d4ed8;--k1bg:#e3ecfd;--k2:#047857;--k2bg:#ddf2e8;--k3:#b45309;--k3bg:#fdeed3;
--k4:#b91c1c;--k4bg:#fde3e3}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--paper);color:var(--ink);line-height:1.85;
font-family:"Noto Serif TC","Source Han Serif TC","Songti TC","Microsoft JhengHei","PingFang TC",serif}
main{max-width:56rem;margin:0 auto;padding:1.5rem 1.25rem 4rem}
header.page{border-bottom:3px double var(--line);padding-bottom:1rem;margin-bottom:1.5rem}
h1{font-size:1.5rem;margin:.2rem 0 .4rem}
h2{font-size:1.2rem;margin:2.2rem 0 .8rem;padding:.15rem .6rem;border-left:5px solid var(--ink);background:var(--card)}
nav.toc{display:flex;flex-wrap:wrap;gap:.4rem;margin-top:.8rem}
nav.toc a{font-size:.85rem;text-decoration:none;border:1px solid var(--line);background:var(--card);
padding:.15rem .6rem;border-radius:999px;color:var(--ink)}
nav.toc a:hover{border-color:var(--ink)}
.meta{font-size:.85rem;color:var(--muted)}
table{border-collapse:collapse;width:100%;background:var(--card);font-size:.95rem}
th,td{border:1px solid var(--line);padding:.35rem .55rem;text-align:left;vertical-align:top}
th{background:#f1efe9}
.num{text-align:right;font-variant-numeric:tabular-nums}
mark.kw{padding:0 .12em;border-radius:.2em;font-weight:600}
.k1{background:var(--k1bg);box-shadow:inset 0 -2px 0 var(--k1);color:var(--k1)}
.k2{background:var(--k2bg);box-shadow:inset 0 -2px 0 var(--k2);color:var(--k2)}
.k3{background:var(--k3bg);box-shadow:inset 0 -2px 0 var(--k3);color:var(--k3)}
.k4{background:var(--k4bg);box-shadow:inset 0 -2px 0 var(--k4);color:var(--k4)}
.chart{margin:1rem 0;background:var(--card);border:1px solid var(--line);padding:1rem}
.bar-row{display:flex;align-items:center;gap:.6rem;margin:.45rem 0}
.bar-label{width:4rem;text-align:right;font-weight:600}
.bar-track{flex:1;background:#f0eee8;border-radius:.4rem;height:1.5rem;overflow:hidden}
.bar-fill{display:block;height:100%;border-radius:.4rem}
.bf1{background:var(--k1)}.bf2{background:var(--k2)}.bf3{background:var(--k3)}.bf4{background:var(--k4)}
.bar-num{width:3rem;font-variant-numeric:tabular-nums;font-weight:600}
.tag{display:inline-block;padding:.05rem .5rem;border-radius:.3rem;font-weight:600;font-size:.85rem}
.filters{display:flex;flex-wrap:wrap;gap:.4rem;align-items:center;margin:.8rem 0}
.filters button{border:1px solid var(--line);background:var(--card);padding:.25rem .8rem;
border-radius:999px;cursor:pointer;font-size:.9rem;font-family:inherit}
.filters button.active{background:var(--ink);color:#fff;border-color:var(--ink)}
#kwic-search{flex:1;min-width:14rem;border:1px solid var(--line);border-radius:.4rem;
padding:.4rem .7rem;font-size:.95rem;font-family:inherit}
td.ctx{font-size:.9rem;color:#4b5563}
td.hitcell{text-align:center;font-weight:600;white-space:nowrap}
td.hitcell a{text-decoration:none}
td.jump a{font-size:.85rem}
.hint{font-size:.85rem;color:var(--muted)}
.para{background:var(--card);border:1px solid var(--line);border-radius:.4rem;
padding:.8rem 1rem .8rem 2.9rem;margin:.7rem 0;position:relative}
.pnum{position:absolute;left:.6rem;top:.7rem;font-size:.75rem;color:var(--muted);
border:1px solid var(--line);border-radius:.3rem;padding:0 .4rem;background:#f6f4ef}
blockquote{margin:.4rem 0;border-left:3px solid var(--line);padding:.2rem .9rem;
background:#f4f2ec;font-family:inherit}
ol.reading li{margin:.8rem 0}
.note{font-size:.88rem;color:var(--muted)}
ul.limits li{margin:.5rem 0}
footer{margin-top:3rem;padding-top:1rem;border-top:1px solid var(--line);font-size:.8rem;color:var(--muted)}
"""

JS = """
(function(){
  var rows = Array.prototype.slice
    .call(document.querySelectorAll('#kwic-table tbody tr'))
    .filter(function(r){ return r.hasAttribute('data-t'); });
  var q = document.getElementById('kwic-search');
  var btns = Array.prototype.slice.call(document.querySelectorAll('.tf'));
  var term = 'all';
  function apply(){
    var s = q.value.trim();
    var shown = 0;
    rows.forEach(function(r){
      var okT = (term === 'all') || (r.getAttribute('data-t') === term);
      var okS = !s || r.textContent.indexOf(s) !== -1;
      var vis = okT && okS;
      r.style.display = vis ? '' : 'none';
      if (vis) shown++;
    });
    document.getElementById('kwic-visible').textContent = shown;
  }
  btns.forEach(function(b){
    b.addEventListener('click', function(){
      term = b.getAttribute('data-t');
      btns.forEach(function(x){ x.classList.toggle('active', x === b); });
      apply();
    });
  });
  q.addEventListener('input', apply);
  apply();
})();
"""


def build_html(paras, hits, counter, rendered, quote_pno, check):
    total_chars = sum(len(p) for p in paras)
    total_hits = sum(counter[t] for t in TERMS)
    maxc = max(counter[t] for t in TERMS) or 1
    P = quote_pno
    C = check

    head = (
        "<!DOCTYPE html>\n"
        '<html lang="zh-Hant">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>《論衡·超奇》關鍵稱謂頻次與語境檢索</title>\n"
        f"<style>{CSS}</style>\n</head>\n<body>\n<main>\n"
    )

    header = (
        '<header class="page">\n'
        "<h1>《論衡·超奇》關鍵稱謂頻次統計＋KWIC 語境檢索</h1>\n"
        f'<p class="meta">文本：chaoqi.txt（{SOURCE_NOTE}）｜'
        f"全文 {len(paras)} 段、{total_chars} 字（含全形縮排與標點）｜"
        f"由 analyze.py 產生（{date.today().isoformat()}）｜離線可開</p>\n"
        '<nav class="toc">'
        '<a href="#source">資料來源</a><a href="#question">研究問題</a>'
        '<a href="#counts">頻次</a><a href="#kwic">語境檢索</a>'
        '<a href="#fulltext">全文回查</a><a href="#reading">解讀</a>'
        '<a href="#limits">方法限制</a></nav>\n'
        "</header>\n"
    )

    legend = "、".join(
        f'<span class="tag k{i+1}">{t}</span>' for i, t in enumerate(TERMS)
    )

    source = f"""
<section id="source">
<h2>資料來源與版本說明</h2>
<ul>
<li>來源：{SOURCE_NOTE}。本頁統計僅代表此一版本。</li>
<li>本機檔案：<code>chaoqi.txt</code>（原始全文，未經改寫；保留「吳君（商）〔高〕」「〔奄〕丘蔽野」等校勘記標記，以及「太吏公」「鋒不則割不深」「易晁錯這策」等疑字，<strong>未比對校勘本，未作任何改動</strong>）。</li>
<li>段落編號 1–{len(paras)} 為本專案自訂（依 chaoqi.txt 內換行分段），非原書卷次。</li>
<li>稱謂色標：{legend}（詞表於 analyze.py 的 TERMS 中定義，可增刪）。</li>
</ul>
</section>
"""

    question = """
<section id="question">
<h2>研究問題</h2>
<ol>
<li>王充在〈超奇〉中使用「儒生、通人、文人、鴻儒」各多少次？</li>
<li>每次出現的語境為何（定義、品評人物、比喻）？</li>
<li>這些語境分佈能否輔助閱讀「儒生→通人→文人→鴻儒」的等級論述？——僅作閱讀輔助；等級高下由原文論證判斷，不由次數推論。</li>
</ol>
</section>
"""

    rows = []
    paras_hit = {}
    for t in TERMS:
        paras_hit[t] = "、".join(str(p) for p in dict.fromkeys(h["para"] for h in hits[t]))
    for i, t in enumerate(TERMS):
        rows.append(
            f'<tr><td><span class="tag k{i+1}">{t}</span></td>'
            f'<td class="num"><strong>{counter[t]}</strong></td>'
            f'<td class="num">{paras_hit[t]}</td>'
            f'<td><a href="#hit-{t}-1">首次命中 ↗</a></td></tr>'
        )
    bars = []
    for i, t in enumerate(TERMS):
        w = counter[t] / maxc * 100
        bars.append(
            f'<div class="bar-row"><span class="bar-label">{t}</span>'
            f'<span class="bar-track"><span class="bar-fill bf{i+1}" style="width:{w:.1f}%"></span></span>'
            f'<span class="bar-num">{counter[t]}</span></div>'
        )
    counts = f"""
<section id="counts">
<h2>一、稱謂頻次（程式實算）</h2>
<table>
<tr><th>稱謂</th><th>次數</th><th>命中段落</th><th>回查</th></tr>
{''.join(rows)}
</table>
<div class="chart">
{''.join(bars)}
</div>
<p class="note">長條圖長度以上表最大值為基準。次數僅描述各稱謂在篇內被提及的多寡，
<strong>不作價值高下的推論</strong>；等級高下須引原文論證（見下方「解讀」）。
核對：四詞 KWIC 條數與字串計數一致（儒生 {C["儒生"]}｜通人 {C["通人"]}｜文人 {C["文人"]}｜鴻儒 {C["鴻儒"]}），
全部命中合計 {total_hits} 條。</p>
</section>
"""

    kwic_rows = []
    for t in TERMS:
        k = TERMS.index(t) + 1
        for h in hits[t]:
            kwic_rows.append(
                f'<tr data-t="{t}">'
                f'<td class="num">{h["idx"]}</td>'
                f'<td><span class="tag k{k}">{t}</span></td>'
                f'<td class="num"><a href="#p{h["para"]}">{h["para"]}</a></td>'
                f'<td class="num">第 {h["pos"] + 1} 字</td>'
                f'<td class="ctx">{html.escape(h["left"])}</td>'
                f'<td class="hitcell"><a class="k{k}" href="#hit-{t}-{h["idx"]}">{t}</a></td>'
                f'<td class="ctx">{html.escape(h["right"])}</td></tr>'
            )
    kwic = f"""
<section id="kwic">
<h2>二、KWIC 語境檢索（全部命中，前後各約 {CONTEXT} 字）</h2>
<div class="filters">
<button class="tf active" data-t="all">全部</button>
{''.join(f'<button class="tf" data-t="{t}">{t}</button>' for t in TERMS)}
<input id="kwic-search" type="search" placeholder="搜尋語境文字，例如：篇章、胸中、鴻儒…">
</div>
<p class="hint">顯示 <strong id="kwic-visible">{total_hits}</strong> / {total_hits} 條。點「段落」數字回到段落，點關鍵詞跳至全文高亮位置。前後 20 字為機械截取，語境功能（定義／品評／比喻）仍須人工閱讀判斷。</p>
<table id="kwic-table">
<thead><tr><th>#</th><th>稱謂</th><th>段落</th><th>段內位置</th><th>前文</th><th>關鍵詞</th><th>後文</th></tr></thead>
<tbody>
{''.join(kwic_rows)}
</tbody>
</table>
</section>
"""

    fulltext = (
        f'<section id="fulltext">\n<h2>三、全文（段落編號＋稱謂高亮）</h2>\n'
        + "".join(
            f'<div class="para" id="p{pno}"><span class="pnum">{pno}</span>{rendered[pno]}</div>\n'
            for pno in sorted(rendered)
        )
        + "</section>\n"
    )

    reading = f"""
<section id="reading">
<h2>四、簡短解讀（每條附原文依據）</h2>
<ol class="reading">
<li><strong>等級高下來自原文的定義與比較，不是來自次數。</strong>全文對四稱謂的直接定義見第 {P["def"]} 段：
<blockquote>故夫能說一經者為儒生，博覽古今者為通人，采掇傳書以上書奏記者為文人，能精思著文連結篇章者為鴻儒。故儒生過俗人，通人勝儒生，文人逾通人，鴻儒超文人。</blockquote>
本頁計得：儒生 {counter["儒生"]} 次、通人 {counter["通人"]} 次、文人 {counter["文人"]} 次、鴻儒 {counter["鴻儒"]} 次——
這些次數僅描述篇內提及的多寡；價值高下須由上述定義句與比較句（第 {P["def"]} 段）等原文論證判斷，不由次數推得。</li>

<li><strong>關於「稀罕程度」，王充自己有論述，但本頁不把次數多寡解釋為因果。</strong>原文說
「夫通覽者，世間比有；著文者，歷世希然」（第 {P["rare_browse"]} 段）、「夫鴻儒希有，而文人比然」（第 {P["rare_hongru"]} 段），
又稱鴻儒「所謂超而又超者也」「世之金玉也」（第 {P["beyond"]} 段）——這些是王充的論證內容；本頁的次數統計僅描述提及密度，不附加任何因果或價值結論。</li>

<li><strong>「文人」不能直接等同現代文學家。</strong>定義句「采掇傳書以上書奏記者為文人」（第 {P["def"]} 段）：「文人」指能運用既有文獻、以書奏應用於實務的著述之士；其「文」涵蓋上書、奏記、著書立說（《新語》《新論》等），不能以今日「純文學／文學家」框架套讀。</li>

<li><strong>王充並非排斥文采，而是要求文實相副。</strong>「有實核於內，有皮殼於外。文墨辭說，士之榮葉、皮殼也……外內表里，自相副稱」（第 {P["inner_outer"]} 段）；「以知為本，筆墨之文，將而送之，豈徒雕文飾辭，苟為華葉之言哉？精誠由中，故其文語感動人深」（第 {P["not_just_carve"]} 段）——「豈徒」句否認的是這些著述「只是」雕飾，而非否定文采本身；「夫華與實俱成者也，無華生實，物希有之」（第 {P["flower_fruit"]} 段）表明華葉與實並存共成。他所貶斥的是「苟有文無實」（第 {P["no_flower_only"]} 段）。</li>

<li><strong>周長生被原文明確稱為鴻儒。</strong>「然則長生非徒文人，所謂鴻儒者也」（第 {P["zhou_shengsheng"]} 段）：原文先說他超出一般文人，隨即明言「所謂鴻儒者也」。本頁直接引用原文稱謂，不另立分類標籤。</li>
</ol>
</section>
"""

    limits = """
<section id="limits">
<h2>五、方法限制與未驗證項目</h2>
<ul class="limits">
<li><strong>固定字串檢索只保證列出字串命中</strong>：本頁列出的是「儒生／通人／文人／鴻儒」四個字串的全部出現位置，不宣稱自動保證人物歸屬或語義分析沒有遺漏。例如「子長」既指司馬遷（「若司馬子長、劉子政之徒」）又出現於「陽成子長作《樂經》」，字串層次無法區分，須人工閱讀。</li>
<li><strong>頻次 ≠ 價值</strong>：次數僅描述提及多寡；等級高下須引原文論證（定義句、比較句、比喻段）。</li>
<li><strong>單字「文」未統計</strong>：歧義大（文王、文軒、文墨、文讀、文軌），字串層次無法自動消歧，需人工判讀。</li>
<li><strong>未比對校勘本</strong>：僅使用維基文庫單一版本；「太吏公」「鋒不則割不深」「易晁錯這策」等疑字僅標記、未改動，正式引用前宜與校勘本核對。</li>
<li><strong>段落編號為專案自訂</strong>（依檔案換行分段），非原書卷次；不同版本的分段可能不同。</li>
<li>樣本為單篇約三千字，統計僅作閱讀輔助地圖；KWIC 前後 20 字的語境功能（定義／品評／比喻）須人工閱讀標註，本頁未做此標註。</li>
<li>頁面互動（搜尋、篩選）為內嵌 JavaScript，尚未經人工瀏覽器實測。</li>
</ul>
</section>
"""

    footer = (
        f'<footer>由 <code>analyze.py</code> 讀取 chaoqi.txt 自動產生（{date.today().isoformat()}）｜'
        f"核對結果：儒生 {C['儒生']}、通人 {C['通人']}、文人 {C['文人']}、鴻儒 {C['鴻儒']}——"
        "各詞 KWIC 條數＝字串計數，核對通過。</footer>\n"
    )

    tail = f"<script>{JS}</script>\n</main>\n</body>\n</html>\n"

    return (
        head
        + header
        + source
        + question
        + counts
        + kwic
        + fulltext
        + reading
        + limits
        + footer
        + tail
    )


def main() -> None:
    paras = load_paras()
    if not paras:
        raise SystemExit("chaoqi.txt 為空或不存在")

    hits, counter, rendered = scan(paras)
    full_counts = verify(paras, hits, counter)

    quote_pno = {name: find_para(paras, key) for name, key in QUOTES.items()}
    check = {t: f"{len(hits[t])}={full_counts[t]}" for t in TERMS}

    print("=== 稱謂頻次 ===")
    for t in TERMS:
        print(f"{t}: {counter[t]}")
    print("=== KWIC 條數核對（條數＝字串計數） ===")
    for t in TERMS:
        print(f"{t}: {len(hits[t])} = {full_counts[t]} → OK")
    print("=== 全部命中明細 ===")
    for t in TERMS:
        for h in hits[t]:
            print(
                f"[{t} #{h['idx']}] 第{h['para']}段 第{h['pos'] + 1}字｜"
                f"前：{h['left']}｜【{t}】｜後：{h['right']}"
            )

    OUT.write_text(build_html(paras, hits, counter, rendered, quote_pno, check), encoding="utf-8")
    print(f"=== 已輸出 {OUT}（{OUT.stat().st_size} bytes） ===")


if __name__ == "__main__":
    main()