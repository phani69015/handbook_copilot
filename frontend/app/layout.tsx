import type { Metadata } from 'next';
import ThemeRegistry from './ThemeRegistry';
import Navbar from '@/components/Navbar';

export const metadata: Metadata = {
  title: 'Handbook Copilot',
  description: 'AI-powered handbook assistant for universities and colleges',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ margin: 0 }}>
        <ThemeRegistry>
          <Navbar />
          {children}
        </ThemeRegistry>
      </body>
    </html>
  );
}
