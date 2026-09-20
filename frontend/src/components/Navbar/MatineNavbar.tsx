import {
  IconAdjustments,
  IconLogout,
  IconReportAnalytics,
  IconSmartHome,
  IconPresentationAnalytics,
} from '@tabler/icons-react';
import { Button, ScrollArea } from '@mantine/core';
import { useNavigate } from 'react-router-dom';
import { LinksGroup } from '../NavbarLinksGroup/NavbarLinksGroup';
import { Logo } from './Logo';
import classes from './NavbarNested.module.css';

const pages = [
  { label: 'Home', icon: IconSmartHome, link: '/' },
  { label: 'Collect Data', icon: IconPresentationAnalytics, link: '/collect' },
  { label: 'View Data', icon: IconReportAnalytics, link: '/view' },
  { label: 'Predictions', icon: IconAdjustments, link: '/predictions' },
  { label: 'NBAI', icon: IconAdjustments, link: '/nbai' },
];

export function Navbar() {
  const navigate = useNavigate();
  const links = pages.map((item) => <LinksGroup {...item} key={item.label} />);

  function handleLogout() {
    sessionStorage.removeItem('access_token');
    sessionStorage.removeItem('refresh_token');
    navigate('/auth', { replace: true });
  }

  return (
    <nav className={classes.navbar}>
      <div className={classes.header}>
          <Logo style={{ width: 250 }} />
      </div>
    
      <ScrollArea className={classes.links}>
        <div className={classes.linksInner}>{links}</div>
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
    </nav>
  );
}

export default Navbar;