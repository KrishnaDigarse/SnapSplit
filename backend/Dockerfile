# === Build stage ===
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline -B
COPY src ./src
RUN mvn package -DskipTests -B

# === Runtime stage ===
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app

# Install Tesseract OCR for AI bill-scanning pipeline
RUN apk add --no-cache tesseract-ocr tesseract-ocr-data-eng

# Create non-root user
RUN addgroup -S spring && adduser -S spring -G spring

# Create uploads directory
RUN mkdir -p /app/uploads/bills && chown -R spring:spring /app

USER spring:spring

COPY --from=build /app/target/*.jar app.jar

EXPOSE 8000

ENTRYPOINT ["java", \
    "-Djava.awt.headless=true", \
    "-jar", "app.jar"]
