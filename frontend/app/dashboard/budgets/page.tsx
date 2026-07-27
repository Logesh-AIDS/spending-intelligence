'use client';

import { useState } from 'react';
import { Sidebar } from '@/components/layout/Sidebar';
import { Header } from '@/components/layout/Header';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Skeleton } from '@/components/ui/skeleton';
import { useGoals, useCreateGoal, useEvaluateGoal, useDeleteGoal, type GoalCreate } from '@/lib/hooks/useGoals';
import { Plus, Trash2, RefreshCw, Target } from 'lucide-react';

const GOAL_TYPES = [
  { value: 'save', label: 'Save Amount' },
  { value: 'limit_category', label: 'Limit Category Spend' },
  { value: 'limit_spending', label: 'Limit Monthly Spending' },
  { value: 'emergency_fund', label: 'Build Emergency Fund' },
];

const CATEGORIES = ['Food', 'Shopping', 'Travel', 'Bills', 'Health', 'Entertainment', 'Education', 'Others'];

const predictionColors: Record<string, string> = {
  on_track: 'text-green-600 bg-green-50',
  at_risk: 'text-yellow-600 bg-yellow-50',
  achieved: 'text-blue-600 bg-blue-50',
  failed: 'text-red-600 bg-red-50',
};

function CreateGoalModal({ onClose }: { onClose: () => void }) {
  const [form, setForm] = useState<GoalCreate>({ title: '', goal_type: 'save', target_amount: 0 });
  const { mutate: create, isPending, error } = useCreateGoal();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    create(form, { onSuccess: onClose });
  };

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md p-6">
        <h2 className="text-lg font-semibold mb-4">Create New Budget Goal</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="title">Goal Title</Label>
            <Input id="title" placeholder="e.g. Save ₹5000 this month"
              value={form.title} onChange={(e) => setForm(f => ({ ...f, title: e.target.value }))} required />
          </div>
          <div>
            <Label>Goal Type</Label>
            <select className="w-full border border-slate-300 rounded-md px-3 py-2 text-sm bg-white mt-1"
              value={form.goal_type} onChange={(e) => setForm(f => ({ ...f, goal_type: e.target.value as any }))}>
              {GOAL_TYPES.map(g => <option key={g.value} value={g.value}>{g.label}</option>)}
            </select>
          </div>
          {form.goal_type === 'limit_category' && (
            <div>
              <Label>Category</Label>
              <select className="w-full border border-slate-300 rounded-md px-3 py-2 text-sm bg-white mt-1"
                value={form.category || ''} onChange={(e) => setForm(f => ({ ...f, category: e.target.value }))}>
                <option value="">Select category</option>
                {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
          )}
          <div>
            <Label htmlFor="target">Target Amount (₹)</Label>
            <Input id="target" type="number" min={1} placeholder="5000"
              value={form.target_amount || ''} onChange={(e) => setForm(f => ({ ...f, target_amount: Number(e.target.value) }))} required />
          </div>
          <div>
            <Label htmlFor="deadline">Deadline (DD/MM/YY, optional)</Label>
            <Input id="deadline" placeholder="31/07/26"
              value={form.deadline || ''} onChange={(e) => setForm(f => ({ ...f, deadline: e.target.value || undefined }))} />
          </div>
          {error && <p className="text-red-600 text-sm">{(error as any)?.response?.data?.detail || 'Failed to create goal'}</p>}
          <div className="flex gap-3 justify-end">
            <Button type="button" variant="outline" onClick={onClose}>Cancel</Button>
            <Button type="submit" disabled={isPending || !form.title || !form.target_amount}>
              {isPending ? 'Creating...' : 'Create Goal'}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}

export default function BudgetsPage() {
  const [showCreate, setShowCreate] = useState(false);
  const { data: goals, isLoading, isError } = useGoals();
  const { mutate: evaluate, isPending: evaluating } = useEvaluateGoal();
  const { mutate: deleteGoal } = useDeleteGoal();

  return (
    <div className="flex h-screen bg-background">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto">
          <div className="container mx-auto py-8 px-4 space-y-6">

            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold">Budget Goals</h1>
                <p className="text-slate-600">Track your financial goals with AI predictions</p>
              </div>
              <Button onClick={() => setShowCreate(true)} className="flex items-center gap-2">
                <Plus size={16} /> New Goal
              </Button>
            </div>

            {isLoading && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {[1, 2, 3].map(i => <Skeleton key={i} className="h-40 rounded-lg" />)}
              </div>
            )}

            {isError && (
              <Card className="p-8 text-center text-red-600">
                <p>Failed to load goals</p>
              </Card>
            )}

            {!isLoading && !goals?.length && (
              <Card className="p-12 text-center">
                <Target className="mx-auto mb-4 text-slate-300" size={48} />
                <p className="text-slate-600 font-medium">No budget goals yet</p>
                <p className="text-slate-500 text-sm mt-1">Create a goal to start tracking your financial targets</p>
              </Card>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {goals?.map((goal) => (
                <Card key={goal.id} className="p-5">
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h3 className="font-semibold">{goal.title}</h3>
                      <p className="text-sm text-slate-500 capitalize">{goal.goal_type.replace('_', ' ')}{goal.category ? ` · ${goal.category}` : ''}</p>
                    </div>
                    <div className="flex gap-2">
                      <button onClick={() => evaluate(goal.id)} className="text-slate-400 hover:text-blue-500" title="Evaluate progress">
                        <RefreshCw size={15} className={evaluating ? 'animate-spin' : ''} />
                      </button>
                      <button onClick={() => deleteGoal(goal.id)} className="text-slate-400 hover:text-red-500">
                        <Trash2 size={15} />
                      </button>
                    </div>
                  </div>

                  {/* Progress bar */}
                  <div className="mb-3">
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-slate-600">₹{goal.current_amount.toLocaleString('en-IN')} / ₹{goal.target_amount.toLocaleString('en-IN')}</span>
                      <span className="font-semibold">{goal.progress_percentage.toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all ${goal.progress_percentage >= 100 ? 'bg-green-500' : goal.progress_percentage >= 60 ? 'bg-blue-500' : 'bg-yellow-500'}`}
                        style={{ width: `${Math.min(goal.progress_percentage, 100)}%` }}
                      />
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    {goal.ai_prediction && (
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${predictionColors[goal.ai_prediction] || 'text-slate-600 bg-slate-100'}`}>
                        {goal.ai_prediction.replace('_', ' ')}
                      </span>
                    )}
                    {goal.deadline && <span className="text-xs text-slate-500">Due: {goal.deadline}</span>}
                    {goal.is_achieved && <span className="text-xs text-green-600 font-semibold">✓ Achieved</span>}
                  </div>
                </Card>
              ))}
            </div>
          </div>
        </main>
      </div>
      {showCreate && <CreateGoalModal onClose={() => setShowCreate(false)} />}
    </div>
  );
}
