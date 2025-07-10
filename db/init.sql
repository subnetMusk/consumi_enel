DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'enel') THEN
      CREATE DATABASE enel;
   END IF;
END
$$;
