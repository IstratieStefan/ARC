import React, { useState, useEffect, useRef } from "react";
import QrScanner from "react-qr-scanner";

export default function QrScanReact({ onDetected }) {
    const [showScanner, setShowScanner] = useState(false);
    const [error, setError] = useState("");
    const [cameras, setCameras] = useState([]);
    const [cameraId, setCameraId] = useState("");
    const scannerRef = useRef();

    // List cameras on open
    useEffect(() => {
        if (!showScanner) return;
        let isActive = true;
        async function getCameras() {
            try {
                await navigator.mediaDevices.getUserMedia({video:true});
                const devices = await navigator.mediaDevices.enumerateDevices();
                const cams = devices.filter(d => d.kind === "videoinput");
                if (isActive) {
                    setCameras(cams);
                    setCameraId(cams[0]?.deviceId || "");
                }
            } catch (e) {
                setError("Camera access error: " + (e?.message || e));
                setShowScanner(false);
            }
        }
        getCameras();
        return () => { isActive = false };
    }, [showScanner]);

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

    // To support react-qr-scanner, set constraints by cameraId
    const previewStyle = { width: "100%", height: "100%" };
    const constraints = cameraId
        ? { deviceId: cameraId }
        : { facingMode: "environment" };

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
                    {/* Camera selector dropdown */}
                    {cameras.length > 1 && (
                        <select
                            value={cameraId}
                            onChange={e => setCameraId(e.target.value)}
                            className="absolute left-2 top-2 z-10 bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-600 rounded p-1 text-sm"
                            style={{minWidth: "120px"}}
                        >
                            {cameras.map(cam => (
                                <option key={cam.deviceId} value={cam.deviceId}>{cam.label || "Camera"}</option>
                            ))}
                        </select>
                    )}
                    <button
                        style={{position: "absolute", right: 8, top: 8, zIndex: 10, background: "rgba(0,0,0,0.7)", color: "#fff", border: "none", borderRadius: "4px", padding: "4px 8px", cursor: "pointer"}}
                        onClick={() => setShowScanner(false)}
                        type="button"
                    >✕</button>
                    {/* QR scanner */}
                    <QrScanner
                        ref={scannerRef}
                        delay={300}
                        onError={handleError}
                        onScan={handleScan}
                        style={previewStyle}
                        constraints={{ video: constraints }}
                    />
                </div>
            )}
            {error && <p className="text-red-500">{error}</p>}
        </div>
    );
}
