'use client';

import { useState } from 'react';
import { Sidebar } from '@/components/layout/Sidebar';
import { Header } from '@/components/layout/Header';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Skeleton } from '@/components/ui/skeleton';
import {
  useTransactions,
  useDeleteTransaction,
  useSendSMS,
  type TransactionFilters,
} from '@/lib/hooks/useTransactions';
import { Plus, Trash2, Search, ChevronLeft, ChevronRight, MessageSquare } from 'lucide-react';

const CATEGORIES = ['Food', 'Shopping', 'Travel', 'Bills', 'Health', 'Entertainment', 'Education', 'Salary', 'Others'];

// ── SMS Modal ─────────────────────────────────────────────────────
function SMSModal({ onClose }: { onClose: () => void }) {
  const [sms, setSms] = useState('');
  const { mutate: sendSMS, isPending, error, isSuccess } = useSendSMS();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendSMS(sms, { onSuccess: () => { setSms(''); onClose(); } });
  };

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-lg p-6">
        <h2 className="text-lg font-semibold mb-4">Parse Bank SMS</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-sm font-medium text-slate-700 mb-1 block">Raw SMS Text</label>
            <textarea
              className="w-full border border-slate-300 rounded-md p-3 text-sm min-h-[100px] focus:outline-none focus:ring-2 focus:ring-slate-900"
              placeholder="Paste your bank SMS here..."
              value={sms}
              onChange={(e) => setSms(e.target.value)}
              required
            />
          </div>
          {error && <p className="text-red-600 text-sm">{(error as any)?.response?.data?.detail || 'Failed to parse SMS'}</p>}
          <div className="flex gap-3 justify-end">
            <Button type="button" variant="outline" onClick={onClose}>Cancel</Button>
            <Button type="submit" disabled={isPending || !sms.trim()}>
              {isPending ? 'Parsing...' : 'Parse & Save'}
            </Button>
          </div>
        </form>
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
          <Button variant="destructive" disabled={isPending}
            onClick={() => del(id, { onSuccess: onClose })}>
            {isPending ? 'Deleting...' : 'Delete'}
          </Button>
        </div>
      </Card>
    </div>
  );
}

// ── Main page ─────────────────────────────────────────────────────
export default function TransactionsPage() {
  const [filters, setFilters] = useState<TransactionFilters>({ page: 1, page_size: 20, sort_by: 'created_at', sort_order: 'desc' });
  const [search, setSearch] = useState('');
  const [showSMS, setShowSMS] = useState(false);
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
              <Button onClick={() => setShowSMS(true)} className="flex items-center gap-2">
                <MessageSquare size={16} /> Parse SMS
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
                  onChange={(e) => setFilters((f) => ({ ...f, transaction_type: (e.target.value as any) || undefined, page: 1 }))}
                >
                  <option value="">All Types</option>
                  <option value="Debit">Debit</option>
                  <option value="Credit">Credit</option>
                </select>

                <select
                  className="border border-slate-300 rounded-md px-3 py-2 text-sm bg-white"
                  value={filters.category || ''}
                  onChange={(e) => setFilters((f) => ({ ...f, category: e.target.value || undefined, page: 1 }))}
                >
                  <option value="">All Categories</option>
                  {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
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
                  <Button variant="ghost" size="sm" onClick={() => { setSearch(''); setFilters({ page: 1, page_size: 20, sort_by: 'created_at', sort_order: 'desc' }); }}>
                    Clear Filters
                  </Button>
                )}
              </div>
            </Card>

            {/* Table */}
            <Card className="overflow-hidden">
              {isLoading && (
                <div className="p-4 space-y-3">
                  {[1, 2, 3, 4, 5].map((i) => <Skeleton key={i} className="h-12 w-full" />)}
                </div>
              )}

              {isError && (
                <div className="p-8 text-center text-red-600">
                  <p className="font-medium">Failed to load transactions</p>
                  <p className="text-sm mt-1 text-slate-500">{(error as any)?.message}</p>
                </div>
              )}

              {!isLoading && !isError && (!data?.transactions?.length) && (
                <div className="p-12 text-center">
                  <MessageSquare className="mx-auto mb-4 text-slate-300" size={48} />
                  <p className="text-slate-600 font-medium">No transactions yet</p>
                  <p className="text-slate-500 text-sm mt-1">Click "Parse SMS" to add your first transaction</p>
                </div>
              )}

              {!isLoading && data?.transactions?.length > 0 && (
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
                        <tr key={txn.id} className="hover:bg-slate-50 transition-colors">
                          <td className="px-4 py-3 text-slate-600">{txn.date}</td>
                          <td className="px-4 py-3 font-medium">{txn.merchant || '—'}</td>
                          <td className="px-4 py-3">
                            <span className="px-2 py-0.5 rounded-full text-xs bg-slate-100 text-slate-700">
                              {txn.category}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-slate-600">{txn.bank}</td>
                          <td className={`px-4 py-3 text-right font-semibold ${txn.transaction_type === 'Credit' ? 'text-green-600' : 'text-red-600'}`}>
                            {txn.transaction_type === 'Credit' ? '+' : '-'}₹{txn.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                          </td>
                          <td className="px-4 py-3 text-right text-slate-600">
                            {txn.balance != null ? `₹${txn.balance.toLocaleString('en-IN', { minimumFractionDigits: 2 })}` : '—'}
                          </td>
                          <td className="px-4 py-3 text-right">
                            <button onClick={() => setDeleteId(txn.id)} className="text-slate-400 hover:text-red-500 transition-colors">
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
                    {data.total_records} transactions · Page {data.current_page} of {data.total_pages}
                  </p>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" disabled={!data.has_previous} onClick={() => setPage((filters.page || 1) - 1)}>
                      <ChevronLeft size={16} />
                    </Button>
                    <Button variant="outline" size="sm" disabled={!data.has_next} onClick={() => setPage((filters.page || 1) + 1)}>
                      <ChevronRight size={16} />
                    </Button>
                  </div>
                </div>
              )}
            </Card>
          </div>
        </main>
      </div>

      {showSMS && <SMSModal onClose={() => setShowSMS(false)} />}
      {deleteId !== null && <DeleteConfirm id={deleteId} onClose={() => setDeleteId(null)} />}
    </div>
  );
}
