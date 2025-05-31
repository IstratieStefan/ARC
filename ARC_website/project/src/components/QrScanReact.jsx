import React, { useState, useRef } from "react";
import QrScanner from "react-qr-scanner";

export default function QrScanReact({ onDetected }) {
    const [showScanner, setShowScanner] = useState(false);
    const [error, setError] = useState("");
    const scannerRef = useRef();

    const handleScan = (result) => {
        if (result) {
            setShowScanner(false);
            onDetected(result.text);
        }
    };

    const handleError = (err) => {
        setError("Camera error: " + (err?.message || err));
        setShowScanner(false);
    };

    return (
        <div>
            <div className="mb-2">
                <button
                    className="mt-3 w-full px-4 py-2 rounded-md border border-gray-300 dark:border-gray-600 bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-white shadow-sm hover:bg-gray-200 dark:hover:bg-gray-700 transition focus:outline-none focus:ring-2 focus:ring-accent"
                    type="button"
                    onClick={() => { setShowScanner(true); setError(""); }}
                >
                    Scan QR Code
                </button>
            </div>
            {showScanner && (
                <div className="mb-4 rounded-md overflow-hidden bg-black border border-gray-300 dark:border-gray-600 aspect-video" style={{position: "relative", width: "100%", maxWidth: "100%", height: "260px"}}>
                    <button
                        style={{position: "absolute", right: 8, top: 8, zIndex: 2, background: "rgba(0,0,0,0.7)", color: "#fff", border: "none", borderRadius: "4px", padding: "4px 8px", cursor: "pointer"}}
                        onClick={() => setShowScanner(false)}
                        type="button"
                    >✕</button>
                    <QrScanner
                        ref={scannerRef}
                        delay={300}
                        onError={handleError}
                        onScan={handleScan}
                        style={{ width: "100%", height: "100%" }}
                        facingMode="environment"
                    />
                </div>
            )}
            {error && <p className="text-red-500">{error}</p>}
        </div>
    );
}
