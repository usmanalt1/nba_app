import logoSrc from './points_logo.svg';
import logoReboundSrc from './rebounds.svg';
import logoAssistSrc from './assists.svg';
import logoPlusMinusSrc from './plus_minus.svg';

export function PointsLogo(props: React.ImgHTMLAttributes<HTMLImageElement>) {
  return <img src={logoSrc} alt="Points Logo" {...props} />;
}

export function ReboundsLogo(props: React.ImgHTMLAttributes<HTMLImageElement>) {
  return <img src={logoReboundSrc} alt="Rebounds Logo" {...props} />;
}

export function AssistsLogo(props: React.ImgHTMLAttributes<HTMLImageElement>) {
  return <img src={logoAssistSrc} alt="Assists Logo" {...props} />;
}

export function PlusMinusLogo(props: React.ImgHTMLAttributes<HTMLImageElement>) {
  return <img src={logoPlusMinusSrc} alt="Plus_Minus Logo" {...props} />;
}
