# Jira Bug Analyzer

This project is designed to fetch and analyze bug data from Jira using a list of bug URLs. It provides a simple interface to interact with the Jira API and perform data analysis on the retrieved bug information.

## Project Structure

```
jira-bug-analyzer
├── main.py          # Main script to fetch and analyze bugs from Jira
├── requirements.txt  # List of dependencies
└── README.md        # Project documentation
```

## Installation

To set up the environment for this project, follow these steps:

1. Clone the repository:
   ```
   git clone <repository-url>
   cd jira-bug-analyzer
   ```

2. It is recommended to create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration

Create a `.env` file in the project root with your Jira credentials:

```
JIRA_EMAIL=you@example.com
JIRA_TOKEN=your_api_token
JIRA_DOMAIN=https://softwareone.atlassian.net
```

## Usage

Fetch bug data from Jira using an issue list file (one issue key per line):

```
python main.py --issue-file issue_keys.txt --output-dir bugs_md
```

Analyze a directory of bug markdown files and write a report:

```
python ana.py --bugs-dir bugs_md --output-file analyzer.md
```

## Contributing

If you would like to contribute to this project, please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.