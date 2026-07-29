'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { TrendingDown, BarChart3, Lock, Smartphone, Download, ShieldCheck, CheckCircle } from 'lucide-react';

interface ApkInfo {
  available: boolean;
  filename?: string;
  size_mb?: number;
  sha256?: string;
  version?: string;
  min_android?: string;
  download_url?: string;
}

function DownloadSection() {
  const [apkInfo, setApkInfo] = useState<ApkInfo | null>(null);
  const [showSafetyInfo, setShowSafetyInfo] = useState(false);
  const [downloading, setDownloading] = useState(false);

  const API_URL = process.env.NEXT_PUBLIC_API_URL?.replace('/api/v1', '') ||
    'https://spending-intelligence-production.up.railway.app';

  useEffect(() => {
    // Check if APK is available
    fetch(`${API_URL}/download/android/info`)
      .then(r => r.json())
      .then(data => setApkInfo(data))
      .catch(() => setApkInfo({ available: false }));
  }, []);

  const handleDownload = () => {
    setShowSafetyInfo(true);
  };

  const confirmDownload = () => {
    setDownloading(true);
    // Direct link to backend download endpoint
    window.location.href = `${API_URL}/download/android`;
    setTimeout(() => setDownloading(false), 3000);
    setShowSafetyInfo(false);
  };

  return (
    <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-2xl p-8 text-white">
      <div className="flex items-center gap-3 mb-4">
        <Smartphone className="w-8 h-8" />
        <div>
          <h3 className="text-xl font-bold">Download Android App</h3>
          <p className="text-blue-200 text-sm">Auto-detect bank SMS • Works offline • Sync everywhere</p>
        </div>
      </div>

      {/* Key features */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-6">
        {[
          'Automatic SMS detection',
          'Works on any network',
          'Real-time sync to web',
        ].map(f => (
          <div key={f} className="flex items-center gap-2 text-sm text-blue-100">
            <CheckCircle className="w-4 h-4 text-green-300 flex-shrink-0" />
            {f}
          </div>
        ))}
      </div>

      {/* APK info */}
      {apkInfo?.available && (
        <div className="bg-blue-800/40 rounded-lg px-4 py-2 mb-4 flex flex-wrap gap-4 text-sm text-blue-200">
          <span>Version {apkInfo.version}</span>
          <span>{apkInfo.size_mb} MB</span>
          <span>{apkInfo.min_android}</span>
        </div>
      )}

      {/* Download button */}
      {apkInfo === null ? (
        <div className="h-10 w-40 bg-blue-500 rounded animate-pulse" />
      ) : apkInfo.available ? (
        <button
          onClick={handleDownload}
          disabled={downloading}
          className="flex items-center gap-2 bg-white text-blue-700 font-semibold px-6 py-3 rounded-lg hover:bg-blue-50 transition-colors disabled:opacity-60"
        >
          <Download className="w-5 h-5" />
          {downloading ? 'Starting download...' : 'Download APK'}
        </button>
      ) : (
        <div className="text-blue-200 text-sm bg-blue-800/40 rounded-lg px-4 py-3">
          📱 Android app coming soon — use the web app in the meantime
        </div>
      )}

      {/* Safety notice */}
      <div className="mt-4 flex items-start gap-2 text-xs text-blue-200">
        <ShieldCheck className="w-4 h-4 flex-shrink-0 mt-0.5" />
        <span>
          Direct download from our secure server. No Play Store listing required.
          Enable "Install from unknown sources" in Android settings to install.
        </span>
      </div>

      {/* Safety confirmation modal */}
      {showSafetyInfo && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
          <div className="bg-white text-slate-900 rounded-xl max-w-sm w-full p-6">
            <div className="flex items-center gap-3 mb-4">
              <ShieldCheck className="w-6 h-6 text-green-600" />
              <h3 className="font-bold text-lg">Before you download</h3>
            </div>

            <div className="space-y-3 text-sm text-slate-600 mb-6">
              <div className="flex gap-2">
                <span className="text-green-600 font-bold">✓</span>
                <span>This APK is built directly from our source code and served from our own server</span>
              </div>
              <div className="flex gap-2">
                <span className="text-green-600 font-bold">✓</span>
                <span>SHA-256 checksum available to verify file integrity after download</span>
              </div>
              <div className="flex gap-2">
                <span className="text-green-600 font-bold">✓</span>
                <span>The app only reads SMS from bank senders and never shares your data with third parties</span>
              </div>
              <div className="flex gap-2">
                <span className="text-amber-600 font-bold">!</span>
                <span>You'll need to allow "Install from unknown sources" on your Android phone to install</span>
              </div>
              {apkInfo?.sha256 && (
                <div className="bg-slate-50 rounded p-2 mt-2">
                  <p className="text-xs font-mono text-slate-500 break-all">
                    SHA-256: {apkInfo.sha256}
                  </p>
                </div>
              )}
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setShowSafetyInfo(false)}
                className="flex-1 border border-slate-300 rounded-lg py-2 text-sm hover:bg-slate-50"
              >
                Cancel
              </button>
              <button
                onClick={confirmDownload}
                className="flex-1 bg-blue-600 text-white rounded-lg py-2 text-sm font-semibold hover:bg-blue-700"
              >
                Download
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Navigation */}
      <nav className="flex items-center justify-between px-6 py-4 bg-white shadow-sm">
        <h1 className="text-2xl font-bold text-slate-900">SpendControl</h1>
        <div className="flex gap-4">
          <Link href="/login">
            <Button variant="outline">Sign In</Button>
          </Link>
          <Link href="/register">
            <Button>Get Started</Button>
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="max-w-6xl mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <h2 className="text-5xl font-bold text-slate-900 mb-4">
            Take Control of Your Spending
          </h2>
          <p className="text-xl text-slate-600 mb-8">
            Smart financial management made simple. Track expenses, visualize trends, and reach your financial goals.
          </p>
          <div className="flex flex-wrap gap-4 justify-center">
            <Link href="/register">
              <Button size="lg">Start Free Today</Button>
            </Link>
            <Link href="/login">
              <Button size="lg" variant="outline">Sign In</Button>
            </Link>
          </div>
        </div>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 py-12">
          <div className="p-8 bg-white rounded-lg shadow-sm">
            <BarChart3 className="w-12 h-12 text-blue-600 mb-4" />
            <h3 className="text-lg font-semibold mb-2">Smart Dashboard</h3>
            <p className="text-slate-600">
              Get a complete overview of your finances with beautiful charts and real-time insights.
            </p>
          </div>

          <div className="p-8 bg-white rounded-lg shadow-sm">
            <TrendingDown className="w-12 h-12 text-green-600 mb-4" />
            <h3 className="text-lg font-semibold mb-2">Track Spending</h3>
            <p className="text-slate-600">
              Categorize transactions and understand your spending patterns at a glance.
            </p>
          </div>

          <div className="p-8 bg-white rounded-lg shadow-sm">
            <Lock className="w-12 h-12 text-purple-600 mb-4" />
            <h3 className="text-lg font-semibold mb-2">Secure & Private</h3>
            <p className="text-slate-600">
              Your financial data is encrypted and secure. We never share your information.
            </p>
          </div>
        </div>

        {/* Download Section */}
        <div className="py-8">
          <DownloadSection />
        </div>
      </main>
    </div>
  );
}
