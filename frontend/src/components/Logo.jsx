
import React, { useState, useEffect } from 'react';
import { getAssetUrl } from '../utils/assetManager';

export default function Logo() {
  const [logoUrl, setLogoUrl] = useState('');

  useEffect(() => {
    const loadLogo = async () => {
      const url = await getAssetUrl('logo.png');
      if (url) setLogoUrl(url);
    };
    loadLogo();
  }, []);

  return logoUrl ? <img src={logoUrl} alt="Aureate Revolution Logo" className="h-12"/> : null;
}
