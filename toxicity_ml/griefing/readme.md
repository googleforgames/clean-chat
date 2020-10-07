### Anomaly Detection Model (Griefing)

A griefer or bad faith player is a player in a multiplayer video game who deliberately irritates and harasses other players within the game (trolling), using aspects of the game in unintended ways. A griefer derives pleasure primarily or exclusively from the act of annoying other users, and as such is a particular nuisance in online gaming communities. To qualify as griefing, a player must be using aspects of the game in unintended ways to annoy other players—if they are trying to gain a strategic advantage, it is instead called "cheating". **Source:** [Wikipedia](https://en.wikipedia.org/wiki/Griefer)

#### **Assets**

**anomaly_detection_model.py**
Work in progress - Model training code used to detect anomalies within game event log data. 
```
USAGE: anomaly_detection_model.py --training_data './data/game_event_logs.csv' --epochs 10 --batch_size 10 --validation_split 0.05 --model_threshold 0.275 --model_filepath ./models/
```


**game_event_log_simulator.py**
Helper script used to simulate game event logs, which is used for model training and testing. Additional methods for capturing training data include working directly with game studios, capturing logs from open source game engines such as [Xonotic](https://xonotic.org/), etc. 
```
USAGE: anomaly_detection_model.py --number_of_records 10000 --output_filename game_event_log.csv 
```
