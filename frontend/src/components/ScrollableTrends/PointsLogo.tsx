import logoSrc from './points_logo.svg';

export function PointsLogo(props: React.ImgHTMLAttributes<HTMLImageElement>) {
  return <img src={logoSrc} alt="Points Logo" {...props} />;
}