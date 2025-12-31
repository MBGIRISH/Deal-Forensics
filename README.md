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

### 7. **Premium Dashboard UI**
- Deal summary card (Seller, Buyer, Value, Industry, Outcome, Key Issue)
- Win Probability Score with visual progress bar
- Loss Driver Analysis bar chart
- Interactive timeline visualization with sentiment
- Sentiment distribution bars
- Competitor intelligence section
- All playbook sections with styled chips/tags
- Dark/Light mode support
- Downloadable PDF reports

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

- **Python**: 3.11+ (recommended) or 3.10+
- **MongoDB**: Optional (for persistent storage)
- **API Keys**: 
  - Google Gemini API key (recommended, free tier available)
  - OpenAI API key (optional, alternative LLM)

## 🚀 Quick Start

### Step 1: Clone the Repository

```bash
git clone https://github.com/MBGIRISH/DealForensics.git
cd DealForensics
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: Installation may take 5-10 minutes as it downloads ML models and dependencies.

### Step 4: Configure Environment

Create a `.env` file in the project root (copy from `env.example`):

```bash
cp env.example .env
```

Edit `.env` and add your API key:

```bash
# Required: LLM Provider (at least one)
GOOGLE_API_KEY=your_google_api_key_here
LLM_PROVIDER=google  # Default is "openai", set to "google" for Gemini

# Optional: OpenAI (if using OpenAI instead of Gemini)
OPENAI_API_KEY=your_openai_api_key_here

# Optional: MongoDB (for persistent storage)
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=deal_forensics
MONGODB_COLLECTION=historical_deals

# Optional: Custom paths (defaults work fine)
VECTOR_DB_PATH=.cache/vector_index
EMBEDDING_CACHE_PATH=.cache/embedding_cache.pkl
REPORT_OUTPUT_DIR=reports
DEFAULT_HISTORICAL_DATA=data/historical_deals.json
```

**Get API Keys:**
- **Google Gemini**: https://aistudio.google.com/app/apikey (Free tier available)
- **OpenAI**: https://platform.openai.com/api-keys

### Step 5: Run the Application

```bash
# Start Streamlit dashboard
streamlit run ui/dashboard.py
```

The application will automatically open in your browser at `http://localhost:8501`

### Step 6: Upload and Analyze

1. **Upload a Document**: Click "Upload Financial/Deal Document" and select a PDF, DOCX, or TXT file
2. **Click "Analyze Deal"**: The system will validate and process your document
3. **View Results**: Explore the comprehensive analysis:
   - Deal summary and metrics
   - Timeline visualization
   - Playbook insights
   - Comparative analytics
   - Downloadable PDF report

## 📁 Project Structure

```
DealForensics/
├── agents/                    # Multi-agent system
│   ├── __init__.py
│   ├── base.py               # Base agent class
│   ├── timeline_agent.py     # Timeline extraction with date parsing
│   ├── comparative_agent.py  # Historical deal comparison
│   ├── playbook_agent.py     # Recovery playbook generation
│   └── graph.py              # LangGraph orchestration
├── core/                      # Core functionality
│   ├── config.py             # Configuration management
│   ├── deal_parser.py        # Document parsing and metadata extraction
│   ├── document_validator.py  # Document validation
│   ├── gemini_client.py      # Google Gemini API client
│   ├── repository.py         # MongoDB/JSON persistence
│   ├── scoring.py            # Business intelligence scoring
│   └── cache.py              # Embedding cache
├── rag/                       # RAG Pipeline
│   ├── loader.py             # Document loading and chunking
│   ├── embedder.py           # HuggingFace embeddings
│   └── vectorstore.py        # FAISS vector store
├── ui/                        # User Interface
│   └── dashboard.py          # Streamlit dashboard
├── utils/                     # Utilities
│   └── pdf_report.py         # PDF report generator
├── deals/                     # Synthetic deal dataset (10 deals)
│   ├── deal_001_enterprise_saas.txt
│   ├── deal_002_healthcare_integration.txt
│   ├── deal_003_financial_crm.txt
│   ├── deal_004_retail_analytics.txt
│   ├── deal_005_manufacturing_erp.txt
│   ├── deal_006_education_lms.txt
│   ├── deal_007_telecom_network.txt
│   ├── deal_008_logistics_platform.txt
│   ├── deal_009_energy_system.txt
│   └── deal_010_consulting_crm.txt
├── data/                      # Historical data
│   └── historical_deals.json  # JSON fallback storage
├── reports/                   # Generated PDF reports (created automatically)
├── .cache/                    # Cache files (created automatically)
├── app.py                     # Main orchestrator
├── main.py                    # CLI entry point
├── requirements.txt           # Python dependencies
├── env.example               # Environment variables template
├── .gitignore                # Git ignore rules
└── README.md                 # This file
```

## 🔧 Configuration

### LLM Provider

The system supports two LLM providers:

1. **Google Gemini** (Recommended, Free Tier Available)
   - Models: `gemini-1.5-flash`, `gemini-1.5-pro`, `gemini-pro`
   - Set `LLM_PROVIDER=google` and provide `GOOGLE_API_KEY`
   - Get API key from: https://aistudio.google.com/app/apikey

2. **OpenAI** (Default, Alternative)
   - Models: `gpt-4`, `gpt-3.5-turbo`
   - Default provider (if `LLM_PROVIDER` not set)
   - Set `LLM_PROVIDER=openai` and provide `OPENAI_API_KEY`
   - Get API key from: https://platform.openai.com/api-keys

### MongoDB Setup (Optional)

MongoDB is optional but recommended for production:

**macOS:**
```bash
brew install mongodb-community
brew services start mongodb-community
```

**Docker:**
```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

**Linux:**
```bash
sudo apt-get install mongodb
sudo systemctl start mongodb
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

## 🎨 Dashboard Features

### Deal Summary Card
- **Seller/Owner**: Account manager or sales rep
- **Buyer/Deal Name**: Customer or deal identifier
- **Deal Value**: Monetary value with currency formatting
- **Industry**: Business sector (Technology, Healthcare, Financial, etc.)
- **Outcome**: Closed Lost/Won status
- **Key Issue**: Primary failure point highlight

### Win Probability Score
- Calculated from Final Deal Health Score (0-100%)
- Visual progress bar with color coding
- Risk level indicators:
  - **Very Low** (<30%): Deal was at high risk
  - **Low** (30-50%): Multiple issues identified
  - **Medium** (50-70%): Some concerns present
  - **High** (>70%): Deal had good potential

### Loss Driver Analysis
- Horizontal bar chart showing risk scores by category
- Categories: Pricing Issues, Communication, Documentation, Competitive Risk, Delivery/Execution
- Color gradient from low (green) to high (red) risk
- Identifies primary failure drivers

### Timeline Visualization
- Interactive timeline chart with phase grouping
- Color-coded by sentiment:
  - 🟢 **Green**: Positive events
  - ⚪ **Gray**: Neutral events
  - 🔴 **Red**: Negative events
- Date range display with proper formatting
- Timeline score indicator
- Sentiment distribution (positive/neutral/negative percentages)

### Comparative Analytics
- **Similarity Bar Chart**: Shows similarity percentages with historical deals
- **Risk Distribution Pie Chart**: Visual breakdown of risk factors
- **Common Patterns**: List of recurring issues across similar deals
- **Shared Risk Factors**: Identified risks common to multiple deals
- **Benchmark Scores**: Average metrics from similar historical deals
- **Comparative Metrics Table**: Side-by-side comparison

### Playbook Sections
- **What Went Wrong** (❌): Root cause analysis with detailed explanations
- **Red Flags** (⚠️): Warning signs that should have been caught earlier
- **Recommendations** (✔️): Actionable steps with:
  - Priority levels (High/Med/Low)
  - Impact scores (1-10)
  - Assigned owners
- **Best Practices** (⭐): Long-term improvements for the organization

### Business Intelligence Metrics
- All 6 metrics displayed in organized columns
- Scores out of 10 with status indicators
- Color-coded based on score ranges

## 🔍 Usage

### Web Dashboard (Recommended)

1. **Start the dashboard:**
   ```bash
   streamlit run ui/dashboard.py
   ```

2. **Upload a document:**
   - Supported formats: PDF, DOCX, DOC, TXT
   - Maximum size: 100 MB
   - Must contain financial/deal-related content

3. **Analyze:**
   - Click "Analyze Deal"
   - Wait for multi-agent analysis (30-60 seconds)
   - View results in dashboard
   - Download PDF report

### Command Line Interface

```bash
# Analyze a document via CLI
python main.py path/to/deal_document.pdf
```

The CLI will display:
- Timeline events summary
- Business intelligence scores
- Key issues identified
- Report location

### Python API

```python
from app import DealForensicsOrchestrator

# Initialize orchestrator
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
metadata = result["metadata"]
```

## 📄 PDF Report Contents

The system generates enterprise-grade PDF reports with:

1. **Title Page**: Deal Forensics AI Report, date, version
2. **Executive Summary**: 5-7 sentence overview of key findings
3. **Deal Overview Table**: Seller, Buyer, Value, Industry, Outcome, Key Failure Point
4. **Timeline Analysis**: Full timeline with dates, sentiment, timeline score
5. **What Went Wrong**: 6-10 root causes with detailed explanations
6. **Red Flags**: 6-10 warning signs that should have been caught
7. **Recommendations**: 8-12 actionable steps with priority, impact, and owner
8. **Best Practices**: 6-10 long-term improvements for the organization
9. **Comparative Analytics**: Similar deals, patterns, risk factors, benchmarks
10. **Business Intelligence Metrics**: All 6 scores with status indicators
11. **Final Summary**: Conclusion and key lessons learned

## 🧪 Testing

### Test with Sample Documents

The system includes 10 realistic synthetic deal documents in the `/deals/` folder:
- `deal_001_enterprise_saas.txt` - Enterprise SaaS Platform
- `deal_002_healthcare_integration.txt` - Healthcare System Integration
- `deal_003_financial_crm.txt` - Financial Services CRM
- `deal_004_retail_analytics.txt` - Retail Analytics Platform
- `deal_005_manufacturing_erp.txt` - Manufacturing ERP
- `deal_006_education_lms.txt` - Education Learning Management
- `deal_007_telecom_network.txt` - Telecom Network Management
- `deal_008_logistics_platform.txt` - Logistics Management
- `deal_009_energy_system.txt` - Energy Management System
- `deal_010_consulting_crm.txt` - Consulting Firm CRM

Each includes: full timeline, pricing discussions, competitor involvement, escalation events, delivery delays, final outcomes.

### Validation Testing

The system includes comprehensive document validation:
- File type checking
- Size validation
- Content relevance detection
- Business keyword verification
- Structured text validation
- LLM-based relevance checking

## 📈 Performance

- **Processing Time**: ~10-30 seconds per document (depends on document size and LLM response time)
- **Vector Search**: <100ms (FAISS in-memory)
- **PDF Generation**: ~2-5 seconds
- **MongoDB Insert**: <50ms (if MongoDB is used)

## 🛠️ Troubleshooting

### Common Issues

1. **"Document Validation Failed"**
   - Ensure document contains financial/deal-related content
   - Check file size (must be 100 bytes - 100 MB)
   - Verify file type (PDF, DOCX, DOC, or TXT)
   - Add more financial keywords to your document

2. **"LLM API Error"**
   - Verify API key is set correctly in `.env`
   - Check API quota/rate limits
   - Ensure internet connection
   - For Google Gemini: Check quota at https://ai.dev/usage
   - Try switching LLM providers

3. **"MongoDB Connection Failed"**
   - System automatically falls back to JSON storage
   - Check MongoDB is running: `mongosh --eval "db.adminCommand('ping')"`
   - Verify `MONGODB_URI` in `.env`
   - MongoDB is optional - JSON fallback works fine

4. **"No timeline events extracted"**
   - Document may lack chronological information
   - System will generate inferred timeline
   - Check document contains dates or time references
   - Add more date mentions in your document

5. **"ModuleNotFoundError"**
   - Ensure virtual environment is activated
   - Reinstall dependencies: `pip install -r requirements.txt`
   - Check Python version (3.11+ recommended)

6. **"Streamlit not found"**
   - Install Streamlit: `pip install streamlit`
   - Or reinstall all dependencies: `pip install -r requirements.txt`

### Debug Mode

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔐 Security

- **API Keys**: Stored in `.env` file (never commit to version control)
- **Document Validation**: Prevents malicious file uploads
- **Text Sanitization**: All text sanitized for PDF generation
- **No Sensitive Data**: No sensitive data logged or stored
- **File Size Limits**: Maximum 100 MB to prevent DoS attacks

## 🛠️ Tech Stack

- **Python**: 3.11+ (recommended)
- **LLM**: Google Gemini (free-tier models: gemini-1.5-flash, gemini-1.5-pro, gemini-pro) or OpenAI
- **Agents**: LangGraph for orchestration
- **RAG**: HuggingFace embeddings + FAISS vector store
- **UI**: Streamlit + Plotly for visualizations
- **PDF**: FPDF2 for report generation
- **Persistence**: MongoDB (optional) or JSON
- **Document Processing**: PyPDF, python-docx, unstructured

## 📝 Development

### Adding New Agents

1. Extend `agents/base.py`:
   ```python
   from agents.base import BaseAgent
   
   class MyAgent(BaseAgent):
       def analyze(self, context: str) -> dict:
           # Your analysis logic
           return result
   ```

2. Add to `agents/graph.py`:
   ```python
   graph.add_node("my_agent", self._my_agent_node)
   ```

### Customizing Scoring

Edit `core/scoring.py` to adjust:
- Keyword lists
- Scoring weights
- Metric calculations

### Adding Historical Deals

Add new deal files to `/deals/` folder or update `data/historical_deals.json`

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues or questions, please open an issue on GitHub: https://github.com/MBGIRISH/DealForensics/issues

## 🎯 Roadmap

- [ ] Real-time collaboration features
- [ ] Advanced analytics dashboard
- [ ] Integration with CRM systems (Salesforce, HubSpot)
- [ ] Custom report templates
- [ ] Multi-language support
- [ ] API rate limiting
- [ ] User authentication
- [ ] Batch processing for multiple documents
- [ ] Email report delivery

## 🙏 Acknowledgments

- **LangChain/LangGraph** for multi-agent orchestration
- **HuggingFace** for embeddings and transformers
- **FAISS** for efficient vector search
- **Streamlit** for beautiful UI framework
- **Google Gemini / OpenAI** for LLM capabilities
- **FPDF2** for PDF generation

## 📚 Additional Resources

- **Google Gemini API**: https://ai.google.dev/
- **OpenAI API**: https://platform.openai.com/
- **LangChain Documentation**: https://python.langchain.com/
- **Streamlit Documentation**: https://docs.streamlit.io/

---

**Built with ❤️ for sales teams who want to learn from every lost deal**

---

**Author**: M B GIRISH  
**Email**: mbgirish2004@gmail.com  
**Version**: 1.0.0  
**Date**: December 2025
