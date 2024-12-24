FROM pgvector/pgvector:pg17

# Add initialization scripts
COPY docker/init.sql /docker-entrypoint-initdb.d/01_init.sql

# Make sure the script is executable
RUN chmod +x /docker-entrypoint-initdb.d/01_init.sql