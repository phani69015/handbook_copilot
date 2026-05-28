'use client';

import { AppBar, Toolbar, Typography, Button, Box, Container } from '@mui/material';
import AutoStoriesIcon from '@mui/icons-material/AutoStories';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Navbar() {
  const pathname = usePathname();

  const navItems = [
    { label: 'Home', href: '/' },
    { label: 'Register College', href: '/register' },
    { label: 'Student Chat', href: '/chat' },
  ];

  return (
    <AppBar
      position="sticky"
      elevation={0}
      sx={{
        bgcolor: 'background.paper',
        borderBottom: '1px solid',
        borderColor: 'divider',
      }}
    >
      <Container maxWidth="lg">
        <Toolbar disableGutters sx={{ gap: 2 }}>
          <AutoStoriesIcon sx={{ color: 'primary.main', fontSize: 32 }} />
          <Typography
            variant="h6"
            component={Link}
            href="/"
            sx={{
              color: 'primary.main',
              textDecoration: 'none',
              fontWeight: 800,
              flexGrow: 1,
            }}
          >
            Handbook Copilot
          </Typography>

          <Box sx={{ display: 'flex', gap: 1 }}>
            {navItems.map((item) => (
              <Button
                key={item.href}
                component={Link}
                href={item.href}
                variant={pathname === item.href ? 'contained' : 'text'}
                size="small"
                sx={{
                  color: pathname === item.href ? 'white' : 'text.secondary',
                }}
              >
                {item.label}
              </Button>
            ))}
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
}
