# 西班牙語聽讀學習網站

A1–C2 分級、以聽讀為主的西班牙語自學靜態網站。

- **前端**：vanilla JS（無框架），部署於 GitHub Pages
- **內容**：每日由 GitHub Actions 自動生成——A1/A2/B1 用 Claude 生成短文，B2/C1/C2 抓真實西語新聞經 Claude 處理；存為 `content/YYYY-MM-DD.json`
- **聽力**：Web Speech API（瀏覽器內建西語 TTS）
- **進度／單字**：Firebase Firestore（Google 登入），未登入或斷線 fallback 到 localStorage

## 設定

1. Firebase：建 project → 加 Web app → 把 config 貼進 `js/config.js` 的 `FIREBASE_CONFIG` → Authentication 啟用 Google → Firestore 套用 `firebase/firestore.rules`
2. GitHub：Settings → Pages → Source = GitHub Actions；設 `ANTHROPIC_API_KEY` secret（供每日內容生成）

## 本地執行

```
python -m http.server 8000          # 前端
python src/generate.py              # 手動生成一天內容（需 ANTHROPIC_API_KEY）
python -m pytest                    # 後端測試
node --test tests/js/               # 前端純函式測試
```
