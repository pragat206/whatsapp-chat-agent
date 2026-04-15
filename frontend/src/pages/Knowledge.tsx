import { useEffect, useState, useRef, FormEvent } from 'react';
import { BookOpen, Upload, Plus, RefreshCw, ToggleLeft, ToggleRight, FileText, X } from 'lucide-react';
import { Card, CardContent, CardHeader } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { knowledgeApi } from '../services/api';
import { formatDate, formatFileSize } from '../lib/utils';
import type { KnowledgeSource } from '../types';
import toast from 'react-hot-toast';

export default function Knowledge() {
  const [sources, setSources] = useState<KnowledgeSource[]>([]);
  const [total, setTotal] = useState(0);
  const [showUpload, setShowUpload] = useState(false);
  const [showManual, setShowManual] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [manualTitle, setManualTitle] = useState('');
  const [manualContent, setManualContent] = useState('');
  const fileRef = useRef<HTMLInputElement>(null);
  const titleRef = useRef<HTMLInputElement>(null);

  const load = () => {
    knowledgeApi.list().then((res) => {
      setSources(res.data.sources || []);
      setTotal(res.data.total || 0);
    }).catch(() => {});
  };

  useEffect(() => { load(); }, []);

  const handleUpload = async (e: FormEvent) => {
    e.preventDefault();
    const file = fileRef.current?.files?.[0];
    const title = titleRef.current?.value;
    if (!file || !title) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);

    try {
      await knowledgeApi.upload(formData);
      toast.success('File uploaded successfully');
      setShowUpload(false);
      load();
    } catch {
      toast.error('Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleManualCreate = async (e: FormEvent) => {
    e.preventDefault();
    try {
      await knowledgeApi.manual({ title: manualTitle, content: manualContent });
      toast.success('Knowledge entry created');
      setShowManual(false);
      setManualTitle('');
      setManualContent('');
      load();
    } catch {
      toast.error('Failed to create entry');
    }
  };

  const handleToggle = async (id: string) => {
    try {
      await knowledgeApi.toggle(id);
      load();
    } catch {
      toast.error('Failed to toggle source');
    }
  };

  const handleReindex = async (id: string) => {
    try {
      await knowledgeApi.reindex(id);
      toast.success('Reindexing queued');
      load();
    } catch {
      toast.error('Failed to queue reindex');
    }
  };

  const typeIcon: Record<string, string> = {
    pdf: 'PDF', docx: 'DOC', txt: 'TXT', csv: 'CSV', xlsx: 'XLS', json: 'JSON', manual: 'TXT', url: 'URL',
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Knowledge Base</h1>
          <p className="text-gray-500 mt-1">{total} knowledge sources</p>
        </div>
        <div className="flex gap-3">
          <Button variant="secondary" onClick={() => setShowManual(true)}>
            <Plus className="w-4 h-4 mr-2" /> Manual Entry
          </Button>
          <Button onClick={() => setShowUpload(true)}>
            <Upload className="w-4 h-4 mr-2" /> Upload File
          </Button>
        </div>
      </div>

      {/* Upload Form */}
      {showUpload && (
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <h3 className="text-sm font-semibold">Upload Document</h3>
              <button onClick={() => setShowUpload(false)}><X className="w-4 h-4 text-gray-400" /></button>
            </div>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleUpload} className="space-y-4">
              <Input label="Title" ref={titleRef} required />
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">File</label>
                <input
                  ref={fileRef}
                  type="file"
                  accept=".pdf,.docx,.txt,.csv,.xlsx,.json"
                  className="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-brand-50 file:text-brand-700 hover:file:bg-brand-100"
                  required
                />
                <p className="text-xs text-gray-400 mt-1">Supported: PDF, DOCX, TXT, CSV, XLSX, JSON (max 50MB)</p>
              </div>
              <Button type="submit" disabled={uploading}>
                {uploading ? 'Uploading...' : 'Upload & Process'}
              </Button>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Manual Entry Form */}
      {showManual && (
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <h3 className="text-sm font-semibold">Manual Knowledge Entry</h3>
              <button onClick={() => setShowManual(false)}><X className="w-4 h-4 text-gray-400" /></button>
            </div>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleManualCreate} className="space-y-4">
              <Input label="Title" value={manualTitle} onChange={(e) => setManualTitle(e.target.value)} required />
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">Content</label>
                <textarea
                  className="w-full px-3.5 py-2.5 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 min-h-[120px]"
                  value={manualContent}
                  onChange={(e) => setManualContent(e.target.value)}
                  placeholder="Enter product knowledge, FAQ answers, or business information..."
                  required
                />
              </div>
              <Button type="submit">Create Entry</Button>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Sources Table */}
      <Card>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-100">
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-6 py-3">Source</th>
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-6 py-3">Type</th>
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-6 py-3">Status</th>
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-6 py-3">Chunks</th>
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-6 py-3">Size</th>
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-6 py-3">Version</th>
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-6 py-3">Added</th>
                <th className="text-left text-xs font-medium text-gray-500 uppercase px-6 py-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {sources.map((src) => (
                <tr key={src.id} className="border-b border-gray-50 hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-gray-100 flex items-center justify-center">
                        <span className="text-xs font-bold text-gray-500">{typeIcon[src.source_type] || '?'}</span>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">{src.title}</p>
                        {src.original_filename && (
                          <p className="text-xs text-gray-500">{src.original_filename}</p>
                        )}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">{src.source_type}</td>
                  <td className="px-6 py-4"><Badge variant={src.status}>{src.status}</Badge></td>
                  <td className="px-6 py-4 text-sm text-gray-600">{src.chunk_count}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    {src.file_size ? formatFileSize(src.file_size) : '—'}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">v{src.version}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">{formatDate(src.created_at)}</td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleToggle(src.id)}
                        className="p-1.5 hover:bg-gray-100 rounded-lg"
                        title={src.is_active ? 'Deactivate' : 'Activate'}
                      >
                        {src.is_active ? (
                          <ToggleRight className="w-4 h-4 text-green-500" />
                        ) : (
                          <ToggleLeft className="w-4 h-4 text-gray-400" />
                        )}
                      </button>
                      <button
                        onClick={() => handleReindex(src.id)}
                        className="p-1.5 hover:bg-gray-100 rounded-lg"
                        title="Reindex"
                      >
                        <RefreshCw className="w-4 h-4 text-gray-400" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {sources.length === 0 && (
                <tr>
                  <td colSpan={8} className="px-6 py-16 text-center">
                    <BookOpen className="w-8 h-8 text-gray-300 mx-auto mb-3" />
                    <p className="text-sm text-gray-400">No knowledge sources yet. Upload your first document.</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
