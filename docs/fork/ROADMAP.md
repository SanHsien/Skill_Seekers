# 路線圖

> 本 repo 後續工作的單一真相源。做完一項，就在同一個 commit 刪掉那一列；新工作只加在這裡。
> 現況段的數字是 2026-10-29 依 `main` `a79d768bb127` 查的快照，開工前先重查 GitHub。

## 現況
本 fork 將文件、程式庫與 PDF 轉為技能及知識庫，維持 Windows 與 Python 最低版本的本線差異（[FORK](../../FORK.md)、[裁決](../DECISIONS.md)）。2026-10-29 `gh` 查詢顯示 CI、CodeQL 成功，Code scanning 為 0，仍有 chromadb 告警 4 筆且目前無修補版；風險與重看條件見既有裁決，不能因掃描成功稱為全數安全（2026-10-29 `gh` 查詢；docs/DECISIONS.md「2026-10-28」）。上游預設分支已是 development，本線水位仍追 main；兩者用途需先確認，不能把成功的 main 檢查當成已審 development（2026-10-29 `gh` 查詢；tools/upstream_baseline.json；docs/UPSTREAM.md）。

## 近期：可以直接動手
| 項目 | 為什麼 | 驗收方式 | 建議執行者 | 證據 |
| --- | --- | --- | --- | --- |
| 確認上游追蹤分支的維護政策 | 2026-10-29 `gh` 查詢的預設分支與現有 main 水位不同，不一定是設定錯誤 | 比對上游 main／development 的發版角色與現有裁決；明列維持 release 線或追開發線的選擇，切換須先審新增差異，不直接改水位求綠燈；先以 `gh api repos/yusufkaraaslan/Skill_Seekers/compare/main...development` 審 development 領先 main 的 commits，結論寫進 docs/UPSTREAM.md | Codex | tools/upstream_baseline.json；docs/UPSTREAM.md「Remote」；FORK.md「分支與 remote」；2026-10-29 `gh` 查詢 |
| 重現依賴延後名稱未正規化的候選缺陷 | 同一 Python 套件可能以底線或連字號出現，導致延後失效 | 用相同套件不同 PEP 503 拼法建立失敗案例；確認可重現才統一載入與查詢的名稱處理，工具測試與 Windows gate 通過 | Codex | tools/check_dependency_freshness.py:60-75、137-144；深掃報告（2026-10-2x）「未修候選」 |

## 中期：等條件成立再做
| 項目 | 觸發條件 | 驗收方式 | 建議執行者 | 證據 |
| --- | --- | --- | --- | --- |
| 修補或重評 chromadb 依賴 | patched version 出現、新版可用，或本專案開始提供 ChromaDB HTTP／改變 HttpClient 暴露面 | 查 `gh api repos/SanHsien/Skill_Seekers/dependabot/alerts?state=open` 的 first_patched_version；最小鎖檔更新後跑 Chroma adapter 測試與 gate，核對告警 state=fixed；無修補時保留 open | Claude Opus | docs/DECISIONS.md「2026-10-28」chromadb；src/skill_seekers/cli/adaptors/chroma.py:289、310 |
| 隨選定追蹤線採用上游修正 | 上游合併既有待審 PR，或新增 commit 命中本線功能 | 逐筆核對 MCP null 參數與 provider 行為，保留 Python 最低版本、允許路徑與發布 guard；產品回歸相對基準無新增失敗，維護 gate 通過才更新水位 | Codex | docs/DECISIONS.md「2026-10-24」PR／issue 軸；tools/upstream_baseline.json |
| 補查 Windows 路徑邊界與工具顯示候選問題 | 實際以磁碟根目錄當 skill 路徑、cp950 主控台或帶標題／程式碼區塊連結觸發問題 | 先重現才修；根目錄合法輸入可讀，兄弟目錄、穿越與連接點逃逸仍拒絕；工具不因輸出編碼崩潰，連結案例不誤判 | Codex | 深掃報告（2026-10-2x）「未修候選」；docs/DECISIONS.md「2026-10-28」embedding |
| 重評 API 路徑信任範圍 | user_path 放寬，或新增 HTTP 端點直接操作請求中的路徑 | 對新端點測工作區外、允許根目錄、連接點與可信快取案例；重新核對原 CodeQL dismiss 理由，不能沿用舊裁決作自動豁免 | Claude Opus | docs/DECISIONS.md「2026-10-25：把本機使用者指定路徑的 API 端點改成真檢查」 |

## 刻意不做
| 不做什麼 | 理由 | 什麼情況下重新考慮 |
| --- | --- | --- |
| 覆寫根目錄上游 ROADMAP 或承諾其中所有產品功能 | 根目錄 ROADMAP.md 屬上游產品，本檔才是 fork 待辦來源 | 維護者選定具體需求與驗收範圍 |
| 無修補版時 dismiss chromadb，或因 CodeQL 為零宣稱全部風險消失 | chromadb 延後與已 dismiss 告警各有不同理由，見 docs/DECISIONS.md | 出現修補或威脅模型改變；dismiss 需另作明確決定 |
| 全面重寫上游 Windows 測試或恢復 Python 3.10 | 既有取捨保留在 docs/DECISIONS.md；維護 CI 不等於全產品測試成功 | 維護者授權平台測試工程或上游完成相容修正 |
| 把舊 TOML 報告直接當現存缺陷，或為無共同祖先強推 | 現行 config_extractor.py 已含 tomllib fallback；無共同祖先是已知歷史 | 有新的可重現 TOML 問題；歷史變更需另外授權 |

## 維護方式
每週依 [上游維護](../UPSTREAM.md) 與 `tools/upstream_baseline.json` 審選定分支的 commit／PR／issue，先釐清 main 與 development 角色，採用理由只記於 [裁決](../DECISIONS.md)。
每月依賴新鮮度、安全公告即重查；維護變更跑 `pwsh -NoProfile -File tools/dev_check.ps1`，產品改動依 [開發指引](../DEVELOPMENT.md) 補 smoke 與受影響回歸，保留 embedding 路徑解析後複查。