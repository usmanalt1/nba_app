import { Link } from 'react-router-dom';
import { Box, Group, ThemeIcon, UnstyledButton, rem } from '@mantine/core';
import classes from './NavbarLinksGroup.module.css';

interface LinksGroupProps {
  icon: React.FC<any>;
  label: string;
  link: string;
}

export function LinksGroup({ icon: Icon, label, link }: LinksGroupProps) {
  return (
    <UnstyledButton className={classes.control} component={Link} to={link}>
      <Group justify="space-between" gap={0}>
        <Box style={{ display: 'flex', alignItems: 'center' }}>
          <ThemeIcon variant="dark" size={30}>
            <Icon style={{ width: rem(18), height: rem(18) }} />
          </ThemeIcon>
          <Box ml="md">{label}</Box>
        </Box>
      </Group>
    </UnstyledButton>
  );
}
