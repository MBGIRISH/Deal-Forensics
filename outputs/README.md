# Output Screenshots

This directory contains screenshots of the Deal Forensics AI system outputs, showcasing the interactive dashboard and various analytical visualizations.

## Screenshot Files

The following screenshots are included in this directory:

### 1. upload_interface.png
**Description:** Document upload interface showing the file upload area, validation requirements, and accepted file types.

**Features shown:**
- Drag-and-drop file upload area
- File type specifications (PDF, DOCX, DOC, TXT)
- File size limits (100 MB maximum)
- Upload requirements checklist
- Accepted and rejected document types
- Dark mode interface

### 2. deal_summary.png
**Description:** Comprehensive deal overview dashboard showing key metrics, win probability, and loss driver analysis.

**Features shown:**
- Deal metadata (seller, buyer, value, industry, outcome)
- Win Probability Score with visual progress bar
- Loss Driver Analysis horizontal bar chart
- Risk scores by category:
  - Competitive Risk
  - Documentation
  - Pricing Issues
  - Delivery/Execution
  - Communication
- Key issue identification banner
- Color-coded risk indicators

### 3. comparative_analytics.png
**Description:** Historical deal comparison visualization featuring similarity scores and risk distribution analysis.

**Features shown:**
- Similarity percentage bar chart comparing against historical deals
- Risk distribution pie chart showing top risk factors
- Benchmark metrics comparison
- Pattern identification across similar deals
- Risk factor breakdown with percentages
- Deal comparison statistics

### 4. playbook_sections.png
**Description:** Additional dashboard view showing playbook sections or other analytical components.

**Note:** This screenshot may show additional dashboard views such as playbook sections, business intelligence metrics, or other analytical components.

## Usage in Documentation

These screenshots are referenced in the main project README.md file under the "Outputs" section. They provide visual documentation of the system's capabilities and user interface.

## Technical Details

- **Format:** PNG
- **Typical size:** 1200-1920px width
- **Color mode:** RGB
- **File naming convention:** lowercase with underscores (e.g., `upload_interface.png`)

## Updating Screenshots

To update screenshots:

1. Run the Streamlit dashboard: `streamlit run ui/dashboard.py`
2. Navigate through different dashboard sections
3. Capture screenshots using:
   - **macOS:** `Cmd + Shift + 4` (select area) or `Cmd + Shift + 3` (full screen)
   - **Windows:** `Win + Shift + S` (Snipping Tool)
   - **Linux:** Use screenshot tool or `gnome-screenshot`
4. Save screenshots with the standard naming convention
5. Replace existing files in this directory
6. Update this README if screenshots change significantly

## Screenshot Guidelines

- **Quality:** Use high resolution for clear display in documentation
- **Format:** PNG preferred for screenshots with text
- **Size:** Keep file sizes reasonable (under 2MB when possible)
- **Naming:** Use descriptive, lowercase names with underscores
- **Content:** Ensure screenshots show relevant, clear information
- **Privacy:** Remove or blur any sensitive information before committing

## File Structure

```
outputs/
├── README.md                     # This file
├── upload_interface.png          # Upload interface screenshot
├── deal_summary.png              # Deal summary dashboard screenshot
├── comparative_analytics.png     # Comparative analytics screenshot
└── playbook_sections.png         # Playbook sections and additional views
```

## Notes

- Screenshots are automatically displayed in the main README.md when referenced
- Ensure all referenced screenshots exist in this directory
- Keep screenshots up-to-date with the latest UI changes
- Consider updating screenshots when major features are added or UI is redesigned
