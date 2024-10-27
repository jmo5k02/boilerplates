# Use the official PostGIS image as the base image
FROM postgres:16.4

ADD create.sql /docker-entrypoint-initdb.d

# Expose the PostgreSQL port
EXPOSE 5432

# Define a volume for PostgreSQL data persistence
VOLUME ["/var/lib/postgresql/data"]

# Start PostgreSQL
CMD ["postgres"]