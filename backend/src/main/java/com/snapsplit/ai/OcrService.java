package com.snapsplit.ai;

import lombok.extern.slf4j.Slf4j;
import net.sourceforge.tess4j.Tesseract;
import net.sourceforge.tess4j.TesseractException;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.imageio.ImageIO;
import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

/**
 * OCR service using Tess4J — equivalent to Python's ai/ocr.py
 *
 * Multi-strategy OCR with quality scoring:
 * 1. Direct PSM 6 (uniform block)
 * 2. Preprocessed (grayscale + threshold)
 * 3. Direct PSM 3 (auto page segmentation)
 *
 * Picks the best result based on text length, word count, digit ratio.
 */
@Slf4j
@Component
public class OcrService {

    @Value("${app.ocr.tessdata-path:#{null}}")
    private String tessdataPath;

    public String extractText(String imagePath) {
        log.info("Starting OCR extraction from: {}", imagePath);

        File imageFile = new File(imagePath);
        if (!imageFile.exists()) {
            throw new OcrException("Image file not found: " + imagePath);
        }

        List<ScoredResult> results = new ArrayList<>();

        // Strategy 1: Direct OCR, PSM 6
        tryStrategy(results, "direct_psm6", () -> {
            Tesseract tess = createTesseract();
            tess.setPageSegMode(6);
            return tess.doOCR(imageFile);
        });

        // Strategy 2: Preprocessed image (grayscale + threshold)
        tryStrategy(results, "preprocessed", () -> {
            BufferedImage processed = preprocessImage(imageFile);
            Tesseract tess = createTesseract();
            tess.setPageSegMode(6);
            return tess.doOCR(processed);
        });

        // Strategy 3: Direct OCR, PSM 3 (auto)
        tryStrategy(results, "direct_psm3", () -> {
            Tesseract tess = createTesseract();
            tess.setPageSegMode(3);
            return tess.doOCR(imageFile);
        });

        if (results.isEmpty()) {
            throw new OcrException("All OCR strategies failed");
        }

        // Pick best result
        ScoredResult best = results.stream()
                .max(Comparator.comparingDouble(r -> r.score))
                .orElseThrow();

        if (best.text.length() < 10) {
            throw new OcrException("No text detected in image. Please ensure the image is clear.");
        }

        log.info("Best strategy: {} with score {:.1f} ({} characters)",
                best.strategy, best.score, best.text.length());
        return best.text;
    }

    private void tryStrategy(List<ScoredResult> results, String name,
            OcrCallable callable) {
        try {
            String text = callable.call().strip();
            double score = scoreText(text);
            results.add(new ScoredResult(name, text, score));
            log.debug("{}: score={}, len={}", name, score, text.length());
        } catch (Exception e) {
            log.warn("Strategy {} failed: {}", name, e.getMessage());
        }
    }

    private double scoreText(String text) {
        if (text.length() < 10)
            return 0;

        double lengthScore = text.length();
        double wordCount = text.split("\\s+").length * 5.0;
        double digitCount = text.chars().filter(Character::isDigit).count() * 3.0;
        long alnumCount = text.chars().filter(Character::isLetterOrDigit).count();
        double alnumRatio = (double) alnumCount / text.length() * 100.0;

        return lengthScore + wordCount + digitCount + alnumRatio;
    }

    private Tesseract createTesseract() {
        Tesseract tess = new Tesseract();
        tess.setLanguage("eng");
        if (tessdataPath != null && !tessdataPath.isEmpty()) {
            tess.setDatapath(tessdataPath);
        }
        return tess;
    }

    /**
     * Basic preprocessing — grayscale conversion + contrast enhancement.
     */
    private BufferedImage preprocessImage(File imageFile) throws IOException {
        BufferedImage original = ImageIO.read(imageFile);
        if (original == null) {
            throw new IOException("Cannot read image: " + imageFile.getAbsolutePath());
        }

        // Convert to grayscale
        BufferedImage grayscale = new BufferedImage(
                original.getWidth(), original.getHeight(), BufferedImage.TYPE_BYTE_GRAY);
        Graphics2D g = grayscale.createGraphics();
        g.drawImage(original, 0, 0, null);
        g.dispose();

        return grayscale;
    }

    @FunctionalInterface
    private interface OcrCallable {
        String call() throws TesseractException, IOException;
    }

    private record ScoredResult(String strategy, String text, double score) {
    }

    public static class OcrException extends RuntimeException {
        public OcrException(String message) {
            super(message);
        }

        public OcrException(String message, Throwable cause) {
            super(message, cause);
        }
    }
}
