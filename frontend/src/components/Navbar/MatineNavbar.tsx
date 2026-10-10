import { useState } from 'react';
import {
  IconChartHistogram,
  IconCrystalBall,
  IconLogout,
  IconMessageChatbot,
  IconReportAnalytics,
  IconSmartHome,
} from '@tabler/icons-react';
import { Burger, Button, Drawer, ScrollArea } from '@mantine/core';
import { useMediaQuery } from '@mantine/hooks';
import { useNavigate } from 'react-router-dom';
import { LinksGroup } from '../NavbarLinksGroup/NavbarLinksGroup';
import { Logo } from './Logo';
import classes from './NavbarNested.module.css';

const pages = [
  { label: 'Home', icon: IconSmartHome, link: '/' },
  { label: 'Can of Worms', icon: IconReportAnalytics, link: '/view' },
  { label: 'Wormalytics', icon: IconChartHistogram, link: '/analytics' },
  { label: 'Wormhole', icon: IconCrystalBall, link: '/predictions' },
  { label: 'Ask Worm', icon: IconMessageChatbot, link: '/nbai' },
];

/* Mirrors the collapse breakpoint in NavbarNested.module.css. */
const COLLAPSE_QUERY = '(max-width: 768px)';

export function Navbar() {
  const navigate = useNavigate();
  const isCollapsed = useMediaQuery(COLLAPSE_QUERY);
  const [menuOpen, setMenuOpen] = useState(false);

  function closeMenu() {
    setMenuOpen(false);
  }

  function handleLogout() {
    sessionStorage.removeItem('access_token');
    sessionStorage.removeItem('refresh_token');
    closeMenu();
    navigate('/auth', { replace: true });
  }

  const body = (
    <>
      <ScrollArea className={classes.links}>
        <div className={classes.linksInner}>
          {pages.map((item) => (
            <LinksGroup {...item} key={item.label} onNavigate={closeMenu} />
          ))}
        </div>
      </ScrollArea>
      <div className={classes.footer}>
        <Button
          fullWidth
          variant="subtle"
          color="gray"
          justify="flex-start"
          leftSection={<IconLogout size={18} />}
          onClick={handleLogout}
        >
          Log out
        </Button>
      </div>
    </>
  );

  return (
    <>
      <header className={classes.topbar}>
        <Logo compact />
        <Burger
          opened={menuOpen}
          onClick={() => setMenuOpen((open) => !open)}
          size="sm"
          color="var(--paper)"
          aria-label="Toggle navigation"
        />
      </header>

      <nav className={classes.navbar}>
        <div className={classes.header}>
          <Logo />
        </div>
        {body}
      </nav>

      <Drawer
        opened={menuOpen && Boolean(isCollapsed)}
        onClose={closeMenu}
        position="left"
        size="260px"
        title={<Logo compact />}
        overlayProps={{ backgroundOpacity: 0.6, blur: 2 }}
        classNames={{
          content: classes.drawerContent,
          header: classes.drawerHeader,
          body: classes.drawerBody,
        }}
      >
        {body}
      </Drawer>
    </>
  );
}

export default Navbar;
