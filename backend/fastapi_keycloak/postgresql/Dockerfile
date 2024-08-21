# Use the official PostGIS image as the base image
FROM postgres:13.16

# Set environment variables
ENV POSTGRES_USER=test
ENV POSTGRES_PASSWORD=test
ENV POSTGRES_DB=test

# Expose the PostgreSQL port
EXPOSE 5432

# Define a volume for PostgreSQL data persistence
VOLUME ["/var/lib/postgresql/data"]

# Start PostgreSQL
CMD ["postgres"]