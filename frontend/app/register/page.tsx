'use client';

import { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  TextField,
  Button,
  Card,
  CardContent,
  Alert,
  Stepper,
  Step,
  StepLabel,
  Chip,
  LinearProgress,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import Link from 'next/link';
import { registerCollege, ingestHandbook } from '@/lib/api';
import { RegisterResponse } from '@/lib/types';

export default function RegisterPage() {
  const [activeStep, setActiveStep] = useState(0);
  const [inviteCode, setInviteCode] = useState('');
  const [collegeName, setCollegeName] = useState('');
  const [openaiKey, setOpenaiKey] = useState('');
  const [registered, setRegistered] = useState<RegisterResponse | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [ingested, setIngested] = useState(false);
  const [ingestResult, setIngestResult] = useState<{ chunks: number; pages: number } | null>(null);
  const [error, setError] = useState('');

  const handleRegister = async () => {
    setError('');
    try {
      const result = await registerCollege({
        college_name: collegeName,
        invite_code: inviteCode,
        openai_api_key: openaiKey,
      });
      setRegistered(result);
      setActiveStep(1);
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleUpload = async () => {
    if (!file || !registered) return;
    setError('');
    setUploading(true);
    try {
      const result = await ingestHandbook(registered.college_code, file, false);
      setIngestResult({ chunks: result.chunks_created, pages: result.pages_processed });
      setIngested(true);
      setActiveStep(2);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <Container maxWidth="md" sx={{ py: 6 }}>
      <Typography variant="h3" gutterBottom sx={{ fontWeight: 800 }}>
        Register Your College
      </Typography>
      <Typography color="text.secondary" sx={{ mb: 4 }}>
        Register your institution and upload the student handbook to get started.
        You need an invite code from the platform administrator.
      </Typography>

      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        <Step><StepLabel>Register</StepLabel></Step>
        <Step><StepLabel>Upload Handbook</StepLabel></Step>
        <Step><StepLabel>Done</StepLabel></Step>
      </Stepper>

      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

      {/* Step 0: Registration Form */}
      {activeStep === 0 && (
        <Card>
          <CardContent sx={{ p: 4 }}>
            <Typography variant="h5" gutterBottom>College Registration</Typography>

            <TextField
              fullWidth
              label="Invite Code"
              placeholder="e.g., INV-a8f3c2"
              value={inviteCode}
              onChange={(e) => setInviteCode(e.target.value)}
              required
              sx={{ mb: 3 }}
              helperText="Contact the platform administrator to get an invite code."
            />

            <TextField
              fullWidth
              label="College Name"
              placeholder="e.g., St. Paul's College, Kalamassery"
              value={collegeName}
              onChange={(e) => setCollegeName(e.target.value)}
              required
              sx={{ mb: 3 }}
            />

            <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
              Optional: OpenAI API Key (for faster AI responses)
            </Typography>
            <Typography variant="caption" color="text.secondary" sx={{ mb: 2, display: 'block' }}>
              If provided, student queries use OpenAI GPT-4o (~1-2s) instead of local model (~5-10s).
              The key is stored securely on the server and never visible to students.
            </Typography>
            <TextField
              fullWidth
              label="OpenAI API Key (optional)"
              placeholder="sk-..."
              type="password"
              value={openaiKey}
              onChange={(e) => setOpenaiKey(e.target.value)}
              sx={{ mb: 4 }}
            />

            <Button
              variant="contained"
              size="large"
              onClick={handleRegister}
              disabled={!inviteCode || !collegeName || collegeName.length < 3}
              fullWidth
            >
              Register College
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Step 1: Upload Handbook */}
      {activeStep === 1 && registered && (
        <Card>
          <CardContent sx={{ p: 4 }}>
            <Alert severity="success" sx={{ mb: 3 }}>
              College registered! Access code: <strong>{registered.college_code}</strong>
            </Alert>

            <Box sx={{ display: 'flex', gap: 1, mb: 3, flexWrap: 'wrap' }}>
              <Chip label={registered.college_name} color="primary" />
              <Chip label={`Code: ${registered.college_code}`} variant="outlined" />
              {registered.has_openai_key && <Chip label="OpenAI Enabled" color="secondary" />}
            </Box>

            <Typography variant="h5" gutterBottom>Upload Student Handbook</Typography>
            <Typography color="text.secondary" sx={{ mb: 3 }}>
              Upload your student handbook PDF. We'll index it for AI-powered search.
            </Typography>

            <Box
              sx={{
                border: '2px dashed',
                borderColor: file ? 'primary.main' : 'divider',
                borderRadius: 2,
                p: 4,
                textAlign: 'center',
                cursor: 'pointer',
                mb: 3,
                bgcolor: file ? 'primary.50' : 'transparent',
                transition: 'all 0.2s',
                '&:hover': { borderColor: 'primary.main', bgcolor: 'rgba(124,58,237,0.04)' },
              }}
              onClick={() => document.getElementById('file-input')?.click()}
            >
              <input
                id="file-input"
                type="file"
                accept=".pdf"
                hidden
                onChange={(e) => setFile(e.target.files?.[0] || null)}
              />
              <CloudUploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
              <Typography variant="h6">
                {file ? file.name : 'Click to upload PDF'}
              </Typography>
              {file && (
                <Typography variant="body2" color="text.secondary">
                  {(file.size / (1024 * 1024)).toFixed(1)} MB
                </Typography>
              )}
            </Box>

            {uploading && <LinearProgress sx={{ mb: 2 }} />}

            <Button
              variant="contained"
              size="large"
              onClick={handleUpload}
              disabled={!file || uploading}
              fullWidth
              startIcon={<CloudUploadIcon />}
            >
              {uploading ? 'Indexing...' : 'Upload & Index Handbook'}
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Step 2: Success */}
      {activeStep === 2 && registered && (
        <Card>
          <CardContent sx={{ p: 4, textAlign: 'center' }}>
            <CheckCircleIcon sx={{ fontSize: 64, color: 'success.main', mb: 2 }} />
            <Typography variant="h4" gutterBottom>All Set!</Typography>

            {ingestResult && (
              <Typography color="text.secondary" sx={{ mb: 3 }}>
                Indexed <strong>{ingestResult.chunks}</strong> chunks from <strong>{ingestResult.pages}</strong> pages.
              </Typography>
            )}

            <Alert severity="info" sx={{ mb: 3, textAlign: 'left' }}>
              <strong>Share these instructions with your students:</strong>
              <ol style={{ margin: '8px 0 0 0', paddingLeft: '20px' }}>
                <li>Go to the <strong>Student Chat</strong> page</li>
                <li>Enter code: <strong>{registered.college_code}</strong></li>
                <li>Start asking questions about the handbook!</li>
              </ol>
            </Alert>

            <Button
              component={Link}
              href="/chat"
              variant="contained"
              size="large"
            >
              Try Student Chat
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Already registered? */}
      {activeStep === 0 && (
        <Box sx={{ mt: 4, textAlign: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            Already registered? Go to{' '}
            <Link href="/chat" style={{ color: '#7C3AED' }}>
              Student Chat
            </Link>{' '}
            to test your handbook.
          </Typography>
        </Box>
      )}
    </Container>
  );
}
