
import { Client } from '@replit/object-storage';

const client = new Client();
const BUCKET_NAME = 'AureateRevolutionAsset';

export const getAssetUrl = async (assetName) => {
  try {
    const url = await client.getSignedUrl(`${BUCKET_NAME}/${assetName}`);
    return url;
  } catch (error) {
    console.error('Error getting asset URL:', error);
    return null;
  }
};

export const listAssets = async () => {
  try {
    const assets = await client.list(BUCKET_NAME);
    return assets;
  } catch (error) {
    console.error('Error listing assets:', error);
    return [];
  }
};
