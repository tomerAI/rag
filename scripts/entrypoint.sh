#!/bin/bash

# Run initialization script
python src/init.py

# Run dbt
cd dbt
dbt run

# Start the application
cd ..
python src/app.py 