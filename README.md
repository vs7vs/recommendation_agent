# Conversational Movie Recommender Agent

A conversational agent built with Streamlit and LangChain that provides personalized movie recommendations using OpenAI's powerful language models.

This project moves beyond traditional recommendation systems by creating an interactive, chat-based experience. Users can converse with the agent, specify their preferences in natural language, and receive movie suggestions in a dynamic and engaging way.


<!-- ---

## 🎬 Demo

![Project Demo GIF](https://user-images.githubusercontent.com/username/repo/your_demo.gif)

*A brief walkthrough of the Recommender Agent in action.*

--- -->

## 🚀 Key Features

* **Conversational Interface:** Chat with the agent in natural language to get movie recommendations.
* **LLM-Powered Intelligence:** Leverages OpenAI's GPT models via LangChain to understand context and user preferences.
* **Stateful Memory:** Remembers previous parts of the conversation to provide more relevant suggestions over time.
* **Simple Web UI:** A clean and user-friendly interface built with the Streamlit framework.

---

## 🛠️ Technologies Used

* **Language:** Python 3
* **Web Framework:** Streamlit
* **LLM Orchestration:** LangChain
* **AI Model:** OpenAI
* **Dependency Management:** Poetry

---

## ⚙️ Getting Started

Follow these instructions to get the recommender agent running on your local machine.

### Prerequisites

* Python 3.9+
* An OpenAI API Key.

### Installation

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
    Create a file named `.env` in the root directory of the project. Add your OpenAI API key to this file:
    ```
    # .env
    OPENAI_API_KEY="sk-YourSecretOpenAI_ApiKey"
    ```

---

## Usage

Once the installation is complete, you can run the Streamlit application.

1.  **Activate the virtual environment managed by Poetry:**
    ```sh
    poetry shell
    ```

2.  **Run the Streamlit app:**
    ```sh
    streamlit run main.py
    ```

3.  Open your web browser and navigate to `http://localhost:8501`. You can now start chatting with the recommender agent!

---

## 📄 License

This project is distributed under the MIT License. See the `LICENSE` file for more information.