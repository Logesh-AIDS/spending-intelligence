'use client';

import { Card } from '@/components/ui/card';
import type { RecentTransaction } from '@/lib/hooks/useDashboard';

interface Props {
  transactions: RecentTransaction[];
}

export function RecentTransactions({ transactions }: Props) {
  if (!transactions?.length) {
    return (
      <Card className="p-6">
        <h2 className="text-lg font-semibold mb-4">Recent Transactions</h2>
        <p className="text-slate-500 text-sm">No transactions yet. Send an SMS to get started.</p>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <h2 className="text-lg font-semibold mb-4">Recent Transactions</h2>
      <div className="space-y-3">
        {transactions.map((txn) => (
          <div key={txn.id} className="flex items-center justify-between py-2 border-b last:border-0">
            <div className="flex-1">
              <p className="text-sm font-medium text-slate-800">
                {txn.merchant || txn.bank}
              </p>
              <p className="text-xs text-slate-500">
                {txn.category} · {txn.date}
              </p>
            </div>
            <span
              className={`text-sm font-semibold ${
                txn.transaction_type === 'Credit' ? 'text-green-600' : 'text-red-600'
              }`}
            >
              {txn.transaction_type === 'Credit' ? '+' : '-'}
              ₹{txn.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
            </span>
          </div>
        ))}
      </div>
    </Card>
  );
}
