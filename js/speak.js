// 單字/短句發音：西語、慢速（方便跟讀）
export function pronounce(text) {
  if (!text || !window.speechSynthesis) return;
  const synth = window.speechSynthesis;
  const u = new SpeechSynthesisUtterance(text);
  u.lang = "es-ES";
  u.rate = 0.75;   // 慢一點
  const voice = synth.getVoices().find((v) => v.lang.startsWith("es"));
  if (voice) u.voice = voice;
  if (synth.speaking || synth.pending) {
    synth.cancel();
    setTimeout(() => synth.speak(u), 60);   // 避開 Chrome cancel→speak 競態
  } else {
    synth.speak(u);
  }
}
