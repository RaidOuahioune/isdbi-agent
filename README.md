# ISDBI Agent

The ISDBI Agent is an intelligent system designed to enhance, analyze, and provide insights into Islamic finance standards and documents, leveraging vector database technology and RAG (Retrieval Augmented Generation).

## Features

- Standards enhancement recommendations
- Compliance verification for financial documents
- Product design guidance for Islamic financial instruments
- Interactive querying of Islamic finance knowledge base
- Vector database for efficient retrieval of financial standards

## Installation and Setup

There are two ways to set up and run this project:

### Option 1: Using Virtual Environment (venv)

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd isdbi-agent
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the root directory with the following:
   ```
   GEMINI_API_KEY=your-gemini-api-key
   ISLAMIC_FINANCE_API_URL=url-to-fastapi-server
   ```
   Note: The `ISLAMIC_FINANCE_API_URL` should point to the FastAPI server that connects to and performs RAG operations on the vector graph database(NEO4J).

5. **Run the application**:
   ```bash
   streamlit run ui/app.py
   ```

### Option 2: Using Docker

1. **Pull the Docker image**:
   ```bash
   docker pull ellzo/isdbi-agent
   ```


3. **Access the application**:
   Open your browser and navigate to `http://localhost:8501`

## Neo4j Graph Database Creation

The repository includes a Jupyter notebook (`createNeoDB.ipynb`) that demonstrates how to create the Neo4j graph database of Islamic financial books. The data source for this notebook is available at [this Google Drive link](https://drive.google.com/drive/folders/1THMlqIs1_jC6KE8sIZxLvOMrnajI1PJC?usp=drive_link).

To use the notebook:
1. Ensure you have Jupyter installed
2. Open the notebook: `jupyter notebook createNeoDB.ipynb`
3. Follow the instructions within the notebook to create the graph database

## Project Structure

- `/agents.py`: Core agent functionality
- `/enhancement.py`: Standards enhancement logic
- `/retreiver.py`: Vector database retrieval functions
- `/server.py`: FastAPI server implementation
- `/ui/`: Streamlit user interface
- `/components/`: Modular components
- `/documentation/`: Project documentation 
- `/notebooks/`: Jupyter notebooks including embedding and graph creation
- `/vector_db_storage/`: Storage for vector embeddings

## Use Cases

1. **Standards Enhancement**: Analyze and propose improvements to AAOIFI standards
2. **Compliance Verification**: Check financial documents for compliance with Islamic finance principles
3. **Product Design**: Design Shariah-compliant financial products
4. **Financial Standards Journaling**: Process and generate journal entries based on Islamic finance standards

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Include appropriate license information]
