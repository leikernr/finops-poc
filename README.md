# Live Cloud Cost Anomaly Detection

I built this project to solve a problem i am seeing in my cloud class: computing bills that these guys didnt see coming. These guys spin up VPC, instances, etc. and keep clicking not wanting to wait or using the cli and doubling the messages. So i started thinking about it and applied that logic to me learning, Kafka + Flink + Grafana.

Many companies rent servers and databases from providers like Amazon or Azure. Sometimes, a software bug causes those servers to work too hard, which can cost the company thousands of dollars in a matter of hours. This project is a working prototype that catches those expensive mistakes the moment they happen.

## How It Works
Sorry if its wrong just taking my research and dropping it here if im wrong please let me know.

The system operates in a few steps:

1. Data Generation: A Python script acts like a fleet of servers, constantly reporting how much computing power they are using. Every 30 seconds, it fakes a massive usage spike.
2. The Nervous System: The data is sent to a message broker called Redpanda. You can think of this as a high speed conveyor belt for data.
3. Real Time Analysis: A streaming engine called Apache Flink watches the conveyor belt. It groups the data into ten second windows, calculates the financial cost, and flags any sudden spikes.
4. Storage and Display: The final calculations are saved into a PostgreSQL database. A visualization tool called Grafana then reads that database to display a live dashboard of our costs and alerts.

## Instructions to Run the Project

You will need Docker and Conda.

- **Docker** -- Docker Desktop on Mac and Windows, Docker Engine plus the
  Compose v2 plugin on Linux.
- **Conda** -- on macOS, miniforge is the easiest route. It defaults to the
  conda-forge channel, which avoids Anaconda's commercial terms:

  ```bash
  brew install --cask miniforge
  conda init zsh        # then restart your terminal
  ```

  **The `conda init` step is required.** Steps 3 and 4 below run
  `conda activate`, which fails with `CondaError: Run 'conda init' before
  'conda activate'` until your shell has been configured. Step 2 will still
  appear to succeed without it, so it is easy to miss.

You do **not** need to install Java, and you do not need a particular version
of Python on your machine -- `setup.sh` installs Python 3.10 and Java 11 inside
the environment it creates, leaving whatever you already have untouched.

Step 1: Start the Databases
Open your terminal in the project folder and start the database containers:
```bash
docker compose up -d
```

Step 2: Set Up the Environment
Run the setup script to install the necessary Python packages:
```bash
chmod +x setup.sh
./setup.sh
```

Step 3: Start the Data Generator
In a new terminal window, activate the environment and start the simulator:
```bash
conda activate finops-env
python data_generator.py
```

Step 4: Start the Anomaly Detector
In a second terminal window, activate the environment and start the streaming engine:
```bash
conda activate finops-env
python anomaly_detector.py
```

Step 5: View the Dashboard
Open Grafana to view the live dashboard. You can import the grafana_dashboard.json file included in this folder to see the exact layout I designed.

more coming soon!
