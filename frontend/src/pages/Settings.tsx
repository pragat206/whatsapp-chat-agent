import { useEffect, useState } from 'react';
import { Settings as SettingsIcon, Save } from 'lucide-react';
import { Card, CardContent, CardHeader } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { settingsApi } from '../services/api';
import type { Setting } from '../types';
import toast from 'react-hot-toast';

export default function Settings() {
  const [settings, setSettings] = useState<Setting[]>([]);
  const [editValues, setEditValues] = useState<Record<string, string>>({});

  useEffect(() => {
    settingsApi.list().then((res) => {
      const data = res.data || [];
      setSettings(data);
      const vals: Record<string, string> = {};
      data.forEach((s: Setting) => { vals[s.key] = s.value || ''; });
      setEditValues(vals);
    }).catch(() => {});
  }, []);

  const handleSave = async (key: string) => {
    try {
      await settingsApi.update(key, { value: editValues[key] });
      toast.success(`Setting "${key}" updated`);
    } catch {
      toast.error('Failed to update setting');
    }
  };

  const categories = [...new Set(settings.map((s) => s.category))];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-500 mt-1">Configure your WhatsApp AI agent platform</p>
      </div>

      {categories.map((category) => (
        <Card key={category}>
          <CardHeader>
            <h3 className="text-sm font-semibold text-gray-900 capitalize flex items-center gap-2">
              <SettingsIcon className="w-4 h-4" />
              {category}
            </h3>
          </CardHeader>
          <CardContent className="space-y-4">
            {settings
              .filter((s) => s.category === category)
              .map((setting) => (
                <div key={setting.key} className="flex items-start gap-4">
                  <div className="flex-1">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {setting.key.replace(/_/g, ' ')}
                    </label>
                    {setting.description && (
                      <p className="text-xs text-gray-400 mb-1.5">{setting.description}</p>
                    )}
                    <input
                      className="w-full px-3.5 py-2.5 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                      value={editValues[setting.key] || ''}
                      onChange={(e) =>
                        setEditValues({ ...editValues, [setting.key]: e.target.value })
                      }
                    />
                  </div>
                  <Button
                    variant="secondary"
                    size="sm"
                    className="mt-7"
                    onClick={() => handleSave(setting.key)}
                  >
                    <Save className="w-4 h-4" />
                  </Button>
                </div>
              ))}
          </CardContent>
        </Card>
      ))}

      {settings.length === 0 && (
        <Card>
          <CardContent className="py-16 text-center">
            <SettingsIcon className="w-8 h-8 text-gray-300 mx-auto mb-3" />
            <p className="text-sm text-gray-400">No settings configured yet. Run the seed script to populate defaults.</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
