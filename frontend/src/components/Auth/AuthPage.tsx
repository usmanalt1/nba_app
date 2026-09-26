import { useState } from 'react';
import type { FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Alert,
  Button,
  Group,
  Paper,
  PasswordInput,
  SegmentedControl,
  Stack,
  Text,
  TextInput,
  Title,
} from '@mantine/core';
import { IconArrowRight, IconLock, IconUserPlus } from '@tabler/icons-react';
import { loginUser, registerUser } from '../../lib/api';
import classes from './AuthPage.module.css';

type AuthMode = 'login' | 'register';

export function AuthPage() {
  const navigate = useNavigate();
  const [mode, setMode] = useState<AuthMode>('login');
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError('');
    setMessage('');
    setLoading(true);

    try {
      if (mode === 'register') {
        await registerUser(username, email, password);
        setMode('login');
        setPassword('');
        setMessage('Account created. Sign in to continue.');
      } else {
        const tokens = await loginUser(username, password);
        sessionStorage.setItem('access_token', tokens.access);
        sessionStorage.setItem('refresh_token', tokens.refresh);
        navigate('/');
      }
    } catch {
      setError(
        mode === 'register'
          ? 'We could not create that account. Check the details and try again.'
          : 'The username or password is incorrect.',
      );
    } finally {
      setLoading(false);
    }
  }

  const isRegistering = mode === 'register';

  return (
    <main className={classes.page}>
      <div className={classes.rail} aria-hidden="true">
        <span>NBA / ACCESS</span>
        <span>SECURE ENTRY</span>
      </div>

      <section className={classes.intro}>
        <Text className={classes.kicker}>NBA ANALYTICS PLATFORM</Text>
        <Title order={1}>Read the game<br />before it happens.</Title>
        <Text className={classes.description}>
          Sign in to explore team trends, model runs, and the signals behind
          every prediction.
        </Text>
        <div className={classes.rule} />
        <Text className={classes.note}>DATA / MODELS / DECISIONS</Text>
      </section>

      <Paper className={classes.panel} shadow="xl" radius="sm">
        <Group justify="space-between" align="flex-start" mb="xl">
          <div>
            <Text className={classes.panelKicker}>
              {isRegistering ? 'NEW USER' : 'WELCOME BACK'}
            </Text>
            <Title order={2}>{isRegistering ? 'Create access' : 'Sign in'}</Title>
          </div>
          {isRegistering ? <IconUserPlus size={24} /> : <IconLock size={24} />}
        </Group>

        <SegmentedControl
          fullWidth
          value={mode}
          onChange={(value) => {
            setMode(value as AuthMode);
            setError('');
            setMessage('');
          }}
          data={[
            { label: 'Sign in', value: 'login' },
            { label: 'Register', value: 'register' },
          ]}
          mb="xl"
        />

        <form onSubmit={handleSubmit}>
          <Stack gap="md">
            <TextInput
              label="Username"
              placeholder="your username"
              value={username}
              onChange={(event) => setUsername(event.currentTarget.value)}
              required
            />

            {isRegistering && (
              <TextInput
                label="Email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(event) => setEmail(event.currentTarget.value)}
                required
              />
            )}

            <PasswordInput
              label="Password"
              placeholder="your password"
              value={password}
              onChange={(event) => setPassword(event.currentTarget.value)}
              required
            />

            {error && <Alert color="red">{error}</Alert>}
            {message && <Alert color="green">{message}</Alert>}

            <Button
              type="submit"
              loading={loading}
              rightSection={<IconArrowRight size={16} />}
              mt="sm"
            >
              {isRegistering ? 'Create account' : 'Enter dashboard'}
            </Button>
          </Stack>
        </form>
      </Paper>
    </main>
  );
}