#!/bin/bash
# Convenient execution script for Linux / WSL users

echo "=========================================================="
echo "    FedGen-Rare: Multi-Center Rare Disease Diagnosis      "
echo "=========================================================="
echo "1. Run 4-Way Comparative Benchmark (FedAvg, FedProx, FedIIC, FedGen-Rare)"
echo "2. Train Standalone FedGen-Rare with Checkpointing"
echo "3. Run Fast Quick-Test (3 Rounds)"
echo "4. View Latest Benchmark Metrics Table"
echo "5. Exit"
echo "=========================================================="
read -p "Select an option [1-5]: " choice

case $choice in
    1)
        read -p "Enter number of rounds (default 10): " rounds
        rounds=${rounds:-10}
        python3 run.py --mode benchmark --rounds $rounds
        ;;
    2)
        read -p "Enter number of rounds (default 12): " rounds
        rounds=${rounds:-12}
        python3 run.py --mode train --rounds $rounds
        ;;
    3)
        python3 run.py --mode quicktest
        ;;
    4)
        python3 run.py --mode results
        ;;
    5)
        echo "Exiting."
        exit 0
        ;;
    *)
        echo "Invalid option."
        exit 1
        ;;
esac
