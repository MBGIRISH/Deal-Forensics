# Deal Forensics AI - Enterprise-Grade Deal Analysis System

A comprehensive multi-agent AI system that analyzes lost sales deals to uncover failure points, benchmark against historical data, and generate actionable recovery playbooks with professional PDF reports.

## 🎯 Overview

Deal Forensics AI uses advanced AI agents powered by LangChain/LangGraph to:
- **Extract chronological timelines** from deal documents with natural language date parsing
- **Identify root causes and warning signs** through deep document analysis
- **Generate actionable recommendations** and best practices
- **Compare against historical lost deals** for pattern detection
- **Produce enterprise-grade PDF reports** with comprehensive insights

## ✨ Key Features

### 1. **Advanced Timeline Extraction**
- Extracts real events: initial outreach, negotiations, pricing discussions, escalations, final decisions
- Natural language date parsing ("January 5th", "two days later", "during negotiation")
- Realistic timestamp inference with 1-7 day gaps (never epoch dates)
- Timeline Score (1-10) based on clarity, ordering, missing events, ambiguity, delays
- Sentiment scoring per event (positive/neutral/negative)
- Color-coded visualization with sentiment markers
- All 5 phases always present: Discovery, Pricing Negotiation, Delivery Planning, Issue/Escalation, Final Decision

### 2. **Comprehensive Playbook Generator**
- **What Went Wrong** (6-10 root causes): Pricing ambiguity, missing documentation, poor communication, competitor advantage, timeline delays
- **Red Flags** (6-10 warnings): Verbal discounts, no written confirmation, undefined penalties, missing warranty terms
- **Recommendations** (8-12 actionable steps): Send written summaries, fix pricing terms, add delivery penalties, require documented approvals
- **Best Practices** (6-10 improvements): CRM-based documentation, standard templates, weekly reviews, competitor intelligence

### 3. **Business Intelligence Metrics**
- **Timeline Score** (0-10): Measures timeline clarity and completeness
- **Pricing Clarity Score** (0-10): Evaluates pricing transparency and consistency
- **Communication Quality Score** (0-10): Assesses response times and clarity
- **Documentation Quality Score** (0-10): Measures completeness of written records
- **Competitive Risk Score** (0-10): Evaluates competitor pressure and differentiation
- **Delivery Execution Score** (0-10): Assesses timeline adherence and planning
- **Final Deal Health Score** (0-10): Overall deal health composite score

### 4. **Comparative Analytics**
- Compares against 3-5 similar historical deals from `/deals/` folder
- Similarity percentages and shared patterns
- Risk distribution analysis with pie charts
- Benchmark metrics and comparative tables
- Common patterns across lost deals
- Shared risk factors identification

### 5. **Enterprise-Grade PDF Reports**
- Title page with version and date
- Executive summary (5-7 sentences)
- Deal overview table with all metadata
- Full timeline with dates, sentiment, and confidence scores
- All playbook sections (What Went Wrong, Red Flags, Recommendations, Best Practices)
- Comparative analytics section
- Business intelligence metrics table
- Final summary paragraph
- Professional styling with icons, dividers, and color highlights

### 6. **Strict Document Validation**
- File type validation (PDF, DOCX, DOC, TXT)
- File size limits (100 bytes - 100 MB)
- Financial keyword detection (minimum 3 required)
- Non-business content filtering
- Structured text validation
- LLM-based relevance checking
- Graceful error messages with guidance

## 🏗️ Architecture

### Multi-Agent System (LangGraph)
```
┌─────────────────┐
│  Timeline Agent │ → Extracts chronological events with dates
└────────┬────────┘
         │
┌────────▼────────┐
│Comparative Agent│ → Benchmarks against historical deals
└────────┬────────┘
         │
┌────────▼────────┐
│ Playbook Agent  │ → Generates insights and recommendations
└─────────────────┘
```

### RAG Pipeline
- **Embeddings**: HuggingFace `sentence-transformers/all-mpnet-base-v2`
- **Vector Store**: FAISS (in-memory, fast similarity search)
- **Chunking**: RecursiveCharacterTextSplitter (1024 chars, 128 overlap)
- **Retrieval**: Top 5 most relevant chunks per agent

### Data Persistence
- **Primary**: MongoDB (optional, configured via `MONGODB_URI`)
- **Fallback**: JSON file (`data/historical_deals.json`)
- **Storage**: Deal metadata, scores, loss summaries

## 📋 Prerequisites

- **Python**: 3.11+ (recommended)
- **MongoDB**: Optional (for persistent storage)
- **API Keys**: 
  - Google Gemini API key (for LLM)
  - OpenAI API key (optional, alternative LLM)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd DealForensics

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root:

```bash
# Required: LLM Provider
GOOGLE_API_KEY=your_google_api_key_here
LLM_PROVIDER=google  # or "openai"

# Optional: OpenAI (if using OpenAI instead)
OPENAI_API_KEY=your_openai_api_key_here

# Optional: MongoDB (for persistent storage)
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=deal_forensics
MONGODB_COLLECTION=historical_deals

# Optional: Custom paths
VECTOR_DB_PATH=.cache/vector_index
EMBEDDING_CACHE_PATH=.cache/embedding_cache.pkl
REPORT_OUTPUT_DIR=reports
DEFAULT_HISTORICAL_DATA=data/historical_deals.json
```

### 3. Run the Application

```bash
# Start Streamlit dashboard
streamlit run ui/dashboard.py
```

The application will open in your browser at `http://localhost:8501`

### 4. Upload and Analyze

1. Upload a financial/deal document (PDF, DOCX, or TXT)
2. Click "Analyze Deal"
3. View comprehensive analysis with:
   - Deal summary and metrics
   - Timeline visualization
   - Playbook insights
   - Comparative analytics
   - Downloadable PDF report

## 📁 Project Structure

```
DealForensics/
├── agents/              # Multi-agent system
│   ├── timeline_agent.py      # Timeline extraction
│   ├── comparative_agent.py   # Historical benchmarking
│   ├── playbook_agent.py      # Insights generation
│   └── graph.py               # LangGraph orchestration
├── core/                # Core functionality
│   ├── config.py              # Configuration management
│   ├── deal_parser.py         # Metadata extraction
│   ├── document_validator.py  # Document validation
│   ├── gemini_client.py       # Gemini API client
│   ├── repository.py          # MongoDB/JSON persistence
│   └── scoring.py             # Business metrics
├── rag/                 # RAG pipeline
│   ├── embedder.py            # HuggingFace embeddings
│   ├── loader.py              # Document loading
│   └── vectorstore.py         # FAISS vector store
├── ui/                  # Streamlit dashboard
│   └── dashboard.py           # Main UI
├── utils/               # Utilities
│   └── pdf_report.py          # PDF report generator
├── deals/               # Historical deal documents (for comparison)
├── data/                # JSON fallback storage
├── app.py               # Main orchestration
├── main.py              # CLI entry point
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🔧 Configuration

### LLM Provider

The system supports two LLM providers:

1. **Google Gemini** (Recommended, Free Tier Available)
   - Models: `gemini-1.5-flash`, `gemini-1.5-pro`, `gemini-pro`
   - Set `LLM_PROVIDER=google` and provide `GOOGLE_API_KEY`

2. **OpenAI** (Alternative)
   - Models: `gpt-4`, `gpt-3.5-turbo`
   - Set `LLM_PROVIDER=openai` and provide `OPENAI_API_KEY`

### MongoDB Setup (Optional)

MongoDB is optional but recommended for production:

```bash
# Install MongoDB (macOS)
brew install mongodb-community
brew services start mongodb-community

# Or use Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

The system automatically falls back to JSON file storage if MongoDB is unavailable.

## 📊 Document Requirements

### Accepted File Types
- **PDF** (.pdf)
- **Word Documents** (.docx, .doc)
- **Text Files** (.txt)

### File Size Limits
- **Minimum**: 100 bytes
- **Maximum**: 100 MB

### Content Requirements
- Must contain financial/deal-related content
- Minimum 3 financial keywords (e.g., deal, contract, pricing, valuation)
- Structured text (minimum 1 substantial line)
- Business context (minimum 1 business indicator)

### Example Documents
- Valuation reports
- Term sheets
- M&A documents
- Investment proposals
- Lost sales deal post-mortems
- Financial contracts

## 🎨 Features in Detail

### Timeline Visualization
- Interactive timeline chart with phase grouping
- Color-coded by sentiment (green=positive, gray=neutral, red=negative)
- Date range display with proper formatting
- Timeline score indicator

### Deal Summary Card
- Seller/Owner
- Buyer/Deal Name
- Deal Value (with currency formatting)
- Industry
- Outcome (Closed Lost/Won)
- Key Issue highlight

### Win Probability Score
- Calculated from Final Deal Health Score
- Visual progress bar
- Risk level indicators (Very Low, Low, Medium, High)

### Loss Driver Analysis
- Horizontal bar chart showing risk scores by category
- Categories: Pricing Issues, Communication, Documentation, Competitive Risk, Delivery/Execution
- Color gradient from low (green) to high (red) risk

### Comparative Analytics
- Similarity percentage bar chart
- Risk distribution pie chart
- Common patterns list
- Shared risk factors
- Benchmark scores table
- Comparative metrics table

### Playbook Sections
- **What Went Wrong**: Root cause analysis with ❌ icons
- **Red Flags**: Warning signs with ⚠️ icons
- **Recommendations**: Actionable steps with ✔️ icons and priority levels
- **Best Practices**: Long-term improvements with ⭐ icons

## 🔍 API Usage

### CLI Interface

```bash
# Analyze a document via CLI
python main.py analyze path/to/document.pdf

# View recent deals
python main.py list --limit 10
```

### Python API

```python
from app import DealForensicsOrchestrator

orchestrator = DealForensicsOrchestrator()

# Analyze a file
with open("deal_document.pdf", "rb") as f:
    result = orchestrator.analyze_file(f.read(), "deal_document.pdf")

# Access results
timeline = result["timeline"]
playbook = result["playbook"]
scorecard = result["scorecard"]
comparative = result["comparative"]
pdf_report = result["report"]  # Bytes
```

## 🧪 Testing

### Test Document

A sample test document is available in the repository. Upload it to test the system:

```bash
# The system includes 10 historical deal documents in /deals/ folder
# These are used for comparative analysis
```

### Validation Testing

The system includes comprehensive document validation:
- File type checking
- Size validation
- Content relevance detection
- Business keyword verification
- Structured text validation

## 📈 Performance

- **Processing Time**: ~10-30 seconds per document (depends on document size and LLM response time)
- **Vector Search**: <100ms (FAISS in-memory)
- **PDF Generation**: ~2-5 seconds
- **MongoDB Insert**: <50ms

## 🛠️ Troubleshooting

### Common Issues

1. **"Document Validation Failed"**
   - Ensure document contains financial/deal-related content
   - Check file size (must be 100 bytes - 100 MB)
   - Verify file type (PDF, DOCX, DOC, or TXT)

2. **"LLM API Error"**
   - Verify API key is set in `.env`
   - Check API quota/rate limits
   - Ensure internet connection

3. **"MongoDB Connection Failed"**
   - System automatically falls back to JSON storage
   - Check MongoDB is running: `mongosh --eval "db.adminCommand('ping')"`
   - Verify `MONGODB_URI` in `.env`

4. **"No timeline events extracted"**
   - Document may lack chronological information
   - System will generate inferred timeline
   - Check document contains dates or time references

### Debug Mode

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔐 Security

- API keys stored in `.env` (never commit to version control)
- Document validation prevents malicious file uploads
- Text sanitization for PDF generation
- No sensitive data logged

## 📝 License

[Specify your license here]

## 🤝 Contributing

[Contributing guidelines if applicable]

## 📧 Support

[Support contact information]

## 🎯 Roadmap

- [ ] Real-time collaboration features
- [ ] Advanced analytics dashboard
- [ ] Integration with CRM systems
- [ ] Custom report templates
- [ ] Multi-language support
- [ ] API rate limiting
- [ ] User authentication

## 🙏 Acknowledgments

- LangChain/LangGraph for multi-agent orchestration
- HuggingFace for embeddings
- FAISS for vector search
- Streamlit for UI
- Google Gemini / OpenAI for LLM capabilities

---

**Built with ❤️ for sales teams who want to learn from lost deals**
