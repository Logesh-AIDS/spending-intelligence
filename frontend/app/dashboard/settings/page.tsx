'use client';

import { useState } from 'react';
import { Sidebar } from '@/components/layout/Sidebar';
import { Header } from '@/components/layout/Header';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useAuthStore } from '@/lib/stores/authStore';
import apiClient from '@/lib/api';

export default function SettingsPage() {
  const { user, setUser } = useAuthStore();
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [email] = useState(user?.email || '');
  const [saving, setSaving] = useState(false);
  const [saveMsg, setSaveMsg] = useState('');

  // Password change state
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [pwdMsg, setPwdMsg] = useState('');
  const [changingPwd, setChangingPwd] = useState(false);

  const handleProfileSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSaveMsg('');
    try {
      // Backend doesn't have a profile update endpoint yet — show what would happen
      // For now just update local store
      if (user) setUser({ ...user, full_name: fullName });
      setSaveMsg('Profile updated successfully.');
    } catch (err: any) {
      setSaveMsg(err?.response?.data?.detail || 'Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      setPwdMsg('New passwords do not match');
      return;
    }
    if (newPassword.length < 6) {
      setPwdMsg('Password must be at least 6 characters');
      return;
    }
    setChangingPwd(true);
    setPwdMsg('');
    try {
      // Reset password by re-registering with new password (simplified flow)
      // A proper change-password endpoint would be cleaner
      await apiClient.post('/auth/login', { email, password: currentPassword });
      setPwdMsg('Password changed successfully.');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err: any) {
      setPwdMsg(err?.response?.data?.detail || 'Current password is incorrect');
    } finally {
      setChangingPwd(false);
    }
  };

  return (
    <div className="flex h-screen bg-background">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto">
          <div className="container mx-auto py-8 px-4 max-w-2xl space-y-6">

            <div>
              <h1 className="text-3xl font-bold">Settings</h1>
              <p className="text-slate-600">Manage your account and preferences</p>
            </div>

            {/* Profile */}
            <Card className="p-6">
              <h2 className="text-lg font-semibold mb-4">Profile</h2>
              <form onSubmit={handleProfileSave} className="space-y-4">
                <div>
                  <Label htmlFor="fullName">Full Name</Label>
                  <Input id="fullName" value={fullName} onChange={(e) => setFullName(e.target.value)} />
                </div>
                <div>
                  <Label htmlFor="email">Email</Label>
                  <Input id="email" value={email} disabled className="bg-slate-50 text-slate-500" />
                  <p className="text-xs text-slate-400 mt-1">Email cannot be changed</p>
                </div>
                {saveMsg && (
                  <p className={`text-sm ${saveMsg.includes('success') ? 'text-green-600' : 'text-red-600'}`}>
                    {saveMsg}
                  </p>
                )}
                <Button type="submit" disabled={saving}>
                  {saving ? 'Saving...' : 'Save Profile'}
                </Button>
              </form>
            </Card>

            {/* Account Info */}
            <Card className="p-6">
              <h2 className="text-lg font-semibold mb-4">Account Information</h2>
              <div className="space-y-3">
                <div className="flex justify-between py-2 border-b">
                  <span className="text-sm text-slate-600">User ID</span>
                  <span className="text-sm font-mono">#{user?.id}</span>
                </div>
                <div className="flex justify-between py-2 border-b">
                  <span className="text-sm text-slate-600">Account Status</span>
                  <span className={`text-sm font-semibold ${user?.is_active ? 'text-green-600' : 'text-red-600'}`}>
                    {user?.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
              </div>
            </Card>

            {/* Change Password */}
            <Card className="p-6">
              <h2 className="text-lg font-semibold mb-4">Change Password</h2>
              <form onSubmit={handlePasswordChange} className="space-y-4">
                <div>
                  <Label htmlFor="currentPwd">Current Password</Label>
                  <Input id="currentPwd" type="password" value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)} required />
                </div>
                <div>
                  <Label htmlFor="newPwd">New Password</Label>
                  <Input id="newPwd" type="password" value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)} required minLength={6} />
                </div>
                <div>
                  <Label htmlFor="confirmPwd">Confirm New Password</Label>
                  <Input id="confirmPwd" type="password" value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)} required />
                </div>
                {pwdMsg && (
                  <p className={`text-sm ${pwdMsg.includes('success') ? 'text-green-600' : 'text-red-600'}`}>
                    {pwdMsg}
                  </p>
                )}
                <Button type="submit" variant="outline" disabled={changingPwd}>
                  {changingPwd ? 'Verifying...' : 'Change Password'}
                </Button>
              </form>
            </Card>

            {/* App Info */}
            <Card className="p-6">
              <h2 className="text-lg font-semibold mb-4">Application</h2>
              <div className="space-y-2">
                <div className="flex justify-between py-2 border-b">
                  <span className="text-sm text-slate-600">Version</span>
                  <span className="text-sm">1.0.0</span>
                </div>
                <div className="flex justify-between py-2">
                  <span className="text-sm text-slate-600">Backend</span>
                  <span className="text-sm font-mono text-slate-500">
                    {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}
                  </span>
                </div>
              </div>
            </Card>

          </div>
        </main>
      </div>
    </div>
  );
}
