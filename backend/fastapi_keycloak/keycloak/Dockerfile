# Use the official Keycloak image as the base image
FROM quay.io/keycloak/keycloak:25.0.4

# Set environment variables
ENV KEYCLOAK_ADMIN=admin
ENV KEYCLOAK_ADMIN_PASSWORD=admin
ENV KC_LOG_LEVEL=INFO

# Expose the default port
EXPOSE 8080

# Use a volume for persistent data
VOLUME ["/opt/keycloak/data/"]

# Set the command to start Keycloak in development mode
CMD ["start-dev"]