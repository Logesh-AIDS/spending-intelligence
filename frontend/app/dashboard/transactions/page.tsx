'use client';

import { useRef, useState } from 'react';
import { Sidebar } from '@/components/layout/Sidebar';
import { Header } from '@/components/layout/Header';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Skeleton } from '@/components/ui/skeleton';
import {
  useTransactions,
  useDeleteTransaction,
  useUploadStatement,
  type TransactionFilters,
} from '@/lib/hooks/useTransactions';
import {
  Plus,
  Trash2,
  Search,
  ChevronLeft,
  ChevronRight,
  Upload,
  FileText,
  CheckCircle2,
  AlertCircle,
  X,
} from 'lucide-react';

const CATEGORIES = [
  'Food', 'Shopping', 'Travel', 'Bills', 'Health',
  'Entertainment', 'Education', 'Salary', 'Others',
];

// ── PDF Upload Modal ──────────────────────────────────────────────
function PDFUploadModal({ onClose }: { onClose: () => void }) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const { mutate: upload, isPending, error, isSuccess, data } = useUploadStatement();

  const handleFile = (file: File) => {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      alert('Please select a PDF file.');
      return;
    }
    setSelectedFile(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;
    upload(selectedFile);
  };

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-lg p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-5">
          <div>
            <h2 className="text-lg font-semibold">Upload Bank Statement</h2>
            <p className="text-slate-500 text-sm mt-0.5">
              Canara Bank PDF statements supported
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 transition-colors"
            aria-label="Close"
          >
            <X size={20} />
          </button>
        </div>

        {/* Success state */}
        {isSuccess && data && (
          <div className="rounded-lg bg-green-50 border border-green-200 p-4 mb-4">
            <div className="flex items-center gap-2 text-green-700 font-medium mb-2">
              <CheckCircle2 size={18} />
              Import complete
            </div>
            <ul className="text-sm text-green-800 space-y-1">
              <li>Transactions found in PDF: <strong>{data.total_parsed}</strong></li>
              <li>Imported: <strong>{data.imported}</strong></li>
              <li>Skipped (duplicates): <strong>{data.skipped_duplicates}</strong></li>
            </ul>
            <Button className="w-full mt-4" onClick={onClose}>
              Done
            </Button>
          </div>
        )}

        {/* Upload form */}
        {!isSuccess && (
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Drop zone */}
            <div
              className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                dragOver
                  ? 'border-blue-400 bg-blue-50'
                  : selectedFile
                  ? 'border-green-400 bg-green-50'
                  : 'border-slate-300 hover:border-slate-400 bg-slate-50'
              }`}
              onClick={() => fileInputRef.current?.click()}
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={handleDrop}
            >
              {selectedFile ? (
                <div className="flex flex-col items-center gap-2">
                  <FileText className="text-green-600" size={36} />
                  <p className="font-medium text-green-700 text-sm">{selectedFile.name}</p>
                  <p className="text-xs text-slate-500">
                    {(selectedFile.size / 1024).toFixed(1)} KB
                  </p>
                  <button
                    type="button"
                    className="text-xs text-slate-400 hover:text-red-500 underline mt-1"
                    onClick={(e) => { e.stopPropagation(); setSelectedFile(null); }}
                  >
                    Remove
                  </button>
                </div>
              ) : (
                <div className="flex flex-col items-center gap-2 text-slate-500">
                  <Upload size={36} className="text-slate-400" />
                  <p className="font-medium text-sm">
                    Drop your PDF here or <span className="text-blue-600 underline">browse</span>
                  </p>
                  <p className="text-xs text-slate-400">PDF only · Max 10 MB</p>
                </div>
              )}
            </div>

            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,application/pdf"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) handleFile(file);
              }}
            />

            {/* Error */}
            {error && (
              <div className="flex items-start gap-2 rounded-lg bg-red-50 border border-red-200 p-3 text-sm text-red-700">
                <AlertCircle size={16} className="mt-0.5 flex-shrink-0" />
                <span>
                  {(error as any)?.response?.data?.detail ||
                    'Failed to parse the statement. Make sure it is a valid Canara Bank PDF.'}
                </span>
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-3 justify-end pt-1">
              <Button type="button" variant="outline" onClick={onClose} disabled={isPending}>
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={!selectedFile || isPending}
                className="min-w-[120px]"
              >
                {isPending ? (
                  <span className="flex items-center gap-2">
                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                    </svg>
                    Importing…
                  </span>
                ) : (
                  'Import Transactions'
                )}
              </Button>
            </div>
          </form>
        )}
      </Card>
    </div>
  );
}

// ── Delete confirm ────────────────────────────────────────────────
function DeleteConfirm({ id, onClose }: { id: number; onClose: () => void }) {
  const { mutate: del, isPending } = useDeleteTransaction();
  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-sm p-6">
        <h2 className="text-lg font-semibold mb-2">Delete Transaction</h2>
        <p className="text-slate-600 text-sm mb-6">This action cannot be undone.</p>
        <div className="flex gap-3 justify-end">
          <Button variant="outline" onClick={onClose}>Cancel</Button>
          <Button
            variant="destructive"
            disabled={isPending}
            onClick={() => del(id, { onSuccess: onClose })}
          >
            {isPending ? 'Deleting...' : 'Delete'}
          </Button>
        </div>
      </Card>
    </div>
  );
}

// ── Main page ─────────────────────────────────────────────────────
export default function TransactionsPage() {
  const [filters, setFilters] = useState<TransactionFilters>({
    page: 1,
    page_size: 20,
    sort_by: 'created_at',
    sort_order: 'desc',
  });
  const [search, setSearch] = useState('');
  const [showUpload, setShowUpload] = useState(false);
  const [deleteId, setDeleteId] = useState<number | null>(null);

  const { data, isLoading, isError, error } = useTransactions(filters);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setFilters((f) => ({ ...f, search: search || undefined, page: 1 }));
  };

  const setPage = (page: number) => setFilters((f) => ({ ...f, page }));

  return (
    <div className="flex h-screen bg-background">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto">
          <div className="container mx-auto py-8 px-4 space-y-6">

            {/* Title + Actions */}
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold">Transactions</h1>
                <p className="text-slate-600">Manage and search your transactions</p>
              </div>
              <Button
                onClick={() => setShowUpload(true)}
                className="flex items-center gap-2"
              >
                <Upload size={16} />
                Upload Statement
              </Button>
            </div>

            {/* Filters */}
            <Card className="p-4">
              <div className="flex flex-wrap gap-3 items-end">
                <form onSubmit={handleSearch} className="flex gap-2 flex-1 min-w-[200px]">
                  <Input
                    placeholder="Search merchant, bank, UPI..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    className="flex-1"
                  />
                  <Button type="submit" variant="outline" size="sm">
                    <Search size={16} />
                  </Button>
                </form>

                <select
                  className="border border-slate-300 rounded-md px-3 py-2 text-sm bg-white"
                  value={filters.transaction_type || ''}
                  onChange={(e) =>
                    setFilters((f) => ({
                      ...f,
                      transaction_type: (e.target.value as any) || undefined,
                      page: 1,
                    }))
                  }
                >
                  <option value="">All Types</option>
                  <option value="Debit">Debit</option>
                  <option value="Credit">Credit</option>
                </select>

                <select
                  className="border border-slate-300 rounded-md px-3 py-2 text-sm bg-white"
                  value={filters.category || ''}
                  onChange={(e) =>
                    setFilters((f) => ({
                      ...f,
                      category: e.target.value || undefined,
                      page: 1,
                    }))
                  }
                >
                  <option value="">All Categories</option>
                  {CATEGORIES.map((c) => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>

                <select
                  className="border border-slate-300 rounded-md px-3 py-2 text-sm bg-white"
                  value={`${filters.sort_by}:${filters.sort_order}`}
                  onChange={(e) => {
                    const [sort_by, sort_order] = e.target.value.split(':') as any;
                    setFilters((f) => ({ ...f, sort_by, sort_order, page: 1 }));
                  }}
                >
                  <option value="created_at:desc">Newest First</option>
                  <option value="created_at:asc">Oldest First</option>
                  <option value="amount:desc">Highest Amount</option>
                  <option value="amount:asc">Lowest Amount</option>
                  <option value="merchant:asc">Merchant A-Z</option>
                </select>

                {(filters.search || filters.transaction_type || filters.category) && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      setSearch('');
                      setFilters({
                        page: 1,
                        page_size: 20,
                        sort_by: 'created_at',
                        sort_order: 'desc',
                      });
                    }}
                  >
                    Clear Filters
                  </Button>
                )}
              </div>
            </Card>

            {/* Table */}
            <Card className="overflow-hidden">
              {isLoading && (
                <div className="p-4 space-y-3">
                  {[1, 2, 3, 4, 5].map((i) => (
                    <Skeleton key={i} className="h-12 w-full" />
                  ))}
                </div>
              )}

              {isError && (
                <div className="p-8 text-center text-red-600">
                  <p className="font-medium">Failed to load transactions</p>
                  <p className="text-sm mt-1 text-slate-500">
                    {(error as any)?.message}
                  </p>
                </div>
              )}

              {!isLoading && !isError && !data?.transactions?.length && (
                <div className="p-12 text-center">
                  <FileText className="mx-auto mb-4 text-slate-300" size={48} />
                  <p className="text-slate-600 font-medium">No transactions yet</p>
                  <p className="text-slate-500 text-sm mt-1">
                    Click <strong>Upload Statement</strong> to import your bank PDF
                  </p>
                  <Button
                    className="mt-4 flex items-center gap-2 mx-auto"
                    onClick={() => setShowUpload(true)}
                  >
                    <Upload size={16} />
                    Upload Statement
                  </Button>
                </div>
              )}

              {!isLoading && data?.transactions && data.transactions.length > 0 && (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-slate-50 border-b border-slate-200">
                      <tr>
                        <th className="text-left px-4 py-3 font-medium text-slate-600">Date</th>
                        <th className="text-left px-4 py-3 font-medium text-slate-600">Merchant</th>
                        <th className="text-left px-4 py-3 font-medium text-slate-600">Category</th>
                        <th className="text-left px-4 py-3 font-medium text-slate-600">Bank</th>
                        <th className="text-right px-4 py-3 font-medium text-slate-600">Amount</th>
                        <th className="text-right px-4 py-3 font-medium text-slate-600">Balance</th>
                        <th className="px-4 py-3"></th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {data.transactions.map((txn) => (
                        <tr
                          key={txn.id}
                          className="hover:bg-slate-50 transition-colors"
                        >
                          <td className="px-4 py-3 text-slate-600">{txn.date}</td>
                          <td className="px-4 py-3 font-medium">{txn.merchant || '—'}</td>
                          <td className="px-4 py-3">
                            <span className="px-2 py-0.5 rounded-full text-xs bg-slate-100 text-slate-700">
                              {txn.category}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-slate-600">{txn.bank}</td>
                          <td
                            className={`px-4 py-3 text-right font-semibold ${
                              txn.transaction_type === 'Credit'
                                ? 'text-green-600'
                                : 'text-red-600'
                            }`}
                          >
                            {txn.transaction_type === 'Credit' ? '+' : '-'}₹
                            {txn.amount.toLocaleString('en-IN', {
                              minimumFractionDigits: 2,
                            })}
                          </td>
                          <td className="px-4 py-3 text-right text-slate-600">
                            {txn.balance != null
                              ? `₹${txn.balance.toLocaleString('en-IN', {
                                  minimumFractionDigits: 2,
                                })}`
                              : '—'}
                          </td>
                          <td className="px-4 py-3 text-right">
                            <button
                              onClick={() => setDeleteId(txn.id)}
                              className="text-slate-400 hover:text-red-500 transition-colors"
                              aria-label="Delete transaction"
                            >
                              <Trash2 size={15} />
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {/* Pagination */}
              {data && data.total_pages > 1 && (
                <div className="px-4 py-3 border-t border-slate-200 flex items-center justify-between">
                  <p className="text-sm text-slate-600">
                    {data.total_records} transactions · Page {data.current_page} of{' '}
                    {data.total_pages}
                  </p>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={!data.has_previous}
                      onClick={() => setPage((filters.page || 1) - 1)}
                    >
                      <ChevronLeft size={16} />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={!data.has_next}
                      onClick={() => setPage((filters.page || 1) + 1)}
                    >
                      <ChevronRight size={16} />
                    </Button>
                  </div>
                </div>
              )}
            </Card>
          </div>
        </main>
      </div>

      {showUpload && <PDFUploadModal onClose={() => setShowUpload(false)} />}
      {deleteId !== null && (
        <DeleteConfirm id={deleteId} onClose={() => setDeleteId(null)} />
      )}
    </div>
  );
}
