import {
  IconAdjustments,
  IconReportAnalytics,
  IconSmartHome,
  IconPresentationAnalytics,
} from '@tabler/icons-react';
import { ScrollArea } from '@mantine/core';
import { LinksGroup } from '../NavbarLinksGroup/NavbarLinksGroup';
import { Logo } from './Logo';
import classes from './NavbarNested.module.css';

const pages = [
  { label: 'Home', icon: IconSmartHome, link: '/' },
  { label: 'Collect Data', icon: IconPresentationAnalytics, link: '/collect' },
  { label: 'View Data', icon: IconReportAnalytics, link: '/view' },
  { label: 'Models', icon: IconAdjustments, link: '/models' },
];

export function Navbar() {
  const links = pages.map((item) => <LinksGroup {...item} key={item.label} />);

  return (
    <nav className={classes.navbar}>
      <div className={classes.header}>
          <Logo style={{ width: 250 }} />
      </div>
    
      <ScrollArea className={classes.links}>
        <div className={classes.linksInner}>{links}</div>
      </ScrollArea>
    </nav>
  );
}

export default Navbar;