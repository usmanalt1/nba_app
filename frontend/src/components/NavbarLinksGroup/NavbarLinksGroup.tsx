import { Link, useLocation } from 'react-router-dom';
import { Box, Group, ThemeIcon, UnstyledButton, rem } from '@mantine/core';
import classes from './NavbarLinksGroup.module.css';

interface LinksGroupProps {
  icon: React.FC<any>;
  label: string;
  link: string;
}

export function LinksGroup({ icon: Icon, label, link }: LinksGroupProps) {
  const location = useLocation();
  const to = link === location.pathname ? { pathname: link, search: location.search } : link;

  return (
    <UnstyledButton className={classes.control} component={Link} to={to}>
      <Group justify="space-between" gap={0}>
        <Box style={{ display: 'flex', alignItems: 'center' }}>
          <ThemeIcon variant="light" size={30}>
            <Icon style={{ width: rem(18), height: rem(18) }} />
          </ThemeIcon>
          <Box ml="md">{label}</Box>
        </Box>
      </Group>
    </UnstyledButton>
  );
}
