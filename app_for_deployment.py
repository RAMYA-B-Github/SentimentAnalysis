#!/usr/bin/env python3
"""
E-Consultation Sentiment Analysis App - Cloud Deployment Version
Optimized for cloud platforms like Render, Railway, Heroku
"""

import os
import json
import csv
import re
from datetime import datetime
from collections import Counter

# Import Flask with error handling
try:
    from flask import Flask, request, jsonify
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

class SimpleSentimentAnalyzer:
    def __init__(self):
        self.positive_words = [
            'good', 'great', 'excellent', 'positive', 'support', 'agree', 'approve', 
            'like', 'love', 'amazing', 'wonderful', 'fantastic', 'perfect', 
            'outstanding', 'brilliant', 'commend', 'endorse', 'recommend', 'beneficial',
            'effective', 'successful', 'impressive', 'satisfactory', 'adequate'
        ]
        self.negative_words = [
            'bad', 'terrible', 'awful', 'negative', 'oppose', 'disagree', 'disapprove', 
            'hate', 'dislike', 'horrible', 'disgusting', 'worst', 'fail', 'problem', 
            'issue', 'concern', 'flawed', 'inadequate', 'insufficient', 'problematic',
            'disappointing', 'unsatisfactory', 'poor', 'weak', 'deficient'
        ]
    
    def analyze_sentiment(self, text):
        if not text:
            return {'label': 'neutral', 'confidence': 0.0, 'polarity': 0.0}
        
        text_lower = text.lower()
        positive_count = sum(1 for word in self.positive_words if word in text_lower)
        negative_count = sum(1 for word in self.negative_words if word in text_lower)
        
        if positive_count > negative_count:
            label = 'positive'
            polarity = min(0.8, 0.3 + (positive_count - negative_count) * 0.1)
        elif negative_count > positive_count:
            label = 'negative'
            polarity = max(-0.8, -0.3 - (negative_count - positive_count) * 0.1)
        else:
            label = 'neutral'
            polarity = 0.0
        
        confidence = min(1.0, 0.5 + abs(positive_count - negative_count) * 0.1)
        
        return {
            'label': label,
            'confidence': round(confidence, 4),
            'polarity': round(polarity, 4)
        }

class SimpleTextSummarizer:
    def __init__(self):
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        }
    
    def generate_summary(self, text, max_sentences=3):
        if not text:
            return "No text provided for summarization."
        
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
        if len(sentences) <= max_sentences:
            return text
        
        # Simple extractive summarization
        word_freq = Counter()
        for sentence in sentences:
            words = re.findall(r'\w+', sentence.lower())
            for word in words:
                if word not in self.stop_words and len(word) > 3:
                    word_freq[word] += 1
        
        # Score sentences
        sentence_scores = []
        for i, sentence in enumerate(sentences):
            words = re.findall(r'\w+', sentence.lower())
            score = sum(word_freq.get(word, 0) for word in words if word not in self.stop_words)
            sentence_scores.append((score, i, sentence))
        
        # Get top sentences
        sentence_scores.sort(reverse=True)
        top_sentences = sorted(sentence_scores[:max_sentences], key=lambda x: x[1])
        
        return '. '.join([sentence for _, _, sentence in top_sentences]) + '.'

# Initialize components
sentiment_analyzer = SimpleSentimentAnalyzer()
text_summarizer = SimpleTextSummarizer()

# Create Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>E-Consultation Sentiment Analysis</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container { 
                max-width: 1000px; 
                margin: 0 auto; 
                background: white; 
                border-radius: 15px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                overflow: hidden;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }
            .header h1 { font-size: 2.5rem; margin-bottom: 10px; }
            .header p { font-size: 1.1rem; opacity: 0.9; }
            .content { padding: 40px; }
            .upload-section { 
                background: #f8f9fa; 
                padding: 30px; 
                border-radius: 10px; 
                margin-bottom: 30px;
                border: 2px dashed #dee2e6;
                text-align: center;
            }
            .upload-section h3 { color: #495057; margin-bottom: 20px; }
            input[type="file"] { 
                margin: 15px 0; 
                padding: 10px;
                border: 1px solid #ced4da;
                border-radius: 5px;
                background: white;
            }
            button { 
                background: linear-gradient(135deg, #28a745, #20c997);
                color: white; 
                padding: 12px 30px; 
                border: none; 
                border-radius: 25px; 
                cursor: pointer; 
                font-size: 1rem;
                font-weight: 600;
                transition: all 0.3s ease;
            }
            button:hover { 
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(40, 167, 69, 0.4);
            }
            .results { 
                margin-top: 30px; 
                padding: 30px; 
                background: #f8f9fa; 
                border-radius: 10px; 
            }
            .status { 
                margin: 15px 0; 
                padding: 15px; 
                border-radius: 8px; 
                font-weight: 500;
            }
            .success { background: #d4edda; color: #155724; border-left: 4px solid #28a745; }
            .error { background: #f8d7da; color: #721c24; border-left: 4px solid #dc3545; }
            .info { background: #d1ecf1; color: #0c5460; border-left: 4px solid #17a2b8; }
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }
            .stat-card {
                background: white;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .stat-number { font-size: 2rem; font-weight: bold; margin-bottom: 5px; }
            .stat-label { color: #6c757d; font-size: 0.9rem; }
            .positive { color: #28a745; }
            .negative { color: #dc3545; }
            .neutral { color: #6c757d; }
            table { 
                width: 100%; 
                border-collapse: collapse; 
                margin-top: 20px;
                background: white;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            th, td { 
                padding: 12px; 
                text-align: left; 
                border-bottom: 1px solid #dee2e6; 
            }
            th { 
                background: #495057; 
                color: white; 
                font-weight: 600;
                text-transform: uppercase;
                font-size: 0.85rem;
                letter-spacing: 0.5px;
            }
            tr:hover { background: #f8f9fa; }
            .sentiment-badge {
                padding: 4px 12px;
                border-radius: 15px;
                font-size: 0.8rem;
                font-weight: 600;
                text-transform: uppercase;
            }
            .sentiment-positive { background: #d4edda; color: #155724; }
            .sentiment-negative { background: #f8d7da; color: #721c24; }
            .sentiment-neutral { background: #e2e3e5; color: #495057; }
            .summary-box {
                background: white;
                padding: 25px;
                border-radius: 10px;
                margin: 20px 0;
                border-left: 4px solid #667eea;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .summary-box h4 { color: #495057; margin-bottom: 15px; }
            @media (max-width: 768px) {
                .header h1 { font-size: 2rem; }
                .content { padding: 20px; }
                .stats-grid { grid-template-columns: 1fr; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🗳️ E-Consultation Sentiment Analysis</h1>
                <p>AI-Powered Analysis of Stakeholder Comments and Feedback</p>
            </div>
            
            <div class="content">
                <div class="upload-section">
                    <h3>📁 Upload Comments File</h3>
                    <p>Upload CSV files containing stakeholder comments for comprehensive sentiment analysis</p>
                    <form id="uploadForm" enctype="multipart/form-data">
                        <input type="file" id="fileInput" accept=".csv" required>
                        <br>
                        <button type="submit">🚀 Upload & Analyze</button>
                    </form>
                </div>
                
                <div id="status"></div>
                <div id="results"></div>
            </div>
        </div>
        
        <script>
            document.getElementById('uploadForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const fileInput = document.getElementById('fileInput');
                const file = fileInput.files[0];
                
                if (!file) {
                    showStatus('Please select a CSV file', 'error');
                    return;
                }
                
                showStatus('📊 Uploading and analyzing comments...', 'info');
                
                const formData = new FormData();
                formData.append('file', file);
                
                try {
                    const response = await fetch('/upload', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        showStatus(`✅ Analysis Complete! Processed ${result.total_comments} comments`, 'success');
                        displayResults(result);
                    } else {
                        showStatus(`❌ Error: ${result.error}`, 'error');
                    }
                } catch (error) {
                    showStatus(`❌ Network Error: ${error.message}`, 'error');
                }
            });
            
            function showStatus(message, type) {
                document.getElementById('status').innerHTML = `<div class="status ${type}">${message}</div>`;
            }
            
            function displayResults(data) {
                let html = '<div class="results">';
                
                // Statistics cards
                html += '<div class="stats-grid">';
                html += `<div class="stat-card">
                    <div class="stat-number">${data.total_comments}</div>
                    <div class="stat-label">Total Comments</div>
                </div>`;
                html += `<div class="stat-card">
                    <div class="stat-number positive">${data.sentiment_distribution.positive || 0}</div>
                    <div class="stat-label">Positive</div>
                </div>`;
                html += `<div class="stat-card">
                    <div class="stat-number negative">${data.sentiment_distribution.negative || 0}</div>
                    <div class="stat-label">Negative</div>
                </div>`;
                html += `<div class="stat-card">
                    <div class="stat-number neutral">${data.sentiment_distribution.neutral || 0}</div>
                    <div class="stat-label">Neutral</div>
                </div>`;
                html += '</div>';
                
                // Summary
                if (data.summary) {
                    html += `<div class="summary-box">
                        <h4>📝 Generated Summary</h4>
                        <p>${data.summary}</p>
                    </div>`;
                }
                
                // Detailed results table
                html += '<table><thead><tr><th>ID</th><th>Comment Preview</th><th>Sentiment</th><th>Confidence</th><th>Polarity</th></tr></thead><tbody>';
                
                data.sentiment_results.forEach(result => {
                    const badgeClass = `sentiment-${result.sentiment}`;
                    html += `<tr>
                        <td>${result.id}</td>
                        <td>${result.text}</td>
                        <td><span class="sentiment-badge ${badgeClass}">${result.sentiment}</span></td>
                        <td>${(result.confidence * 100).toFixed(1)}%</td>
                        <td>${result.polarity.toFixed(3)}</td>
                    </tr>`;
                });
                
                html += '</tbody></table></div>';
                document.getElementById('results').innerHTML = html;
            }
        </script>
    </body>
    </html>
    '''

@app.route('/upload', methods=['POST'])
def upload_and_analyze():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file selected'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Process CSV directly from memory
        content = file.read().decode('utf-8')
        lines = content.strip().split('\n')
        
        if len(lines) < 2:
            return jsonify({'error': 'CSV file must have at least a header and one data row'}), 400
        
        # Parse CSV
        reader = csv.DictReader(lines)
        comments = []
        
        for i, row in enumerate(reader, 1):
            # Find text column
            text = None
            for key in row.keys():
                if any(word in key.lower() for word in ['comment', 'text', 'feedback', 'suggestion', 'remarks']):
                    text = row[key]
                    break
            
            if not text and row:
                text = next((v for v in row.values() if v and len(str(v).strip()) > 10), None)
            
            if text and len(str(text).strip()) > 5:
                comments.append({
                    'id': row.get('id', i),
                    'text': str(text).strip()
                })
        
        if not comments:
            return jsonify({'error': 'No valid comments found in CSV file'}), 400
        
        # Analyze sentiments
        sentiment_results = []
        for comment in comments:
            sentiment = sentiment_analyzer.analyze_sentiment(comment['text'])
            sentiment_results.append({
                'id': comment['id'],
                'text': comment['text'][:200] + '...' if len(comment['text']) > 200 else comment['text'],
                'sentiment': sentiment['label'],
                'confidence': sentiment['confidence'],
                'polarity': sentiment['polarity']
            })
        
        # Generate summary
        all_text = ' '.join([comment['text'] for comment in comments])
        summary = text_summarizer.generate_summary(all_text)
        
        # Calculate distribution
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        total_polarity = 0
        
        for result in sentiment_results:
            sentiment_counts[result['sentiment']] += 1
            total_polarity += result['polarity']
        
        avg_polarity = total_polarity / len(sentiment_results) if sentiment_results else 0
        
        return jsonify({
            'sentiment_results': sentiment_results,
            'summary': summary,
            'sentiment_distribution': sentiment_counts,
            'average_polarity': round(avg_polarity, 4),
            'total_comments': len(sentiment_results)
        })
        
    except Exception as e:
        return jsonify({'error': f'Processing error: {str(e)}'}), 500

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'message': 'E-Consultation Sentiment Analysis API is running'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
