📊 Stock Analyzer App

A simple and interactive web application built with **Streamlit** to analyze historical stock data using Yahoo Finance.


🚀 Features

- 🔍 Search for any stock using its ticker symbol (e.g., `AAPL`, `TSLA`, `GOOGL`)
- 📅 View historical stock data for the past all years
- 📈 Visualize closing price trends using line charts
- 📉 Optional display of raw tabular data
- ✅ Fully deployed and accessible via Streamlit Cloud



🛠️ Technologies Used

- [Streamlit](https://streamlit.io/) – for building the web UI
- [yfinance](https://pypi.org/project/yfinance/) – to fetch stock market data
- [pandas](https://pandas.pydata.org/) – for data manipulation
- [matplotlib](https://matplotlib.org/) – for chart visualization (optional)



📦 Installation 

Clone the repository
git clone https://github.com/codiantdivyanshu/Stock_analyzer.git
cd Stock_analyzer

 Create a virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

Install dependencies
pip install -r requirements.txt

 Run the Streamlit app
streamlit run stock_app.py


🧠 How It Works
User inputs a stock ticker symbol (e.g., TSLA)

App fetches 1 year of historical stock data from Yahoo Finance

Data is displayed in a table and visualized using line charts

Checkbox allows toggling the raw data table view

📁 Project Structure
Stock_analyzer
│
├── .devcontainer/
│   ├── devcontainer.json         
│   └── Dockerfile                
│
├── .gitignore               
├── LICENSE                      
├── README.md                    
├── requirements.txt            
├── runtime.txt                 
└── streamlit_app.py              #
     

🧑‍💻 Author
Divyanshu Gupta
@codiantdivyanshu


