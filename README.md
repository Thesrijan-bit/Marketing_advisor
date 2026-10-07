# Marketing_advisor

# Marketing Advisor

An AI agent that analyzes current trends across different niches and gives you data-backed insights on **what videos to create next**.

## Overview

Creating content that performs well starts with knowing what's trending. Marketing Advisor automates that research: it looks at trend data for a niche you choose, identifies what's gaining traction, and turns it into actionable video ideas.

## Features

- **Niche trend analysis**: track what's rising in niches like fitness, tech, finance, food, and more
- **Video idea generation**: get suggested topics, titles, and angles based on current trends
- **Insight summaries**: understand *why* a topic is trending and who it appeals to
- **Multi-niche support**: switch between niches or compare them side by side

## How It Works

1. **Input**: you choose a niche (e.g. "personal finance").
2. **Collect**: the agent gathers trend data from your configured sources.
3. **Analyze**: an LLM identifies patterns, rising topics, and content gaps.
4. **Output**: you receive a report with trend insights and recommended video ideas.

## Getting Started

### Prerequisites

- Python 3.10+
- An API key for your LLM provider
- API keys for any trend data sources you use

### Installation

```bash
git clone https://github.com/Thesrijan-bit/Marketing_advisor.git
cd Marketing_advisor
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```
LLM_API_KEY=your_api_key_here
TREND_API_KEY=your_trend_source_key_here
```

### Usage

```bash
python main.py --niche "personal finance"
```

## Example Output

```
Niche: Personal Finance

Top Trends:
1. Budgeting with the envelope method (rising)
2. Side hustles for students (steady)

Suggested Videos:
- "I Tried the Envelope Method for 30 Days"
- "5 Side Hustles You Can Start This Weekend"
```

## Roadmap

- [ ] Add more trend data sources
- [ ] Generate full video scripts and hooks
- [ ] Build a simple web dashboard
- [ ] Schedule automatic weekly reports

## Contributing

Contributions are welcome! Open an issue to discuss a change, or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
