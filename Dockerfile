# Use the official PostgreSQL image
FROM postgres:15

# Install build dependencies and the postgresql-server-dev package
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    postgresql-server-dev-15

# Clone and install pgvector
RUN git clone --branch v0.4.4 https://github.com/pgvector/pgvector.git && \
    cd pgvector && \
    make && \
    make install

# Add initialization scripts
COPY docker/init.sql /docker-entrypoint-initdb.d/01_init.sql
