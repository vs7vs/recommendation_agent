# Conversational Fut-Edu Agent

A conversational agent that uses LangGraph and external tools to provide intelligent, context-aware responses and perform tasks.

This project uses a sophisticated graph-based architecture to create a stateful agent capable of complex interactions. It can use tools like web search and website scraping to gather information, reason about it, and even pause to ask the user for clarification before completing its tasks.

---

## 🎬 Demo

A screenshot of the agent running in the terminal is a great way to showcase the project.

![Screenshot of the agent interacting in the terminal](path/to/your/screenshot.png)

*A brief walkthrough of the agent in action within the terminal.*

---

## 🚀 Key Features

* **Graph-Based Logic:** Built with LangGraph for robust, stateful, and cyclical reasoning.
* **Tool Usage:** Can use external tools like web search and website scraping to answer questions and complete tasks.
* **Interactive Terminal UI:** A clean and readable command-line interface powered by the Rich library.
* **Human-in-the-Loop:** The agent can pause and ask for clarifying input from the user before continuing its task.
* **LLM-Powered Intelligence:** Leverages OpenAI's GPT models to understand context, make decisions, and generate responses.

---

## 🛠️ Technologies Used

* **Language:** Python 3
* **LLM Orchestration:** LangChain & LangGraph
* **Terminal UI:** Rich
* **AI Model:** OpenAI (GPT-4o)

---

## ⚙️ Getting Started

Follow these instructions to get the agent running on your local machine.

### ### Prerequisites

* Python 3.9+
* An OpenAI API Key
* A Tavily API Key (for the web search tool)

### ### Installation

1.  **Clone the repository:**
    ```sh
    git clone [https://github.com/vs7vs/recommender_agent.git](https://github.com/vs7vs/recommender_agent.git)
    cd recommender_agent
    ```

2.  **Install dependencies:**
    This project uses Poetry for dependency management. If you don't have it, you can install it [here](https://python-poetry.org/docs/#installation).
    ```sh
    poetry install
    ```

3.  **Set up your environment variables:**
    Create a file named `.env` in the root directory and add your API keys:
    ```
    # .env file
    OPENAI_API_KEY="sk-YourSecretOpenAI_ApiKey"
    TAVILY_API_KEY="tvly-YourSecretTavily_ApiKey"
    ```

---

## ## Usage

Once the installation is complete, you can run the application from your terminal.

1.  **Activate the virtual environment managed by Poetry:**
    ```sh
    poetry shell
    ```

2.  **Run the application:**
    ```sh
    python main.py
    ```

3.  The agent will start in your terminal. Follow the on-screen prompts to begin the conversation.

---

## 📄 License

This project is distributed under the MIT License. See the `LICENSE` file for more information.