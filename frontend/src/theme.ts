import { createTheme, type MantineColorsTuple } from '@mantine/core';

const home: MantineColorsTuple = [
  '#fdeee7',
  '#fbd9c9',
  '#f7b294',
  '#f38b5f',
  '#ef6f3d',
  '#eb6535',
  '#e8622c',
  '#d1541f',
  '#b04618',
  '#8f3812',
];

const dark: MantineColorsTuple = [
  '#edeae1', // 0 paper (lightest text)
  '#d6d3c7', // 1
  '#a9a69c', // 2 paper-dim
  '#6e7680', // 3
  '#2b383f', // 4 line (borders)
  '#212b31', // 5
  '#1b252b', // 6 panel (surfaces)
  '#172025', // 7
  '#141c21', // 8 court
  '#0b1013', // 9 ink (darkest)
];

export const theme = createTheme({
  primaryColor: 'home',
  colors: { home, dark },
  fontFamily: "'Inter', system-ui, sans-serif",
  fontFamilyMonospace: "'IBM Plex Mono', ui-monospace, monospace",
  headings: {
    fontFamily: "'Oswald', system-ui, sans-serif",
    fontWeight: '600',
  },
  defaultRadius: 'sm',
  components: {
    Button: {
      defaultProps: { radius: 'sm' },
    },
    Tabs: {
      styles: {
        tab: {
          fontFamily: "'IBM Plex Mono', monospace",
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
        },
      },
    },
  },
});
