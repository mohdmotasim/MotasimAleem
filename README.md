# NSE Dark Horse Scanner

A comprehensive stock analysis dashboard for Indian equity markets with portfolio tracking, dark horse scoring, and mutual fund analysis.

## Features

- **Dark Horse Scanner**: Identify undervalued stocks with strong fundamentals using a proprietary scoring algorithm
- **Portfolio Health**: Analyze your portfolio's overall health and diversification
- **Current Holdings**: Track your stock positions with multi-portfolio support
- **Exit Tracker**: Get sell signals and exit recommendations for your holdings
- **Mutual Fund Tracker**: Research and track mutual fund investments
- **Stock Research**: Detailed analysis of individual stocks with news sentiment

## Running Locally

### Prerequisites

- Python 3.10 - 3.13 (Python 3.14+ may not have pre-built wheels for all packages)
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd Bis
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the app:
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Cloud Deployment

This app is deployed on Streamlit Community Cloud for private access.

### Important: Data Persistence

**⚠️ Cloud Deployment Notice:** Portfolio data is NOT automatically saved on Streamlit Community Cloud. Local file storage is not persistent between sessions.

**To save your portfolio data:**
1. Use the 💾 **Save** button in the Portfolio Health or Current Holdings tabs
2. Download the portfolio JSON file to your local computer
3. When you return, use the 📥 **Load** button to restore your data

**Recommended workflow:**
- Export your portfolio after making changes
- Keep the exported JSON file as backup
- Import the file at the start of each session

### Deployment Instructions

1. **Push code to GitHub**
   - Ensure your code is pushed to a GitHub repository
   - The repository should contain: `app.py`, `requirements.txt`, and `.streamlit/` folder

2. **Deploy to Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Connect your GitHub account
   - Select your repository
   - Set the main file path to `app.py`
   - Click "Deploy"

3. **Configure Private Access**
   - In your Streamlit Cloud dashboard
   - Go to your app settings
   - Click "Sharing"
   - Change visibility to "Private"
   - Add your brother's email address to the allowed users list
   - Click "Save"

4. **No Secrets Required**
   - This app uses only public APIs (yfinance, mfapi.in, nsepython)
   - No API keys or secrets need to be configured

### Managing Access

To add or remove users who can access your app:
1. Go to your app's settings on Streamlit Cloud
2. Click "Sharing"
3. Add or remove email addresses from the allowed users list
4. Changes take effect immediately

## Multi-Portfolio Support

The app supports multiple portfolios for different users or investment strategies:

- Create separate portfolios for different family members
- Each portfolio maintains independent holdings and data
- Switch between portfolios using the dropdown selector
- Export/import portfolio data for backup

## CSV Import from Kite

You can import your holdings from Kite account CSV exports:

1. Download holdings CSV from your Kite account
2. Go to "Current Holdings" tab
3. Expand "Import from Kite CSV"
4. Upload the CSV file
5. Choose import mode:
   - **Replace All**: Clear existing holdings and import from CSV
   - **Smart Update**: Update existing holdings, add new ones
   - **Append Only**: Add to existing holdings without updating

## Dependencies

- streamlit==1.36.0
- yfinance==0.2.38
- nsepython>=2.0
- pandas>=2.0.0
- plotly>=5.0.0
- feedparser>=6.0.0
- requests>=2.31.0

## Troubleshooting

**App not loading on cloud:**
- Check the deployment logs on Streamlit Cloud
- Ensure all dependencies are in requirements.txt
- Verify Python version compatibility (3.10-3.13)

**Data not persisting:**
- Remember to export your portfolio using the 💾 Save button
- Import your data at the start of each session using 📥 Load
- This is a limitation of Streamlit Community Cloud's free tier

**Scanner not working:**
- yfinance may be rate-limited, wait 30 seconds and try again
- Some stocks may not have complete data available

## License

This is a personal project for investment research and analysis.
