export const LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"];

// Firebase：在 Firebase console 建 project → 加一個 Web app → 把設定物件貼進來
//（Project settings → General → Your apps → SDK setup and configuration）
// apiKey 留空時前端不啟用雲端同步，改用 localStorage
export const FIREBASE_CONFIG = {
  apiKey: "",
  authDomain: "",
  projectId: "",
  appId: "",
};
