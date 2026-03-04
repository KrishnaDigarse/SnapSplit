package com.snapsplit.ai;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import java.util.List;
import java.util.Map;

/**
 * LLM client for Groq API — equivalent to Python's ai/llm.py
 *
 * Calls Groq's chat completions API with JSON mode to extract
 * structured bill data from OCR text.
 */
@Slf4j
@Component
public class LlmService {

    private static final String GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions";

    private final RestClient restClient;
    private final ObjectMapper objectMapper;

    @Value("${app.groq.api-key:}")
    private String apiKey;

    @Value("${app.groq.model:llama-3.3-70b-versatile}")
    private String model;

    public LlmService(ObjectMapper objectMapper) {
        this.restClient = RestClient.builder().build();
        this.objectMapper = objectMapper;
    }

    /**
     * Extract structured bill data from OCR text using Groq LLM.
     * Python equivalent: llm.extract_bill_data(ocr_text)
     */
    public Map<String, Object> extractBillData(String ocrText) {
        if (apiKey == null || apiKey.isBlank()) {
            throw new LlmException("GROQ_API_KEY not configured. Set app.groq.api-key in application.yml");
        }

        if (ocrText == null || ocrText.strip().length() < 10) {
            throw new LlmException("OCR text is too short or empty");
        }

        log.info("Extracting bill data via Groq LLM (model: {})", model);

        String prompt = BillPrompts.getExtractionPrompt(ocrText);

        // Build Groq API request body (OpenAI-compatible)
        Map<String, Object> requestBody = Map.of(
                "model", model,
                "messages", List.of(
                        Map.of("role", "system", "content",
                                "You are a precise bill parser that extracts structured data from receipts. Always return valid JSON only."),
                        Map.of("role", "user", "content", prompt)),
                "temperature", 0,
                "max_tokens", 2048,
                "response_format", Map.of("type", "json_object"));

        // Call API with retry (up to 3 attempts)
        String responseJson = null;
        Exception lastError = null;
        for (int attempt = 1; attempt <= 3; attempt++) {
            try {
                responseJson = callGroqApi(requestBody);
                break;
            } catch (Exception e) {
                lastError = e;
                log.warn("Groq API attempt {}/3 failed: {}", attempt, e.getMessage());
                if (attempt < 3) {
                    try {
                        Thread.sleep(1000L * attempt);
                    } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                    }
                }
            }
        }

        if (responseJson == null) {
            throw new LlmException("Groq API failed after 3 attempts: " +
                    (lastError != null ? lastError.getMessage() : "unknown error"));
        }

        // Parse the LLM output JSON
        try {
            @SuppressWarnings("unchecked")
            Map<String, Object> data = objectMapper.readValue(responseJson,
                    new TypeReference<Map<String, Object>>() {
                    });

            // Validate required fields
            for (String field : List.of("items", "subtotal", "tax", "total")) {
                if (!data.containsKey(field)) {
                    throw new LlmException("LLM response missing required field: " + field);
                }
            }

            log.info("LLM extracted {} items", ((List<?>) data.get("items")).size());
            return data;
        } catch (JsonProcessingException e) {
            throw new LlmException("LLM returned invalid JSON: " + e.getMessage());
        }
    }

    private String callGroqApi(Map<String, Object> requestBody) {
        try {
            String body = objectMapper.writeValueAsString(requestBody);

            String response = restClient.post()
                    .uri(GROQ_API_URL)
                    .header("Authorization", "Bearer " + apiKey)
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(body)
                    .retrieve()
                    .body(String.class);

            // Parse the completion response
            @SuppressWarnings("unchecked")
            Map<String, Object> parsed = objectMapper.readValue(response,
                    new TypeReference<Map<String, Object>>() {
                    });

            @SuppressWarnings("unchecked")
            List<Map<String, Object>> choices = (List<Map<String, Object>>) parsed.get("choices");
            if (choices == null || choices.isEmpty()) {
                throw new LlmException("Groq API returned empty choices");
            }

            @SuppressWarnings("unchecked")
            Map<String, Object> message = (Map<String, Object>) choices.get(0).get("message");
            String content = (String) message.get("content");

            if (content == null || content.isBlank()) {
                throw new LlmException("Groq API returned empty content");
            }

            log.info("Groq response: {} chars", content.length());
            return content.strip();
        } catch (LlmException e) {
            throw e;
        } catch (Exception e) {
            throw new LlmException("Groq API call failed: " + e.getMessage());
        }
    }

    public static class LlmException extends RuntimeException {
        public LlmException(String message) {
            super(message);
        }
    }
}
