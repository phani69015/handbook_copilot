'use client';

import { useState, useRef, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  TextField,
  Button,
  Card,
  CardContent,
  Alert,
  Chip,
  IconButton,
  InputAdornment,
  CircularProgress,
  Divider,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import DeleteIcon from '@mui/icons-material/Delete';
import SwapHorizIcon from '@mui/icons-material/SwapHoriz';
import { getCollege, queryHandbook } from '@/lib/api';
import { ChatMessage, College } from '@/lib/types';

export default function ChatPage() {
  const [college, setCollege] = useState<College | null>(null);
  const [codeInput, setCodeInput] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleJoin = async () => {
    setError('');
    try {
      const data = await getCollege(codeInput);
      if (!data.is_indexed) {
        setError("This college's handbook hasn't been uploaded yet. Ask your administrator.");
        return;
      }
      setCollege(data);
    } catch (err: any) {
      setError(err.message || 'Invalid code. Check with your college administration.');
    }
  };

  const handleAsk = async () => {
    if (!question.trim() || !college) return;

    const userMsg: ChatMessage = { role: 'user', content: question };
    setMessages((prev) => [...prev, userMsg]);
    setQuestion('');
    setLoading(true);
    setError('');

    try {
      const response = await queryHandbook(college.college_code, question);
      const assistantMsg: ChatMessage = {
        role: 'assistant',
        content: response.answer,
        citations: response.citations,
        chunks_used: response.chunks_used,
        confidence: response.confidence,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      setError(err.message);
      const errorMsg: ChatMessage = {
        role: 'assistant',
        content: `Error: ${err.message}`,
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleAsk();
    }
  };

  // College Code Entry Screen
  if (!college) {
    return (
      <Container maxWidth="sm" sx={{ py: 10, textAlign: 'center' }}>
        <Typography variant="h3" gutterBottom sx={{ fontWeight: 800 }}>
          Student Chat
        </Typography>
        <Typography color="text.secondary" sx={{ mb: 4 }}>
          Enter your college code to start asking questions about the handbook.
        </Typography>

        {error && <Alert severity="error" sx={{ mb: 3, textAlign: 'left' }}>{error}</Alert>}

        <Card>
          <CardContent sx={{ p: 4 }}>
            <TextField
              fullWidth
              label="College Code"
              placeholder="e.g., SPC-a3b2"
              value={codeInput}
              onChange={(e) => setCodeInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleJoin()}
              sx={{ mb: 3 }}
              helperText="Get this code from your college administration."
            />
            <Button
              variant="contained"
              size="large"
              fullWidth
              onClick={handleJoin}
              disabled={!codeInput.trim()}
            >
              Enter Chat
            </Button>
          </CardContent>
        </Card>
      </Container>
    );
  }

  // Chat Interface
  return (
    <Box sx={{ height: 'calc(100vh - 64px)', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ px: 3, py: 2, borderBottom: '1px solid', borderColor: 'divider', bgcolor: 'background.paper' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box>
            <Typography variant="h5" sx={{ fontWeight: 700 }}>{college.college_name}</Typography>
            <Typography variant="caption" color="text.secondary">
              Code: {college.college_code} | {college.total_chunks} indexed chunks
              {college.has_openai_key && ' | Fast Mode (OpenAI)'}
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <IconButton size="small" onClick={() => setMessages([])} title="Clear chat">
              <DeleteIcon />
            </IconButton>
            <IconButton size="small" onClick={() => { setCollege(null); setMessages([]); }} title="Switch college">
              <SwapHorizIcon />
            </IconButton>
          </Box>
        </Box>
      </Box>

      {/* Messages */}
      <Box sx={{ flex: 1, overflow: 'auto', px: 3, py: 2 }}>
        <Container maxWidth="md">
          {messages.length === 0 && (
            <Box sx={{ textAlign: 'center', py: 8 }}>
              <Typography variant="h5" color="text.secondary" gutterBottom>
                Ask anything about the handbook
              </Typography>
              <Typography color="text.secondary">
                Try: "What are the fee deadlines?" or "What is the attendance policy?"
              </Typography>
            </Box>
          )}

          {messages.map((msg, idx) => (
            <Box key={idx} sx={{ mb: 3 }}>
              {msg.role === 'user' ? (
                <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                  <Box
                    sx={{
                      bgcolor: 'primary.main',
                      color: 'white',
                      px: 3,
                      py: 1.5,
                      borderRadius: '16px 16px 4px 16px',
                      maxWidth: '70%',
                    }}
                  >
                    <Typography>{msg.content}</Typography>
                  </Box>
                </Box>
              ) : (
                <Card sx={{ border: '1px solid', borderColor: 'divider' }}>
                  <CardContent sx={{ p: 3 }}>
                    <Typography sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.7 }}>
                      {msg.content}
                    </Typography>

                    {msg.citations && msg.citations.length > 0 && (
                      <>
                        <Divider sx={{ my: 2 }} />
                        <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
                          Sources:
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                          {msg.citations.map((cit, i) => (
                            <Chip
                              key={i}
                              label={`${cit.section} — Page ${cit.page}`}
                              size="small"
                              variant="outlined"
                              color="primary"
                              sx={{ fontSize: '0.75rem' }}
                            />
                          ))}
                        </Box>
                        <Box sx={{ display: 'flex', gap: 2, mt: 1 }}>
                          <Typography variant="caption" color="text.secondary">
                            Chunks: {msg.chunks_used}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            Confidence: {((msg.confidence || 0) * 100).toFixed(0)}%
                          </Typography>
                        </Box>
                      </>
                    )}
                  </CardContent>
                </Card>
              )}
            </Box>
          ))}

          {loading && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
              <CircularProgress size={20} />
              <Typography color="text.secondary">Searching handbook...</Typography>
            </Box>
          )}

          <div ref={messagesEndRef} />
        </Container>
      </Box>

      {/* Input */}
      <Box sx={{ px: 3, py: 2, borderTop: '1px solid', borderColor: 'divider', bgcolor: 'background.paper' }}>
        <Container maxWidth="md">
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          <TextField
            fullWidth
            placeholder="Ask a question about the handbook..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    onClick={handleAsk}
                    disabled={!question.trim() || loading}
                    color="primary"
                  >
                    <SendIcon />
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />
        </Container>
      </Box>
    </Box>
  );
}
