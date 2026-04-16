import { useEffect, useState, FormEvent } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Bot,
  UserCheck,
  Send,
  PhoneForwarded,
  RotateCcw,
  StickyNote,
  User,
} from 'lucide-react';
import { Card, CardContent, CardHeader } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { conversationsApi } from '../services/api';
import { formatDateTime, cn } from '../lib/utils';
import type { Conversation, Message, Note } from '../types';
import toast from 'react-hot-toast';

export default function ConversationDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [replyText, setReplyText] = useState('');
  const [noteText, setNoteText] = useState('');
  const [sending, setSending] = useState(false);

  const loadConversation = () => {
    if (!id) return;
    conversationsApi.get(id).then((res) => setConversation(res.data)).catch(() => {});
  };

  useEffect(() => {
    loadConversation();
  }, [id]);

  const handleSendReply = async (e: FormEvent) => {
    e.preventDefault();
    if (!id || !replyText.trim()) return;
    setSending(true);
    try {
      await conversationsApi.send(id, replyText);
      setReplyText('');
      toast.success('Reply sent');
      loadConversation();
    } catch {
      toast.error('Failed to send reply');
    } finally {
      setSending(false);
    }
  };

  const handleHandoff = async () => {
    if (!id) return;
    try {
      await conversationsApi.handoff(id, 'Manual handoff from dashboard');
      toast.success('Handoff initiated');
      loadConversation();
    } catch {
      toast.error('Failed to initiate handoff');
    }
  };

  const handleResumeAI = async () => {
    if (!id) return;
    try {
      await conversationsApi.resumeAi(id);
      toast.success('AI mode resumed');
      loadConversation();
    } catch {
      toast.error('Failed to resume AI');
    }
  };

  const handleAddNote = async (e: FormEvent) => {
    e.preventDefault();
    if (!id || !noteText.trim()) return;
    try {
      await conversationsApi.addNote(id, noteText);
      setNoteText('');
      toast.success('Note added');
      loadConversation();
    } catch {
      toast.error('Failed to add note');
    }
  };

  if (!conversation) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-gray-400">Loading conversation...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button onClick={() => navigate('/conversations')} className="p-2 hover:bg-gray-100 rounded-lg">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-xl font-bold text-gray-900">
              {conversation.contact.display_name || conversation.contact.phone_number}
            </h1>
            <p className="text-sm text-gray-500">{conversation.contact.phone_number}</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Badge variant={conversation.status}>{conversation.status}</Badge>
          {conversation.is_ai_active ? (
            <Button variant="secondary" size="sm" onClick={handleHandoff}>
              <PhoneForwarded className="w-4 h-4 mr-2" />
              Handoff to Human
            </Button>
          ) : (
            <Button variant="secondary" size="sm" onClick={handleResumeAI}>
              <RotateCcw className="w-4 h-4 mr-2" />
              Resume AI
            </Button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chat Transcript */}
        <div className="lg:col-span-2 space-y-4">
          <Card className="h-[600px] flex flex-col">
            <CardHeader>
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-gray-900">Conversation</h3>
                <span className="text-xs text-gray-400">{conversation.message_count} messages</span>
              </div>
            </CardHeader>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
              {(conversation.messages || []).map((msg) => (
                <div
                  key={msg.id}
                  className={cn(
                    'flex',
                    msg.direction === 'outbound' ? 'justify-end' : 'justify-start'
                  )}
                >
                  <div
                    className={cn(
                      'max-w-[75%] rounded-2xl px-4 py-3',
                      msg.direction === 'outbound'
                        ? 'bg-brand-600 text-white rounded-br-md'
                        : 'bg-gray-100 text-gray-900 rounded-bl-md'
                    )}
                  >
                    <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                    <div className={cn(
                      'flex items-center gap-2 mt-1.5',
                      msg.direction === 'outbound' ? 'justify-end' : 'justify-start'
                    )}>
                      {msg.is_ai_generated && (
                        <Bot className="w-3 h-3 opacity-60" />
                      )}
                      <span className={cn(
                        'text-xs',
                        msg.direction === 'outbound' ? 'text-blue-100' : 'text-gray-400'
                      )}>
                        {formatDateTime(msg.created_at)}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Reply Box */}
            <div className="border-t border-gray-100 px-6 py-4">
              <form onSubmit={handleSendReply} className="flex gap-3">
                <input
                  type="text"
                  placeholder="Type a reply..."
                  className="flex-1 px-4 py-2.5 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                  value={replyText}
                  onChange={(e) => setReplyText(e.target.value)}
                />
                <Button type="submit" disabled={sending || !replyText.trim()}>
                  <Send className="w-4 h-4" />
                </Button>
              </form>
            </div>
          </Card>
        </div>

        {/* Sidebar Info */}
        <div className="space-y-4">
          {/* Contact Info */}
          <Card>
            <CardHeader>
              <h3 className="text-sm font-semibold text-gray-900">Contact</h3>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <p className="text-xs text-gray-500">Name</p>
                <p className="text-sm font-medium">{conversation.contact.display_name || '—'}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Phone</p>
                <p className="text-sm font-medium">{conversation.contact.phone_number}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">City</p>
                <p className="text-sm font-medium">{conversation.contact.city || '—'}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Language</p>
                <p className="text-sm font-medium">{conversation.language}</p>
              </div>
            </CardContent>
          </Card>

          {/* Status */}
          <Card>
            <CardHeader>
              <h3 className="text-sm font-semibold text-gray-900">Details</h3>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between">
                <span className="text-xs text-gray-500">Status</span>
                <Badge variant={conversation.status}>{conversation.status}</Badge>
              </div>
              <div className="flex justify-between">
                <span className="text-xs text-gray-500">State</span>
                <span className="text-sm">{conversation.state}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-xs text-gray-500">Handler</span>
                <span className="text-sm inline-flex items-center gap-1">
                  {conversation.is_ai_active ? (
                    <><Bot className="w-3.5 h-3.5 text-purple-500" /> AI</>
                  ) : (
                    <><UserCheck className="w-3.5 h-3.5 text-orange-500" /> Human</>
                  )}
                </span>
              </div>
            </CardContent>
          </Card>

          {/* Tags */}
          <Card>
            <CardHeader>
              <h3 className="text-sm font-semibold text-gray-900">Tags</h3>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {conversation.tags.length > 0 ? (
                  conversation.tags.map((tag) => (
                    <span
                      key={tag.id}
                      className="px-2.5 py-1 rounded-full text-xs font-medium"
                      style={{ backgroundColor: tag.color + '20', color: tag.color }}
                    >
                      {tag.name}
                    </span>
                  ))
                ) : (
                  <p className="text-xs text-gray-400">No tags</p>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Internal Notes */}
          <Card>
            <CardHeader>
              <h3 className="text-sm font-semibold text-gray-900">Internal Notes</h3>
            </CardHeader>
            <CardContent className="space-y-3">
              <form onSubmit={handleAddNote} className="flex gap-2">
                <input
                  type="text"
                  placeholder="Add a note..."
                  className="flex-1 px-3 py-2 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                  value={noteText}
                  onChange={(e) => setNoteText(e.target.value)}
                />
                <Button type="submit" size="sm" disabled={!noteText.trim()}>
                  <StickyNote className="w-4 h-4" />
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
