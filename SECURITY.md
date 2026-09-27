# 安全政策

## 支援範圍

安全修正以本 fork 的最新 `main` 為主；上游版本的問題也會視需要回報原作者。

## 私下回報

若發現針對本 fork 維護骨架或衍生程式的安全漏洞，請使用 GitHub Security Advisories 的 **Report a vulnerability** 私下回報：
<https://github.com/SanHsien/Skill_Seekers/security/advisories/new>。
若該入口不可用，請透過 GitHub 個人檔案聯絡維護者，不要先建立公開 Issue。

若問題屬於上游核心邏輯，亦可向原作者 yusufkaraaslan 通報。

回報請包含影響範圍、重現步驟、受影響版本與最小必要證據。請勿在回報中附上真實 API key、token、個人機密文件或帳密。

## 特別注意

- **命令列工具與網路存取**：Skill Seekers 在抓取網站與解析 GitHub 倉庫時會向外部網路發起請求。在 Windows 環境下執行時，請勿傳入未經信任的本機路徑或惡意 URL。
- **憑證與環境變數**：`.env` 檔案已列入 `.gitignore`，請勿將包含 GitHub Token 或 Anthropic API Key 的設定檔提交至倉庫。
