# Personal Assistant Application

## Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Dmoore628/PersonalAssistant.git
   cd PersonalAssistant
   ```

2. **Install Dependencies**:
   Ensure you have Python 3.11+ installed. Then, run:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables**:
   Create a `.env` file in the root directory and configure the necessary environment variables.

4. **Run Docker Services**:
   Start the services using Docker Compose:
   ```bash
   docker-compose up --build
   ```

5. **Start the Application**:
   Run the main services manually if needed:
   ```bash
   python services/voice_processing/main.py
   python services/cua/main.py
   ```

## Usage Instructions

- **Voice Commands**: Activate the assistant using the wake word.
- **HUD Overlay**: Displays real-time task status.
- **External Services**: Open Microsoft Office files, web browsers, and PDFs.
- **Knowledge Graph**: Query and update the knowledge graph in real-time.

## Contribution

Refer to the `CONTRIBUTING.md` file for guidelines on contributing to this project.