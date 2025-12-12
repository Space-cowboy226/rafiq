// ================================
// Rafiq – QR Scanner Logic
// ================================

let scanner = null;

function onScanSuccess(decodedText) {
  const id = decodedText.trim() || "UNKNOWN";

  console.log("SCANNED:", id);

  // Stop the scanner
  scanner.stop();

  // Redirect to pilgrim.html and pass the ID
  window.location.href = `pilgrim.html?id=${encodeURIComponent(id)}`;
}

function startScanner() {
  scanner = new Html5Qrcode("reader");

  scanner.start(
    { facingMode: "environment" },
    { fps: 10, qrbox: 250 },
    onScanSuccess
  )
  .catch(err => {
    console.error("Camera error:", err);
    document.getElementById("result-placeholder").innerText =
      "تعذّر تشغيل الكاميرا. تحقق من تصريح المتصفح.";
  });
}

window.onload = () => startScanner();
