# Network Monitoring Dashboard

A security network monitoring dashboard that displays real-time predictions from a deep learning model.
This dashboard demonstrates the functionality of an intrusion detection model by showing live network traffic simulations and highlighting potential attacks.

## Features

- Real-time attack detection using a trained DL model
- Summary statistics: total events, attacks, normal traffic, most targeted ports
- Interactive table displaying the latest network traffic events
- Visualization of port-specific attack counts

## Project Structure
```
network-monitoring-dashboard/
|
├── backend/
│ ├── app.py # FastAPI backend server
│ ├── my_model.keras # Trained DL model
| ├── icons/ # Icons for the frontend
│ └── live_simulation.csv # Sample live network data
│
├── frontend/
│ ├── index.html # Frontend dashboard page
│
├── requirements.txt # Python dependencies
└── README.md # Project documentation
```

## Installation

#### 1. Make sure Git LFS is installed (required for the large `live_simulation.csv` file):
```
        git lfs install
```
#### 2. Clone the repository:
```
        git clone https://github.com/eman-sameh/network-monitoring-dashboard.git  
        cd network-monitoring-dashboard
```
#### 3. Pull the large files managed by Git LFS:
```
        git lfs pull
```
#### 4. (Optional) Create a virtual environment:
```
        python -m venv venv  
        venv\Scripts\activate    # On Windows
```
#### 5. Install the required packages:
```
        pip install -r requirements.txt
```
## Usage

#### 1. Run the backend server:

   uvicorn backend.app:app --reload

#### 2. Open `index.html` in your browser to view the dashboard.

#### 3. The dashboard will show real-time predictions from the DL model based on `live_simulation.csv`.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Author

Eman Sameh Ali El-Ghareeb
