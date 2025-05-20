# GeoStatAI

A Python-based statistical assistant that uses GPT-4, Ollama models, and MCP (Model Context Protocol) to analyze and provide insights on Georgian statistical data. The application processes data scraped from [საქსტატი (Geostat)](https://www.geostat.ge/ka), Georgia's National Statistics Office, and uses advanced AI to provide meaningful analysis and insights from the statistical data.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Ollama (for local LLM support)

## Installation

### 1. Installing Python Dependencies

Install the required dependencies:
```bash
pip install -r requirements.txt
```

The `requirements.txt` file contains all necessary Python packages for the project.

### 2. Installing and Setting Up Ollama

Ollama is an open-source tool that lets you run large language models locally. This project uses Ollama to provide LLM capabilities without relying solely on cloud-based APIs.

#### For Windows:
1. Download the Ollama installer from [ollama.com](https://ollama.com/download)
2. Run the installer and follow the on-screen instructions
3. After installation, Ollama will run as a service in the background

#### For macOS:
1. Download Ollama from [ollama.com](https://ollama.com/download)
2. Open the downloaded file and drag Ollama to your Applications folder
3. Launch Ollama from your Applications folder
4. Ollama will appear in your menu bar when running

#### For Linux:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

After installation, Ollama should be running as a service at `http://localhost:11434`.

### 3. Installing Recommended LLM Models

Once Ollama is installed, you need to download the language models used by this application. Open a terminal or command prompt and run the following commands:

```bash
# Install llama3:8b (~4.7 GB) - Best reasoning, supports Georgian with translation
ollama pull llama3:8b

# Install mistral (~4.1 GB) - Lighter, often good with multilingual input
ollama pull mistral

# Install llama2:7b (~3.8 GB) - Older, but still usable
ollama pull llama2:7b
```

> **Note:** Model downloads may take some time depending on your internet connection. Each model requires significant disk space as indicated.

## Configuration

1. Create a `.env` file in the root directory of the project
2. Add your OpenAI API key to the `.env` file (optional if you're only using Ollama models):
```
OPENAI_API_KEY=your_api_key_here
```

## Running the Application

To start the application, run:
```bash
python app.py
```

The application will:
1. Load the data from `data/scraped_data_mcp1.json`
2. Present you with a prompt where you can enter your questions
3. Use the configured LLM (Ollama or GPT-4) to analyze the data and provide insights
4. Display the results including:
   - A title
   - Raw data statistics
   - Analysis of the data

To exit the application, type "exit", "quit", or "გასვლა" (in Georgian).

## Using Different Ollama Models

The application is configured to use the `llama3:8b` model by default. To use a different model, you can modify the model parameter in the `call_ollama` function call or set it as an environment variable.

```python
# Example of using a different model
    response = call_ollama(prompt, model="mistral")
```

## Troubleshooting Ollama

If you encounter issues with Ollama:

1. **Check if Ollama is running:**
   ```bash
   curl http://localhost:11434
   ```
   You should receive a response if the service is active.

2. **Restart the Ollama service:**
   - Windows: Restart the Ollama service from Services Manager
   - macOS: Quit and restart the Ollama application
   - Linux: `sudo systemctl restart ollama`

3. **Verify model installation:**
   ```bash
   ollama list
   ```
   This shows all installed models.

## Project Structure

- `app.py`: Main application file
- `domain.py`: Domain-specific logic
- `llm/`: LLM-related functionality
- `mcp/`: Model Context Protocol implementation for managing data context and analysis flow
- `data/`: Contains the data files
- `.env`: Environment variables (API keys)
- `requirements.txt`: List of Python package dependencies

## Notes

- Always ensure you have the latest dependencies installed by running `pip install -r requirements.txt` after pulling new changes
- For optimal performance with Georgian language content, use the `llama3:8b` model which has better support for Georgian with translation capabilities