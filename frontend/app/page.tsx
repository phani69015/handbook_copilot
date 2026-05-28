'use client';

import {
  Box,
  Container,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  Chip,
  Alert,
} from '@mui/material';
import BoltIcon from '@mui/icons-material/Bolt';
import DescriptionIcon from '@mui/icons-material/Description';
import SchoolIcon from '@mui/icons-material/School';
import Link from 'next/link';
import { useEffect, useState } from 'react';
import { listColleges } from '@/lib/api';
import { College } from '@/lib/types';

export default function HomePage() {
  const [colleges, setColleges] = useState<College[]>([]);
  const [error, setError] = useState('');

  useEffect(() => {
    listColleges()
      .then((data) => setColleges(data.colleges))
      .catch((err) => setError(err.message));
  }, []);

  return (
    <Box>
      {/* Hero Section */}
      <Box
        sx={{
          background: 'linear-gradient(135deg, #7C3AED 0%, #A78BFA 50%, #C4B5FD 100%)',
          py: { xs: 8, md: 12 },
          textAlign: 'center',
        }}
      >
        <Container maxWidth="md">
          <Typography variant="h2" sx={{ color: 'white', mb: 2, fontSize: { xs: '2rem', md: '3rem' } }}>
            Handbook Copilot
          </Typography>
          <Typography variant="h5" sx={{ color: 'rgba(255,255,255,0.9)', mb: 4, fontWeight: 400 }}>
            AI-powered handbook assistant for universities and colleges.
            Instant, cited answers from your student handbook.
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Button
              component={Link}
              href="/register"
              variant="contained"
              size="large"
              sx={{ bgcolor: 'white', color: 'primary.main', '&:hover': { bgcolor: '#f0e6ff' } }}
            >
              Register College
            </Button>
            <Button
              component={Link}
              href="/chat"
              variant="outlined"
              size="large"
              sx={{ borderColor: 'white', color: 'white', '&:hover': { borderColor: 'white', bgcolor: 'rgba(255,255,255,0.1)' } }}
            >
              Student Chat
            </Button>
          </Box>
        </Container>
      </Box>

      {/* Features */}
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Typography variant="h4" textAlign="center" gutterBottom>
          Why Handbook Copilot?
        </Typography>
        <Typography variant="body1" textAlign="center" color="text.secondary" sx={{ mb: 6 }}>
          Stop making students dig through 300-page PDFs for simple answers.
        </Typography>

        <Grid container spacing={4}>
          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%', textAlign: 'center', p: 2 }}>
              <CardContent>
                <BoltIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
                <Typography variant="h6" gutterBottom>Instant Answers</Typography>
                <Typography color="text.secondary">
                  Students get accurate, cited answers in seconds. No more repetitive questions for admin staff.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%', textAlign: 'center', p: 2 }}>
              <CardContent>
                <DescriptionIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
                <Typography variant="h6" gutterBottom>Cited Sources</Typography>
                <Typography color="text.secondary">
                  Every answer includes exact section and page references. Students can verify in the original document.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%', textAlign: 'center', p: 2 }}>
              <CardContent>
                <SchoolIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
                <Typography variant="h6" gutterBottom>Any College</Typography>
                <Typography color="text.secondary">
                  Register your institution, upload the handbook PDF, and students are ready to go in minutes.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>

      {/* How It Works */}
      <Box sx={{ bgcolor: 'background.paper', py: 8 }}>
        <Container maxWidth="lg">
          <Typography variant="h4" textAlign="center" gutterBottom>
            How It Works
          </Typography>
          <Grid container spacing={3} sx={{ mt: 4 }}>
            {[
              { step: '1', title: 'Register', desc: 'Admin registers the college with an invite code' },
              { step: '2', title: 'Upload', desc: 'Upload the student handbook PDF — indexed automatically' },
              { step: '3', title: 'Share', desc: 'Share the college access code with students' },
              { step: '4', title: 'Ask', desc: 'Students enter code and ask questions instantly' },
            ].map((item) => (
              <Grid item xs={6} md={3} key={item.step}>
                <Box textAlign="center">
                  <Box
                    sx={{
                      width: 48,
                      height: 48,
                      borderRadius: '50%',
                      bgcolor: 'primary.main',
                      color: 'white',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      mx: 'auto',
                      mb: 2,
                      fontWeight: 700,
                      fontSize: '1.2rem',
                    }}
                  >
                    {item.step}
                  </Box>
                  <Typography variant="h6" gutterBottom>{item.title}</Typography>
                  <Typography variant="body2" color="text.secondary">{item.desc}</Typography>
                </Box>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* CTA Cards */}
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Typography variant="h4" textAlign="center" gutterBottom sx={{ mb: 4 }}>
          Get Started
        </Typography>
        <Grid container spacing={4}>
          <Grid item xs={12} md={6}>
            <Card
              sx={{
                background: 'linear-gradient(135deg, #7C3AED 0%, #5B21B6 100%)',
                color: 'white',
                p: 4,
                textAlign: 'center',
              }}
            >
              <CardContent>
                <SchoolIcon sx={{ fontSize: 56, mb: 2 }} />
                <Typography variant="h5" gutterBottom>College Admin</Typography>
                <Typography sx={{ mb: 3, opacity: 0.9 }}>
                  Register your college and upload the student handbook. Requires an invite code.
                </Typography>
                <Button
                  component={Link}
                  href="/register"
                  variant="contained"
                  size="large"
                  sx={{ bgcolor: 'white', color: 'primary.main', '&:hover': { bgcolor: '#f0e6ff' } }}
                >
                  Register College
                </Button>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card
              sx={{
                background: 'linear-gradient(135deg, #A78BFA 0%, #7C3AED 100%)',
                color: 'white',
                p: 4,
                textAlign: 'center',
              }}
            >
              <CardContent>
                <BoltIcon sx={{ fontSize: 56, mb: 2 }} />
                <Typography variant="h5" gutterBottom>Student</Typography>
                <Typography sx={{ mb: 3, opacity: 0.9 }}>
                  Enter your college code and start asking questions. Get instant, cited answers.
                </Typography>
                <Button
                  component={Link}
                  href="/chat"
                  variant="contained"
                  size="large"
                  sx={{ bgcolor: 'white', color: 'primary.main', '&:hover': { bgcolor: '#f0e6ff' } }}
                >
                  Student Chat
                </Button>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>

      {/* Registered Colleges */}
      <Box sx={{ bgcolor: 'background.paper', py: 8 }}>
        <Container maxWidth="lg">
          <Typography variant="h4" textAlign="center" gutterBottom>
            Registered Colleges
          </Typography>
          {error && (
            <Alert severity="warning" sx={{ mt: 2, mb: 2 }}>
              Backend not available. {error}
            </Alert>
          )}
          {colleges.length > 0 ? (
            <Grid container spacing={2} sx={{ mt: 2 }}>
              {colleges.map((college) => (
                <Grid item xs={12} sm={6} md={4} key={college.college_code}>
                  <Card sx={{ p: 2 }}>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>{college.college_name}</Typography>
                      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        <Chip label={`Code: ${college.college_code}`} size="small" color="primary" variant="outlined" />
                        <Chip
                          label={college.is_indexed ? 'Indexed' : 'Pending'}
                          size="small"
                          color={college.is_indexed ? 'success' : 'warning'}
                        />
                        {college.has_openai_key && (
                          <Chip label="Fast (OpenAI)" size="small" color="secondary" />
                        )}
                        <Chip label={`${college.total_chunks} chunks`} size="small" variant="outlined" />
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          ) : !error ? (
            <Typography textAlign="center" color="text.secondary" sx={{ mt: 2 }}>
              No colleges registered yet. Be the first!
            </Typography>
          ) : null}
        </Container>
      </Box>

      {/* Footer */}
      <Box sx={{ py: 4, textAlign: 'center', borderTop: '1px solid', borderColor: 'divider' }}>
        <Typography variant="body2" color="text.secondary">
          Handbook Copilot — Built with Next.js, FastAPI, Qdrant, and AI
        </Typography>
      </Box>
    </Box>
  );
}
