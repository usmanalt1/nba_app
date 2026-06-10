import logoSrc from './logo.svg';

export function Logo(props: React.ImgHTMLAttributes<HTMLImageElement>) {
  return <img src={logoSrc} alt="Logo" {...props} />;
}