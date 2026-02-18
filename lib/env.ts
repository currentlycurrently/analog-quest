// Environment variable validation and types

const requiredEnvVars = [
  'DATABASE_URL',
] as const;

const optionalEnvVars = [
  'NEXT_PUBLIC_API_URL',
  'ENABLE_WRITE_OPS',
  'VERCEL_URL',
  'NODE_ENV',
] as const;

type RequiredEnvVars = {
  [K in typeof requiredEnvVars[number]]: string;
};

type OptionalEnvVars = {
  [K in typeof optionalEnvVars[number]]?: string;
};

export type EnvVars = RequiredEnvVars & OptionalEnvVars;

function validateEnv(): EnvVars {
  const missingVars: string[] = [];

  for (const varName of requiredEnvVars) {
    if (!process.env[varName]) {
      missingVars.push(varName);
    }
  }

  if (missingVars.length > 0) {
    throw new Error(
      `Missing required environment variables: ${missingVars.join(', ')}\n` +
      `Please check your .env.local file`
    );
  }

  return {
    DATABASE_URL: process.env.DATABASE_URL!,
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    ENABLE_WRITE_OPS: process.env.ENABLE_WRITE_OPS,
    VERCEL_URL: process.env.VERCEL_URL,
    NODE_ENV: process.env.NODE_ENV,
  };
}

export const env = validateEnv();